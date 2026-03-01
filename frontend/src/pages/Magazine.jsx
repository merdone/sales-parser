import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useProducts } from '../hooks/useProducts';
import './Magazine.css';

const CATEGORY_LABELS = [
    { value: 'Wszystko', label: 'All' },
    { value: 'słodycze i przekąski', label: 'Sweets & Snacks' },
    { value: 'mięso i wędliny', label: 'Meat & Deli' },
    { value: 'nabiał i jajka', label: 'Dairy & Eggs' },
    { value: 'ryby i owoce morza', label: 'Fish & Seafood' },
    { value: 'pieczywo i wypieki', label: 'Bakery' },
    { value: 'napoje', label: 'Beverages' },
    { value: 'mrożonki', label: 'Frozen' },
    { value: 'produkty suche', label: 'Dry Goods' },
    { value: 'produkty śniadaniowe', label: 'Breakfast' },
    { value: 'gotowe dania', label: 'Ready Meals' },
    { value: 'inne', label: 'Other' },
];

const ZOOM_MIN = 0.7;
const ZOOM_MAX = 2.2;
const ZOOM_STEP = 0.1;

const getBoundingBox = (points = []) => {
    if (!Array.isArray(points) || points.length === 0) return null;
    const xs = points.map((p) => Number(p.x ?? p?.get?.('x') ?? 0));
    const ys = points.map((p) => Number(p.y ?? p?.get?.('y') ?? 0));
    const left = Math.max(0, Math.min(...xs));
    const top = Math.max(0, Math.min(...ys));
    const right = Math.min(100, Math.max(...xs));
    const bottom = Math.min(100, Math.max(...ys));
    const width = Math.max(0, right - left);
    const height = Math.max(0, bottom - top);
    if (width === 0 || height === 0) return null;
    return { left, top, right, bottom };
};

