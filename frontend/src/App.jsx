import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import Login from './pages/Login';
import RegisterCompany from './pages/RegisterCompany';
import Dashboard from './pages/Dashboard';
import Users from './pages/Users';
import Products from './pages/Products';
import Customers from './pages/Customers';
import Sales from './pages/Sales';
import SalesHistory from './pages/SalesHistory';
import Purchases from './pages/Purchases';
import ChangePassword from './pages/ChangePassword';

const ProtectedRoute = ({ children, requiredRole }) => {
  const { user, token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  if (requiredRole && user?.role_id !== requiredRole) {
    return <Navigate to="/products" replace />;
  }
  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">{children}</main>
    </div>
  );
};

const AppRoutes = () => {
  const { token } = useAuth();
  return (
    <Routes>
      <Route path="/" element={!token ? <Login /> : <Navigate to="/products" replace />} />
      <Route path="/login" element={!token ? <Login /> : <Navigate to="/products" replace />} />
      <Route path="/register-company" element={!token ? <RegisterCompany /> : <Navigate to="/products" replace />} />

      <Route path="/dashboard" element={<ProtectedRoute requiredRole="ADMIN"><Dashboard /></ProtectedRoute>} />
      <Route path="/users" element={<ProtectedRoute requiredRole="ADMIN"><Users /></ProtectedRoute>} />
      <Route path="/products" element={<ProtectedRoute><Products /></ProtectedRoute>} />
      <Route path="/customers" element={<ProtectedRoute><Customers /></ProtectedRoute>} />
      <Route path="/sales" element={<ProtectedRoute><Sales /></ProtectedRoute>} />
      <Route path="/sales-history" element={<ProtectedRoute><SalesHistory /></ProtectedRoute>} />
      <Route path="/purchases" element={<ProtectedRoute><Purchases /></ProtectedRoute>} />
      <Route path="/change-password" element={<ProtectedRoute><ChangePassword /></ProtectedRoute>} />

      <Route path="*" element={<Navigate to={token ? "/products" : "/login"} replace />} />
    </Routes>
  );
};

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
