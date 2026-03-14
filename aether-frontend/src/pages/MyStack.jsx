import React, { useState, useEffect } from 'react';
import { Bookmark, LayoutGrid, List, Search, ArrowUpRight, FolderHeart, Trash2 } from 'lucide-react';

export default function MyStack() {
    const [viewMode, setViewMode] = useState('grid');
    const [searchQuery, setSearchQuery] = useState('');
    const [savedTools, setSavedTools] = useState([]);
    const [, setIsLoading] = useState(false);

    const API_BASE = "http://localhost:8000";

    useEffect(() => {
        const fetchStack = async () => {
            setIsLoading(true);
            try {
                const stackNames = JSON.parse(localStorage.getItem('aether_saved_stack') || '[]');
                if (stackNames.length === 0) {
                    setSavedTools([]);
                    return;
                }

                // Fetch full details for each saved tool
                const fetchPromises = stackNames.map(name =>
                    fetch(`${API_BASE}/tool/${encodeURIComponent(name)}`).then(res => {
                        if (!res.ok) throw new Error("Not found");
                        return res.json();
                    }).catch(() => null) // Ignore deleted/missing tools gracefully
                );

                const results = await Promise.all(fetchPromises);
                const validTools = results.filter(Boolean).map((data, idx) => ({
                    id: String(idx),
                    name: data.name,
                    category: data.analysis?.job_to_be_done?.[0] || 'כללי',
                    trustScore: data.trust_score,
                    dateSaved: new Date().toLocaleDateString('he-IL'), // Mocking date since localStorage is just an array of names currently
                    isActive: false // Future feature for active stack logic
                }));

                setSavedTools(validTools);

            } catch (error) {
                console.error("Failed to fetch stack", error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchStack();
    }, []);

    const filteredTools = savedTools.filter(tool =>
        tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tool.category.includes(searchQuery)
    );

    return (
        <div className="flex flex-col w-full min-h-[85vh] animate-in fade-in duration-700 rtl" dir="rtl">

            {/* Header / Dashboard Area */}
            <div className="w-full mb-10 pb-8 border-b border-white/10 flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2 truncate flex items-center gap-3">
                        <FolderHeart className="w-8 h-8 text-cyan-500" />
                        המחסנית שלי (My Stack)
                    </h1>
                    <p className="text-white/60 text-sm">ניהול הכלים השמורים והמערכות הפעילות שלך.</p>
                </div>

                <div className="flex items-center gap-4 bg-white/5 backdrop-blur-md p-1 rounded-xl border border-white/20 shadow-sm w-fit">
                    <button
                        onClick={() => setViewMode('grid')}
                        className={`p-2 rounded-lg transition-colors ${viewMode === 'grid' ? 'bg-white/10 backdrop-blur-md text-white' : 'text-white/50 hover:text-white'}`}
                    >
                        <LayoutGrid className="w-4 h-4" />
                    </button>
                    <div className="w-px h-6 bg-white/20 backdrop-blur-md"></div>
                    <button
                        onClick={() => setViewMode('list')}
                        className={`p-2 rounded-lg transition-colors ${viewMode === 'list' ? 'bg-white/10 backdrop-blur-md text-white' : 'text-white/50 hover:text-white'}`}
                    >
                        <List className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Controls Row */}
            <div className="w-full flex justify-between items-center mb-6">
                <div className="relative w-full max-w-sm">
                    <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/50" />
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="חיפוש במחסנית שלך..."
                        className="w-full bg-white/5 backdrop-blur-md border border-white/20 rounded-xl pr-10 pl-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-neutral-900/10 focus:border-white/20 transition-all shadow-sm"
                    />
                </div>

                <span className="text-sm font-medium text-white/60 bg-white/5 backdrop-blur-md border border-white/20 px-3 py-1.5 rounded-lg shadow-sm">
                    סה"כ כלים: {filteredTools.length}
                </span>
            </div>

            {/* Empty State */}
            {filteredTools.length === 0 && (
                <div className="flex flex-col items-center justify-center p-12 bg-white/5 backdrop-blur-md border border-white/20 border-dashed rounded-3xl mt-4">
                    <Bookmark className="w-12 h-12 text-neutral-300 mb-4" />
                    <h3 className="text-lg font-medium text-white mb-1">לא נמצאו כלים במחסנית</h3>
                    <p className="text-sm text-white/60 text-center max-w-sm">
                        חיפשת משהו ולא מצאת, או שעדיין לא הוספת כלים למחסנית שלך כדי לבנות את הסטאק המושלם.
                    </p>
                </div>
            )}

            {/* Grid View */}
            {filteredTools.length > 0 && viewMode === 'grid' && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12 animate-in slide-in-from-bottom-4 duration-500">
                    {filteredTools.map(tool => (
                        <div key={tool.id} className="group flex flex-col p-5 bg-white/5 backdrop-blur-md border border-white/20 rounded-2xl shadow-sm hover:border-white/20 transition-all hover:shadow-md cursor-pointer relative overflow-hidden">

                            {/* Top row */}
                            <div className="flex justify-between items-start mb-6">
                                <span className="px-2.5 py-1 bg-white/10 backdrop-blur-md text-white/70 text-xs font-semibold rounded-md tracking-wider">
                                    {tool.category}
                                </span>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation(); // prevent card click if we add one later
                                        const savedStack = JSON.parse(localStorage.getItem('aether_saved_stack') || '[]');
                                        const updatedStack = savedStack.filter(name => name !== tool.name);
                                        localStorage.setItem('aether_saved_stack', JSON.stringify(updatedStack));
                                        setSavedTools(currentTools => currentTools.filter(t => t.name !== tool.name));
                                    }}
                                    className="text-white/50 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
                                    title="הסר מהמחסנית"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>

                            {/* Content */}
                            <h3 className="text-xl font-bold text-white mb-1 flex justify-between items-center pr-1">
                                {tool.name}
                                <ArrowUpRight className="w-5 h-5 text-neutral-300 group-hover:text-white transition-colors" />
                            </h3>
                            <div className="flex items-center gap-2 mt-auto pt-6 border-t border-white/10 w-full justify-between">
                                <div className="flex items-center gap-1.5">
                                    <span className="text-xs text-white/50">Trust Score</span>
                                    <span className={`text-sm font-bold ${tool.trustScore >= 90 ? 'text-emerald-500' : 'text-amber-500'}`}>
                                        {tool.trustScore}
                                    </span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className={`w-2 h-2 rounded-full ${tool.isActive ? 'bg-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.8)]' : 'bg-neutral-300'}`}></span>
                                    <span className="text-xs text-white/60">{tool.isActive ? 'פעיל בצוות' : 'שמור לעתיד'}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* List View */}
            {filteredTools.length > 0 && viewMode === 'list' && (
                <div className="flex flex-col w-full bg-white/5 backdrop-blur-md border border-white/20 rounded-2xl overflow-hidden shadow-sm animate-in slide-in-from-bottom-4 duration-500">
                    <div className="flex w-full bg-white/5 backdrop-blur-md border-b border-white/20 px-6 py-3 text-xs font-semibold text-white/60 uppercase tracking-wider">
                        <div className="flex-1">שם הכלי</div>
                        <div className="w-32 hidden md:block text-right">קטגוריה</div>
                        <div className="w-32 text-center">אמינות</div>
                        <div className="w-32 text-center">סטטוס</div>
                        <div className="w-16"></div>
                    </div>
                    {filteredTools.map((tool, idx) => (
                        <div key={tool.id} className={`flex w-full px-6 py-4 items-center group cursor-pointer hover:bg-white/5 backdrop-blur-md transition-colors ${idx !== filteredTools.length - 1 ? 'border-b border-white/10' : ''}`}>
                            <div className="flex-1 font-bold text-white">{tool.name}</div>
                            <div className="w-32 hidden md:block text-sm text-white/60 text-right">{tool.category}</div>
                            <div className="w-32 text-center text-sm font-bold text-emerald-500">{tool.trustScore}</div>
                            <div className="w-32 flex justify-center text-sm">
                                <span className={`px-2 py-1 rounded-md text-xs font-medium border ${tool.isActive ? 'bg-cyan-50 text-cyan-600 border-cyan-100' : 'bg-white/10 backdrop-blur-md text-white/60 border-white/20'}`}>
                                    {tool.isActive ? 'פעיל' : 'שמור'}
                                </span>
                            </div>
                            <div className="w-16 flex justify-end">
                                <button className="text-white/50 hover:text-white transition-colors">
                                    <ArrowUpRight className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

        </div>
    );
}
