/**
 * Authentication API Service
 * Handles all auth-related API calls
 */

const API_BASE = "http://localhost:8000/auth";
const USERS_API = "http://localhost:8000/users";

// ============================================
// TYPES
// ============================================

export interface User {
  id: string;
  username: string;
  email: string;
  role: string; // "teacher" or "admin"
  profile: {
    fullName: string | null;
    school: string | null;
    experience: string | null;
    avatar: string | null;
  };
  lastLogin: string;
  createdAt: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  accessToken: string;
  tokenType: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface RegisterResponse {
  accessToken: string;
  tokenType: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ForgotPasswordResponse {
  message: string;
  resetToken?: string; // For testing/development
}

export interface ResetPasswordRequest {
  token: string;
  newPassword: string;
}

export interface ResetPasswordResponse {
  message: string;
}

export interface UpdateProfileRequest {
  fullName?: string;
  school?: string;
  experience?: string;
  avatar?: string;
}

// ============================================
// API ERROR
// ============================================

export class AuthApiError extends Error {
  public status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "AuthApiError";
    this.status = status;
  }
}

// ============================================
// TOKEN MANAGEMENT
// ============================================

const TOKEN_KEY = "jwt_token";

export function saveToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function getAuthHeaders(): HeadersInit {
  const token = getToken();
  console.log("[authApi] getAuthHeaders - token exists:", !!token);
  if (token) {
    console.log("[authApi] Token (first 30 chars):", token.substring(0, 30) + "...");
  }
  
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
    console.log("[authApi] Authorization header set:", `Bearer ${token.substring(0, 20)}...`);
  }
  
  return headers;
}

// ============================================
// API FUNCTIONS
// ============================================

/**
 * Helper function to extract error message from FastAPI error response
 */
function extractErrorMessage(errorData: any): string {
  if (!errorData || !errorData.detail) {
    return "エラーが発生しました";
  }

  // If detail is an array (validation errors from FastAPI)
  if (Array.isArray(errorData.detail)) {
    return errorData.detail
      .map((err: any) => {
        if (typeof err === "string") {
          return err;
        }
        if (err.msg) {
          // Format: "field: message" or just "message"
          const field = err.loc && err.loc.length > 1 ? err.loc[err.loc.length - 1] : "";
          return field ? `${field}: ${err.msg}` : err.msg;
        }
        return JSON.stringify(err);
      })
      .join(", ");
  }

  // If detail is a string
  if (typeof errorData.detail === "string") {
    return errorData.detail;
  }

  // Fallback
  return "登録に失敗しました";
}

/**
 * Register new user
 */
export async function register(data: RegisterRequest): Promise<RegisterResponse> {
  try {
    const response = await fetch(`${API_BASE}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = extractErrorMessage(errorData);
      throw new AuthApiError(errorMessage, response.status);
    }

    return response.json();
  } catch (error) {
    if (error instanceof AuthApiError) throw error;
    throw new AuthApiError("ネットワークエラーが発生しました", 0);
  }
}

/**
 * Login user
 */
export async function login(data: LoginRequest): Promise<LoginResponse> {
  try {
    const response = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = extractErrorMessage(errorData);
      throw new AuthApiError(errorMessage || "ログインに失敗しました", response.status);
    }

    return response.json();
  } catch (error) {
    if (error instanceof AuthApiError) throw error;
    throw new AuthApiError("ネットワークエラーが発生しました", 0);
  }
}

/**
 * Get current user profile
 */
export async function getCurrentUser(): Promise<User> {
  try {
    const headers = getAuthHeaders();
    console.log("[authApi] getCurrentUser - headers:", headers);
    
    const response = await fetch(`${USERS_API}/me`, {
      method: "GET",
      headers: headers,
    });

    console.log("[authApi] getCurrentUser - response status:", response.status);

    if (!response.ok) {
      if (response.status === 401) {
        const errorText = await response.text();
        console.log("[authApi] 401 error details:", errorText);
        throw new AuthApiError("認証が必要です", 401);
      }
      throw new AuthApiError("ユーザー情報の取得に失敗しました", response.status);
    }

    return response.json();
  } catch (error) {
    if (error instanceof AuthApiError) throw error;
    throw new AuthApiError("ネットワークエラーが発生しました", 0);
  }
}

/**
 * Update current user profile
 */
export async function updateProfile(data: UpdateProfileRequest): Promise<User> {
  try {
    const response = await fetch(`${USERS_API}/me`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = extractErrorMessage(errorData);
      throw new AuthApiError(errorMessage || "プロフィールの更新に失敗しました", response.status);
    }

    return response.json();
  } catch (error) {
    if (error instanceof AuthApiError) throw error;
    throw new AuthApiError("ネットワークエラーが発生しました", 0);
  }
}

/**
 * Request password reset
 */
export async function forgotPassword(data: ForgotPasswordRequest): Promise<ForgotPasswordResponse> {
  try {
    const response = await fetch(`${API_BASE}/forgot-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = extractErrorMessage(errorData);
      throw new AuthApiError(errorMessage || "パスワードリセットリクエストに失敗しました", response.status);
    }

    return response.json();
  } catch (error) {
    if (error instanceof AuthApiError) throw error;
    throw new AuthApiError("ネットワークエラーが発生しました", 0);
  }
}

/**
 * Reset password with token
 */
export async function resetPassword(data: ResetPasswordRequest): Promise<ResetPasswordResponse> {
  try {
    const response = await fetch(`${API_BASE}/reset-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = extractErrorMessage(errorData);
      throw new AuthApiError(errorMessage || "パスワードのリセットに失敗しました", response.status);
    }

    return response.json();
  } catch (error) {
    if (error instanceof AuthApiError) throw error;
    throw new AuthApiError("ネットワークエラーが発生しました", 0);
  }
}
