import React from 'react';
import { PiMicrophone, PiMicrophoneSlash, PiSignInFill, PiSignOutFill } from 'react-icons/pi';
interface VoiceChatMultiUserProps {
  isJoined: boolean; 
  isProcessing: boolean;
  partialTranscript: string;
  onJoinRoom: () => Promise<void>; 
  onLeaveRoom: () => void;          
  disabled: boolean;
  renderFormattedTranscript: (text: string) => (React.ReactElement | null)[] | null;
  transcribedText: string;
  participants: { name: string; identity: string }[];
  micEnabled: boolean;
  toggleMic: () => void;
}

const VoiceChatMultiUser: React.FC<VoiceChatMultiUserProps> = ({
  isJoined,
  isProcessing,
  partialTranscript,
  onJoinRoom,
  onLeaveRoom,
  disabled,
  renderFormattedTranscript,
  transcribedText,
  participants,
  micEnabled,
  toggleMic,
}) => {
  return (
    <div>
      <div className="flex gap-2 mb-4">
        {!isJoined ? (
          <button
            onClick={onJoinRoom}
            disabled={disabled || isProcessing}
            className="flex items-center gap-1 px-3 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
          >
            <PiSignInFill size={20} />
            Join Room
          </button>
        ) : (
          <button
            onClick={onLeaveRoom}
            disabled={disabled || isProcessing}
            className="flex items-center gap-1 px-3 py-2 rounded bg-red-600 text-white hover:bg-red-700"
          >
            <PiSignOutFill size={20} />
            Leave Room
          </button>
        )}
        {isJoined && (
          <button
            onClick={toggleMic}
            disabled={disabled || isProcessing}
            className="flex items-center gap-1 px-3 py-2 rounded bg-gray-200 hover:bg-gray-300"
          >
            {micEnabled ? (
              <>
                <PiMicrophone size={20} className="text-green-600" />
                Mic On
              </>
            ) : (
              <>
                <PiMicrophoneSlash size={20} className="text-gray-500" />
                Mic Off
              </>
            )}
          </button>
        )}
      </div>
      <div className="mb-4">
        <strong>Participants:</strong>
        <ul>
          {participants.map((p) => (
            <li key={p.identity}>{p.identity}</li>
          ))}
        </ul>
      </div>
      <div>
        <strong>Partial Transcript:</strong> {partialTranscript}
      </div>
      <div>
        <strong>Transcript:</strong>
        {renderFormattedTranscript(transcribedText)}
      </div>
      {isProcessing && <div>Processing...</div>}
    </div>
  );
};

export default VoiceChatMultiUser;