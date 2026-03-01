import { useState, useCallback } from 'react';

export function useCart() {
    const [cart, setCart] = useState(() => {
        const savedCart = localStorage.getItem('cart');
        return savedCart ? JSON.parse(savedCart) : [];
    });

    const saveCart = useCallback((newCart) => {
        localStorage.setItem('cart', JSON.stringify(newCart));
    }, []);

    const addToCart = useCallback((product) => {
        setCart((prevCart) => {
            const newCart = [...prevCart, product];
            saveCart(newCart);
            return newCart;
        });
    }, [saveCart]);

    const removeFromCart = useCallback((index) => {
        setCart((prevCart) => {
            const newCart = prevCart.filter((_, i) => i !== index);
            saveCart(newCart);
            return newCart;
        });
    }, [saveCart]);

    const clearCart = useCallback(() => {
        setCart([]);
        saveCart([]);
    }, [saveCart]);

    const cartTotal = cart.reduce((total, item) => {
        const price = parseFloat(
            item.new_price?.toString().replace(',', '.').replace('zl', '') || '0'
        );
        return total + price;
    }, 0);

    const cartCount = cart.length;

    return {
        cart,
        addToCart,
        removeFromCart,
        clearCart,
        cartTotal,
        cartCount,
    };
}

