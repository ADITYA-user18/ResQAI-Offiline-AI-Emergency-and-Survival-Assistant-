import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
import * as chatService from '../services/chatService';
import { useAuth } from './AuthContext';

const ChatContext = createContext(null);

export const ChatProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loadingChats, setLoadingChats] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [systemHealth, setSystemHealth] = useState(null);

  // Fetch all chats
  const fetchChats = useCallback(async () => {
    if (!isAuthenticated) return;
    setLoadingChats(true);
    try {
      const data = await chatService.getAllChats();
      setChats(data.chats || []);
    } catch (error) {
      console.error('Error fetching chats:', error);
    } finally {
      setLoadingChats(false);
    }
  }, [isAuthenticated]);

  // Load a single conversation
  const loadChat = useCallback(async (chatId) => {
    if (!isAuthenticated || !chatId) return;
    setLoadingMessages(true);
    try {
      const data = await chatService.getConversation(chatId);
      setCurrentChatId(chatId);
      setMessages(data.messages || []);
    } catch (error) {
      console.error(`Error loading chat ${chatId}:`, error);
      // Reset if not found or unauthorized
      setCurrentChatId(null);
      setMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  }, [isAuthenticated]);

  // Create a new empty chat
  const startNewChat = async (title = 'New Emergency Console') => {
    if (!isAuthenticated) return null;
    try {
      const newChat = await chatService.createNewChat(title);
      await fetchChats();
      setCurrentChatId(newChat.chat_id);
      setMessages([]);
      return newChat.chat_id;
    } catch (error) {
      console.error('Error creating new chat:', error);
      return null;
    }
  };

  // Send an emergency message (RAG inquiry)
  const sendQuery = async (query) => {
    if (!isAuthenticated || !query.trim()) return;
    setSendingMessage(true);

    // Optimistically push user message to UI
    const tempUserMsgId = `temp-user-${Date.now()}`;
    const userMsg = {
      message_id: tempUserMsgId,
      chat_id: currentChatId || '',
      role: 'user',
      content: query,
      created_at: new Date().toISOString(),
    };
    
    setMessages((prev) => [...prev, userMsg]);

    try {
      let tempChatId = currentChatId;
      
      // Create empty assistant message for streaming
      const assistantMsgId = `temp-assistant-${Date.now()}`;
      const assistantMsg = {
        message_id: assistantMsgId,
        chat_id: tempChatId || '',
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      await chatService.askEmergencyStream(
        query, 
        currentChatId,
        (token) => {
          setMessages((prev) => 
            prev.map(msg => 
              msg.message_id === assistantMsgId 
                ? { ...msg, content: msg.content + token }
                : msg
            )
          );
        },
        async (meta) => {
          if (!currentChatId) {
            setCurrentChatId(meta.chat_id);
            tempChatId = meta.chat_id;
            setMessages((prev) => 
              prev.map(msg => 
                (msg.message_id === tempUserMsgId || msg.message_id === assistantMsgId)
                  ? { ...msg, chat_id: meta.chat_id }
                  : msg
              )
            );
            await fetchChats();
          }
        }
      );
      
      // Pull full conversation again to get exact DB IDs
      if (tempChatId) {
        const fullConv = await chatService.getConversation(tempChatId);
        setMessages(fullConv.messages || []);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      
      // In case of failure, push a mock system error message
      const errorMsg = {
        message_id: `temp-error-${Date.now()}`,
        chat_id: currentChatId || '',
        role: 'assistant',
        content: '🚨 **CONNECTION FAILURE**: Local offline AI core could not be reached. Please check if the backend server and Ollama are active.',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => {
        // Replace the empty assistant message with the error message
        const withoutTemp = prev.filter(m => m.role !== 'assistant' || m.content !== '');
        return [...withoutTemp, errorMsg];
      });
    } finally {
      setSendingMessage(false);
    }
  };

  // Delete chat session
  const removeChat = async (chatId) => {
    if (!isAuthenticated) return;
    try {
      await chatService.deleteChat(chatId);
      await fetchChats();
      if (currentChatId === chatId) {
        setCurrentChatId(null);
        setMessages([]);
      }
    } catch (error) {
      console.error(`Error deleting chat ${chatId}:`, error);
    }
  };

  // Rename chat session
  const renameChatSession = async (chatId, title) => {
    if (!isAuthenticated) return;
    try {
      await chatService.renameChat(chatId, title);
      await fetchChats();
    } catch (error) {
      console.error(`Error renaming chat ${chatId}:`, error);
    }
  };

  // Fetch system health metrics
  const fetchHealth = useCallback(async () => {
    try {
      const health = await chatService.getSystemHealth();
      setSystemHealth(health);
    } catch (error) {
      console.error('Failed to get system health:', error);
      setSystemHealth({
        status: 'offline',
        faiss_loaded: false,
        knowledge_loaded: false,
        ollama_available: false,
        model: 'None',
        vector_count: 0,
        chunk_count: 0,
      });
    }
  }, []);

  // Sync state on authentication changes
  useEffect(() => {
    if (isAuthenticated) {
      fetchChats();
      fetchHealth();
      // Poll health every 30 seconds
      const timer = setInterval(fetchHealth, 30000);
      return () => clearInterval(timer);
    } else {
      setChats([]);
      setCurrentChatId(null);
      setMessages([]);
      setSystemHealth(null);
    }
  }, [isAuthenticated, fetchChats, fetchHealth]);

  const value = {
    chats,
    currentChatId,
    messages,
    loadingChats,
    loadingMessages,
    sendingMessage,
    systemHealth,
    fetchChats,
    loadChat,
    startNewChat,
    sendQuery,
    removeChat,
    renameChatSession,
    fetchSystemHealth: fetchHealth,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
