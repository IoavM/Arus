import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';

const Purchases = () => {
  const [products, setProducts] = useState([]);
  const [items, setItems] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [unitCost, setUnitCost] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const res = await apiClient.get('/products', { params: { status_filter: 'ACTIVE' } });
        setProducts(res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchProducts();
  }, []);

  const handleAddItem = (e) => {
    e.preventDefault();
    if (!selectedProductId || quantity <= 0 || !unitCost || parseFloat(unitCost) < 0) return;

    const prod = products.find((p) => p.id === selectedProductId);
    if (!prod) return;

    const costNum = parseFloat(unitCost);
    const subtotal = costNum * quantity;

    setItems([...items, {
      product_id: prod.id,
      product_name: prod.name,
      sku: prod.sku,
      quantity: parseInt(quantity, 10),
      unit_cost: costNum,
      subtotal
    }]);

    setSelectedProductId('');
    setQuantity(1);
    setUnitCost('');
  };

  const handleRemoveItem = (index) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const totalAmount = items.reduce((acc, curr) => acc + curr.subtotal, 0);

  const handleSubmitPurchase = async () => {
    if (items.length === 0) return;
    setMessage({ type: '', text: '' });
    setLoading(true);

    try {
      await apiClient.post('/purchases', {
        items: items.map((i) => ({
          product_id: i.product_id,
          quantity: i.quantity,
          unit_cost: i.unit_cost
        }))
      });
      setMessage({ type: 'success', text: '¡Compra registrada con éxito! El inventario ha sido incrementado.' });
      setItems([]);
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Error al procesar compra' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>🚚 Registro de Compras (Abastecimiento)</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Ingreso de mercancía al almacén con actualización atómica de stock (HU-008)</p>
      </div>

      {message.text && (
        <div className={message.type === 'error' ? 'alert-error' : 'card'} style={message.type === 'success' ? { backgroundColor: 'var(--success-bg)', color: 'var(--success)', marginBottom: '1rem' } : {}}>
          {message.text}
        </div>
      )}

      <div className="grid-2">
        {/* Form para agregar items */}
        <div className="card">
          <h3 className="card-title">Agregar Artículo a la Compra</h3>
          <form onSubmit={handleAddItem}>
            <div className="form-group">
              <label className="form-label">Seleccionar Producto</label>
              <select
                className="form-control"
                value={selectedProductId}
                onChange={(e) => setSelectedProductId(e.target.value)}
                required
              >
                <option value="">-- Seleccionar Producto --</option>
                {products.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} (SKU: {p.sku}) - Stock actual: {p.current_stock}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Cantidad Adquirida</label>
              <input
                type="number"
                min="1"
                className="form-control"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Costo Unitario de Adquisición ($)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                className="form-control"
                placeholder="0.00"
                value={unitCost}
                onChange={(e) => setUnitCost(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="btn btn-secondary" style={{ width: '100%' }}>
              + Agregar Renglón
            </button>
          </form>
        </div>

        {/* Detalle de la compra actual */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <h3 className="card-title">Detalle de la Compra</h3>

          {items.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              No hay artículos agregados a esta compra.
            </p>
          ) : (
            <div style={{ flex: 1 }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Cant.</th>
                    <th>Costo U.</th>
                    <th>Subtotal</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item, idx) => (
                    <tr key={idx}>
                      <td>{item.product_name}</td>
                      <td>{item.quantity}</td>
                      <td>${item.unit_cost.toFixed(2)}</td>
                      <td>${item.subtotal.toFixed(2)}</td>
                      <td>
                        <button onClick={() => handleRemoveItem(idx)} className="btn btn-danger" style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}>
                          ✕
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span className="stat-label">Costo Total Compra</span>
              <div className="stat-value">${totalAmount.toFixed(2)}</div>
            </div>
            <button onClick={handleSubmitPurchase} disabled={items.length === 0 || loading} className="btn btn-primary" style={{ padding: '0.875rem 2rem' }}>
              {loading ? 'Procesando...' : 'Confirmar e Incrementar Stock'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Purchases;
