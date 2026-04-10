import React, { useState, useEffect } from 'react';
import { ArrowLeft, Mail, Github, Compass } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function Activation() {
    const navigate = useNavigate();
    const { loginWithGoogle, currentUser } = useAuth();
    const [email, setEmail] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSent, setIsSent] = useState(false);

    const handleMagicLink = (e) => {
        e.preventDefault();
        if (!email) return;

        setIsLoading(true);
        // Simulate network request
        setTimeout(() => {
            setIsLoading(false);
            setIsSent(true);
        }, 1200);
    };

    const handleGoogleLogin = async () => {
        try {
            await loginWithGoogle();
            navigate('/');
        } catch (error) {
            alert("שגיאת התחברות מגוגל: " + error.message);
            console.error("Login failed:", error);
        }
    };

    useEffect(() => {
        if (currentUser) {
            // Only navigate on mount if already logged in, not tracking state changes vigorously 
            navigate('/');
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <div className="flex flex-col items-center justify-center min-h-[85vh] w-full rtl" dir="rtl">

            {/* Nav Back */}
            <div className="w-full max-w-md flex justify-start mb-6">
                <button
                    onClick={() => navigate('/')}
                    className="flex items-center gap-2 text-white/60 hover:text-white transition-colors text-sm font-medium"
                >
                    <ArrowLeft className="w-4 h-4" />
                    חזרה הביתה
                </button>
            </div>

            {/* Main Activation Card */}
            <div className="w-full max-w-md bg-white/5 backdrop-blur-md rounded-3xl p-8 md:p-10 border border-white/20 shadow-xl animate-in slide-in-from-bottom-8 fade-in duration-700">

                {/* Branding / Header */}
                <div className="flex flex-col items-center mb-8">
                    <div className="w-12 h-12 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center mb-6 shadow-inner">
                        <Compass className="w-6 h-6 text-white" />
                    </div>
                    <h1 className="text-2xl font-bold text-white mb-2 tracking-tight">ברוכים הבאים ל-Aether</h1>
                    <p className="text-white/60 text-sm text-center">היכנס או צור חשבון כדי לשמור כלים ולנהל את מחסנית הטכנולוגיה שלך.</p>
                </div>

                {!isSent ? (
                    <div className="flex flex-col gap-4">
                        {/* OAuth Buttons */}
                        <button onClick={handleGoogleLogin} className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-white/5 backdrop-blur-md border border-white/20 rounded-xl text-white/80 font-medium hover:bg-white/5 backdrop-blur-md transition-all shadow-sm">
                            <svg className="w-5 h-5" viewBox="0 0 24 24">
                                <path
                                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                                    fill="#4285F4"
                                />
                                <path
                                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.16v2.84C3.99 20.53 7.7 23 12 23z"
                                    fill="#34A853"
                                />
                                <path
                                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.16C1.43 8.55 1 10.22 1 12s.43 3.45 1.16 4.93l3.68-2.84z"
                                    fill="#FBBC05"
                                />
                                <path
                                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.16 7.07l3.68 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                                    fill="#EA4335"
                                />
                            </svg>
                            המשך עם Google
                        </button>

                        <button className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-white/20 backdrop-blur-md border border-white/20 rounded-xl text-white font-medium hover:bg-white/10 backdrop-blur-md transition-all shadow-sm">
                            <Github className="w-5 h-5" />
                            המשך עם GitHub
                        </button>

                        <div className="flex items-center gap-3 my-4">
                            <div className="h-px bg-white/20 backdrop-blur-md flex-1"></div>
                            <span className="text-xs font-medium text-white/50 uppercase tracking-widest">או</span>
                            <div className="h-px bg-white/20 backdrop-blur-md flex-1"></div>
                        </div>

                        {/* Magic Link Form */}
                        <form onSubmit={handleMagicLink} className="flex flex-col gap-3">
                            <div className="relative">
                                <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none">
                                    <Mail className="w-5 h-5 text-white/50" />
                                </div>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="your@email.com"
                                    className="w-full bg-white/5 backdrop-blur-md border border-white/20 text-white rounded-xl pr-10 pl-4 py-3 focus:outline-none focus:ring-2 focus:ring-neutral-900/10 focus:border-white/20 transition-all"
                                    required
                                    dir="ltr"
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={isLoading || !email}
                                className="w-full flex items-center justify-center py-3 bg-white/5 backdrop-blur-md border border-white/20 text-white rounded-xl font-medium hover:bg-white/5 backdrop-blur-md transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isLoading ? (
                                    <span className="flex items-center gap-2">
                                        <div className="w-4 h-4 rounded-full border-2 border-white/30 border-t-neutral-900 animate-spin"></div>
                                        שולח...
                                    </span>
                                ) : (
                                    'התחבר עם לינק קסם'
                                )}
                            </button>
                        </form>
                    </div>
                ) : (
                    // Success State (Magic Link Sent)
                    <div className="flex flex-col items-center justify-center text-center py-6 animate-in zoom-in-95 duration-500">
                        <div className="w-16 h-16 bg-emerald-50 rounded-full flex items-center justify-center mb-6">
                            <Mail className="w-8 h-8 text-emerald-500" />
                        </div>
                        <h2 className="text-xl font-bold text-white mb-2">בדוק את תיבת המייל שלך</h2>
                        <p className="text-white/60 text-sm mb-8">
                            שלחנו לינק התחברות קסום לכתובת <strong className="text-white" dir="ltr">{email}</strong>
                        </p>
                        <button
                            onClick={() => setIsSent(false)}
                            className="text-sm font-medium text-white/60 hover:text-white transition-colors"
                        >
                            לא קיבלת? נסה שוב
                        </button>
                    </div>
                )}
            </div>

            {/* Footer Terms */}
            <p className="text-xs text-white/50 mt-8 text-center max-w-sm">
                בהמשך התהליך, אתה מסכים ל<a href="/terms" className="underline hover:text-white/80">תנאי השימוש</a> ול<a href="/privacy" className="underline hover:text-white/80">מדיניות הפרטיות</a> שלנו.
            </p>
        </div>
    );
}
