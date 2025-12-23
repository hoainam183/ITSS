import React, { createContext, useContext, useState, useEffect } from "react";
import type { ReactNode } from "react";
import type {
  User,
  LoginRequest,
  RegisterRequest,
} from "../services/authApi";
import {
  login as apiLogin,
  register as apiRegister,
  getCurrentUser,
  saveToken,
  removeToken,
  getToken,
} from "../services/authApi";

// ============================================
// CONTEXT TYPES
// ============================================

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

// ============================================
// CONTEXT CREATION
// ============================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============================================
// AUTH PROVIDER
// ============================================

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user on mount if token exists
  useEffect(() => {
    const initAuth = async () => {
      const token = getToken();
      console.log("[AuthContext] useEffect running, token exists:", !!token);
      
      if (token) {
        try {
          console.log("[AuthContext] Attempting to fetch user with existing token");
          const userData = await getCurrentUser();
          console.log("[AuthContext] User fetched successfully:", userData.username);
          setUser(userData);
        } catch (error) {
          // Token invalid or expired, remove it silently
          // This is expected behavior when token expires
          console.log("[AuthContext] Token expired or invalid, clearing storage");
          removeToken();
          setUser(null);
        }
      } else {
        console.log("[AuthContext] No token found in storage");
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  // Login function
  const login = async (credentials: LoginRequest) => {
    console.log("[AuthContext] Login attempt started");
    const response = await apiLogin(credentials);
    console.log("[AuthContext] Login response:", response);
    console.log("[AuthContext] Token received:", response.accessToken);
    console.log("[AuthContext] Login successful, saving token");
    saveToken(response.accessToken);
    
    // Verify token was saved
    const savedToken = getToken();
    console.log("[AuthContext] Token saved in localStorage:", savedToken?.substring(0, 20) + "...");
    
    // Fetch user data after login
    console.log("[AuthContext] Fetching user data after login");
    const userData = await getCurrentUser();
    console.log("[AuthContext] User data fetched:", userData.username);
    setUser(userData);
    console.log("[AuthContext] Login complete");
  };

  // Register function
  const register = async (data: RegisterRequest) => {
    await apiRegister(data);
    // Note: User needs to login after registration
  };

  // Logout function
  const logout = () => {
    removeToken();
    setUser(null);
  };

  // Refresh user data
  const refreshUser = async () => {
    if (getToken()) {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
      } catch (error) {
        // If refresh fails, logout
        logout();
      }
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// ============================================
// CUSTOM HOOK
// ============================================

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
