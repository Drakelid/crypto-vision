import React, { useState, useMemo } from 'react';
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
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormHelperText,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { addDays } from 'date-fns';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import * as cryptoApi from '../api/crypto';
import { formatCurrency, formatDate } from '../utils/format';
import { Prediction, Cryptocurrency, ModelVersion } from '../types';
import Page from '../components/Page';

interface FormData {
  cryptocurrency_id: string;
  model_version_id: string;
  timestamp: Date;
  prediction_time: Date;
  horizon: string;
  predicted_price: string;
}

const HORIZON_OPTIONS = [
  { value: '1h', label: '1 Hour' },
  { value: '4h', label: '4 Hours' },
  { value: '1d', label: '1 Day' },
  { value: '7d', label: '1 Week' },
  { value: '30d', label: '1 Month' },
];

const PredictionsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedPrediction, setSelectedPrediction] = useState<Prediction | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Form state
  const [formData, setFormData] = useState<FormData>({
    cryptocurrency_id: '',
    model_version_id: '',
    timestamp: new Date(),
    prediction_time: addDays(new Date(), 1),
    horizon: '1d',
    predicted_price: '',
  });

  // Fetch data
  const { 
    data: predictions = [], 
    isLoading: isLoadingPredictions, 
    isError: isPredictionsError,
    error: predictionsError
  } = useQuery<Prediction[], Error>({
    queryKey: ['predictions'],
    queryFn: async () => {
      // For now, we'll fetch all predictions without filtering by cryptocurrency
      // In a real app, you might want to add filtering or pagination
      const response = await axios.get<Prediction[]>('/predictions/');
      return response.data;
    }
  });

  const { 
    data: cryptocurrencies = [], 
    isLoading: isLoadingCryptocurrencies 
  } = useQuery<Cryptocurrency[]>({
    queryKey: ['cryptocurrencies'],
    queryFn: () => cryptoApi.getCryptocurrencies()
  });

  const { 
    data: modelVersions = [], 
    isLoading: isLoadingModelVersions 
  } = useQuery<ModelVersion[]>({
    queryKey: ['modelVersions'],
    queryFn: () => cryptoApi.getModelVersions()
  });

  // Mutations
  const createPrediction = useMutation({
    mutationFn: (data: Omit<Prediction, 'id'>) => cryptoApi.createPrediction(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['predictions'] });
      handleCloseForm();
    },
  });

  const updatePrediction = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Prediction> }) => 
      cryptoApi.updatePrediction(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['predictions'] });
      handleCloseForm();
    },
  });

  const deletePrediction = useMutation({
    mutationFn: (id: number) => cryptoApi.deletePrediction(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['predictions'] });
    },
  });

  // Event handlers
  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleOpenForm = (prediction: Prediction | null = null) => {
    setSelectedPrediction(prediction);
    setFormErrors({});
    
    if (prediction) {
      setFormData({
        cryptocurrency_id: prediction.cryptocurrency_id.toString(),
        model_version_id: prediction.model_version_id.toString(),
        timestamp: new Date(prediction.timestamp),
        prediction_time: new Date(prediction.prediction_time),
        horizon: prediction.horizon,
        predicted_price: prediction.predicted_price.toString(),
      });
    } else {
      setFormData({
        cryptocurrency_id: '',
        model_version_id: '',
        timestamp: new Date(),
        prediction_time: addDays(new Date(), 1),
        horizon: '1d',
        predicted_price: '',
      });
    }
    setIsFormOpen(true);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setSelectedPrediction(null);
    setFormErrors({});
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSelectChange = (e: SelectChangeEvent) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleDateChange = (name: string) => (date: Date | null) => {
    if (date) {
      setFormData(prev => ({
        ...prev,
        [name]: date
      }));
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    
    if (!formData.cryptocurrency_id) {
      errors.cryptocurrency_id = 'Cryptocurrency is required';
    }
    if (!formData.model_version_id) {
      errors.model_version_id = 'Model version is required';
    }
    if (!formData.predicted_price || isNaN(Number(formData.predicted_price))) {
      errors.predicted_price = 'Valid predicted price is required';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    const predictionData = {
      cryptocurrency_id: parseInt(formData.cryptocurrency_id, 10),
      model_version_id: parseInt(formData.model_version_id, 10),
      timestamp: formData.timestamp.toISOString(),
      prediction_time: formData.prediction_time.toISOString(),
      horizon: formData.horizon,
      predicted_price: parseFloat(formData.predicted_price),
    };

    if (selectedPrediction) {
      updatePrediction.mutate({
        id: selectedPrediction.id,
        data: predictionData
      });
    } else {
      createPrediction.mutate(predictionData);
    }
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this prediction?')) {
      deletePrediction.mutate(id);
    }
  };

  // Memoized data
  const paginatedPredictions = useMemo(() => {
    return predictions.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
  }, [predictions, page, rowsPerPage]);

  const isLoading = isLoadingPredictions || isLoadingCryptocurrencies || isLoadingModelVersions;
  const isError = isPredictionsError;

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (isError) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Error loading predictions: {predictionsError?.message || 'Unknown error'}
      </Alert>
    );
  }

  return (
    <Page title="Predictions">
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Predictions
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => handleOpenForm()}
          >
            New Prediction
          </Button>
        </Box>

        <Paper sx={{ width: '100%', overflow: 'hidden' }}>
          <TableContainer sx={{ maxHeight: 600 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Cryptocurrency</TableCell>
                  <TableCell>Model Version</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Prediction Time</TableCell>
                  <TableCell>Horizon</TableCell>
                  <TableCell align="right">Predicted Price</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedPredictions.map((prediction) => (
                  <TableRow key={prediction.id}>
                    <TableCell>
                      {prediction.cryptocurrency?.name || 'N/A'}
                    </TableCell>
                    <TableCell>
                      {prediction.model_version?.name || 'N/A'}
                    </TableCell>
                    <TableCell>{formatDate(prediction.timestamp)}</TableCell>
                    <TableCell>{formatDate(prediction.prediction_time)}</TableCell>
                    <TableCell>{prediction.horizon}</TableCell>
                    <TableCell align="right">
                      {formatCurrency(prediction.predicted_price)}
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Edit">
                        <IconButton onClick={() => handleOpenForm(prediction)}>
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton 
                          onClick={() => handleDelete(prediction.id)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
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

        <Dialog open={isFormOpen} onClose={handleCloseForm} maxWidth="md" fullWidth>
          <form onSubmit={handleSubmit}>
            <DialogTitle>
              {selectedPrediction ? 'Edit Prediction' : 'Create New Prediction'}
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal" required>
                    <InputLabel id="cryptocurrency-select-label">Cryptocurrency</InputLabel>
                    <Select
                      labelId="cryptocurrency-select-label"
                      id="cryptocurrency_id"
                      name="cryptocurrency_id"
                      value={formData.cryptocurrency_id}
                      onChange={handleSelectChange}
                      label="Cryptocurrency"
                      error={!!formErrors.cryptocurrency_id}
                    >
                      {cryptocurrencies.map((crypto) => (
                        <MenuItem key={crypto.id} value={crypto.id.toString()}>
                          {crypto.name} ({crypto.symbol})
                        </MenuItem>
                      ))}
                    </Select>
                    {formErrors.cryptocurrency_id && (
                      <FormHelperText error>{formErrors.cryptocurrency_id}</FormHelperText>
                    )}
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal" required>
                    <InputLabel id="model-version-select-label">Model Version</InputLabel>
                    <Select
                      labelId="model-version-select-label"
                      id="model_version_id"
                      name="model_version_id"
                      value={formData.model_version_id}
                      onChange={handleSelectChange}
                      label="Model Version"
                      error={!!formErrors.model_version_id}
                    >
                      {modelVersions.map((version) => (
                        <MenuItem key={version.id} value={version.id.toString()}>
                          {version.name} (v{version.version})
                        </MenuItem>
                      ))}
                    </Select>
                    {formErrors.model_version_id && (
                      <FormHelperText error>{formErrors.model_version_id}</FormHelperText>
                    )}
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DatePicker
                      label="Timestamp"
                      value={formData.timestamp}
                      onChange={handleDateChange('timestamp')}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          fullWidth
                          margin="normal"
                          required
                        />
                      )}
                    />
                  </LocalizationProvider>
                </Grid>
                <Grid item xs={12} md={6}>
                  <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DatePicker
                      label="Prediction Time"
                      value={formData.prediction_time}
                      onChange={handleDateChange('prediction_time')}
                      minDate={formData.timestamp}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          fullWidth
                          margin="normal"
                          required
                        />
                      )}
                    />
                  </LocalizationProvider>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal" required>
                    <InputLabel id="horizon-select-label">Horizon</InputLabel>
                    <Select
                      labelId="horizon-select-label"
                      id="horizon"
                      name="horizon"
                      value={formData.horizon}
                      onChange={handleSelectChange}
                      label="Horizon"
                    >
                      {HORIZON_OPTIONS.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    margin="normal"
                    label="Predicted Price"
                    name="predicted_price"
                    type="number"
                    value={formData.predicted_price}
                    onChange={handleInputChange}
                    required
                    error={!!formErrors.predicted_price}
                    helperText={formErrors.predicted_price}
                    inputProps={{
                      step: '0.00000001',
                      min: '0',
                    }}
                  />
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseForm}>Cancel</Button>
              <Button type="submit" variant="contained" color="primary">
                {selectedPrediction ? 'Update' : 'Create'}
              </Button>
            </DialogActions>
          </form>
        </Dialog>
      </Box>
    </Page>
  );
};

export default PredictionsPage;
