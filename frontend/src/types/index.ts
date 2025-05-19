export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Cryptocurrency {
  id: number;
  symbol: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface Prediction {
  id: number;
  cryptocurrency_id: number;
  model_version_id: number;
  timestamp: string;
  prediction_time: string;
  horizon: string;
  predicted_price: number;
  created_at: string;
  updated_at: string;
  cryptocurrency?: Cryptocurrency;
}

export interface ModelVersion {
  id: number;
  name: string;
  description: string;
  version: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PriceData {
  timestamp: string;
  price: number;
  volume: number;
  market_cap: number;
}

export interface TimeRange {
  start: string;
  end: string;
  label: string;
}

export interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
}
