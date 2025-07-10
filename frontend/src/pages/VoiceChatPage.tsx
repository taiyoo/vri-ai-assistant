import React, { useState } from 'react';
import { useVoiceInput } from '../hooks/useVoiceInput';
import { useVoiceInputMultiUser } from '../hooks/useVoiceInputMultiUser';
import VoiceChat1on1 from './VoiceChat1on1';
import VoiceChatMultiUser from './VoiceChatMultiUser';

const TABS = [
  { label: 'Voice chat - 1on1', key: '1on1' },
  { label: 'Voice chat - multiuser', key: 'multiuser' },
];

const VoiceChatPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('1on1');
  const oneOnOne = useVoiceInput();
  const multiUser = useVoiceInputMultiUser();

  const renderFormattedTranscript = (text: string) => {
    if (!text) return null;
    return text.split('\n').map((line, index) => {
      if (!line.trim()) return null;
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
    <div className="voice-chat-page min-h-screen flex flex-col">
      {/* Header: Title and Tabs */}
      <div className="w-full flex flex-col items-center pt-8 pb-2 bg-white z-10">
        <h1 className="text-2xl font-bold mb-2">Voice Chat</h1>
        <div className="flex space-x-4 mb-2">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              className={`px-4 py-2 rounded font-medium border-b-2 transition-colors duration-150 ${
                activeTab === tab.key
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-blue-600'
              }`}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      {/* Main Content: Centered */}
      <div className="flex-1 flex flex-col items-center justify-center">
        <div className="w-full max-w-xl">
          {activeTab === '1on1' && (
            <VoiceChat1on1
              isRecording={oneOnOne.isRecording}
              isProcessing={oneOnOne.isProcessing}
              partialTranscript={oneOnOne.partialTranscript}
              onStartRecording={oneOnOne.startRecording}
              onStopRecording={oneOnOne.stopRecording}
              disabled={oneOnOne.isProcessing}
              renderFormattedTranscript={renderFormattedTranscript}
              transcribedText={oneOnOne.transcribedText}
            />
          )}
          {activeTab === 'multiuser' && (
            <VoiceChatMultiUser
              isJoined={multiUser.isJoined}
              isProcessing={multiUser.isProcessing}
              partialTranscript={multiUser.partialTranscript}
              onJoinRoom={multiUser.joinRoom}
              onLeaveRoom={multiUser.leaveRoom}
              disabled={multiUser.isProcessing}
              renderFormattedTranscript={renderFormattedTranscript}
              transcribedText={multiUser.transcribedText}
              participants={multiUser.participants}
              micEnabled={multiUser.micEnabled}
              toggleMic={multiUser.toggleMic}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default VoiceChatPage;