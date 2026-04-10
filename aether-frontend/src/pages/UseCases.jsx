import React, { useState, useEffect } from 'react';
import { Layers, Search, Video, FileText, Image as ImageIcon, Code, Mic, Building2, TrendingUp, Presentation, ArrowUpLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../api';

export default function UseCases() {
    const navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState('');
    const [counts, setCounts] = useState({});

    useEffect(() => {
        const fetchCounts = async () => {
            try {
                const res = await apiFetch('/vault/categories/stats');
                if (res.ok) {
                    const data = await res.json();
                    setCounts(data);
                }
            } catch (err) {
                console.error("Failed to fetch category stats", err);
            }
        };
        fetchCounts();
    }, []);

    const categories = [
        { id: 'dev', name: 'פיתוח קוד', icon: Code, count: counts['dev'] || 0, color: 'text-blue-500', bg: 'bg-blue-50' },
        { id: 'design', name: 'יצירת תמונות ועיצוב', icon: ImageIcon, count: counts['design'] || 0, color: 'text-fuchsia-500', bg: 'bg-fuchsia-50' },
        { id: 'text', name: 'כתיבה וטקסט', icon: FileText, count: counts['text'] || 0, color: 'text-emerald-500', bg: 'bg-emerald-50' },
        { id: 'video', name: 'עריכת וידאו', icon: Video, count: counts['video'] || 0, color: 'text-amber-500', bg: 'bg-amber-50' },
        { id: 'audio', name: 'דיבוב ושמע', icon: Mic, count: counts['audio'] || 0, color: 'text-violet-500', bg: 'bg-violet-50' },
        { id: 'marketing', name: 'שיווק ו-SEO', icon: TrendingUp, count: counts['marketing'] || 0, color: 'text-cyan-500', bg: 'bg-cyan-50' },
        { id: 'presentations', name: 'מצגות משקיעים', icon: Presentation, count: counts['presentations'] || 0, color: 'text-rose-500', bg: 'bg-rose-50' },
        { id: 'enterprise', name: 'כלים ארגוניים', icon: Building2, count: counts['enterprise'] || 0, color: 'text-white/60', bg: 'bg-white/10 backdrop-blur-md' },
    ];

    const filteredCategories = categories.filter(c => c.name.toLowerCase().includes(searchQuery.toLowerCase()));

    const handleCategoryClick = (categoryName) => {
        navigate(`/vault?q=${encodeURIComponent(categoryName)}`);
    };

    return (
        <div className="flex flex-col w-full min-h-[85vh] animate-in fade-in duration-700 rtl" dir="rtl">

            {/* Header Content */}
            <div className="w-full flex flex-col items-center text-center mb-12">
                <div className="w-16 h-16 bg-white/10 backdrop-blur-md rounded-2xl flex items-center justify-center mb-6 shadow-sm border border-white/20">
                    <Layers className="w-8 h-8 text-white" />
                </div>
                <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight">
                    אינדקס תרחישי שימוש
                </h1>
                <p className="text-white/60 text-lg max-w-2xl">
                    סייר בין מאות כלים מאומתים המחולקים לתעשיות וצורכי הארגון. בחר קטגוריה כדי למקד את החיפוש.
                </p>
            </div>

            {/* Smart Search Bar */}
            <div className="w-full max-w-2xl mx-auto relative mb-12">
                <Search className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/50" />
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="חפש קטגוריה או תעשייה (לדוגמה: וידאו, שיווק)..."
                    className="w-full bg-white/5 backdrop-blur-md border border-white/20 rounded-2xl pr-12 pl-4 py-4 text-white focus:outline-none focus:ring-2 focus:ring-neutral-900/10 focus:border-white/20 transition-all shadow-sm text-lg"
                />
            </div>

            {/* Masonry-esque Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 animate-in slide-in-from-bottom-8 duration-700">
                {filteredCategories.length > 0 ? filteredCategories.map((category) => {
                    const Icon = category.icon;
                    return (
                        <div
                            key={category.id}
                            onClick={() => handleCategoryClick(category.name)}
                            className="group flex flex-col p-6 bg-white/5 backdrop-blur-md border border-white/20 rounded-3xl hover:border-white/20 transition-all hover:shadow-lg cursor-pointer text-right relative overflow-hidden"
                        >
                            <div className="flex justify-between items-start mb-6">
                                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${category.bg} ${category.color} transition-transform group-hover:scale-110`}>
                                    <Icon className="w-6 h-6" />
                                </div>
                                <span className="bg-white/5 backdrop-blur-md border border-white/10 px-2 py-1 rounded-md text-xs font-semibold text-white/50">
                                    {category.count} כלים
                                </span>
                            </div>

                            <h3 className="text-xl font-bold text-white mb-2 truncate">
                                {category.name}
                            </h3>

                            <div className="mt-4 pt-4 border-t border-neutral-50 flex items-center gap-2 text-sm font-medium text-white/50 group-hover:text-white transition-colors">
                                צפה בכלים המומלצים
                                <ArrowUpLeft className="w-4 h-4" />
                            </div>
                        </div>
                    );
                }) : (
                    <div className="col-span-1 md:col-span-2 lg:col-span-4 flex flex-col items-center justify-center py-20 text-white/60">
                        <Search className="w-12 h-12 text-neutral-200 mb-4" />
                        <p>לא מצאנו קטגוריות התואמות לחיפוש שלך.</p>
                    </div>
                )}
            </div>

        </div>
    );
}
