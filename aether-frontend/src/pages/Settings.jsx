import React, { useState } from 'react';
import { User, Bell, Shield, Wallet, LogOut, ChevronLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Settings() {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('profile');

    const tabs = [
        { id: 'profile', label: 'פרופיל אישי', icon: User },
        { id: 'notifications', label: 'התראות', icon: Bell },
        { id: 'security', label: 'אבטחה', icon: Shield },
        { id: 'billing', label: 'ניהול מנוי', icon: Wallet },
    ];

    return (
        <div className="flex flex-col md:flex-row w-full max-w-5xl mx-auto min-h-[80vh] gap-8 animate-in fade-in duration-700 rtl" dir="rtl">

            {/* Sidebar Navigation */}
            <aside className="w-full md:w-64 flex flex-col gap-2">
                <div className="mb-6 px-4">
                    <h1 className="text-2xl font-bold text-white">הגדרות חשבון</h1>
                    <p className="text-sm text-white/60 mt-1">ניהול ההעדפות שלך ב-Aether</p>
                </div>

                <nav className="flex flex-row md:flex-col gap-1 overflow-x-auto md:overflow-hidden pb-4 md:pb-0 px-4 md:px-0 scrollbar-hide">
                    {tabs.map(tab => {
                        const Icon = tab.icon;
                        const isActive = activeTab === tab.id;
                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all whitespace-nowrap ${isActive
                                        ? 'bg-white/20 backdrop-blur-md text-white shadow-md'
                                        : 'text-white/70 hover:bg-white/10 backdrop-blur-md hover:text-white'
                                    }`}
                            >
                                <Icon className="w-5 h-5" />
                                {tab.label}
                            </button>
                        );
                    })}
                </nav>

                <div className="mt-auto px-4 pt-8 border-t border-white/10 hidden md:block">
                    <button onClick={() => navigate('/')} className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-red-500 hover:bg-red-50 rounded-xl transition-colors w-full">
                        <LogOut className="w-5 h-5" />
                        התנתקות
                    </button>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 bg-white/5 backdrop-blur-md border border-white/20 rounded-3xl p-6 md:p-10 shadow-sm animate-in slide-in-from-left-4 duration-500">

                {activeTab === 'profile' && (
                    <div className="max-w-xl animate-in fade-in duration-300">
                        <h2 className="text-xl font-bold text-white mb-6 border-b border-white/10 pb-4">פרטים אישיים</h2>

                        <div className="flex items-center gap-6 mb-8">
                            <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600 text-2xl font-bold uppercase ring-4 ring-white shadow-sm">
                                YB
                            </div>
                            <div className="flex flex-col gap-2">
                                <button className="px-4 py-2 bg-white/10 backdrop-blur-md text-white text-sm font-medium rounded-lg hover:bg-white/20 backdrop-blur-md transition-colors">
                                    החלף תמונה
                                </button>
                                <button className="text-xs text-white/60 hover:text-red-500 transition-colors text-right">
                                    הסר תמונה
                                </button>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div className="flex flex-col gap-2">
                                <label className="text-sm font-semibold text-white/80">שם מלא</label>
                                <input type="text" defaultValue="יובל בלנק" className="w-full bg-white/5 backdrop-blur-md border border-white/20 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-neutral-900/10 focus:border-white/20 transition-all" />
                            </div>
                            <div className="flex flex-col gap-2">
                                <label className="text-sm font-semibold text-white/80">דואר אלקטרוני</label>
                                <input type="email" defaultValue="yuval@example.com" disabled className="w-full bg-white/10 backdrop-blur-md border border-white/20 text-white/60 rounded-xl px-4 py-3 cursor-not-allowed" dir="ltr" />
                                <span className="text-xs text-white/50">יש לפנות לתמיכה כדי לשנות כתובת אימייל מקושרת.</span>
                            </div>
                            <div className="flex flex-col gap-2">
                                <label className="text-sm font-semibold text-white/80">תפקיד / טייטל</label>
                                <input type="text" placeholder="לדוגמה: מנהל שיווק, מייסד..." className="w-full bg-white/5 backdrop-blur-md border border-white/20 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-neutral-900/10 focus:border-white/20 transition-all" />
                            </div>
                        </div>

                        <div className="mt-10 pt-6 border-t border-white/10 flex justify-end">
                            <button className="px-6 py-3 bg-white/20 backdrop-blur-md text-white text-sm font-medium rounded-xl hover:bg-white/10 backdrop-blur-md transition-all shadow-md">
                                שמור שינויים
                            </button>
                        </div>
                    </div>
                )}

                {activeTab === 'notifications' && (
                    <div className="max-w-xl animate-in fade-in duration-300">
                        <h2 className="text-xl font-bold text-white mb-6 border-b border-white/10 pb-4">הגדרות התראה</h2>
                        <div className="space-y-6">
                            {[
                                { title: 'כלים חדשים במחסנית', desc: 'קבל עדכון כשכלי חדש ששמרת מעדכן פיצ׳רים.' },
                                { title: 'ניוזלטר שבועי', desc: 'סיכום הכלים החמים של השבוע בעולמות ה-AI.' },
                                { title: 'התראות אבטחה', desc: 'עדכונים חשובים על החשבון שלך.' }
                            ].map((item, i) => (
                                <div key={i} className="flex items-center justify-between p-4 border border-white/10 rounded-2xl">
                                    <div className="flex flex-col">
                                        <span className="font-semibold text-white mb-1">{item.title}</span>
                                        <span className="text-sm text-white/60">{item.desc}</span>
                                    </div>
                                    <label className="relative inline-flex items-center cursor-pointer">
                                        <input type="checkbox" className="sr-only peer" defaultChecked={i !== 1} />
                                        <div className="w-11 h-6 bg-white/20 backdrop-blur-md peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white/5 backdrop-blur-md after:border-white/30 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
                                    </label>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'security' && (
                    <div className="max-w-xl animate-in fade-in duration-300">
                        <h2 className="text-xl font-bold text-white mb-6 border-b border-white/10 pb-4">אבטחה ופרטיות</h2>
                        <div className="p-6 bg-amber-50 border border-amber-200 rounded-2xl flex items-start gap-4 mb-8">
                            <Shield className="w-6 h-6 text-amber-600 shrink-0 mt-1" />
                            <div>
                                <h3 className="font-semibold text-amber-900 mb-1">החשבון שלך מוגן באמצעות התחברות ללא סיסמה</h3>
                                <p className="text-sm text-amber-700 leading-relaxed">אנו משתמשים ב-Magic Links או ספקי זהות (Google/GitHub) כדי לשמור על האבטחה המקסימלית של המידע שלך. אין סיסמאות שניתן לגנוב.</p>
                            </div>
                        </div>
                        <button className="flex justify-between items-center w-full px-5 py-4 border border-white/20 rounded-xl hover:bg-white/5 backdrop-blur-md transition-colors text-right">
                            <div className="flex flex-col">
                                <span className="font-medium text-white">היסטוריית התחברויות</span>
                                <span className="text-sm text-white/60">צפה במכשירים שהתחברו לחשבון שלך</span>
                            </div>
                            <ChevronLeft className="w-5 h-5 text-white/50" />
                        </button>
                    </div>
                )}

                {activeTab === 'billing' && (
                    <div className="max-w-xl animate-in fade-in duration-300">
                        <h2 className="text-xl font-bold text-white mb-6 border-b border-white/10 pb-4">ניהול מנוי</h2>
                        <div className="p-8 border border-white/20 rounded-3xl bg-white/5 backdrop-blur-md flex flex-col md:flex-row justify-between items-center gap-6 mb-8">
                            <div>
                                <span className="inline-block px-3 py-1 bg-white/20 backdrop-blur-md text-white/80 text-xs font-bold uppercase tracking-wider rounded-lg mb-3">תוכנית נוכחית</span>
                                <h3 className="text-2xl font-bold text-white mb-1">Aether Free</h3>
                                <p className="text-white/60 text-sm">גישה לחיפושים בסיסיים ושמירת כלים מוגבלת.</p>
                            </div>
                            <button onClick={() => navigate('/upgrade')} className="px-6 py-3 bg-cyan-600 text-white font-medium rounded-xl hover:bg-cyan-700 transition-colors shadow-lg whitespace-nowrap">
                                שדרג ל-Pro
                            </button>
                        </div>
                    </div>
                )}

            </main>
        </div>
    );
}
