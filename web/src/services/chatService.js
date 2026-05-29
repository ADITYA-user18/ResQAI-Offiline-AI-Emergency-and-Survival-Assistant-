import api from './api';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const askEmergencyStream = async (query, chatId = null, onChunk, onMetadata) => {
  const token = localStorage.getItem('resqai_token');
  const payload = { query };
  if (chatId) payload.chat_id = chatId;

  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop(); // Keep the incomplete line in the buffer
    
    for (const line of lines) {
      if (line.trim().startsWith('data: ')) {
        try {
          const data = JSON.parse(line.trim().slice(6));
          if (data.type === 'metadata') {
            if (onMetadata) onMetadata(data);
          } else if (data.type === 'chunk') {
            if (onChunk) onChunk(data.content);
          }
        } catch (e) {
          // ignore parsing errors for partial JSON chunks if any
        }
      }
    }
  }
};

export const createNewChat = async (title = 'New Chat') => {
  const response = await api.post('/new-chat', { title });
  return response.data;
};

export const getAllChats = async () => {
  const response = await api.get('/chats');
  return response.data;
};

export const getConversation = async (chatId) => {
  const response = await api.get(`/chat/${chatId}`);
  return response.data;
};

export const deleteChat = async (chatId) => {
  const response = await api.delete(`/chat/${chatId}`);
  return response.data;
};

export const renameChat = async (chatId, title) => {
  const response = await api.patch(`/chat/${chatId}/title`, { title });
  return response.data;
};

export const getSystemHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};
