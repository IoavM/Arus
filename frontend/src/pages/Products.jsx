import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';

const Products = () => {
  const [products, setProducts] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({ sku: '', name: '', description: '', sale_price: '', current_stock: '', min_stock: '', category_id: '' });
  const [error, setError] = useState('');
  const [categories, setCategories] = useState([]);
  const [newCategory, setNewCategory] = useState('');

  const fetchProducts = async () => {
    try {
      const response = await apiClient.get('/products', { params: { query } });
      setProducts(response.data);
    } catch (err) {
      setError('Error al cargar catálogo de productos e inventario');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await apiClient.get('/categories');
      setCategories(response.data);
    } catch (err) {
      setError('Error al cargar las categorías');
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [query]);

  useEffect(() => {
    fetchCategories();
  }, []);

  const handleCreateCategory = async () => {
    if (!newCategory.trim()) return;
    setError('');
    try {
      const response = await apiClient.post('/categories', { name: newCategory.trim() });
      setCategories([...categories, response.data]);
      setFormData({ ...formData, category_id: response.data.id });
      setNewCategory('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al crear categoría');
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (editingProduct) {
        await apiClient.put(`/products/${editingProduct.id}`, {
          name: formData.name,
          description: formData.description,
          sale_price: parseFloat(formData.sale_price),
          min_stock: parseInt(formData.min_stock, 10) || 0,
          category_id: formData.category_id || null
        });
      } else {
        await apiClient.post('/products', {
          sku: formData.sku,
          name: formData.name,
          description: formData.description,
          sale_price: parseFloat(formData.sale_price),
          current_stock: parseInt(formData.current_stock, 10) || 0,
          min_stock: parseInt(formData.min_stock, 10) || 0,
          category_id: formData.category_id || null
        });
      }
      setShowModal(false);
      setEditingProduct(null);
      setFormData({ sku: '', name: '', description: '', sale_price: '', current_stock: '', min_stock: '', category_id: '' });
      fetchProducts();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al guardar producto');
    }
  };

  const handleEdit = (p) => {
    setEditingProduct(p);
    setFormData({
      sku: p.sku,
      name: p.name,
      description: p.description || '',
      sale_price: p.sale_price,
      current_stock: p.current_stock,
      min_stock: p.min_stock ?? 0,
      category_id: p.category_id || ''
    });
    setShowModal(true);
  };

  const handleToggleStatus = async (p) => {
    const newStatus = p.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    try {
      await apiClient.patch(`/products/${p.id}/status`, { status: newStatus });
      fetchProducts();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error al cambiar estado');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>📦 Gestión de Productos e Inventario</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Catálogo de mercancías y existencias en almacén (HU-004 & HU-009)</p>
        </div>
        <button onClick={() => { setEditingProduct(null); setFormData({ sku: '', name: '', description: '', sale_price: '', current_stock: '', min_stock: '', category_id: '' }); setShowModal(true); }} className="btn btn-primary">
          + Nuevo Producto
        </button>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <input
          type="text"
          className="form-control"
          placeholder="🔍 Buscar producto por SKU o nombre..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      {error && <div className="alert-error">{error}</div>}

      <div className="card">
        {loading ? (
          <p style={{ color: 'var(--text-secondary)' }}>Cargando inventario...</p>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Código / SKU</th>
                  <th>Nombre del Producto</th>
                  <th>Categoría</th>
                  <th>Precio Venta</th>
                  <th>Stock Disponible</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {products.map((p) => (
                  <tr key={p.id}>
                    <td><code>{p.sku}</code></td>
                    <td><strong>{p.name}</strong></td>
                    <td>
                      <span className="badge" style={{ backgroundColor: 'var(--bg-surface-hover)', color: 'var(--text-secondary)' }}>
                        {categories.find((c) => c.id === p.category_id)?.name || 'Sin categoría'}
                      </span>
                    </td>
                    <td>${parseFloat(p.sale_price).toFixed(2)}</td>
                    <td>
                      <span className={`badge ${p.current_stock > 10 ? 'badge-success' : p.current_stock > 0 ? 'badge-warning' : 'badge-danger'}`}>
                        {p.current_stock} unidades
                      </span>
                      {p.current_stock < p.min_stock && (
                        <span className="badge badge-warning" style={{ marginLeft: '0.5rem' }} title={`Stock mínimo definido: ${p.min_stock}`}>
                          ⚠ Stock bajo
                        </span>
                      )}
                    </td>
                    <td>
                      <span className={`badge ${p.status === 'ACTIVE' ? 'badge-success' : 'badge-danger'}`}>
                        {p.status === 'ACTIVE' ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td style={{ display: 'flex', gap: '0.5rem' }}>
                      <button onClick={() => handleEdit(p)} className="btn btn-secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}>
                        Editar
                      </button>
                      <button onClick={() => handleToggleStatus(p)} className={`btn ${p.status === 'ACTIVE' ? 'btn-danger' : 'btn-secondary'}`} style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}>
                        {p.status === 'ACTIVE' ? 'Inactivar' : 'Activar'}
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
          <div className="auth-card" style={{ maxWidth: '520px' }}>
            <h3 style={{ marginBottom: '1rem' }}>{editingProduct ? 'Editar Producto' : 'Registrar Producto'}</h3>
            <form onSubmit={handleSave}>
              {!editingProduct && (
                <div className="form-group">
                  <label className="form-label">SKU / Código de Barras</label>
                  <input
                    type="text"
                    className="form-control"
                    required
                    value={formData.sku}
                    onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                  />
                </div>
              )}
              <div className="form-group">
                <label className="form-label">Nombre del Producto</label>
                <input
                  type="text"
                  className="form-control"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Descripción (Opcional)</label>
                <input
                  type="text"
                  className="form-control"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Categoría (Opcional)</label>
                <select
                  className="form-control"
                  value={formData.category_id}
                  onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                >
                  <option value="">Sin categoría</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Nueva categoría..."
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleCreateCategory(); } }}
                  />
                  <button type="button" onClick={handleCreateCategory} className="btn btn-secondary" style={{ whiteSpace: 'nowrap' }}>
                    + Crear
                  </button>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Precio de Venta ($)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  className="form-control"
                  required
                  value={formData.sale_price}
                  onChange={(e) => setFormData({ ...formData, sale_price: e.target.value })}
                />
              </div>
              {!editingProduct && (
                <div className="form-group">
                  <label className="form-label">Stock Inicial</label>
                  <input
                    type="number"
                    min="0"
                    className="form-control"
                    required
                    value={formData.current_stock}
                    onChange={(e) => setFormData({ ...formData, current_stock: e.target.value })}
                  />
                </div>
              )}
              <div className="form-group">
                <label className="form-label">Stock Mínimo</label>
                <input
                  type="number"
                  min="0"
                  className="form-control"
                  value={formData.min_stock}
                  onChange={(e) => setFormData({ ...formData, min_stock: e.target.value })}
                />
                <small style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                  Umbral para marcar el producto como "Stock bajo". Usa 0 para no definir umbral.
                </small>
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

export default Products;
