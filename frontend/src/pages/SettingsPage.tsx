import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormGroup,
  FormControlLabel,
  Switch,
  Button,
  Divider,
  TextField,
  Grid,
  Alert,
  CircularProgress,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  SelectChangeEvent,
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import Page from '../components/Page';
import { useAuth } from '../contexts/AuthContext';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as settingsApi from '../api/settings';

type ThemeMode = 'light' | 'dark' | 'system';

type Settings = {
  theme: ThemeMode;
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
};

const defaultSettings: Settings = {
  theme: 'system',
  notifications: {
    email: true,
    push: true,
    priceAlerts: true,
    predictionUpdates: true,
  },
  dashboard: {
    defaultView: 'overview',
    refreshInterval: 60, // seconds
  },
  apiKeys: {},
};

const SettingsPage: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [settings, setSettings] = useState<Settings>(defaultSettings);
  const [isDirty, setIsDirty] = useState(false);
  const [saveStatus, setSaveStatus] = useState<{
    type: 'idle' | 'success' | 'error';
    message: string;
  }>({ type: 'idle', message: '' });

  // Fetch user settings
  const { data: userSettings, isLoading } = useQuery(
    ['userSettings'],
    () => settingsApi.getUserSettings(),
    {
      enabled: !!user,
      onSuccess: (data) => {
        if (data) {
          setSettings({ ...defaultSettings, ...data });
        }
      },
    }
  );

  // Save settings mutation
  const saveSettingsMutation = useMutation(
    (newSettings: Settings) => settingsApi.updateUserSettings(newSettings),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['userSettings']);
        setSaveStatus({
          type: 'success',
          message: 'Settings saved successfully!',
        });
        setIsDirty(false);
        // Hide success message after 3 seconds
        setTimeout(
          () => setSaveStatus({ type: 'idle', message: '' }),
          3000
        );
      },
      onError: (error: any) => {
        setSaveStatus({
          type: 'error',
          message: error.message || 'Failed to save settings',
        });
      },
    }
  );

  // Reset settings to default
  const resetToDefaults = () => {
    if (window.confirm('Are you sure you want to reset all settings to default?')) {
      setSettings(defaultSettings);
      setIsDirty(true);
    }
  };

  // Handle form field changes
  const handleSettingChange = (path: string, value: any) => {
    const pathParts = path.split('.');
    setSettings((prev) => {
      const newSettings = { ...prev };
      let current: any = newSettings;

      // Navigate to the nested property
      for (let i = 0; i < pathParts.length - 1; i++) {
        current = current[pathParts[i]];
      }

      // Update the value
      current[pathParts[pathParts.length - 1]] = value;
      return newSettings;
    });
    setIsDirty(true);
  };

  // Handle theme change
  const handleThemeChange = (event: SelectChangeEvent<ThemeMode>) => {
    const theme = event.target.value as ThemeMode;
    handleSettingChange('theme', theme);
    // Apply theme
    if (theme === 'system') {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.setAttribute(
        'data-theme',
        prefersDark ? 'dark' : 'light'
      );
    } else {
      document.documentElement.setAttribute('data-theme', theme);
    }
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    saveSettingsMutation.mutate(settings);
  };

  // Apply theme on initial load
  useEffect(() => {
    if (userSettings?.theme) {
      if (userSettings.theme === 'system') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute(
          'data-theme',
          prefersDark ? 'dark' : 'light'
        );
      } else {
        document.documentElement.setAttribute('data-theme', userSettings.theme);
      }
    }
  }, [userSettings?.theme]);

  if (isLoading) {
    return (
      <Page title="Settings">
        <CircularProgress />
      </Page>
    );
  }

  return (
    <Page
      title="Settings"
      actions={
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            onClick={resetToDefaults}
            disabled={saveSettingsMutation.isLoading}
          >
            Reset to Defaults
          </Button>
          <Button
            variant="contained"
            startIcon={
              saveSettingsMutation.isLoading ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <SaveIcon />
              )
            }
            onClick={handleSubmit}
            disabled={!isDirty || saveSettingsMutation.isLoading}
          >
            Save Changes
          </Button>
        </Box>
      }
    >
      {saveStatus.type !== 'idle' && (
        <Alert
          severity={saveStatus.type}
          sx={{ mb: 3 }}
          onClose={() => setSaveStatus({ type: 'idle', message: '' })}
        >
          {saveStatus.message}
        </Alert>
      )}

      <Grid container spacing={4}>
        {/* Appearance Settings */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Appearance
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <FormControl fullWidth margin="normal">
              <InputLabel id="theme-select-label">Theme</InputLabel>
              <Select
                labelId="theme-select-label"
                id="theme-select"
                value={settings.theme}
                label="Theme"
                onChange={handleThemeChange}
              >
                <MenuItem value="light">Light</MenuItem>
                <MenuItem value="dark">Dark</MenuItem>
                <MenuItem value="system">System Default</MenuItem>
              </Select>
            </FormControl>
          </Paper>
        </Grid>

        {/* Dashboard Settings */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Dashboard
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <FormControl fullWidth margin="normal">
              <InputLabel id="default-view-label">Default View</InputLabel>
              <Select
                labelId="default-view-label"
                id="default-view"
                value={settings.dashboard.defaultView}
                label="Default View"
                onChange={(e) =>
                  handleSettingChange(
                    'dashboard.defaultView',
                    e.target.value
                  )
                }
              >
                <MenuItem value="overview">Overview</MenuItem>
                <MenuItem value="market">Market</MenuItem>
                <MenuItem value="portfolio">Portfolio</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              margin="normal"
              label="Refresh Interval (seconds)"
              type="number"
              value={settings.dashboard.refreshInterval}
              onChange={(e) =>
                handleSettingChange(
                  'dashboard.refreshInterval',
                  parseInt(e.target.value) || 60
                )
              }
              inputProps={{ min: 10, max: 3600 }}
              helperText="How often to refresh dashboard data"
            />
          </Paper>
        </Grid>

        {/* Notification Settings */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Notifications
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Typography variant="subtitle2" gutterBottom>
              Email Notifications
            </Typography>
            <FormGroup>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.notifications.email}
                    onChange={(e) =>
                      handleSettingChange(
                        'notifications.email',
                        e.target.checked
                      )
                    }
                  />
                }
                label="Enable email notifications"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.notifications.priceAlerts}
                    onChange={(e) =>
                      handleSettingChange(
                        'notifications.priceAlerts',
                        e.target.checked
                      )
                    }
                    disabled={!settings.notifications.email}
                  />
                }
                label="Price alerts"
                sx={{ ml: 4 }}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.notifications.predictionUpdates}
                    onChange={(e) =>
                      handleSettingChange(
                        'notifications.predictionUpdates',
                        e.target.checked
                      )
                    }
                    disabled={!settings.notifications.email}
                  />
                }
                label="Prediction updates"
                sx={{ ml: 4 }}
              />
            </FormGroup>

            <Divider sx={{ my: 3 }} />

            <Typography variant="subtitle2" gutterBottom>
              Push Notifications
            </Typography>
            <FormGroup>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.notifications.push}
                    onChange={(e) =>
                      handleSettingChange(
                        'notifications.push',
                        e.target.checked
                      )
                    }
                  />
                }
                label="Enable push notifications"
              />
            </FormGroup>
          </Paper>
        </Grid>

        {/* API Keys */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              API Keys
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Typography variant="body2" color="text.secondary" paragraph>
              Manage your API keys for programmatic access to your account.
            </Typography>

            <Box>
              {Object.entries(settings.apiKeys).map(([key, value]) => (
                <Box
                  key={key}
                  display="flex"
                  alignItems="center"
                  gap={2}
                  mb={2}
                >
                  <TextField
                    label="Key Name"
                    value={key}
                    disabled
                    sx={{ flex: 1 }}
                  />
                  <TextField
                    label="API Key"
                    value={value}
                    type="password"
                    disabled
                    sx={{ flex: 2 }}
                  />
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={() => {
                      const newApiKeys = { ...settings.apiKeys };
                      delete newApiKeys[key];
                      handleSettingChange('apiKeys', newApiKeys);
                    }}
                  >
                    Revoke
                  </Button>
                </Box>
              ))}

              <Button
                variant="outlined"
                onClick={() => {
                  const newKeyName = `API Key ${Object.keys(settings.apiKeys).length + 1}`;
                  const newApiKeys = {
                    ...settings.apiKeys,
                    [newKeyName]: `api_${Math.random().toString(36).substr(2, 32)}`,
                  };
                  handleSettingChange('apiKeys', newApiKeys);
                }}
                sx={{ mt: 2 }}
              >
                Generate New API Key
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Page>
  );
};

export default SettingsPage;
