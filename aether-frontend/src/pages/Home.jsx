import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Activity, Box, GitBranch, Coins, Zap, ArrowRight } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { apiFetch } from '../api';
import PremiumSearchSkeleton from '../components/PremiumSearchSkeleton';

export default function Home({ setAppError }) {
    const { t, i18n } = useTranslation();
    const [query, setQuery] = useState('');
    const [isSearching, setIsSearching] = useState(false);
    const [hasResults, setHasResults] = useState(false);
    const [results, setResults] = useState([]);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setIsSearching(true);
        setHasResults(false);
        setAppError(null);

        // Create an AbortController for a 60-second fetch timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000); // 60s timeout

        try {
            // Target the Semantic Search Engine
            const resp = await apiFetch(`/search/intent?q=${encodeURIComponent(query)}`, {
                signal: controller.signal
            });

            if (!resp.ok) {
                // Determine if it was a server error (500)
                const errorData = await resp.json().catch(() => null);
                throw new Error(errorData?.detail || "Semantic Search failed");
            }

            const data = await resp.json();

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
        // The main container uses dynamic direction from i18n state
        <div className="min-h-[85vh] flex flex-col items-center pt-20 px-4 w-full relative overflow-hidden">

            <main className={`w-full flex flex-col items-center transition-all duration-500 relative z-10 ${hasResults ? 'max-w-3xl' : 'max-w-2xl'}`}>

                {/* Hero Header */}
                {!hasResults && (
                    <div className="text-center mb-10 transition-opacity duration-500 animate-in fade-in">
                        <span className="text-cyan-400 font-bold mb-3 block text-xs tracking-widest uppercase">
                            {t('engine_tag')}
                        </span>
                        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-2">
                            {t('welcome')}
                        </h1>
                    </div>
                )}

                {/* Smart Search Bar */}
                <form onSubmit={handleSearch} className="w-full relative mb-8 z-10">
                    <div className={`relative flex flex-col w-full p-2 border bg-white/5 backdrop-blur-md rounded-3xl transition-all duration-300 focus-within:border-white/20/30 focus-within:shadow-xl ${hasResults ? 'border-white/20 shadow-md' : 'border-white/20 shadow-lg'}`}>
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder={t('search_placeholder')}
                            className="w-full bg-transparent text-white placeholder-neutral-400 px-5 pt-4 pb-14 outline-none text-lg resize-none font-medium"
                            disabled={isSearching}
                        />
                        <div className={`absolute bottom-3 ${i18n.dir() === 'rtl' ? 'left-3' : 'right-3'} flex items-center`}>
                            <button
                                type="submit"
                                disabled={isSearching || !query.trim()}
                                className="px-6 py-2.5 rounded-2xl bg-white/20 backdrop-blur-md border border-white/10 hover:bg-white/10 backdrop-blur-md disabled:bg-white/10 backdrop-blur-md disabled:border-white/20 disabled:text-white/50 text-white text-sm font-semibold transition-all shadow-md"
                            >
                                {isSearching ? t('analyzing') : hasResults ? t('search_again') : t('match_tool')}
                            </button>
                        </div>
                    </div>
                </form>

                {/* Searching State */}
                {isSearching && <PremiumSearchSkeleton />}

                {/* Idle State: Prompt Suggestions */}
                {!hasResults && !isSearching && (
                    <div className="w-full">
                        <div className="flex flex-wrap items-center justify-center gap-3 mb-10 w-full animate-in fade-in duration-500 delay-150">
                            {[
                                { key: 'image', text: t('prompts.image') },
                                { key: 'deck', text: t('prompts.deck') },
                                { key: 'debug', text: t('prompts.debug') },
                            ].map((prompt, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => setQuery(prompt.text)}
                                    className="px-5 py-2.5 rounded-full border border-white/20 bg-white/5 backdrop-blur-md text-white/70 hover:bg-white/5 backdrop-blur-md hover:text-white hover:border-white/30 text-sm font-semibold transition-all shadow-sm"
                                >
                                    {prompt.text}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Result State: The 3-Card Drop */}
                {hasResults && (
                    <div className="w-full flex flex-col gap-5 mt-4 mb-20 animate-in slide-in-from-top-4 fade-in duration-700">
                        <div className={`${i18n.dir() === 'rtl' ? 'text-right' : 'text-left'} mb-2`}>
                            <span className="text-white/60 text-sm font-bold uppercase tracking-widest">
                                {t('found_results', { count: results.length })}
                            </span>
                        </div>

                        {results.map((tool, idx) => {
                            const toolName = tool.tool_name || tool.title || 'Unknown Tool';
                            const toolId = tool.id || toolName.trim().toLowerCase().replace(/\s+/g, '-');
                            const reason = tool.match_reason || tool.summary || (tool.analysis && tool.analysis.executive_summary) || t('no_summary');
                            const primaryIntent = tool.primary_intent || t('general_solution');

                            const isSponsored = tool.is_sponsored || false;
                            const isTopMatch = isSponsored || idx === 0;

                            const metrics = tool.metrics || (tool.analysis && tool.analysis.metrics) || {};
                            const pricing = metrics.pricing || tool.pricing || (isSponsored ? 'Enterprise' : 'Freemium');
                            const learningCurve = metrics.learning_curve || tool.learningCurve || (tool.trust_score > 90 ? 'Easy' : 'Moderate');
                            const integration = metrics.integration || tool.integration || 'Web / API';

                            return (
                                <div key={toolId || idx} className={`flex flex-col p-8 rounded-3xl bg-white/5 backdrop-blur-md border transition-all duration-300 ${isTopMatch ? 'border-white/20 shadow-xl scale-[1.01]' : 'border-white/20 shadow-sm hover:shadow-md hover:border-white/30'}`}>

                                    {/* Card Header */}
                                    <div className="flex justify-between items-start mb-6">
                                        <div className="flex flex-col gap-1.5">
                                            <div className="flex items-center gap-3">
                                                <h3 className="text-2xl font-bold text-white">
                                                    {toolName}
                                                </h3>
                                                {isTopMatch && <span className="text-xs bg-white/20 backdrop-blur-md text-white px-2.5 py-1 rounded-md font-semibold tracking-wide">{t('top_match')}</span>}
                                                {isSponsored && <span className="text-xs bg-amber-100 text-amber-700 px-2.5 py-1 rounded-md font-semibold tracking-wide border border-amber-200">{t('promoted')}</span>}
                                            </div>
                                            <p className="font-semibold text-emerald-600 text-sm">{t('solving', { intent: primaryIntent })}</p>
                                            <p className="text-white/70 text-sm mt-3 leading-relaxed max-w-2xl">{reason}</p>
                                        </div>
                                    </div>

                                    {/* Decision Matrix */}
                                    <div className="grid grid-cols-3 gap-6 py-5 my-5 border-t border-b border-white/10 bg-white/5 backdrop-blur-md rounded-2xl px-6">
                                        <div className="flex flex-col gap-1">
                                            <span className="text-white/50 text-xs font-bold uppercase tracking-widest">{t('learning_curve')}</span>
                                            <span className="text-white text-sm font-semibold">{learningCurve}</span>
                                        </div>
                                        <div className={`flex flex-col gap-1 ${i18n.dir() === 'rtl' ? 'border-r pr-6' : 'border-l pl-6'} border-white/20`}>
                                            <span className="text-white/50 text-xs font-bold uppercase tracking-widest">{t('pricing')}</span>
                                            <span className="text-white text-sm font-semibold">{pricing}</span>
                                        </div>
                                        <div className={`flex flex-col gap-1 ${i18n.dir() === 'rtl' ? 'border-r pr-6' : 'border-l pl-6'} border-white/20`}>
                                            <span className="text-white/50 text-xs font-bold uppercase tracking-widest">{t('integration')}</span>
                                            <span className="text-white text-sm font-semibold">{integration}</span>
                                        </div>
                                    </div>

                                    {/* Action Buttons */}
                                    <div className="flex justify-between items-center mt-2">
                                        <button
                                            onClick={() => {
                                                let savedStack = JSON.parse(localStorage.getItem('aether_saved_stack') || '[]');
                                                const isCurrentlySaved = savedStack.includes(toolId);

                                                if (isCurrentlySaved) {
                                                    savedStack = savedStack.filter(name => name !== toolId);
                                                } else {
                                                    savedStack.push(toolId);
                                                }

                                                localStorage.setItem('aether_saved_stack', JSON.stringify(savedStack));
                                                setResults([...results]);
                                            }}
                                            className="px-4 py-2 text-sm font-bold transition-all flex items-center gap-2 hover:opacity-80"
                                        >
                                            {(() => {
                                                const savedStack = JSON.parse(localStorage.getItem('aether_saved_stack') || '[]');
                                                const isSaved = savedStack.includes(toolId);
                                                return isSaved ? (
                                                    <><ShieldCheck className="w-4 h-4 text-emerald-400" /> <span className="text-white">{t('in_my_stack')}</span></>
                                                ) : (
                                                    <><ShieldCheck className="w-4 h-4 text-white/50" /> <span className="text-white/50">{t('save_to_stack')}</span></>
                                                );
                                            })()}
                                        </button>

                                        <Link to={`/tool/${encodeURIComponent(toolId)}`} className="px-6 py-2.5 text-sm font-bold text-white border border-white/20 rounded-xl hover:bg-white/5 backdrop-blur-md hover:border-white/20 transition-all shadow-sm">
                                            {t('read_analysis')}
                                        </Link>
                                    </div>

                                </div>
                            );
                        })}
                    </div>
                )}


            </main>
        </div>
    );
}
