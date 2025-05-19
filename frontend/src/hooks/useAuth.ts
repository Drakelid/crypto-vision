import React, { 
  useState, 
  useEffect, 
  useCallback, 
  ComponentType, 
  FC, 
  ReactNode 
} from 'react';
import { 
  useNavigate, 
  useLocation, 
  Navigate 
} from 'react-router-dom';
import { 
  useQuery, 
  useQueryClient, 
  UseQueryOptions 
} from '@tanstack/react-query';
import * as authApi from '../api/auth';
import { User } from '../types';

// Extend the User type to include roles and permissions
interface AuthUser extends User {
  roles?: string[];
  permissions?: string[];
}

export const useAuth = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();
  const [isInitialized, setIsInitialized] = useState(false);
  const [returnTo, setReturnTo] = useState<string | null>(null);

  // Fetch user data with proper typing
  const queryOptions: UseQueryOptions<AuthUser | null, Error> = {
    queryKey: ['currentUser'],
    queryFn: async (): Promise<AuthUser | null> => {
      try {
        const user = await authApi.getCurrentUser();
        // Cast to unknown first to avoid type errors
        return user as unknown as AuthUser;
      } catch (error) {
        return null;
      }
    },
    retry: false,
    staleTime: 1000 * 60 * 5, // 5 minutes
  };

  const {
    data: user,
    isLoading,
    isError,
    refetch: refetchUser
  } = useQuery<AuthUser | null, Error>(queryOptions);

  // Handle initialization after query settles
  useEffect(() => {
    if (!isLoading && !isInitialized) {
      setIsInitialized(true);
    }
  }, [isLoading, isInitialized]);

  // Check if user is authenticated
  const isAuthenticated = !!user && !isError;

  // Login function
  const login = useCallback(
    async (email: string, password: string) => {
      try {
        await authApi.login(email, password);
        await refetchUser();
        navigate(returnTo || '/dashboard', { replace: true });
        setReturnTo(null);
      } catch (error) {
        console.error('Login failed:', error);
        throw error;
      }
    },
    [navigate, refetchUser, returnTo]
  );

  // Logout function
  const logout = useCallback(async () => {
    try {
      await authApi.logout();
      queryClient.clear();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  }, [navigate, queryClient]);

  // Register function
  const register = useCallback(
    async (userData: { email: string; password: string; full_name: string }) => {
      try {
        await authApi.register(userData);
        await login(userData.email, userData.password);
      } catch (error) {
        console.error('Registration failed:', error);
        throw error;
      }
    },
    [login]
  );

  // Update user profile
  const updateProfile = useCallback(
    async (userData: Partial<User>) => {
      try {
        const updatedUser = await authApi.updateProfile(userData);
        queryClient.setQueryData<AuthUser | null>(['currentUser'], (oldData) => 
          oldData ? { ...oldData, ...updatedUser } : null
        );
        return updatedUser;
      } catch (error) {
        console.error('Profile update failed:', error);
        throw error;
      }
    },
    [queryClient]
  );

  // Change password
  const changePassword = useCallback(
    async (currentPassword: string, newPassword: string) => {
      try {
        await authApi.changePassword(currentPassword, newPassword);
      } catch (error) {
        console.error('Password change failed:', error);
        throw error;
      }
    },
    []
  );

  // Request password reset
  const requestPasswordReset = useCallback(async (email: string) => {
    try {
      await authApi.requestPasswordReset(email);
    } catch (error) {
      console.error('Password reset request failed:', error);
      throw error;
    }
  }, []);

  // Reset password
  const resetPassword = useCallback(
    async (token: string, newPassword: string) => {
      try {
        await authApi.resetPassword(token, newPassword);
      } catch (error) {
        console.error('Password reset failed:', error);
        throw error;
      }
    },
    []
  );

  // Verify email
  const verifyEmail = useCallback(async (token: string) => {
    try {
      await authApi.verifyEmail(token);
      await refetchUser();
    } catch (error) {
      console.error('Email verification failed:', error);
      throw error;
    }
  }, [refetchUser]);

  // Handle protected routes
  useEffect(() => {
    if (!isInitialized) return;

    const isAuthPage = ['/login', '/register', '/forgot-password'].includes(
      location.pathname
    );

    if (!isAuthenticated && !isAuthPage) {
      // Store the current location to return to after login
      setReturnTo(`${location.pathname}${location.search}`);
      navigate('/login', { replace: true });
    } else if (isAuthenticated && isAuthPage) {
      // Redirect to dashboard if already authenticated
      navigate(returnTo || '/dashboard', { replace: true });
      setReturnTo(null);
    }
  }, [isAuthenticated, isInitialized, location, navigate]);

  return {
    user: user || null,
    isAuthenticated,
    isLoading: !isInitialized || isLoading,
    login,
    logout,
    register,
    updateProfile,
    changePassword,
    requestPasswordReset,
    resetPassword,
    verifyEmail,
    refetchUser: async () => {
      const result = await refetchUser();
      return result.data || null;
    },
  };
};

// Hook to check if user has specific role or permission
export const useAuthCheck = (requiredRole?: string) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  
  const hasRole = useCallback((role: string): boolean => {
    if (!user) return false;
    const roles = (user as AuthUser).roles || [];
    return roles.includes(role);
  }, [user]);

  const hasPermission = useCallback((permission: string): boolean => {
    if (!user) return false;
    const permissions = (user as AuthUser).permissions || [];
    return permissions.includes(permission);
  }, [user]);

  const isAuthorized = requiredRole 
    ? hasRole(requiredRole) 
    : isAuthenticated;

  return {
    isAuthorized,
    hasRole,
    hasPermission,
    isLoading,
    user: user || null,
  } as const;
};

// Simple loading component
const LoadingSpinner: React.FC = () => {
  return React.createElement('div', null, 'Loading...');
};

// Higher-Order Component for protecting routes
export function withAuth<P extends object>(
  Component: ComponentType<P>,
  requiredRole?: string
): React.FC<P> {
  const WrappedComponent: React.FC<P> = (props) => {
    const { user, isAuthenticated, isLoading } = useAuth();
    const location = useLocation();
    const navigate = useNavigate();
    const [isAuthorized, setIsAuthorized] = React.useState(false);

    React.useEffect(() => {
      if (isLoading) return;

      if (!isAuthenticated) {
        navigate('/login', { state: { from: location }, replace: true });
        return;
      }
      
      if (requiredRole && !(user as AuthUser)?.roles?.includes(requiredRole)) {
        navigate('/unauthorized', { replace: true });
        return;
      }
      
      setIsAuthorized(true);
    }, [isAuthenticated, isLoading, location, navigate, requiredRole, user]);

    if (isLoading || !isAuthorized) {
      return React.createElement(LoadingSpinner);
    }

    return React.createElement(Component, props as any);
  };
  
  const componentName = (Component as any).displayName || (Component as any).name || 'Component';
  (WrappedComponent as any).displayName = `withAuth(${componentName})`;
  
  return WrappedComponent;
};
