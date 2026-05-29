import api from './api';

export const signup = async (username, password, deviceId = null) => {
  const response = await api.post('/auth/signup', {
    username,
    password,
    device_id: deviceId || `web-client-${Math.random().toString(36).substr(2, 9)}`,
  });
  if (response.data && response.data.access_token) {
    localStorage.setItem('resqai_token', response.data.access_token);
    localStorage.setItem('resqai_user', JSON.stringify(response.data.user));
  }
  return response.data;
};

export const login = async (username, password) => {
  const response = await api.post('/auth/login', {
    username,
    password,
  });
  if (response.data && response.data.access_token) {
    localStorage.setItem('resqai_token', response.data.access_token);
    localStorage.setItem('resqai_user', JSON.stringify(response.data.user));
  }
  return response.data;
};

export const logout = async () => {
  try {
    await api.post('/auth/logout');
  } catch (error) {
    console.error('Logout error on backend, clearing local storage anyway', error);
  } finally {
    localStorage.removeItem('resqai_token');
    localStorage.removeItem('resqai_user');
  }
};

export const getMe = async () => {
  const response = await api.get('/auth/me');
  if (response.data && response.data.user) {
    localStorage.setItem('resqai_user', JSON.stringify(response.data.user));
  }
  return response.data;
};

export const getStoredUser = () => {
  const user = localStorage.getItem('resqai_user');
  return user ? JSON.parse(user) : null;
};

export const getStoredToken = () => {
  return localStorage.getItem('resqai_token');
};
