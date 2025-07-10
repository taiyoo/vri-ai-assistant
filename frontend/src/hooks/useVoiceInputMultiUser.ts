import { useState, useCallback, useRef, useEffect } from 'react';
import { Room, RoomEvent, Track } from 'livekit-client';
import useSnackbar from './useSnackbar';
import useHttp from './useHttp';

interface LiveKitTokenResponse {
  token: string;
  room: string;
  url: string;
}

interface ParticipantTranscript {
  identity: string;
  name: string;
  transcript: string;
  partial: string;
}

export const useVoiceInputMultiUser = () => {
  const { open } = useSnackbar();
  const { post } = useHttp();
  const [isJoined, setIsJoined] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [participants, setParticipants] = useState<ParticipantTranscript[]>([]);
  const roomRef = useRef<Room | null>(null);
  const [micEnabled, setMicEnabled] = useState(true);

  // Helper: get partial transcript and transcript for all participants
  const partialTranscript = participants
    .filter((p) => p.partial)
    .map((p) => `${p.name}: ${p.partial}`)
    .join('\n');
  const transcribedText = participants
    .filter((p) => p.transcript)
    .map((p) => `${p.name}: ${p.transcript}`)
    .join('\n');

  // Join room
  const joinRoom = useCallback(async () => {    
    console.log('joinRoom called');
    setIsProcessing(true);
    try {
      const { data } = await post<LiveKitTokenResponse, { room_name?: string }>(
        '/livekit/token',
        { room_name: 'multiuser-room' }
      );
      const room = new Room();
      roomRef.current = room;

      room.on(RoomEvent.Connected, () => {
        console.log('Room connected');
        setIsJoined(true);
        setIsProcessing(false);
      });

      room.on(RoomEvent.ParticipantConnected, (participant) => {
        setParticipants((prev) => [
          ...prev,
          {
            identity: participant.identity,
            name: participant.name || participant.identity,
            transcript: '',
            partial: '',
          },
        ]);
      });

      room.on(RoomEvent.ParticipantDisconnected, (participant) => {
        setParticipants((prev) =>
          prev.filter((p) => p.identity !== participant.identity)
        );
      });

      room.on(RoomEvent.TranscriptionReceived, (segments, participant) => {
        setParticipants((prev) =>
          prev.map((p) => {
            if (p.identity !== participant?.identity) return p;
            let transcript = p.transcript;
            let partial = p.partial;
            segments.forEach((segment) => {
              if (segment.final) {
                transcript += `${segment.text}\n`;
                partial = '';
              } else {
                partial = segment.text;
              }
            });
            return { ...p, transcript, partial };
          })
        );
      });

      room.on(RoomEvent.TrackSubscribed, (track, _publication, participant) => {
        if (track.kind === Track.Kind.Audio && !participant.isLocal) {
          const audioEl = new Audio();
          audioEl.srcObject = new MediaStream([track.mediaStreamTrack]);
          audioEl.play().catch(console.error);
        }
      });

      await room.connect(data.url, data.token);
      await room.localParticipant.setMicrophoneEnabled(true);
      setMicEnabled(true);

      // Add local participant
      setParticipants((prev) => [
        ...prev,
        {
          identity: room.localParticipant.identity,
          name: room.localParticipant.name || 'You',
          transcript: '',
          partial: '',
        },
      ]);
    } catch (error) {
      open('Failed to join room');
      setIsProcessing(false);
    }
  }, [open, post]);

  // Leave room
  const leaveRoom = useCallback(() => {    
    if (roomRef.current) {
      roomRef.current.disconnect();
      roomRef.current = null;
    }
    setIsJoined(false);
    setParticipants([]);
  }, []);

  // Toggle mic for local participant
  const toggleMic = useCallback(async () => {
    if (!roomRef.current) return;
    const enabled = !micEnabled;
    await roomRef.current.localParticipant.setMicrophoneEnabled(enabled);
    setMicEnabled(enabled);
  }, [micEnabled]);

  useEffect(() => {
    return () => {
      if (roomRef.current) {
        roomRef.current.disconnect();
      }
    };
  }, []);

  return {
    isJoined,
    isProcessing,
    partialTranscript,
    transcribedText,
    joinRoom,
    leaveRoom,
    participants, // still available if you want to show all users' transcripts
    micEnabled,
    toggleMic
  };
};