import { useEffect, useMemo, useState } from 'react';
import CategoryDropdown from '../components/CategoryDropdown';
import ProductGrid from '../components/ProductGrid';
import SortButtons from '../components/SortButtons';
import { useProducts } from '../hooks/useProducts';
import './Home.css';

const CATEGORIES = [
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

const STORE_LABELS = {
    all: 'All stores',
};

const PROMOTION_LABELS = {
    all: 'All promotions',
};

export default function Home({ onAddToCart }) {
    const [selectedCategory, setSelectedCategory] = useState('Wszystko');
    const [selectedStore, setSelectedStore] = useState('all');
    const [selectedPromotion, setSelectedPromotion] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [storeOptions, setStoreOptions] = useState([{ value: 'all', label: STORE_LABELS.all }]);
    const [promotionOptions, setPromotionOptions] = useState([{ value: 'all', label: PROMOTION_LABELS.all }]);
    const { products, loading, error, loadProducts, sortProducts } = useProducts();

    useEffect(() => {
        loadProducts(selectedCategory, selectedStore, selectedPromotion);
    }, [selectedCategory, selectedStore, selectedPromotion, loadProducts]);

    useEffect(() => {
        const loadStores = async () => {
            try {
                const res = await fetch('/api/stores');
                if (!res.ok) throw new Error('Failed to load stores');
                const data = await res.json();
                const options = [{ value: 'all', label: STORE_LABELS.all }];
                (data.stores || []).forEach((store) => {
                    options.push({ value: store, label: store });
                });
                setStoreOptions(options);
            } catch (err) {
                console.error(err);
            }
        };

        const loadPromotions = async () => {
            try {
                const res = await fetch('/api/promotions-types');
                if (!res.ok) throw new Error('Failed to load promotion types');
                const data = await res.json();
                const options = [{ value: 'all', label: PROMOTION_LABELS.all }];
                (data.promotion_types || []).forEach((promotion) => {
                    options.push({ value: promotion, label: promotion });
                });
                setPromotionOptions(options);
            } catch (err) {
                console.error(err);
            }
        };

        loadStores();
        loadPromotions();
    }, []);

    const selectedLabel = useMemo(() => {
        return CATEGORIES.find((cat) => cat.value === selectedCategory)?.label ?? 'All';
    }, [selectedCategory]);

    const filteredProducts = useMemo(() => {
        const term = searchQuery.trim().toLowerCase();
        if (!term) return products;
        return products.filter((item) => {
            const fields = [item.product_name, item.chain_name, item.promotion_name];
            return fields.some((value) =>
                value && String(value).toLowerCase().includes(term)
            );
        });
    }, [products, searchQuery]);

    return (
        <section className="page">
            <div className="page-header">
                <div>
                    <h2>Latest Promotions</h2>
                    <p>Browse deals, sort offers, and add items to your cart.</p>
                </div>
                <span className="chip">Category: {selectedLabel}</span>
            </div>

            <div className="controls">
                <CategoryDropdown
                    categories={CATEGORIES}
                    selectedCategory={selectedCategory}
                    onCategoryChange={setSelectedCategory}
                />
                <CategoryDropdown
                    categories={storeOptions}
                    selectedCategory={selectedStore}
                    onCategoryChange={setSelectedStore}
                />
                <CategoryDropdown
                    categories={promotionOptions}
                    selectedCategory={selectedPromotion}
                    onCategoryChange={setSelectedPromotion}
                />
                <input
                    className="search-input"
                    type="search"
                    placeholder="Search products, stores, promotions"
                    value={searchQuery}
                    onChange={(event) => setSearchQuery(event.target.value)}
                    aria-label="Search offers"
                    spellCheck="false"
                />
                <SortButtons onSort={sortProducts} />
            </div>

            <ProductGrid
                products={filteredProducts}
                loading={loading}
                error={error}
                onAddToCart={onAddToCart}
                selectedCategory={selectedCategory}
                selectedStore={selectedStore}
                selectedPromotion={selectedPromotion}
            />
        </section>
    );
}
