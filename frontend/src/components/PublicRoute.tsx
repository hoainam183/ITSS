import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

interface PublicRouteProps {
  children: React.ReactNode;
}

/**
 * PublicRoute component
 * Redirects to home if user is already authenticated
 * Used for login, register, forgot-password pages
 */
const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <section>
        <div className="loading-container">
          <p>読み込み中...</p>
        </div>
      </section>
    );
  }

  // Redirect to home if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  // Render children if not authenticated
  return <>{children}</>;
};

export default PublicRoute;

