import axios from 'axios';

// API base URL - defaults to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

/**
 * Analyze audio file
 * @param {File} file - Audio file to analyze
 * @returns {Promise} Analysis results
 */
export const analyzeAudio = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post('/api/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing audio:', error);
    throw error;
  }
};

/**
 * Get API health status
 * @returns {Promise} Health status
 */
export const getHealth = async () => {
  try {
    const response = await api.get('/api/health');
    return response.data;
  } catch (error) {
    console.error('Error checking API health:', error);
    throw error;
  }
};

/**
 * Get supported formats
 * @returns {Promise} Supported formats and limits
 */
export const getFormats = async () => {
  try {
    const response = await api.get('/api/formats');
    return response.data;
  } catch (error) {
    console.error('Error fetching formats:', error);
    throw error;
  }
};

export default api;
