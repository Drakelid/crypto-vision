import api from './client';

export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  notifications: {
    email: boolean;
    push: boolean;
    priceAlerts: boolean;
    predictionUpdates: boolean;
  };
  dashboard: {
    defaultView: 'overview' | 'market' | 'portfolio';
    refreshInterval: number;
  };
  apiKeys: {
    [key: string]: string;
  };
}

export const getUserSettings = async (): Promise<UserSettings> => {
  try {
    const response = await api.get<UserSettings>('/settings');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch user settings:', error);
    throw error;
  }
};

export const updateUserSettings = async (
  settings: Partial<UserSettings>
): Promise<UserSettings> => {
  try {
    const response = await api.patch<UserSettings>('/settings', settings);
    return response.data;
  } catch (error) {
    console.error('Failed to update user settings:', error);
    throw error;
  }
};

export const generateApiKey = async (name: string): Promise<string> => {
  try {
    const response = await api.post<{ key: string }>('/settings/api-keys', { name });
    return response.data.key;
  } catch (error) {
    console.error('Failed to generate API key:', error);
    throw error;
  }
};

export const revokeApiKey = async (keyId: string): Promise<void> => {
  try {
    await api.delete(`/settings/api-keys/${keyId}`);
  } catch (error) {
    console.error('Failed to revoke API key:', error);
    throw error;
  }
};
