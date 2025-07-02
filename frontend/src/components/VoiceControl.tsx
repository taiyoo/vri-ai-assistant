import React, { useState } from 'react';
import { PiMicrophone, PiMicrophoneSlash } from 'react-icons/pi';
import './VoiceControl.css';
interface VoiceControlProps {
  // Existing props
  disabled?: boolean;
  className?: string;
  onTranscriptionReceived?: (text: string) => void;
  // TTS props
  ttsEnabled?: boolean;
  onToggleTts?: () => void;
  textToSpeak?: string;
  isSpeaking?: boolean;
  onSpeakComplete?: () => void;
  // Props for recording control
  isRecording?: boolean;
  isProcessing?: boolean;
  partialTranscript?: string;
  onStartRecording?: () => Promise<void>;
  onStopRecording?: () => void;
}

export const VoiceControl: React.FC<VoiceControlProps> = ({ 
  disabled = false,
  className = '',
  onTranscriptionReceived,
  isRecording = false,
  isProcessing = false,
  partialTranscript = '',
  onStartRecording,
  onStopRecording
}) => {
  const [error, setError] = useState<string | null>(null);
  
  // Handle microphone button click
  const handleMicClick = async () => {
    if (disabled || isProcessing) return;
    
    try {
      if (isRecording) {
        onStopRecording?.();
      } else {
        await onStartRecording?.();
      }
    } catch (error) {
      console.error('Error toggling recording:', error);
      setError('Failed to access microphone. Please check permissions.');
    }
  };
  
  return (
    <div className={`voice-control ${className} ${disabled ? 'disabled' : ''}`}>
      {/* Transcription display */}
      <div className="transcription-container">
        {partialTranscript && (
          <div className="transcription-bubble partial">
            {partialTranscript}
          </div>
        )}
        {onTranscriptionReceived && (
          <div className="transcription-display">
            {/* This would show final transcriptions */}
          </div>
        )}
      </div>
      
      {/* Error message if any */}
      {error && (
        <div className="voice-control-error">
          {error}
        </div>
      )}
      
      <div className="voice-control-buttons">
        {/* Microphone toggle button */}
        <button
          onClick={handleMicClick}
          disabled={disabled || isProcessing}
          className={`mic-button ${isRecording ? 'recording' : ''} ${isProcessing ? 'processing' : ''} ${disabled ? 'disabled' : ''}`}
          aria-label={isRecording ? "Stop recording" : "Start recording"}
        >
          {isProcessing ? (
            <div className="loading-spinner"></div>
          ) : isRecording ? (
            <PiMicrophoneSlash size={20} />
          ) : (
            <PiMicrophone size={20} />
          )}
        </button>
      </div>
    </div>
  );
};