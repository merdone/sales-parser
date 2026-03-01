import { useState } from 'react'
import { NavLink, Routes, Route } from 'react-router-dom'
import './App.css'
import CartModal from './components/CartModal'
import Home from './pages/Home'
import Magazine from './pages/Magazine'
import { useCart } from './hooks/useCart'

function App() {
    const [isCartOpen, setIsCartOpen] = useState(false);
    const { cart, addToCart, removeFromCart, clearCart, cartTotal, cartCount } = useCart();

    return (
        <div className="app">
            <header className="header">
                <div className="brand">
                    <span className="brand-mark">🛒</span>
                    <div>
                        <h1>Promo Basket</h1>
                        <p>Smart offers from your favorite stores</p>
                    </div>
                </div>
                <nav className="nav">
                    <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                        Home
                    </NavLink>
                    <NavLink to="/magazine" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                        Leaflet
                    </NavLink>
                </nav>
                <button
                    className="cart-btn-main"
                    onClick={() => setIsCartOpen(true)}
                >
                    Cart <span className="badge">{cartCount}</span>
                </button>
            </header>

            <main className="main">
                <Routes>
                    <Route
                        path="/"
                        element={<Home onAddToCart={addToCart} />}
                    />
                    <Route
                        path="/magazine"
                        element={<Magazine onAddToCart={addToCart} />}
                    />
                </Routes>
            </main>

            {isCartOpen && (
                <CartModal
                    cart={cart}
                    cartTotal={cartTotal}
                    onRemoveFromCart={removeFromCart}
                    onClearCart={clearCart}
                    onClose={() => setIsCartOpen(false)}
                />
            )}
        </div>
    );
}

export default App;
