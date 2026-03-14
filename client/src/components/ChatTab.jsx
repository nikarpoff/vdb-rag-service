import { useState, useRef, useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import './ChatTab.css';

export function ChatTab() {
  const { messages, loading, sendMessage, clearChat } = useChat();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    
    const message = input;
    setInput('');
    await sendMessage(message);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-tab">
      <div className="chat-container">
        <div className="chat-messages" id="chatMessages">
          {messages.length === 0 ? (
            <div className="empty-chat">
              <div className="empty-icon">💬</div>
              <div className="empty-title">Начните диалог</div>
              <div className="empty-text">
                Задайте вопрос, и LLM найдёт релевантную информацию в ваших документах
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  {msg.role === 'assistant' && msg.sources?.length > 0 && (
                    <div className="context-badge">
                      📚 Использован контекст из {msg.sources.length} документов
                    </div>
                  )}
                  <div className="message-text">{msg.content}</div>
                  {msg.role === 'assistant' && msg.sources?.length > 0 && (
                    <div className="sources">
                      Источники: {msg.sources.join(', ')}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          
          {loading && (
            <div className="message assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input-container" onSubmit={handleSubmit}>
          <div className="chat-input-wrapper">
            <textarea
              className="chat-input"
              placeholder="Введите ваш вопрос..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={loading}
            />
            <button 
              type="submit" 
              className="send-btn"
              disabled={loading || !input.trim()}
            >
              ➤
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
