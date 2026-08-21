import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';

const Sales = () => {
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState('');
  const [cart, setCart] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const fetchData = async () => {
    try {
      const [custRes, prodRes] = await Promise.all([
        apiClient.get('/customers', { params: { status_filter: 'ACTIVE' } }),
        apiClient.get('/products', { params: { status_filter: 'ACTIVE' } })
      ]);
      setCustomers(custRes.data);
      setProducts(prodRes.data);

      // Auto-select default customer (Consumidor Final) if available
      const defaultCust = custRes.data.find((c) => c.is_default_consumer || c.is_default);
      if (defaultCust) {
        setSelectedCustomerId(defaultCust.id);
      } else if (custRes.data.length > 0) {
        setSelectedCustomerId(custRes.data[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddToCart = (e) => {
    e.preventDefault();
    if (!selectedProductId || quantity <= 0) return;

    const prod = products.find((p) => p.id === selectedProductId);
    if (!prod) return;

    const qtyNum = parseInt(quantity, 10);
    if (prod.current_stock < qtyNum) {
      alert(`Stock insuficiente para '${prod.name}'. Disponibles: ${prod.current_stock}`);
      return;
    }

    const priceNum = parseFloat(prod.sale_price);
    const subtotal = priceNum * qtyNum;

    // Check if item already in cart
    const existingIndex = cart.findIndex((i) => i.product_id === prod.id);
    if (existingIndex >= 0) {
      const updated = [...cart];
      const newQty = updated[existingIndex].quantity + qtyNum;
      if (prod.current_stock < newQty) {
        alert(`Stock insuficiente para '${prod.name}'. Disponibles: ${prod.current_stock}`);
        return;
      }
      updated[existingIndex].quantity = newQty;
      updated[existingIndex].subtotal = newQty * priceNum;
      setCart(updated);
    } else {
      setCart([...cart, {
        product_id: prod.id,
        product_name: prod.name,
        sku: prod.sku,
        quantity: qtyNum,
        unit_price: priceNum,
        subtotal
      }]);
    }

    setSelectedProductId('');
    setQuantity(1);
  };

  const handleRemoveFromCart = (index) => {
    setCart(cart.filter((_, i) => i !== index));
  };

  const totalAmount = cart.reduce((acc, curr) => acc + curr.subtotal, 0);

  const handleSubmitSale = async () => {
    if (!selectedCustomerId || cart.length === 0) return;
    setMessage({ type: '', text: '' });
    setLoading(true);

    try {
      await apiClient.post('/sales', {
        customer_id: selectedCustomerId,
        items: cart.map((i) => ({
          product_id: i.product_id,
          quantity: i.quantity,
          unit_price: i.unit_price
        }))
      });
      setMessage({ type: 'success', text: '¡Venta confirmada exitosamente! Inventario actualizado.' });
      setCart([]);
      fetchData(); // Refresh product stock
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Error al registrar venta' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>🛒 Terminal de Ventas (POS)</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Registro de transacciones comerciales de salida con deducción atómica de inventario (HU-006)</p>
      </div>

      {message.text && (
        <div className={message.type === 'error' ? 'alert-error' : 'card'} style={message.type === 'success' ? { backgroundColor: 'var(--success-bg)', color: 'var(--success)', marginBottom: '1rem' } : {}}>
          {message.text}
        </div>
      )}

      <div className="grid-2">
        {/* Formulario de venta */}
        <div className="card">
          <h3 className="card-title">1. Datos de Venta & Productos</h3>

          <div className="form-group">
            <label className="form-label">Cliente Seleccionado</label>
            <select
              className="form-control"
              value={selectedCustomerId}
              onChange={(e) => setSelectedCustomerId(e.target.value)}
              required
            >
              {customers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} {c.is_default_consumer || c.is_default ? '(Consumidor Final)' : ''}
                </option>
              ))}
            </select>
          </div>

          <form onSubmit={handleAddToCart} style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
            <div className="form-group">
              <label className="form-label">Seleccionar Producto</label>
              <select
                className="form-control"
                value={selectedProductId}
                onChange={(e) => setSelectedProductId(e.target.value)}
              >
                <option value="">-- Buscar Producto por Nombre/SKU --</option>
                {products.map((p) => (
                  <option key={p.id} value={p.id} disabled={p.current_stock <= 0}>
                    {p.name} (SKU: {p.sku}) - ${parseFloat(p.sale_price).toFixed(2)} [Stock: {p.current_stock}]
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Cantidad</label>
              <input
                type="number"
                min="1"
                className="form-control"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
              />
            </div>

            <button type="submit" className="btn btn-secondary" style={{ width: '100%' }}>
              + Agregar a la Venta
            </button>
          </form>
        </div>

        {/* Carrito / Comprobante */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <h3 className="card-title">2. Comprobante de Venta</h3>

          {cart.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              El comprobante no contiene productos agregados.
            </p>
          ) : (
            <div style={{ flex: 1 }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Cant.</th>
                    <th>P. Unit.</th>
                    <th>Subtotal</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {cart.map((item, idx) => (
                    <tr key={idx}>
                      <td>{item.product_name}</td>
                      <td>{item.quantity}</td>
                      <td>${item.unit_price.toFixed(2)}</td>
                      <td>${item.subtotal.toFixed(2)}</td>
                      <td>
                        <button onClick={() => handleRemoveFromCart(idx)} className="btn btn-danger" style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}>
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
              <span className="stat-label">Total a Cobrar</span>
              <div className="stat-value">${totalAmount.toFixed(2)}</div>
            </div>
            <button onClick={handleSubmitSale} disabled={cart.length === 0 || !selectedCustomerId || loading} className="btn btn-primary" style={{ padding: '0.875rem 2rem' }}>
              {loading ? 'Procesando Venta...' : 'Confirmar Venta'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sales;
