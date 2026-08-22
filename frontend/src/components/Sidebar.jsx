import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isAdmin = user?.role_id === 'ADMIN';

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span>⚡ Arus ERP</span>
      </div>
      <nav>
        <ul className="nav-menu">
          {isAdmin && (
            <li>
              <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                📊 Dashboard
              </NavLink>
            </li>
          )}
          <li>
            <NavLink to="/products" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              📦 Productos / Inventario
            </NavLink>
          </li>
          <li>
            <NavLink to="/customers" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              👥 Clientes
            </NavLink>
          </li>
          <li>
            <NavLink to="/sales" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              🛒 Ventas (POS)
            </NavLink>
          </li>
          <li>
            <NavLink to="/sales-history" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              📜 Historial Ventas
            </NavLink>
          </li>
          <li>
            <NavLink to="/purchases" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              🚚 Compras
            </NavLink>
          </li>
          {isAdmin && (
            <li>
              <NavLink to="/users" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                ⚙️ Usuarios
              </NavLink>
            </li>
          )}
          <li>
            <NavLink to="/change-password" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              🔑 Cambiar Contraseña
            </NavLink>
          </li>
        </ul>

      </nav>
      <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
          <strong>{user?.full_name}</strong>
          <br />
          <span className="badge badge-success">{user?.role_id}</span>
        </div>
        <button onClick={handleLogout} className="btn btn-secondary" style={{ width: '100%' }}>
          Cerrar Sesión
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
