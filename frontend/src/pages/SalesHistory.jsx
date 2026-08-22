import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';

const SalesHistory = () => {
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSale, setSelectedSale] = useState(null);
  const [error, setError] = useState('');
  const [customers, setCustomers] = useState([]);
  const [filters, setFilters] = useState({ customer_id: '', date_from: '', date_to: '' });
  const [filtersApplied, setFiltersApplied] = useState(false);

  const fetchCustomers = async () => {
    try {
      const response = await apiClient.get('/customers');
      setCustomers(response.data);
    } catch (err) {
      // La lista de clientes es solo para el filtro; un fallo aquí no debe bloquear el historial.
    }
  };

  const fetchSales = async (activeFilters = {}) => {
    setLoading(true);
    try {
      const params = {};
      if (activeFilters.customer_id) params.customer_id = activeFilters.customer_id;
      if (activeFilters.date_from) params.date_from = activeFilters.date_from;
      if (activeFilters.date_to) params.date_to = activeFilters.date_to;

      const response = await apiClient.get('/sales', { params });
      setSales(response.data);
    } catch (err) {
      setError('Error al cargar historial de ventas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
    fetchSales();
  }, []);

  const handleApplyFilters = (e) => {
    e.preventDefault();
    const hasFilters = Boolean(filters.customer_id || filters.date_from || filters.date_to);
    setFiltersApplied(hasFilters);
    fetchSales(filters);
  };

  const handleClearFilters = () => {
    setFilters({ customer_id: '', date_from: '', date_to: '' });
    setFiltersApplied(false);
    fetchSales();
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>📜 Historial de Ventas Realizadas</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Consulta de transacciones comerciales inmutables y detalle de comprobantes (HU-007)</p>
      </div>

      {error && <div className="alert-error">{error}</div>}

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <form onSubmit={handleApplyFilters} style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'flex-end' }}>
          <div className="form-group" style={{ marginBottom: 0, minWidth: '200px' }}>
            <label className="form-label">Cliente</label>
            <select
              className="form-control"
              value={filters.customer_id}
              onChange={(e) => setFilters({ ...filters, customer_id: e.target.value })}
            >
              <option value="">Todos los clientes</option>
              {customers.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Desde</label>
            <input
              type="date"
              className="form-control"
              value={filters.date_from}
              onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Hasta</label>
            <input
              type="date"
              className="form-control"
              value={filters.date_to}
              onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
            />
          </div>
          <button type="submit" className="btn btn-primary">Aplicar Filtros</button>
          <button type="button" onClick={handleClearFilters} className="btn btn-secondary">Limpiar Filtros</button>
        </form>
      </div>

      <div className="card">
        {loading ? (
          <p style={{ color: 'var(--text-secondary)' }}>Cargando ventas...</p>
        ) : sales.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>
            {filtersApplied ? 'No hay ventas para el filtro aplicado.' : 'No hay ventas registradas en la empresa.'}
          </p>
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
