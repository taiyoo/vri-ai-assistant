import { useState, useCallback, useRef, useEffect } from 'react';
import { Room, RoomEvent, Track} from 'livekit-client';
import useSnackbar from './useSnackbar';
import { useTranslation } from 'react-i18next';
import useHttp from './useHttp';

// Type definition for the token response
interface LiveKitTokenResponse {
  token: string;
  room: string;
  url: string;
}

// Add interface for cached token info
interface CachedTokenInfo {
  token: string;
  url: string;
  room: string;
  expiresAt: number; // timestamp when token expires
}

export const useVoiceInput = () => {
  const { t } = useTranslation();
  const { open } = useSnackbar();
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcribedText, setTranscribedText] = useState('');
  const [partialTranscript, setPartialTranscript] = useState('');

  const { post } = useHttp();
  
  // Room reference
  const roomRef = useRef<Room | null>(null);
  const roomNameRef = useRef<string | null>(null);
  const tokenRef = useRef<string | null>(null);
  
// Add token cache reference with expiration
  const tokenCacheRef = useRef<CachedTokenInfo | null>(null);
  
  // Helper to check if token is still valid
  const isTokenValid = useCallback(() => {
    if (!tokenCacheRef.current) return false;
    
    // Add a buffer of 30 seconds to prevent edge cases
    const bufferTime = 30 * 1000; 
    return Date.now() + bufferTime < tokenCacheRef.current.expiresAt;
  }, []);

  // Get token from the server or cache
  const getToken = useCallback(async () => {
    // Check if we have a valid cached token
    if (isTokenValid() && tokenCacheRef.current) {
      console.log('Using cached LiveKit token');
      return tokenCacheRef.current;
    }
    
    try {
      console.log('Requesting new LiveKit token');
      const { data } = await post<LiveKitTokenResponse, { room_name?: string }>(
        '/livekit/token',
        { room_name: roomNameRef.current || undefined }
      );
      
      // Store the token and room information
      tokenRef.current = data.token;
      roomNameRef.current = data.room;
      
      // Cache the token with expiration (LiveKit default is 1 hour)
      // We'll set it to 50 minutes to be safe
      const expiresAt = Date.now() + (50 * 60 * 1000);
      
      const tokenInfo = {
        token: data.token,
        url: data.url,
        room: data.room,
        expiresAt
      };
      
      tokenCacheRef.current = tokenInfo;
      
      return tokenInfo;
    } catch (error) {
      console.error('Error getting LiveKit token:', error);
      open(t('error.tokenFetchFailed'));
      throw error;
    }
  }, [post, open, t, isTokenValid]);
  
  
  // Start recording
  const startRecording = useCallback(async () => {
    try {
      // Clear previous transcriptions when starting a new session
      setTranscribedText('');
      setPartialTranscript('');

      setIsProcessing(true);
      
      // Get token and LiveKit URL
      const { token, url } = await getToken();
      
      // Create and connect to room
      const room = new Room({
        adaptiveStream: true,
        dynacast: true,
        audioCaptureDefaults: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000, // Better for transcription
        }
      });
      
      // Add more verbose logging
      room.on(RoomEvent.Connected, () => {
        console.log('Connected to LiveKit room:', room.name);
      });
      
      room.on(RoomEvent.ParticipantConnected, (participant) => {
        console.log('Participant connected:', participant.identity);
      });
      
      // Handle transcription events
      room.on(RoomEvent.TranscriptionReceived, (transcriptionSegments, participant) => {
        console.log('Transcription segments received:', transcriptionSegments);
        console.log('From participant:', participant?.identity);
        
        // Determine speaker type (user or assistant)
        const speakerName = participant?.isLocal ? 'You' : 'Assistant';
        
        transcriptionSegments.forEach(segment => {
          // segment.text: the transcribed text
          // segment.final: whether this is a final segment
          if (segment.final) {
            setTranscribedText(prev => {
              // Only add a new line if the previous text doesn't end with a newline
              const separator = prev && !prev.endsWith('\n') ? '\n' : '';
              return `${prev}${separator}${speakerName}: ${segment.text}\n`;
            });
            setPartialTranscript('');
          } else {
            setPartialTranscript(`${speakerName}: ${segment.text}`);
          }
        });
      });

      // Add this to your useVoiceInput hook
      room.on(RoomEvent.TrackSubscribed, (track, _publication, participant) => {
        console.log('Track subscribed:', {
          kind: track.kind,
          participantId: participant.identity
        });
        
        // Automatically play audio tracks from other participants (like the agent)
        if (track.kind === Track.Kind.Audio && !participant.isLocal) {
          console.log('Playing audio from participant:', participant.identity);
          // Create an audio element to play the track
          const audioEl = new Audio();
          audioEl.srcObject = new MediaStream([track.mediaStreamTrack]);
          audioEl.play().catch(console.error);
        }
      });

      // Connect to LiveKit server
      console.log('Connecting to LiveKit server:', url);
      await room.connect(url, token);
      console.log('Successfully connected to room:', room.name);
      
      // Enable local microphone with explicit options
      try {
        console.log('Enabling microphone...');
        await room.localParticipant.setMicrophoneEnabled(true, {
          noiseSuppression: true,
          echoCancellation: true,
          autoGainControl: true
        });
        console.log('Microphone enabled successfully');
      } catch (error) {
        console.error('Error starting recording:', error);
        setIsProcessing(false);
        open(t('error.microphoneAccessFailed'));
      }
      
      // Store room reference
      roomRef.current = room;
      
      setIsRecording(true);
      setIsProcessing(false);
    } catch (error) {
      // Existing error handling...
    }
  }, [getToken, open, t]);
  
  // Stop recording
  const stopRecording = useCallback(() => {
    if (!isRecording) return;
    
    setIsProcessing(true);
    
    try {
      // Disconnect from room if connected
      if (roomRef.current) {
        roomRef.current.disconnect();
        roomRef.current = null;
      }
    } catch (error) {
      console.error('Error stopping recording:', error);
    }
    
    setIsRecording(false);
    setIsProcessing(false);
  }, [isRecording]);
  
  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (roomRef.current) {
        roomRef.current.disconnect();
      }
    };
  }, []);
  
  return {
    isRecording,
    isProcessing,
    transcribedText,
    partialTranscript,
    startRecording,
    stopRecording,
  };
};