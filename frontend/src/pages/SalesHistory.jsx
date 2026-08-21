import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';

const SalesHistory = () => {
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSale, setSelectedSale] = useState(null);
  const [error, setError] = useState('');

  const fetchSales = async () => {
    try {
      const response = await apiClient.get('/sales');
      setSales(response.data);
    } catch (err) {
      setError('Error al cargar historial de ventas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSales();
  }, []);

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>📜 Historial de Ventas Realizadas</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Consulta de transacciones comerciales inmutables y detalle de comprobantes (HU-007)</p>
      </div>

      {error && <div className="alert-error">{error}</div>}

      <div className="card">
        {loading ? (
          <p style={{ color: 'var(--text-secondary)' }}>Cargando ventas...</p>
        ) : sales.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>No hay ventas registradas en la empresa.</p>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>ID Venta</th>
                  <th>Fecha & Hora</th>
                  <th>Cliente</th>
                  <th>Vendedor / Cajero</th>
                  <th>Monto Total</th>
                  <th>Estado</th>
                  <th>Detalle</th>
                </tr>
              </thead>
              <tbody>
                {sales.map((s) => (
                  <tr key={s.id}>
                    <td><code>{s.id.substring(0, 8)}...</code></td>
                    <td>{new Date(s.created_at).toLocaleString('es-ES')}</td>
                    <td><strong>{s.customer_name}</strong></td>
                    <td>{s.user_name}</td>
                    <td><strong>${parseFloat(s.total_amount).toFixed(2)}</strong></td>
                    <td>
                      <span className="badge badge-success">Confirmada</span>
                    </td>
                    <td>
                      <button onClick={() => setSelectedSale(s)} className="btn btn-secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}>
                        Ver Comprobante
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedSale && (
        <div className="auth-wrapper" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 1000, background: 'rgba(0,0,0,0.7)' }}>
          <div className="auth-card" style={{ maxWidth: '560px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1.25rem' }}>Comprobante de Venta</h3>
              <span className="badge badge-success">Confirmada (Inmutable)</span>
            </div>

            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
              <p><strong>ID Transacción:</strong> {selectedSale.id}</p>
              <p><strong>Fecha:</strong> {new Date(selectedSale.created_at).toLocaleString('es-ES')}</p>
              <p><strong>Cliente:</strong> {selectedSale.customer_name}</p>
              <p><strong>Vendedor:</strong> {selectedSale.user_name}</p>
            </div>

            <h4 style={{ fontSize: '0.95rem', marginBottom: '0.5rem' }}>Artículos Vendidos:</h4>
            <table className="table" style={{ marginBottom: '1.5rem' }}>
              <thead>
                <tr>
                  <th>Producto</th>
                  <th>Cant.</th>
                  <th>P. Unit.</th>
                  <th>Subtotal</th>
                </tr>
              </thead>
              <tbody>
                {selectedSale.items.map((item, idx) => (
                  <tr key={idx}>
                    <td>{item.product_name}</td>
                    <td>{item.quantity}</td>
                    <td>${parseFloat(item.unit_price).toFixed(2)}</td>
                    <td>${parseFloat(item.subtotal).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
              <div>
                <span className="stat-label">Total Venta</span>
                <div className="stat-value" style={{ fontSize: '1.5rem' }}>${parseFloat(selectedSale.total_amount).toFixed(2)}</div>
              </div>
              <button onClick={() => setSelectedSale(null)} className="btn btn-secondary">
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SalesHistory;
