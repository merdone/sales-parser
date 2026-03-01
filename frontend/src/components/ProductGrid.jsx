import { Link } from 'react-router-dom';
import './ProductGrid.css';

const API_URL = window.location.origin;

export default function ProductGrid({ products, loading, error, onAddToCart, selectedCategory, selectedStore, selectedPromotion }) {
    if (loading) {
        return <div className="grid"><p className="state-text">Loading offers...</p></div>;
    }

    if (error) {
        return <div className="grid"><p className="state-text error">Error: {error}</p></div>;
    }

    if (!products || products.length === 0) {
        return <div className="grid"><p className="state-text">No products yet.</p></div>;
    }

    const pages = Array.from(
        new Set(products.map((item) => item.source_image_url).filter(Boolean))
    );

    return (
        <div className="grid">
            {products.map((product, index) => {
                const imageUrl = product.image_url ? `${API_URL}${product.image_url}` : 'https://placehold.co/200x150';
                const rawPageIndex = product.source_image_url ? pages.indexOf(product.source_image_url) : 0;
                const pageIndex = rawPageIndex >= 0 ? rawPageIndex : 0;

                return (
                    <div key={index} className="card">
                        <div className="img-wrapper">
                            <img src={imageUrl} className="product-img" alt={product.product_name} loading="lazy" />
                        </div>
                        <div className="card-content">
                            <b>{product.product_name}</b>
                            <div className="price-container">
                                {product.old_price && (
                                    <span className="old-price">{product.old_price}</span>
                                )}
                                <span className="new-price">{product.new_price} zl</span>
                            </div>
                            <div className="card-actions">
                                <button
                                    className="add-btn"
                                    onClick={() => onAddToCart(product)}
                                >
                                    Add to cart
                                </button>
                                <Link
                                    to={`/magazine?category=${encodeURIComponent(selectedCategory)}&store=${encodeURIComponent(selectedStore)}&promotion=${encodeURIComponent(selectedPromotion)}&page=${pageIndex}`}
                                    className="source-link"
                                >
                                    View original page
                                </Link>
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
