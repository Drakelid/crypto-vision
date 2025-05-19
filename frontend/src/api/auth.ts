import axios from './client';
import { Token, User } from '../types';

// Authentication methods
export const login = async (email: string, password: string): Promise<{ user: User; token: string }> => {
  const response = await axios.post<Token>('/auth/login/access-token', {
    username: email,
    password,
  });
  
  const { access_token } = response.data;
  localStorage.setItem('auth_token', access_token);
  
  // Get user info
  const userResponse = await axios.get<User>('/users/me');
  return { user: userResponse.data, token: access_token };
};

export const register = async (userData: {
  email: string;
  password: string;
  full_name: string;
}): Promise<{ user: User; token: string }> => {
  // Register the user
  await axios.post('/auth/register', {
    email: userData.email,
    password: userData.password,
    full_name: userData.full_name,
  });

  // Automatically log in the user after registration
  return login(userData.email, userData.password);
};

export const logout = (): void => {
  localStorage.removeItem('auth_token');
  // Optional: Call the backend to invalidate the token
  // axios.post('/auth/logout').catch(() => {});
};

export const getCurrentUser = async (): Promise<User> => {
  const response = await axios.get<User>('/users/me');
  return response.data;
};

export const updateProfile = async (data: Partial<User>): Promise<User> => {
  const response = await axios.patch<User>('/users/me', data);
  return response.data;
};

export const changePassword = async (currentPassword: string, newPassword: string): Promise<void> => {
  await axios.post('/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
  });
};

export const requestPasswordReset = async (email: string): Promise<void> => {
  await axios.post('/auth/forgot-password', { email });
};

export const resetPassword = async (token: string, newPassword: string): Promise<void> => {
  await axios.post('/auth/reset-password', {
    token,
    new_password: newPassword,
  });
};

export const verifyEmail = async (token: string): Promise<void> => {
  await axios.post('/auth/verify-email', { token });
};
