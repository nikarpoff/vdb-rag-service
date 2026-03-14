import { useState, useCallback } from 'react';
import { api } from '../api';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = useCallback(async (content) => {
    setLoading(true);
    setError(null);
    
    // Add user message
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content,
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await api.chat(content);
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.message,
        sources: response.data.sources || [],
      };
      setMessages(prev => [...prev, assistantMessage]);
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearChat,
  };
}