export default function Magazine({ onAddToCart }) {
    const [searchParams, setSearchParams] = useSearchParams();
    const categoryParam = searchParams.get('category') || 'Wszystko';
    const storeParam = searchParams.get('store') || 'all';
    const promotionParam = searchParams.get('promotion') || 'all';
    const pageParam = Number(searchParams.get('page') || '0');
    const pageIndex = Number.isNaN(pageParam) ? 0 : pageParam;

    const { products, loading, error, loadProducts } = useProducts();
    const [toast, setToast] = useState(null);
    const [zoom, setZoom] = useState(1);

    useEffect(() => {
        loadProducts(categoryParam, storeParam, promotionParam);
    }, [categoryParam, storeParam, promotionParam, loadProducts]);

    const pages = useMemo(() => {
        const urls = products
            .map((item) => item.source_image_url)
            .filter(Boolean);
        return Array.from(new Set(urls));
    }, [products]);

    const maxIndex = Math.max(0, pages.length - 1);
    const safeIndex = Math.min(Math.max(pageIndex, 0), maxIndex);
    const spreadIndex = Math.floor(safeIndex / 2) * 2;
    const leftPage = pages[spreadIndex] || null;
    const rightPage = pages[spreadIndex + 1] || null;
    const isSinglePage = Boolean(leftPage) && !rightPage;

    const categoryLabel = CATEGORY_LABELS.find((cat) => cat.value === categoryParam)?.label ?? 'All';

    const updatePage = (nextIndex) => {
        const clamped = Math.min(Math.max(nextIndex, 0), maxIndex);
        setSearchParams((prev) => {
            const params = new URLSearchParams(prev);
            params.set('category', categoryParam);
            params.set('store', storeParam);
            params.set('promotion', promotionParam);
            params.set('page', String(clamped));
            return params;
        });
    };

    const updateZoom = (delta) => {
        setZoom((prev) => Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, Number((prev + delta).toFixed(2)))));
    };

    const handleFitToScreen = () => {
        setZoom(1);
    };

    const selectThumbnail = (index) => {
        updatePage(index);
    };

    const pageItems = useMemo(() => {
        return products.filter((item) => item.source_image_url === leftPage || item.source_image_url === rightPage);
    }, [products, leftPage, rightPage]);

    const handlePageClick = (event, pageUrl) => {
        if (!pageUrl || !onAddToCart) return;
        const bounds = event.currentTarget.getBoundingClientRect();
        const xPercent = ((event.clientX - bounds.left) / bounds.width) * 100;
        const yPercent = ((event.clientY - bounds.top) / bounds.height) * 100;

        const matching = pageItems.find((item) => {
            if (item.source_image_url !== pageUrl) return false;
            const bbox = getBoundingBox(item.coordinates);
            if (!bbox) return false;
            return xPercent >= bbox.left && xPercent <= bbox.right && yPercent >= bbox.top && yPercent <= bbox.bottom;
        });

        if (matching) {
            onAddToCart(matching);
            setToast(`${matching.product_name} added to cart`);
            window.clearTimeout(handlePageClick.toastTimer);
            handlePageClick.toastTimer = window.setTimeout(() => setToast(null), 1800);
        }
    };

    if (loading) {
        return (
            <section className="page">
                <h2>Leaflet Viewer</h2>
                <p className="muted">Loading leaflet pages...</p>
            </section>
        );
    }

    if (error) {
        return (
            <section className="page">
                <h2>Leaflet Viewer</h2>
                <p className="error">Error: {error}</p>
            </section>
        );
    }

    return (
        <section className="page">
            <div className="page-header">
                <div>
                    <h2>Leaflet Viewer</h2>
                    <p>Flip through the original leaflet and jump to the right section.</p>
                </div>
                <span className="chip">Section: {categoryLabel}</span>
            </div>

            <div className="viewer">
                <div className="viewer-toolbar">
                    <span className="viewer-title">Leaflet spread</span>
                    <div className="viewer-actions">
                        {toast && <span className="toast">{toast}</span>}
                        <div className="zoom-controls">
                            <button className="ghost-btn" onClick={() => updateZoom(-ZOOM_STEP)} disabled={zoom <= ZOOM_MIN}>
                                −
                            </button>
                            <span className="zoom-value">{Math.round(zoom * 100)}%</span>
                            <button className="ghost-btn" onClick={() => updateZoom(ZOOM_STEP)} disabled={zoom >= ZOOM_MAX}>
                                +
                            </button>
                            <button className="ghost-btn" onClick={handleFitToScreen}>
                                Fit
                            </button>
                        </div>
                    </div>
                </div>
                <div className="viewer-stage">
                    <div className="spread-wrap" style={{ '--spread-scale': zoom }}>
                        <div className={`page-spread ${isSinglePage ? 'single' : ''}`}>
                            {leftPage ? (
                                <button
                                    type="button"
                                    className="page-button"
                                    onClick={(event) => handlePageClick(event, leftPage)}
                                >
                                    <img src={leftPage} alt="Leaflet page" className="leaflet-page" />
                                </button>
                            ) : (
                                <div className="page-placeholder">No pages available</div>
                            )}
                            {rightPage && (
                                <button
                                    type="button"
                                    className="page-button"
                                    onClick={(event) => handlePageClick(event, rightPage)}
                                >
                                    <img src={rightPage} alt="Leaflet page" className="leaflet-page" />
                                </button>
                            )}
                        </div>
                    </div>
                </div>
                <div className="viewer-controls">
                    <button className="ghost-btn" onClick={() => updatePage(spreadIndex - 2)} disabled={spreadIndex === 0}>
                        ◀ Previous
                    </button>
                    <span className="viewer-status">
                        Page {Math.min(spreadIndex + 1, pages.length)} of {pages.length || 1}
                    </span>
                    <button
                        className="ghost-btn"
                        onClick={() => updatePage(spreadIndex + 2)}
                        disabled={spreadIndex + 2 > maxIndex}
                    >
                        Next ▶
                    </button>
                </div>
                <div className="thumbnail-strip">
                    {pages.map((pageUrl, idx) => (
                        <button
                            key={`${pageUrl}-${idx}`}
                            type="button"
                            className={`thumbnail ${idx === spreadIndex || idx === spreadIndex + 1 ? 'active' : ''}`}
                            onClick={() => selectThumbnail(idx)}
                        >
                            <img src={pageUrl} alt={`Leaflet page ${idx + 1}`} />
                            <span>{idx + 1}</span>
                        </button>
                    ))}
                </div>
            </div>
        </section>
    );
}
