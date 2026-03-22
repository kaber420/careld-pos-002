import { writable } from 'svelte/store';

// activeModal can be: null, 'reception', 'detail', 'gallery', 'ticket', 'status'
export const activeModal = writable(null);

// modalContext holds data needed by the active modal (e.g., the device object)
export const modalContext = writable(null);

export function openModal(name, context = null) {
    if (context !== null) {
        modalContext.set(context);
    }
    activeModal.set(name);
}

export function closeModal() {
    activeModal.set(null);
    modalContext.set(null);
}
