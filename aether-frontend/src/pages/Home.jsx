import React, { useState } from 'react';
import { ShieldCheck, Activity, Box, GitBranch, Coins, Zap, ArrowRight } from 'lucide-react';
import LiveMonitorWidget from '../components/LiveMonitorWidget';

export default function Home({ setAppError }) {
    const [query, setQuery] = useState('');
    const [isSearching, setIsSearching] = useState(false);
    const [hasResults, setHasResults] = useState(false);
    const [results, setResults] = useState([]);

    const API_BASE = "http://localhost:8000";

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
            const resp = await fetch(`${API_BASE}/search/intent?q=${encodeURIComponent(query)}`, {
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
                setAppError("לא מצאנו כלי שמתאים לכוונתך בדיוק. נסה לתאר זאת אחרת.");
            }
        } catch (error) {
            console.error(error);
            if (error.name === 'AbortError') {
                setAppError("חיפוש מורכב זה לוקח זמן רב מדי. אנא נסה למקד את החיפוש.");
            } else {
                setAppError(error.message || "המנוע תחת עומס. נסה שוב בעוד מספר רגעים.");
            }
        } finally {
            clearTimeout(timeoutId);
            setIsSearching(false);
        }
    };



    return (
        // המיכל הראשי מוגדר בגובה מינימלי כדי למנוע קפיצות, מיושר לאמצע. רקע שקוף למחצה סביב החיפוש.
        <div className="min-h-[85vh] flex flex-col items-center pt-20 px-4 w-full rtl relative overflow-hidden" dir="rtl">

            <main className={`w-full flex flex-col items-center transition-all duration-500 relative z-10 ${hasResults ? 'max-w-3xl' : 'max-w-2xl'}`}>

                {/* אזור הכותרות - נעלם באלגנטיות כשיש תוצאות כדי לפנות מקום */}
                {!hasResults && (
                    <div className="text-center mb-10 transition-opacity duration-500 animate-in fade-in">
                        <span className="text-cyan-400 font-bold mb-3 block text-xs tracking-widest uppercase">
                            ✦ מנוע התאמה אדריכלי
                        </span>
                        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-2">
                            איזו עבודה תרצה שה-AI יבצע?
                        </h1>
                    </div>
                )}

                {/* שורת החיפוש החכמה - המנוע שלנו */}
                <form onSubmit={handleSearch} className="w-full relative mb-8 z-10">
                    <div className={`relative flex flex-col w-full p-2 border bg-white/5 backdrop-blur-md rounded-3xl transition-all duration-300 focus-within:border-white/20/30 focus-within:shadow-xl ${hasResults ? 'border-white/20 shadow-md' : 'border-white/20 shadow-lg'}`}>
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="לדוגמה: בניית אפליקציית React ו-Tailwind מאפס..."
                            className="w-full bg-transparent text-white placeholder-neutral-400 px-5 pt-4 pb-14 outline-none text-lg resize-none font-medium"
                            disabled={isSearching}
                        />
                        <div className="absolute bottom-3 left-3 flex items-center">
                            <button
                                type="submit"
                                disabled={isSearching || !query.trim()}
                                className="px-6 py-2.5 rounded-2xl bg-white/20 backdrop-blur-md border border-white/10 hover:bg-white/10 backdrop-blur-md disabled:bg-white/10 backdrop-blur-md disabled:border-white/20 disabled:text-white/50 text-white text-sm font-semibold transition-all shadow-md"
                            >
                                {isSearching ? 'Analyzing Intent...' : hasResults ? 'חפש שוב' : 'התאם לי כלי'}
                            </button>
                        </div>
                    </div>
                </form>

                {/* מצב 1: הצעות לפרומפטים (Idle State) */}
                {!hasResults && !isSearching && (
                    <div className="w-full">
                        <div className="w-full mb-8">
                           <LiveMonitorWidget />
                        </div>
                        
                        <div className="flex flex-wrap items-center justify-center gap-3 mb-10 w-full animate-in fade-in duration-500 delay-150">
                            {[
                                "יצירת תמונות מציאותיות וריאליסטיות",
                                "בניית מצגת משקיעים מתוך טקסט",
                                "דיבוג שגיאות עמוקות בשרת (Backend)",
                            ].map((prompt, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => setQuery(prompt)}
                                    className="px-5 py-2.5 rounded-full border border-white/20 bg-white/5 backdrop-blur-md text-white/70 hover:bg-white/5 backdrop-blur-md hover:text-white hover:border-white/30 text-sm font-semibold transition-all shadow-sm"
                                >
                                    {prompt}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* מצב 2: The 3-Card Drop (Result State) */}
                {hasResults && (
                    <div className="w-full flex flex-col gap-5 mt-4 mb-20 animate-in slide-in-from-top-4 fade-in duration-700">
                        <div className="text-right mb-2">
                            <span className="text-white/60 text-sm font-bold uppercase tracking-widest">נמצאו 3 הכלים המדויקים ביותר לאינטנט שלך</span>
                        </div>

                        {results.map((tool, idx) => {
                            const toolName = tool.tool_name || tool.title || 'Unknown Tool';
                            const toolId = tool.id || toolName.trim().toLowerCase().replace(/\s+/g, '-');
                            const reason = tool.match_reason || tool.summary || (tool.analysis && tool.analysis.executive_summary) || 'אין תקציר זמין כרגע';
                            const primaryIntent = tool.primary_intent || 'פתרון כללי למשימה';

                            // Safe unwrapping for new metrics
                            const isSponsored = tool.is_sponsored || false;
                            const isTopMatch = isSponsored || idx === 0;

                            const metrics = tool.metrics || (tool.analysis && tool.analysis.metrics) || {};
                            const pricing = metrics.pricing || tool.pricing || (isSponsored ? 'Enterprise' : 'Freemium');
                            const learningCurve = metrics.learning_curve || tool.learningCurve || (tool.trust_score > 90 ? 'קל מאוד' : 'בינוני');
                            const integration = metrics.integration || tool.integration || 'Web / API';

                            return (
                                <div key={toolId || idx} className={`flex flex-col p-8 rounded-3xl bg-white/5 backdrop-blur-md border transition-all duration-300 ${isTopMatch ? 'border-white/20 shadow-xl scale-[1.01]' : 'border-white/20 shadow-sm hover:shadow-md hover:border-white/30'}`}>

                                    {/* כותרת הקלף והסבר ההתאמה */}
                                    <div className="flex justify-between items-start mb-6">
                                        <div className="flex flex-col gap-1.5">
                                            <div className="flex items-center gap-3">
                                                <h3 className="text-2xl font-bold text-white">
                                                    {toolName}
                                                </h3>
                                                {isTopMatch && <span className="text-xs bg-white/20 backdrop-blur-md text-white px-2.5 py-1 rounded-md font-semibold tracking-wide">TOP MATCH</span>}
                                                {isSponsored && <span className="text-xs bg-amber-100 text-amber-700 px-2.5 py-1 rounded-md font-semibold tracking-wide border border-amber-200">Promoted</span>}
                                            </div>
                                            <p className="font-semibold text-emerald-600 text-sm">פותר את: {primaryIntent}</p>
                                            <p className="text-white/70 text-sm mt-3 leading-relaxed max-w-2xl">{reason}</p>
                                        </div>
                                    </div>

                                    {/* מטריצת ההחלטה (The Decision Matrix) */}
                                    <div className="grid grid-cols-3 gap-6 py-5 my-5 border-t border-b border-white/10 bg-white/5 backdrop-blur-md rounded-2xl px-6">
                                        <div className="flex flex-col gap-1">
                                            <span className="text-white/50 text-xs font-bold uppercase tracking-widest">עקומת למידה</span>
                                            <span className="text-white text-sm font-semibold">{learningCurve}</span>
                                        </div>
                                        <div className="flex flex-col gap-1 border-r border-white/20 pr-6">
                                            <span className="text-white/50 text-xs font-bold uppercase tracking-widest">תמחור מודל</span>
                                            <span className="text-white text-sm font-semibold">{pricing}</span>
                                        </div>
                                        <div className="flex flex-col gap-1 border-r border-white/20 pr-6">
                                            <span className="text-white/50 text-xs font-bold uppercase tracking-widest">אינטגרציה</span>
                                            <span className="text-white text-sm font-semibold">{integration}</span>
                                        </div>
                                    </div>

                                    {/* הנעה לפעולה לקלף */}
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
                                                // Trigger a fast local re-render by mutating state carefully or relying on component remount.
                                                // For MVP, we will just force update the array reference to trigger a render.
                                                setResults([...results]);
                                            }}
                                            className="px-4 py-2 text-sm font-bold transition-all flex items-center gap-2 hover:opacity-80"
                                        >
                                            {(() => {
                                                const savedStack = JSON.parse(localStorage.getItem('aether_saved_stack') || '[]');
                                                const isSaved = savedStack.includes(toolId);
                                                return isSaved ? (
                                                    <><ShieldCheck className="w-4 h-4 text-emerald-400" /> <span className="text-white">במחסנית שלי</span></>
                                                ) : (
                                                    <><ShieldCheck className="w-4 h-4 text-white/50" /> <span className="text-white/50">שמור למחסנית</span></>
                                                );
                                            })()}
                                        </button>

                                        <a href={`/tool/${encodeURIComponent(toolId)}`} className="px-6 py-2.5 text-sm font-bold text-white border border-white/20 rounded-xl hover:bg-white/5 backdrop-blur-md hover:border-white/20 transition-all shadow-sm">
                                            קרא ניתוח ותרחישים מלאים
                                        </a>
                                    </div>

                                </div>
                            );
                        })}
                    </div>
                )}

                {/* Commander Section (Pro Highlights) */}
                {!hasResults && !isSearching && (
                    <div className="w-full mt-24 mb-24 animate-in fade-in duration-1000 delay-300">
                        <div className="text-center mb-16">
                            <span className="text-emerald-400 font-bold uppercase tracking-[0.3em] text-[10px] mb-4 block">
                                Beyond Search: Enterprise Grade
                            </span>
                            <h2 className="text-3xl md:text-4xl font-black text-white">
                                הכלים של ה-<span className="text-emerald-500">Commanders</span>
                            </h2>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            {[
                                { title: 'Playground', icon: <Box className="w-5 h-5" />, desc: 'השקיעו בשני מודלים במקביל וראו מי מהם באמת מתאים לכם לפני החיווי.', path: '/playground', color: 'border-emerald-500/20 text-emerald-400 bg-emerald-500/5' },
                                { title: 'The Pulse', icon: <Activity className="w-5 h-5" />, desc: 'דאטה חי על Latency וביצועי API של הספקים המובילים בעולם.', path: '/pulse', color: 'border-rose-500/20 text-rose-400 bg-rose-500/5' },
                                { title: 'AI Architect', icon: <GitBranch className="w-5 h-5" />, desc: 'בניית שרשראות עבודה (Workflows) מורכבות על בסיס נתוני המעבדה.', path: '/architect', color: 'border-indigo-500/20 text-indigo-400 bg-indigo-500/5' },
                                { title: 'Optimizer', icon: <Coins className="w-5 h-5" />, desc: 'חסוך מאות שקלים בחודש בזיהוי כפילויות במחסנית הכלים שלך.', path: '/optimizer', color: 'border-yellow-500/20 text-yellow-400 bg-yellow-500/5' }
                            ].map((feature, idx) => (
                                <a 
                                    href={feature.path} 
                                    key={idx} 
                                    className={`group p-8 rounded-3xl border ${feature.color} backdrop-blur-md transition-all hover:-translate-y-2 hover:shadow-2xl relative overflow-hidden`}
                                >
                                    <div className="absolute -top-10 -right-10 w-32 h-32 bg-white/5 rounded-full blur-3xl pointer-events-none group-hover:bg-white/10 transition-all"></div>
                                    <div className="mb-6 flex justify-between items-center">
                                        {feature.icon}
                                        <Zap className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                                    </div>
                                    <h3 className="text-lg font-black text-white mb-2">{feature.title}</h3>
                                    <p className="text-white/40 text-xs font-medium leading-relaxed">{feature.desc}</p>
                                </a>
                            ))}
                        </div>
                        
                        <div className="mt-12 text-center">
                            <a href="/pricing" className="inline-flex items-center gap-2 text-white/40 hover:text-emerald-400 text-xs font-black uppercase tracking-widest transition-all">
                                גלה את כל הפיצ'רים של Aether Pro <ArrowRight className="w-3 h-3" />
                            </a>
                        </div>
                    </div>
                )}

            </main>
        </div>
    );
}
