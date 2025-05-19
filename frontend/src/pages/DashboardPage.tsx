import React from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import Page from '../components/Page';
import { useQuery } from '@tanstack/react-query';
import * as cryptoApi from '../api/crypto';
import { formatCurrency } from '../utils/format';

const DashboardPage: React.FC = () => {
  const { data: cryptocurrencies, isLoading } = useQuery(
    ['cryptocurrencies'],
    () => cryptoApi.getCryptocurrencies()
  );

  // Mock data for the dashboard
  const stats = [
    { title: 'Total Cryptocurrencies', value: cryptocurrencies?.length || 0, change: '+5%' },
    { title: 'Active Predictions', value: '24', change: '+12%' },
    { title: 'Prediction Accuracy', value: '87.5%', change: '+2.3%' },
    { title: 'Total Users', value: '1,284', change: '+15%' },
  ];

  return (
    <Page title="Dashboard">
      <Grid container spacing={3}>
        {/* Stats Cards */}
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                {stat.title}
              </Typography>
              <Box display="flex" alignItems="flex-end">
                <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mr: 1 }}>
                  {stat.value}
                </Typography>
                <Typography
                  variant="body2"
                  color={stat.change.startsWith('+') ? 'success.main' : 'error.main'}
                  sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}
                >
                  {stat.change}
                </Typography>
              </Box>
            </Paper>
          </Grid>
        ))}

        {/* Recent Predictions */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Recent Predictions
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Your recent cryptocurrency price predictions will appear here.
            </Typography>
            {/* Add a chart or table here */}
          </Paper>
        </Grid>

        {/* Market Overview */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Market Overview
            </Typography>
            {isLoading ? (
              <Typography>Loading...</Typography>
            ) : (
              <Box>
                {cryptocurrencies?.slice(0, 5).map((crypto) => (
                  <Box key={crypto.id} display="flex" justifyContent="space-between" mb={2}>
                    <Typography>{crypto.name}</Typography>
                    <Typography fontWeight="bold">
                      {formatCurrency(0)} {/* Replace with actual price data */}
                    </Typography>
                  </Box>
                ))}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Page>
  );
};

export default DashboardPage;
