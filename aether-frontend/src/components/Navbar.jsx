import { useState, useEffect } from "react";
import { Search, Bell, LogIn, LogOut } from "lucide-react";
import { useAuth } from "../AuthContext";

export function Navbar() {
    const [isScrolled, setIsScrolled] = useState(false);
    const { currentUser, loginWithGoogle, logout } = useAuth();

    // UI-only check for rendering the button
    const isAdmin = currentUser?.email && (
        currentUser.email === "yuval@example.com" || 
        import.meta.env.VITE_ADMIN_EMAILS?.includes(currentUser.email)
    );

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 20);
        };
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <nav
            className={`fixed top-0 left-0 w-full z-50 transition-all duration-300 ${isScrolled
                ? "bg-aether-black/80 backdrop-blur-md border-b border-aether-border"
                : "bg-transparent backdrop-blur-sm"
                }`}
            dir="ltr"
        >
            <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                {/* Logo */}
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-aether-accent to-blue-600 blur-[2px] opacity-80 animate-pulse" />
                    <span className="text-xl font-medium tracking-tight text-white/90">
                        Aether
                    </span>
                </div>

                {/* Desktop Navigation */}
                <div className="hidden md:flex items-center gap-8">
                    {["Discover", "Library", "Agents", "Settings"].map((item) => (
                        <a
                            key={item}
                            href="#"
                            className="text-sm font-medium text-white/60 hover:text-white transition-colors duration-200"
                        >
                            {item}
                        </a>
                    ))}
                    {isAdmin && (
                        <a 
                            href="/admin/vault" 
                            className="text-sm font-bold text-cyan-400 hover:text-cyan-300 drop-shadow-[0_0_8px_rgba(6,182,212,0.5)] transition-all duration-200"
                        >
                            Admin Vault
                        </a>
                    )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-4">
                    <button className="p-2 text-white/60 hover:text-white hover:bg-white/5 rounded-full transition-all">
                        <Search className="w-5 h-5" />
                    </button>
                    {/* User Profile / Auth */}
                    {currentUser ? (
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-white/10 border border-white/5 overflow-hidden" title={currentUser.email}>
                                <img
                                    src={currentUser.photoURL || "https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"}
                                    alt="User"
                                    className="w-full h-full object-cover opacity-80 hover:opacity-100 transition-opacity"
                                    referrerPolicy="no-referrer"
                                />
                            </div>
                            <button onClick={logout} className="p-2 text-white/60 hover:text-rose-400 hover:bg-white/5 rounded-full transition-all" title="התנתק">
                                <LogOut className="w-5 h-5" />
                            </button>
                        </div>
                    ) : (
                        <button
                            onClick={loginWithGoogle}
                            className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-full text-white text-sm font-medium transition-all"
                        >
                            <LogIn className="w-4 h-4" /> Sign In
                        </button>
                    )}
                </div>
            </div>
        </nav>
    );
}
