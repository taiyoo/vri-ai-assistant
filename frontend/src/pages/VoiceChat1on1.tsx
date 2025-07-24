import React from 'react';
import {VoiceControl} from '../components/VoiceControl';

interface VoiceChat1on1Props {
  isRecording: boolean;
  isProcessing: boolean;
  partialTranscript: string;
  onStartRecording: () => Promise<void>;
  onStopRecording: () => void;
  disabled: boolean;
  renderFormattedTranscript: (text: string) => (React.ReactNode | null)[] | null;
  transcribedText: string;
}

const VoiceChat1on1: React.FC<VoiceChat1on1Props> = ({
  isRecording,
  isProcessing,
  partialTranscript,
  onStartRecording,
  onStopRecording,
  disabled,
  renderFormattedTranscript,
  transcribedText,
}) => {
  return (
    <div className="flex flex-col items-center w-full">
      <VoiceControl
        isRecording={isRecording}
        isProcessing={isProcessing}
        partialTranscript={partialTranscript}
        onStartRecording={onStartRecording}
        onStopRecording={onStopRecording}
        disabled={disabled}
      />
      <div className="mt-6 w-full max-w-xl">
        {partialTranscript && (
          <>
            <div className="mb-2 text-gray-500">Live Transcript:</div>
            <div className="p-3 bg-gray-100 rounded min-h-[2rem] mb-4">
              <div className={partialTranscript.startsWith('You:') ? 'text-blue-600' : 'text-green-600'}>
                {partialTranscript}
              </div>
            </div>
          </>
        )}
        {transcribedText && (
          <>
            <div className="mb-2 text-gray-500">Conversation:</div>
            <div className="p-3 bg-white border rounded min-h-[2rem] max-h-96 overflow-y-auto">
              {renderFormattedTranscript(transcribedText)}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default VoiceChat1on1;
