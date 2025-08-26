import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

const analysisService = {
  // Upload file for analysis
  uploadFile: async (file, onUploadProgress) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API_URL}/analysis/upload`, formData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get all analyses for current user
  getAnalyses: async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/analysis`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get specific analysis by ID
  getAnalysis: async (analysisId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/analysis/${analysisId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Update analysis
  updateAnalysis: async (analysisId, updateData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.put(`${API_URL}/analysis/${analysisId}`, updateData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Delete analysis
  deleteAnalysis: async (analysisId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.delete(`${API_URL}/analysis/${analysisId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Download analysis report
  downloadReport: async (analysisId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/analysis/${analysisId}/download`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get public analyses
  getPublicAnalyses: async () => {
    try {
      const response = await axios.get(`${API_URL}/analysis/public`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get analysis status
  getAnalysisStatus: async (analysisId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/analysis/${analysisId}/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  }
};

export default analysisService;
