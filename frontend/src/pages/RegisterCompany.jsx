import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import apiClient from '../api/client';

const RegisterCompany = () => {
  const [formData, setFormData] = useState({
    company_name: '',
    tax_id: '',
    owner_name: '',
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await apiClient.post('/auth/register-company', formData);
      login(response.data.access_token, response.data.user);
      navigate('/products');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al registrar la empresa. Intente nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <h2 style={{ fontSize: '1.75rem', fontWeight: 700, textAlign: 'center', marginBottom: '0.5rem' }}>
          ⚡ Arus ERP
        </h2>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
          Registrar Nueva Empresa (Tenant)
        </p>

        {error && <div className="alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Nombre Comercial de la Empresa</label>
            <input
              type="text"
              name="company_name"
              className="form-control"
              placeholder="Ej: Micronegocio Alfa"
              value={formData.company_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">NIT / Documento Fiscal</label>
            <input
              type="text"
              name="tax_id"
              className="form-control"
              placeholder="Ej: 900123456"
              value={formData.tax_id}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Nombre del Propietario / Administrador</label>
            <input
              type="text"
              name="owner_name"
              className="form-control"
              placeholder="Ej: Juan Pérez"
              value={formData.owner_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Correo Electrónico</label>
            <input
              type="email"
              name="email"
              className="form-control"
              placeholder="dueno@empresa.com"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Contraseña</label>
            <input
              type="password"
              name="password"
              className="form-control"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={6}
            />
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? 'Creando Empresa...' : 'Crear Espacio de Trabajo'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          ¿Ya tienes cuenta? <Link to="/login">Iniciar Sesión</Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterCompany;
