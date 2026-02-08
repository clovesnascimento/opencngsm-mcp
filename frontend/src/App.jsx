import React, { useState } from 'react';
import VoiceButton from './components/VoiceButton';
import './App.css';

/**
 * Example App using VoiceButton
 */
function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');

  // Handle voice transcription
  const handleVoiceTranscript = (transcription) => {
    console.log('Voice transcription:', transcription);

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: transcription,
      isVoice: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);

    // Simulate bot response (replace with actual API call)
    setTimeout(() => {
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        text: `You said (via voice): "${transcription}"`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
    }, 500);
  };

  // Handle text input
  const handleTextSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: inputText,
      isVoice: false,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');

    // Simulate bot response
    setTimeout(() => {
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        text: `You said: "${inputText}"`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
    }, 500);
  };

  // Handle voice error
  const handleVoiceError = (error) => {
    console.error('Voice error:', error);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🤖 OpenCngsm v3.0</h1>
        <p>Chat with text or voice</p>
      </header>

      <main className="app-main">
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <p>👋 Start a conversation!</p>
              <p className="hint">Type a message or use the voice button</p>
            </div>
          ) : (
            messages.map(msg => (
              <div
                key={msg.id}
                className={`message ${msg.type}`}
              >
                <div className="message-content">
                  {msg.isVoice && <span className="voice-badge">🎤</span>}
                  {msg.text}
                </div>
                <div className="message-time">
                  {msg.timestamp.toLocaleTimeString()}
                </div>
              </div>
            ))
          )}
        </div>

        <div className="input-container">
          <form onSubmit={handleTextSubmit} className="text-input-form">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type a message..."
              className="text-input"
            />
            <button type="submit" className="send-button">
              Send
            </button>
          </form>

          <div className="voice-input-section">
            <VoiceButton
              onTranscript={handleVoiceTranscript}
              onError={handleVoiceError}
              apiUrl="/api/voice/transcribe"
              language="pt"
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
