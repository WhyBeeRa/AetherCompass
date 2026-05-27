import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ShieldCheck, ArrowRight, Loader2, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { apiFetch } from '../api';
import PremiumSearchSkeleton from '../components/PremiumSearchSkeleton';

export default function Home({ setAppError }) {
    const { t } = useTranslation();
    const [query, setQuery] = useState('');
    const [isSearching, setIsSearching] = useState(false);
    const [hasResults, setHasResults] = useState(false);
    const [results, setResults] = useState([]);
    const prompts = Array.isArray(t('prompts', { returnObjects: true })) ? t('prompts', { returnObjects: true }) : [];

    const handleSearch = async (e, forcedQuery) => {
        if (e) e.preventDefault();
        const searchQuery = forcedQuery || query;
        if (!searchQuery.trim()) return;

        if (forcedQuery) setQuery(forcedQuery);

        setIsSearching(true);
        setHasResults(false);
        setAppError(null);

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 45000);

        try {
            const resp = await apiFetch(`/search/intent?q=${encodeURIComponent(searchQuery)}`, {
                signal: controller.signal
            });

            if (!resp.ok) {
                const errorData = await resp.json().catch(() => null);
                throw new Error(errorData?.detail || "Semantic Search failed");
            }

            const data = await resp.json();

            // The "Magic Moment" - 1.5s Labor Illusion
            await new Promise(resolve => setTimeout(resolve, 1500));

            if (data && data.length > 0) {
                setResults(data.slice(0, 3));
                setHasResults(true);
            } else {
                setAppError(t('no_results_found'));
            }
        } catch (error) {
            console.error(error);
            if (error.name === 'AbortError') {
                setAppError(t('abort_error'));
            } else {
                setAppError(error.message || t('generic_error'));
            }
        } finally {
            clearTimeout(timeoutId);
            setIsSearching(false);
        }
    };

    return (
        <div className="min-h-[85vh] flex flex-col items-center pt-24 px-4 w-full relative overflow-hidden font-sans selection:bg-cyan-500/30">
            
            {/* Definitive Entrance: English Hero Section */}
            {!hasResults && !isSearching && (
                <main className="w-full max-w-4xl flex flex-col items-center animate-in fade-in duration-1000 slide-in-from-top-4">
                    
                    {/* Teal Label */}
                    <div className="inline-flex items-center gap-2 mb-8 px-4 py-1.5 rounded-full bg-cyan-500/5 border border-cyan-500/20">
                        <span className="text-[10px] md:text-xs font-bold text-cyan-400 tracking-[0.2em] uppercase">
                            ARCHITECTURAL MATCHING ENGINE ✦
                        </span>
                    </div>

                    {/* Bold Global Headline */}
                    <h1 className="text-5xl md:text-8xl font-black text-white text-center leading-[1] tracking-[-0.04em] mb-12 max-w-4xl drop-shadow-2xl">
                        What job would you like <br className="hidden md:block" /> AI to perform?
                    </h1>


                    {/* Search Architecture */}
                    <div className="w-full max-w-3xl mb-12 relative group">
                        <form 
                            onSubmit={(e) => handleSearch(e)}
                            className="relative flex flex-col md:flex-row items-stretch md:items-center p-3 md:p-2 bg-[#121418]/40 backdrop-blur-2xl border border-white/10 rounded-3xl md:rounded-[2.5rem] gap-2 md:gap-0 transition-all duration-700 focus-within:border-cyan-500/30 focus-within:bg-[#121418]/60 shadow-[0_0_50px_rgba(0,0,0,0.5)] group-hover:border-white/20"
                        >
                            <input
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="...Example: Build a React and Tailwind app from scratch"
                                className="w-full bg-transparent text-white placeholder-white/20 px-4 py-4 md:px-8 md:py-5 outline-none text-base md:text-xl font-medium"
                                disabled={isSearching}
                            />
                            <button
                                type="submit"
                                disabled={isSearching || !query.trim()}
                                className="shrink-0 px-6 py-4 md:px-10 md:py-5 rounded-2xl md:rounded-[2rem] bg-indigo-600 hover:bg-indigo-500 text-white text-xs md:text-sm font-black uppercase tracking-widest transition-all active:scale-95 shadow-[0_0_20px_rgba(79,70,229,0.4)] hover:shadow-[0_0_30px_rgba(79,70,229,0.6)]"
                            >
                                Match tool
                            </button>
                        </form>
                    </div>


                    {/* Suggestion Pills */}
                    <div className="flex flex-wrap justify-center gap-4 max-w-3xl animate-in fade-in transition-all duration-700 delay-300">
                        {prompts.map((p) => (
                            <button
                                key={p.id}
                                onClick={() => handleSearch(null, p.intent)}
                                className="group/pill px-6 py-2.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/20 text-white/50 hover:text-white text-sm font-medium transition-all flex items-center gap-2 active:scale-95"
                            >
                                <Sparkles className="w-3.5 h-3.5 text-cyan-400 opacity-0 group-hover/pill:opacity-100 transition-opacity" />
                                {p.label}
                            </button>
                        ))}
                    </div>
                </main>
            )}

            {/* Results / Searching State View */}
            {(isSearching || hasResults) && (
                <div className="w-full max-w-3xl animate-in fade-in duration-700">
                    <div className="flex items-center justify-between mb-8 border-b border-white/10 pb-6">
                        <h2 className="text-xl font-bold text-white tracking-tight">
                            {isSearching ? "Architecting your matches..." : "Architectural Match Found"}
                        </h2>
                        <button 
                            onClick={() => { setHasResults(false); setQuery(''); }}
                            className="text-xs text-white/50 hover:text-white transition-colors"
                        >
                            New Search
                        </button>
                    </div>

                    {isSearching ? (
                        <PremiumSearchSkeleton />
                    ) : (
                        <div className="space-y-6">
                            {results.map((tool, idx) => {
                                const toolId = tool.id || tool.tool_name?.toLowerCase().replace(/\s+/g, '-');
                                return (
                                    <div key={toolId || idx} className="p-6 md:p-8 rounded-2xl md:rounded-[2rem] bg-white/5 backdrop-blur-md border border-white/10 hover:border-white/20 transition-all duration-300 group">
                                        <div className="flex justify-between items-start mb-6 gap-4">
                                            <div className="min-w-0 flex-1">
                                                <div className="flex flex-wrap items-center gap-2 md:gap-3 mb-2">
                                                    <h3 className="text-xl md:text-2xl font-bold text-white group-hover:text-cyan-400 transition-colors truncate">
                                                        {tool.tool_name || tool.title}
                                                    </h3>
                                                    {idx === 0 && <span className="px-3 py-1 bg-cyan-500/20 text-cyan-400 text-[10px] font-bold rounded-md tracking-widest uppercase shrink-0">Top Match</span>}
                                                </div>
                                                <p className="text-white/60 text-sm md:text-base leading-relaxed max-w-xl">
                                                    {tool.match_reason || tool.summary}
                                                </p>
                                            </div>
                                            <Link 
                                                to={`/tool/${encodeURIComponent(toolId)}`}
                                                className="p-3 rounded-xl bg-white/5 border border-white/10 text-white hover:bg-white/10 transition-all shrink-0"
                                            >
                                                <ArrowRight className="w-5 h-5" />
                                            </Link>
                                        </div>
                                        
                                        <div className="flex items-center gap-6 text-xs font-bold uppercase tracking-widest text-white/40">
                                            <div className="flex flex-col gap-1">
                                                <span>Pricing</span>
                                                <span className="text-white/80">{tool.metrics?.pricing || tool.pricing || 'Freemium'}</span>
                                            </div>
                                            <div className="h-8 w-px bg-white/10" />
                                            <div className="flex flex-col gap-1">
                                                <span>Trust Score</span>
                                                <span className="text-emerald-400">{tool.trust_score}%</span>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
