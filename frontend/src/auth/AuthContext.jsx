import { createContext, useContext, useEffect, useState } from "react";
import { apiFetch } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({children}) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
    (async () => {
        const { data } = await apiFetch('/api/auth/me/');
        if (data && data.authenticated) {
        setUser({ username: data.username });
        }
        setLoading(false);
    })();
    }, []);

   async function login(username, password) {
        const { ok, data } = await apiFetch('/api/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });

        if (ok && data?.success) {
            setUser({ username: data.username });
            return { ok: true };
        }

        return { ok: false, error: data?.error || 'Ошибка входа' };
    }

    async function logout() {
        await apiFetch('/api/auth/logout/', { method: 'POST' });
        setUser(null);
    }
    
    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}


export const useAuth = () => useContext(AuthContext);