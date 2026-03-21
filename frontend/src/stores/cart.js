import { writable, derived } from 'svelte/store';

function createCart() {
  const { subscribe, set, update } = writable([]);

  return {
    subscribe,
    addItem: (product) => update(items => {
      const existing = items.find(i => i.id === product.id);
      if (existing) {
        return items.map(i => i.id === product.id 
          ? { ...i, quantity: i.quantity + 1 } 
          : i
        );
      }
      return [...items, { ...product, quantity: 1 }];
    }),
    removeItem: (productId) => update(items => items.filter(i => i.id !== productId)),
    updateQuantity: (productId, quantity) => update(items => {
      if (quantity <= 0) return items.filter(i => i.id !== productId);
      return items.map(i => i.id === productId ? { ...i, quantity } : i);
    }),
    clear: () => set([]),
  };
}

export const cart = createCart();

export const cartTotal = derived(cart, ($cart) => {
  return $cart.reduce((total, item) => total + (item.unit_price * item.quantity), 0);
});

export const cartItemsCount = derived(cart, ($cart) => {
  return $cart.reduce((count, item) => count + item.quantity, 0);
});
