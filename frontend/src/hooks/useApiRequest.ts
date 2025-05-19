import { useState, useCallback, useRef } from 'react';
import { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import api from '../api/client';

type ApiRequestOptions<T> = {
  onSuccess?: (data: T) => void;
  onError?: (error: AxiosError) => void;
  onFinally?: () => void;
  successMessage?: string;
  errorMessage?: string;
  throwOnError?: boolean;
};

type ApiRequestState<T> = {
  data: T | null;
  isLoading: boolean;
  error: string | null;
  isSuccess: boolean;
};

const useApiRequest = <T,>(
  defaultOptions: ApiRequestOptions<T> = {}
) => {
  const [state, setState] = useState<ApiRequestState<T>>({
    data: null,
    isLoading: false,
    error: null,
    isSuccess: false,
  });

  const requestIdRef = useRef(0);

  const reset = useCallback(() => {
    setState({
      data: null,
      isLoading: false,
      error: null,
      isSuccess: false,
    });
  }, []);

  const request = useCallback(
    async (
      config: AxiosRequestConfig,
      options: ApiRequestOptions<T> = {}
    ): Promise<T | null> => {
      const currentRequestId = ++requestIdRef.current;
      const mergedOptions = { ...defaultOptions, ...options };
      const {
        onSuccess,
        onError,
        onFinally,
        successMessage,
        errorMessage,
        throwOnError = false,
      } = mergedOptions;

      // Skip if already loading
      if (state.isLoading) {
        console.warn('Request already in progress');
        return null;
      }


      setState((prev) => ({
        ...prev,
        isLoading: true,
        error: null,
        isSuccess: false,
      }));

      try {
        const response: AxiosResponse<T> = await api({
          ...config,
          // Ensure we don't cache API requests
          headers: {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            Pragma: 'no-cache',
            Expires: '0',
            ...config.headers,
          },
        });

        // Only process if this is the most recent request
        if (currentRequestId === requestIdRef.current) {
          setState({
            data: response.data,
            isLoading: false,
            error: null,
            isSuccess: true,
          });

          if (successMessage) {
            // You can integrate with a notification system here
            console.log(successMessage);
          }


          onSuccess?.(response.data);
          return response.data;
        }
      } catch (error) {
        const axiosError = error as AxiosError;
        
        // Only process if this is the most recent request
        if (currentRequestId === requestIdRef.current) {
          const errorMsg = errorMessage || 
            axiosError.response?.data?.message || 
            axiosError.message || 
            'An error occurred';

          setState({
            data: null,
            isLoading: false,
            error: errorMsg,
            isSuccess: false,
          });

          if (errorMessage) {
            // You can integrate with a notification system here
            console.error(errorMsg);
          }

          onError?.(axiosError);

          if (throwOnError) {
            throw axiosError;
          }
        }
      } finally {
        if (currentRequestId === requestIdRef.current) {
          setState((prev) => ({
            ...prev,
            isLoading: false,
          }));
          onFinally?.();
        }
      }

      return null;
    },
    [defaultOptions, state.isLoading]
  );

  // Convenience methods for common HTTP methods
  const get = useCallback(
    (url: string, params?: any, options?: ApiRequestOptions<T>) =>
      request({ method: 'GET', url, params }, options),
    [request]
  );

  const post = useCallback(
    (url: string, data?: any, options?: ApiRequestOptions<T>) =>
      request({ method: 'POST', url, data }, options),
    [request]
  );

  const put = useCallback(
    (url: string, data?: any, options?: ApiRequestOptions<T>) =>
      request({ method: 'PUT', url, data }, options),
    [request]
  );

  const patch = useCallback(
    (url: string, data?: any, options?: ApiRequestOptions<T>) =>
      request({ method: 'PATCH', url, data }, options),
    [request]
  );

  const del = useCallback(
    (url: string, options?: ApiRequestOptions<T>) =>
      request({ method: 'DELETE', url }, options),
    [request]
  );

  return {
    ...state,
    request,
    get,
    post,
    put,
    patch,
    delete: del,
    reset,
  };
};

export default useApiRequest;
