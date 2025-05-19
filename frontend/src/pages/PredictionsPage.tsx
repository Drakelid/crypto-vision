import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  SelectChangeEvent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Tooltip,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import Page from '../components/Page';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as cryptoApi from '../api/crypto';
import { formatCurrency, formatDate } from '../utils/format';
import { Prediction } from '../types';

const PredictionsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedPrediction, setSelectedPrediction] = useState<Prediction | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    cryptocurrency_id: '',
    model_version_id: '',
    timestamp: new Date(),
    prediction_time: new Date(),
    horizon: '1d',
    predicted_price: '',
  });

  // Fetch data
  const { data: predictions = [], isLoading } = useQuery(
    ['predictions'],
    () => cryptoApi.getPredictions()
  );

  const { data: cryptocurrencies = [] } = useQuery(
    ['cryptocurrencies'],
    () => cryptoApi.getCryptocurrencies()
  );

  const { data: modelVersions = [] } = useQuery(
    ['modelVersions'],
    () => cryptoApi.getModelVersions()
  );

  // Mutations
  const createPrediction = useMutation(
    (data: any) => cryptoApi.createPrediction(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['predictions']);
        handleCloseForm();
      },
    }
  );

  const updatePrediction = useMutation(
    ({ id, data }: { id: number; data: any }) => cryptoApi.updatePrediction(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['predictions']);
        handleCloseForm();
      },
    }
  );

  const deletePrediction = useMutation(
    (id: number) => cryptoApi.deletePrediction(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['predictions']);
      },
    }
  );

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleOpenForm = (prediction: Prediction | null = null) => {
    if (prediction) {
      setSelectedPrediction(prediction);
      setFormData({
        cryptocurrency_id: prediction.cryptocurrency_id.toString(),
        model_version_id: prediction.model_version_id.toString(),
        timestamp: new Date(prediction.timestamp),
        prediction_time: new Date(prediction.prediction_time),
        horizon: prediction.horizon,
        predicted_price: prediction.predicted_price.toString(),
      });
    } else {
      setSelectedPrediction(null);
      setFormData({
        cryptocurrency_id: '',
        model_version_id: '',
        timestamp: new Date(),
        prediction_time: new Date(),
        horizon: '1d',
        predicted_price: '',
      });
    }
    setIsFormOpen(true);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setSelectedPrediction(null);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSelectChange = (e: SelectChangeEvent) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleDateChange = (name: string, date: Date | null) => {
    if (date) {
      setFormData(prev => ({
        ...prev,
        [name]: date,
      }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = {
      ...formData,
      cryptocurrency_id: parseInt(formData.cryptocurrency_id, 10),
      model_version_id: parseInt(formData.model_version_id, 10),
      predicted_price: parseFloat(formData.predicted_price),
    };

    if (selectedPrediction) {
      updatePrediction.mutate({ id: selectedPrediction.id, data });
    } else {
      createPrediction.mutate(data);
    }
  };

  return (
    <Page
      title="Predictions"
      actions={
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenForm()}
        >
          New Prediction
        </Button>
      }
    >
      <Grid container spacing={3}>
        {/* Predictions Table */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Cryptocurrency</TableCell>
                    <TableCell>Model Version</TableCell>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Prediction Time</TableCell>
                    <TableCell>Horizon</TableCell>
                    <TableCell align="right">Predicted Price</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {isLoading ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        Loading...
                      </TableCell>
                    </TableRow>
                  ) : predictions.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        No predictions found. Create your first prediction!
                      </TableCell>
                    </TableRow>
                  ) : (
                    predictions
                      .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                      .map((prediction) => (
                        <TableRow key={prediction.id}>
                          <TableCell>
                            {prediction.cryptocurrency?.name || 'N/A'}
                          </TableCell>
                          <TableCell>
                            {prediction.model_version_id}
                          </TableCell>
                          <TableCell>{formatDate(prediction.timestamp)}</TableCell>
                          <TableCell>{formatDate(prediction.prediction_time)}</TableCell>
                          <TableCell>{prediction.horizon}</TableCell>
                          <TableCell align="right">
                            {formatCurrency(prediction.predicted_price)}
                          </TableCell>
                          <TableCell>
                            <Tooltip title="Edit">
                              <IconButton
                                size="small"
                                onClick={() => handleOpenForm(prediction)}
                              >
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete">
                              <IconButton
                                size="small"
                                onClick={() => deletePrediction.mutate(prediction.id)}
                                color="error"
                              >
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={predictions.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />
          </Paper>
        </Grid>
      </Grid>

      {/* Add/Edit Prediction Dialog */}
      {isFormOpen && (
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            {selectedPrediction ? 'Edit Prediction' : 'Create New Prediction'}
          </Typography>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth margin="normal" required>
                  <InputLabel>Cryptocurrency</InputLabel>
                  <Select
                    name="cryptocurrency_id"
                    value={formData.cryptocurrency_id}
                    onChange={handleSelectChange}
                    label="Cryptocurrency"
                  >
                    {cryptocurrencies.map((crypto) => (
                      <MenuItem key={crypto.id} value={crypto.id.toString()}>
                        {crypto.name} ({crypto.symbol.toUpperCase()})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth margin="normal" required>
                  <InputLabel>Model Version</InputLabel>
                  <Select
                    name="model_version_id"
                    value={formData.model_version_id}
                    onChange={handleSelectChange}
                    label="Model Version"
                  >
                    {modelVersions.map((model) => (
                      <MenuItem key={model.id} value={model.id.toString()}>
                        {model.name} (v{model.version})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth margin="normal" required>
                  <InputLabel>Horizon</InputLabel>
                  <Select
                    name="horizon"
                    value={formData.horizon}
                    onChange={handleSelectChange}
                    label="Horizon"
                  >
                    <MenuItem value="1h">1 Hour</MenuItem>
                    <MenuItem value="4h">4 Hours</MenuItem>
                    <MenuItem value="12h">12 Hours</MenuItem>
                    <MenuItem value="1d">1 Day</MenuItem>
                    <MenuItem value="7d">7 Days</MenuItem>
                    <MenuItem value="30d">30 Days</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Timestamp"
                    value={formData.timestamp}
                    onChange={(date) => handleDateChange('timestamp', date)}
                    renderInput={(params) => (
                      <TextField {...params} fullWidth margin="normal" required />
                    )}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Prediction Time"
                    value={formData.prediction_time}
                    onChange={(date) => handleDateChange('prediction_time', date)}
                    renderInput={(params) => (
                      <TextField {...params} fullWidth margin="normal" required />
                    )}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  fullWidth
                  margin="normal"
                  label="Predicted Price"
                  name="predicted_price"
                  type="number"
                  value={formData.predicted_price}
                  onChange={handleInputChange}
                  required
                  inputProps={{
                    step: '0.00000001',
                    min: '0',
                  }}
                />
              </Grid>
              <Grid item xs={12}>
                <Box display="flex" justifyContent="flex-end" gap={2} mt={2}>
                  <Button
                    variant="outlined"
                    onClick={handleCloseForm}
                    disabled={createPrediction.isLoading || updatePrediction.isLoading}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={createPrediction.isLoading || updatePrediction.isLoading}
                  >
                    {selectedPrediction ? 'Update' : 'Create'} Prediction
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </Paper>
      )}
    </Page>
  );
};

export default PredictionsPage;
