import { useState, useCallback } from 'react';

const API_URL = window.location.origin;

export function useProducts() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [currentProducts, setCurrentProducts] = useState([]);
    const [rawProducts, setRawProducts] = useState([]);

    const loadProducts = useCallback(async (category = "Wszystko", store = "all", promotion = "all") => {
        setLoading(true);
        setError(null);
        try {
            let url = `${API_URL}/api/promotions`;
            const params = [];
            if (category && category !== "Wszystko") {
                params.push(`category=${encodeURIComponent(category)}`);
            }
            if (store && store !== "all") {
                params.push(`store=${encodeURIComponent(store)}`);
            }
            if (promotion && promotion !== "all") {
                params.push(`promotion=${encodeURIComponent(promotion)}`);
            }
            if (params.length) {
                url += `?${params.join('&')}`;
            }

            const res = await fetch(url);
            if (!res.ok) throw new Error("Network error");

            const data = await res.json();

            // Присваиваем временные ID если их нет
            const productsWithIds = data.map((p, index) => ({
                ...p,
                id: p.id || index,
            }));

            setRawProducts(productsWithIds);
            setProducts(productsWithIds);
            setCurrentProducts(productsWithIds);
        } catch (err) {
            console.error(err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    const sortProducts = useCallback((criteria) => {
        if (!currentProducts.length) return;

        let sorted = [...currentProducts];
        const getPrice = (p) => {
            if (!p.new_price) return 0;
            return parseFloat(
                p.new_price.toString().replace(',', '.').replace('zl', '')
            );
        };

        if (criteria === 'price_asc') {
            sorted.sort((a, b) => getPrice(a) - getPrice(b));
        } else if (criteria === 'price_desc') {
            sorted.sort((a, b) => getPrice(b) - getPrice(a));
        } else if (criteria === 'name') {
            sorted.sort((a, b) => a.product_name.localeCompare(b.product_name));
        }

        setProducts(sorted);
    }, [currentProducts]);

    return {
        products,
        rawProducts,
        loading,
        error,
        loadProducts,
        sortProducts,
    };
}
