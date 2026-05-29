import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

import { Suspense, lazy } from 'react';

// Lazy loaded Pages
const Home = lazy(() => import('../pages/Home'));
const Login = lazy(() => import('../pages/Login'));
const Signup = lazy(() => import('../pages/Signup'));
const Dashboard = lazy(() => import('../pages/Dashboard'));
const Chat = lazy(() => import('../pages/Chat'));
const Profile = lazy(() => import('../pages/Profile'));
const NotFound = lazy(() => import('../pages/NotFound'));

const Loader = () => (
  <div className="min-h-screen flex items-center justify-center bg-cyber-dark terminal-scanlines">
    <div className="text-center">
      <div className="relative w-16 h-16 mx-auto mb-4">
        <div className="absolute inset-0 rounded-full border-4 border-cyber-blue/20 animate-pulse"></div>
        <div className="absolute inset-0 rounded-full border-4 border-t-cyber-blue animate-spin"></div>
      </div>
      <p className="font-mono text-sm text-cyber-blue text-glow-blue animate-pulse">
        LOADING COMPONENT...
      </p>
    </div>
  </div>
);

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-cyber-dark terminal-scanlines">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto mb-4">
            <div className="absolute inset-0 rounded-full border-4 border-cyber-blue/20 animate-pulse"></div>
            <div className="absolute inset-0 rounded-full border-4 border-t-cyber-blue animate-spin"></div>
          </div>
          <p className="font-mono text-sm text-cyber-blue text-glow-blue animate-pulse">
            AUTHENTICATING OFFLINE CORE...
          </p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Public Route Component (Redirects to dashboard if already authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-cyber-dark terminal-scanlines">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto mb-4">
            <div className="absolute inset-0 rounded-full border-4 border-cyber-blue/20 animate-pulse"></div>
            <div className="absolute inset-0 rounded-full border-4 border-t-cyber-blue animate-spin"></div>
          </div>
          <p className="font-mono text-sm text-cyber-blue text-glow-blue animate-pulse">
            INITIALIZING SECURE LINK...
          </p>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

const AppRoutes = () => {
  return (
    <Suspense fallback={<Loader />}>
      <Routes>
        {/* Public Pages */}
        <Route path="/" element={<Home />} />
        
        {/* Auth Pages (redirect if logged in) */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/signup"
          element={
            <PublicRoute>
              <Signup />
            </PublicRoute>
          }
        />

        {/* Protected Console Dashboards */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Chat />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />

        {/* 404 Route */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  );
};

export default AppRoutes;
