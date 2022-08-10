import { readable, writable } from 'svelte/store';

export const current_user = writable({authenticated: "loading"});
// export const current_user = writable({benutzername: "admin", rolle: "admin", isAuthenticated: true, apps: [{ name: "benutzer", titel: "Benutzer" }, { name: "material", titel: "Material" }, { name: "kalender", titel: "Kalender" }, { name: "einstellungen", titel: "Einstellungen" }]});
export const current_view = writable("loading");
