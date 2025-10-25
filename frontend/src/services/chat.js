import api from './api';

export const chatService = {
  async query(question) {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const response = await api.post('/chat/query', { 
        query: question,
        user_id: user.user_id || 1
      });
      return response.data;
    } catch (error) {
      throw error.response?.data?.message || 'Failed to get chat response';
    }
  },

  async getKnowledgeBase() {
    try {
      const response = await api.get('/chat/kb');
      return response.data;
    } catch (error) {
      throw error.response?.data?.message || 'Failed to fetch knowledge base';
    }
  },

  async getChatLogs() {
    try {
      const response = await api.get('/chat/logs');
      return response.data;
    } catch (error) {
      throw error.response?.data?.message || 'Failed to fetch chat logs';
    }
  }
};