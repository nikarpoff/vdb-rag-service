import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: '/v1',
});

export const api = {
  // Documents
  listDocuments: () => axiosInstance.get('/documents'),
  
  uploadDocument: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axiosInstance.post('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  
  getDocument: (id) => axiosInstance.get(`/documents/${id}`),
  
  deleteDocument: (id) => axiosInstance.delete(`/documents/${id}`),
  
  // Search
  search: (query) => axiosInstance.get('/retrieve', { params: { query } }),
  
  // Chat
  chat: (message) => axiosInstance.post('/chat', { message }),
};

export default api;
