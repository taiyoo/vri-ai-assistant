import React from 'react';
import {VoiceControl} from '../components/VoiceControl';
import {useVoiceInput} from '../hooks/useVoiceInput';

const VoiceChatPage: React.FC = () => {
  // useVoiceInput should provide these states and handlers
  const {
    isRecording,
    isProcessing,
    partialTranscript,
    transcribedText,
    startRecording,
    stopRecording,
  } = useVoiceInput();

  // Format transcribed text with appropriate styling for each speaker
  const renderFormattedTranscript = (text: string) => {
    if (!text) return null;
    
    // Split by line breaks
    return text.split('\n').map((line, index) => {
      if (!line.trim()) return null;
      
      // Check if line starts with "You: " or "Assistant: "
      const isUser = line.startsWith('You:');
      const isAssistant = line.startsWith('Assistant:');
      
      if (!isUser && !isAssistant) return <div key={index}>{line}</div>;
      
      return (
        <div 
          key={index} 
          className={`mb-2 ${isUser ? 'text-blue-600' : 'text-green-600'}`}
        >
          {line}
        </div>
      );
    });
  };

  return (
    <div className="voice-chat-page flex flex-col items-center justify-center min-h-screen p-4">
      <h1 className="text-2xl font-bold mb-4">Voice Chat</h1>
      <VoiceControl
        isRecording={isRecording}
        isProcessing={isProcessing}
        partialTranscript={partialTranscript}
        onStartRecording={startRecording}
        onStopRecording={stopRecording}
        disabled={isProcessing}
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

export default VoiceChatPage;