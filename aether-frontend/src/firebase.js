import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from "firebase/auth";

// Your web app's Firebase configuration
// IMPORTANT: Replace these with your actual Firebase project config later
const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyD-PLACEHOLDER",
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "aether-ai-compass.firebaseapp.com",
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "aether-ai-compass",
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "aether-ai-compass.appspot.com",
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "123456789",
    appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:123456789:web:abcdefgh"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

export { auth, googleProvider, signInWithPopup, signOut };
