import { readable, writable } from 'svelte/store';

export const current_user = writable({isAuthenticated: false});