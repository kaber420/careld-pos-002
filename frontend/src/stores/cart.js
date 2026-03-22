import { writable, derived } from 'svelte/store';

function createCart() {
  const { subscribe, set, update } = writable([]);

  return {
    subscribe,
    addItem: (product) => update(items => {
      const existing = items.find(i => i.id === product.id);
      const stock = product.stock_quantity || 0;
      
      if (existing) {
        if (existing.quantity >= stock) return items;
        return items.map(i => i.id === product.id 
          ? { ...i, quantity: i.quantity + 1 } 
          : i
        );
      }
      if (stock <= 0) return items;
      return [...items, { ...product, quantity: 1 }];
    }),
    removeItem: (productId) => update(items => items.filter(i => i.id !== productId)),
    updateQuantity: (productId, quantity, stockQuantity) => update(items => {
      if (quantity <= 0) return items.filter(i => i.id !== productId);
      const stock = stockQuantity || items.find(i => i.id === productId)?.stock_quantity || 0;
      const finalQuantity = Math.min(quantity, stock);
      return items.map(i => i.id === productId ? { ...i, quantity: finalQuantity } : i);
    }),
    clear: () => set([]),
  };
}

export const cart = createCart();

export const cartTotal = derived(cart, ($cart) => {
  return $cart.reduce((total, item) => total + ((item.unit_price || 0) * item.quantity), 0);
});

export const cartItemsCount = derived(cart, ($cart) => {
  return $cart.reduce((count, item) => count + item.quantity, 0);
});
