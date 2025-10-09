import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth endpoints
export const register = (email, password) => {
  return api.post('/auth/register', { email, password });
};

export const login = async (email, password) => {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);
  
  const response = await api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token);
  }
  
  return response;
};

export const logout = () => {
  localStorage.removeItem('token');
};

export const getCurrentUser = () => {
  return api.get('/auth/me');
};

// Switch endpoints
export const getSwitches = () => {
  return api.get('/switches');
};

export const getSwitch = (id) => {
  return api.get(`/switches/${id}`);
};

export const createSwitch = (switchData) => {
  return api.post('/switches', switchData);
};

export const updateSwitch = (id, switchData) => {
  return api.patch(`/switches/${id}`, switchData);
};

export const deleteSwitch = (id) => {
  return api.delete(`/switches/${id}`);
};

export const checkIn = (id) => {
  return api.post(`/switches/${id}/checkin`);
};

export default api;
