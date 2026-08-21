import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ full_name: '', email: '', password: '', role_id: 'SELLER' });
  const [error, setError] = useState('');

  const fetchUsers = async () => {
    try {
      const response = await apiClient.get('/users');
      setUsers(response.data);
    } catch (err) {
      setError('Error al cargar la lista de colaboradores.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await apiClient.post('/users', formData);
      setShowModal(false);
      setFormData({ full_name: '', email: '', password: '', role_id: 'SELLER' });
      fetchUsers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al registrar usuario');
    }
  };

  const handleToggleStatus = async (user) => {
    const newStatus = user.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    try {
      await apiClient.patch(`/users/${user.id}/status`, { status: newStatus });
      fetchUsers();
    } catch (err) {
      alert(err.response?.data?.detail || 'No se pudo cambiar el estado del usuario');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>⚙️ Gestión de Usuarios Colaboradores</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Administre las cuentas y roles de su empresa (RBAC)</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn btn-primary">
          + Nuevo Colaborador
        </button>
      </div>

      {error && <div className="alert-error">{error}</div>}

      <div className="card">
        {loading ? (
          <p style={{ color: 'var(--text-secondary)' }}>Cargando usuarios...</p>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Nombre Completo</th>
                  <th>Correo Electrónico</th>
                  <th>Rol Asignado</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td><strong>{u.full_name}</strong></td>
                    <td>{u.email}</td>
                    <td>
                      <span className={`badge ${u.role_id === 'ADMIN' ? 'badge-success' : 'badge-secondary'}`}>
                        {u.role_id === 'ADMIN' ? 'Administrador' : 'Vendedor'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${u.status === 'ACTIVE' ? 'badge-success' : 'badge-danger'}`}>
                        {u.status === 'ACTIVE' ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td>
                      <button
                        onClick={() => handleToggleStatus(u)}
                        className={`btn ${u.status === 'ACTIVE' ? 'btn-danger' : 'btn-secondary'}`}
                        style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
                      >
                        {u.status === 'ACTIVE' ? 'Inactivar' : 'Activar'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="auth-wrapper" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 1000, background: 'rgba(0,0,0,0.7)' }}>
          <div className="auth-card" style={{ maxWidth: '480px' }}>
            <h3 style={{ marginBottom: '1rem' }}>Crear Colaborador</h3>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label className="form-label">Nombre Completo</label>
                <input
                  type="text"
                  className="form-control"
                  required
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Correo Electrónico</label>
                <input
                  type="email"
                  className="form-control"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Contraseña Inicial</label>
                <input
                  type="password"
                  className="form-control"
                  required
                  minLength={6}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Rol del Usuario</label>
                <select
                  className="form-control"
                  value={formData.role_id}
                  onChange={(e) => setFormData({ ...formData, role_id: e.target.value })}
                >
                  <option value="SELLER">Vendedor (Operaciones comerciales)</option>
                  <option value="ADMIN">Administrador (Acceso total)</option>
                </select>
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

export default Users;
