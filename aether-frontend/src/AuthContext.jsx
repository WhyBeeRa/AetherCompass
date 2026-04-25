import React, { createContext, useContext, useState, useEffect } from 'react';
import { auth, googleProvider, signInWithPopup, signOut } from './firebase';
import { onAuthStateChanged } from 'firebase/auth';

const AuthContext = createContext();

export function useAuth() {
    return useContext(AuthContext);
}

export function AuthProvider({ children }) {
    const [currentUser, setCurrentUser] = useState(null);
    const [loading, setLoading] = useState(true);

    async function loginWithGoogle() {
        try {
            const result = await signInWithPopup(auth, googleProvider);
            return result.user;
        } catch (error) {
            console.error("Google Login Error:", error);
            throw error;
        }
    }

    async function logout() {
        return signOut(auth);
    }

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, user => {
            setCurrentUser(user);
            setLoading(false);
        });

        return unsubscribe;
    }, []);

    const [isDevAdmin] = useState(() => {
        if (typeof window === 'undefined') return false;
        // Lock in dev mode for the duration of the session if localhost is detected once
        const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        if (isLocal) {
            console.log("[Auth] Dev Mode Active: Bypass Enabled");
            return true;
        }
        return false;
    });

    const isAdmin = !!(
        isDevAdmin ||
        // [PRODUCTION] Standard Firebase Admin Whitelist
        (currentUser?.email && 
         (import.meta.env.VITE_ADMIN_EMAILS?.toLowerCase().split(',').map(e => e.trim()) || []).includes(currentUser.email.toLowerCase()))
    );

    const value = {
        currentUser,
        isAdmin,
        loginWithGoogle,
        logout
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
}
