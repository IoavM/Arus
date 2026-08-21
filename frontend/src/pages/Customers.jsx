import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';

const Customers = () => {
  const [customers, setCustomers] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [formData, setFormData] = useState({ name: '', tax_number: '', phone: '', email: '' });
  const [error, setError] = useState('');

  const fetchCustomers = async () => {
    try {
      const response = await apiClient.get('/customers', { params: { query } });
      setCustomers(response.data);
    } catch (err) {
      setError('Error al cargar directorio de clientes');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, [query]);

  const handleSave = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (editingCustomer) {
        await apiClient.put(`/customers/${editingCustomer.id}`, formData);
      } else {
        await apiClient.post('/customers', formData);
      }
      setShowModal(false);
      setEditingCustomer(null);
      setFormData({ name: '', tax_number: '', phone: '', email: '' });
      fetchCustomers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al guardar cliente');
    }
  };

  const handleEdit = (c) => {
    if (c.is_default || c.is_default_consumer) return;
    setEditingCustomer(c);
    setFormData({
      name: c.name,
      tax_number: c.tax_number || c.tax_id || '',
      phone: c.phone || '',
      email: c.email || ''
    });
    setShowModal(true);
  };

  const handleToggleStatus = async (c) => {
    if (c.is_default || c.is_default_consumer) return;
    const newStatus = c.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    try {
      await apiClient.patch(`/customers/${c.id}/status`, { status: newStatus });
      fetchCustomers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error al cambiar estado');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>👥 Gestión de Clientes</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Directorio de compradores de su empresa (HU-005)</p>
        </div>
        <button onClick={() => { setEditingCustomer(null); setFormData({ name: '', tax_number: '', phone: '', email: '' }); setShowModal(true); }} className="btn btn-primary">
          + Nuevo Cliente
        </button>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <input
          type="text"
          className="form-control"
          placeholder="🔍 Buscar cliente por nombre o documento..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      {error && <div className="alert-error">{error}</div>}

      <div className="card">
        {loading ? (
          <p style={{ color: 'var(--text-secondary)' }}>Cargando clientes...</p>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Nombre / Razón Social</th>
                  <th>Identificación Fiscal</th>
                  <th>Teléfono</th>
                  <th>Correo</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((c) => {
                  const isDefault = c.is_default || c.is_default_consumer;
                  const taxDoc = c.tax_number || c.tax_id || '-';
                  return (
                    <tr key={c.id}>
                      <td>
                        <strong>{c.name}</strong>
                        {isDefault && <span className="badge badge-success" style={{ marginLeft: '0.5rem' }}>Cliente Por Defecto</span>}
                      </td>
                      <td>{taxDoc}</td>
                      <td>{c.phone || '-'}</td>
                      <td>{c.email || '-'}</td>
                      <td>
                        <span className={`badge ${c.status === 'ACTIVE' ? 'badge-success' : 'badge-danger'}`}>
                          {c.status === 'ACTIVE' ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td>
                        {!isDefault && (
                          <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <button onClick={() => handleEdit(c)} className="btn btn-secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}>
                              Editar
                            </button>
                            <button onClick={() => handleToggleStatus(c)} className={`btn ${c.status === 'ACTIVE' ? 'btn-danger' : 'btn-secondary'}`} style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}>
                              {c.status === 'ACTIVE' ? 'Inactivar' : 'Activar'}
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="auth-wrapper" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 1000, background: 'rgba(0,0,0,0.7)' }}>
          <div className="auth-card" style={{ maxWidth: '480px' }}>
            <h3 style={{ marginBottom: '1rem' }}>{editingCustomer ? 'Editar Cliente' : 'Registrar Cliente'}</h3>
            <form onSubmit={handleSave}>
              <div className="form-group">
                <label className="form-label">Nombre / Razón Social</label>
                <input
                  type="text"
                  className="form-control"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Documento Identificación Fiscal (NIT/CC)</label>
                <input
                  type="text"
                  className="form-control"
                  value={formData.tax_number}
                  onChange={(e) => setFormData({ ...formData, tax_number: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Teléfono</label>
                <input
                  type="text"
                  className="form-control"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Correo Electrónico</label>
                <input
                  type="email"
                  className="form-control"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary" style={{ flex: 1 }}>
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>
                  Guardar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Customers;
