import './CartModal.css';

const API_URL = window.location.origin;

export default function CartModal({ cart, cartTotal, onRemoveFromCart, onClearCart, onClose }) {
    return (
        <div className="modal" style={{ display: 'block' }}>
            <div className="modal-content">
                <span className="close-btn" onClick={onClose}>&times;</span>
                <h2>Your cart</h2>
                <div id="cart-items">
                    {cart.length === 0 ? (
                        <p>Your cart is empty</p>
                    ) : (
                        cart.map((item, index) => {
                            const imageUrl = item.image_url ? `${API_URL}${item.image_url}` : '';
                            return (
                                <div key={index} className="cart-item">
                                    <div style={{ display: 'flex', alignItems: 'center' }}>
                                        {imageUrl && <img src={imageUrl} alt={item.product_name} />}
                                        <div>
                                            <b>{item.product_name}</b><br />
                                            <small>{item.new_price} zl</small>
                                        </div>
                                    </div>
                                    <span
                                        className="remove-btn"
                                        onClick={() => onRemoveFromCart(index)}
                                    >
                                        ✕
                                    </span>
                                </div>
                            );
                        })
                    )}
                </div>
                <div className="cart-footer">
                    <h3>Total: <span id="cart-total">{cartTotal.toFixed(2)}</span> zl</h3>
                    <button className="clear-btn" onClick={onClearCart}>Clear cart</button>
                </div>
            </div>
        </div>
    );
}
