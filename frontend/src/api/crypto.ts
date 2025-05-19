import axios from './client';
import { Cryptocurrency, PriceData, Prediction, ModelVersion, ApiResponse } from '../types';

export const getCryptocurrencies = async (): Promise<Cryptocurrency[]> => {
  const response = await axios.get<Cryptocurrency[]>('/cryptocurrencies/');
  return response.data;
};

export const getCryptocurrency = async (id: number): Promise<Cryptocurrency> => {
  const response = await axios.get<Cryptocurrency>(`/cryptocurrencies/${id}`);
  return response.data;
};

export const getPriceHistory = async (cryptoId: number, start: string, end: string): Promise<PriceData[]> => {
  const response = await axios.get<PriceData[]>(
    `/cryptocurrencies/${cryptoId}/prices?start_date=${start}&end_date=${end}`
  );
  return response.data;
};

export const getPredictions = async (cryptoId: number, modelVersionId?: number): Promise<Prediction[]> => {
  const url = modelVersionId 
    ? `/predictions/?cryptocurrency_id=${cryptoId}&model_version_id=${modelVersionId}`
    : `/predictions/?cryptocurrency_id=${cryptoId}`;
  
  const response = await axios.get<Prediction[]>(url);
  return response.data;
};

export const getModelVersions = async (): Promise<ModelVersion[]> => {
  const response = await axios.get<ModelVersion[]>('/model-versions/');
  return response.data;
};

export const getModelVersion = async (id: number): Promise<ModelVersion> => {
  const response = await axios.get<ModelVersion>(`/model-versions/${id}`);
  return response.data;
};

export const createPrediction = async (data: {
  cryptocurrency_id: number;
  model_version_id: number;
  timestamp: string;
  prediction_time: string;
  horizon: string;
  predicted_price: number;
}): Promise<Prediction> => {
  const response = await axios.post<Prediction>('/predictions/', data);
  return response.data;
};

export const updatePrediction = async (
  id: number,
  data: Partial<Prediction>
): Promise<Prediction> => {
  const response = await axios.patch<Prediction>(`/predictions/${id}`, data);
  return response.data;
};

export const deletePrediction = async (id: number): Promise<void> => {
  await axios.delete(`/predictions/${id}`);
};
