import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await apiClient.get('/dashboard/summary');
        setSummary(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Error al cargar métricas del resumen del negocio');
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>📊 Resumen Ejecutivo del Negocio</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Vista consolidada de métricas clave aisladas por empresa (HU-010)</p>
      </div>

      {error && <div className="alert-error">{error}</div>}

      {loading ? (
        <p style={{ color: 'var(--text-secondary)' }}>Cargando métricas...</p>
      ) : summary ? (
        <div>
          <div className="grid-4" style={{ marginBottom: '2rem' }}>
            <div className="stat-card">
              <span className="stat-label">💰 Total Vendido ($)</span>
              <div className="stat-value" style={{ color: 'var(--success)' }}>
                ${parseFloat(summary.total_sales_amount).toFixed(2)}
              </div>
            </div>

            <div className="stat-card">
              <span className="stat-label">🛒 Ventas Realizadas</span>
              <div className="stat-value">
                {summary.total_sales_count}
              </div>
            </div>

            <div className="stat-card">
              <span className="stat-label">📦 Productos Activos</span>
              <div className="stat-value">
                {summary.active_products_count}
              </div>
            </div>

            <div className="stat-card">
              <span className="stat-label">👥 Clientes Registrados</span>
              <div className="stat-value">
                {summary.active_customers_count}
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="card-title">Estado Operativo de la Empresa</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '1rem' }}>
              Su empresa cuenta actualmente con <strong>{summary.active_users_count} colaboradores activos</strong> en el sistema bajo el modelo de control de acceso por roles.
            </p>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <span className="badge badge-success">Multi-Tenant Aislado</span>
              <span className="badge badge-success">Auditoría Inmutable Activa</span>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default Dashboard;
