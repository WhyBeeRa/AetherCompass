import React, { useState } from 'react';
import { Send, Box, Sparkles, Zap, ChevronRight, Terminal, Layers } from 'lucide-react';

export default function Playground() {
    const [prompt, setPrompt] = useState('');
    const [isRunning, setIsRunning] = useState(false);
    const [results, setResults] = useState([]);

    const runSimulation = () => {
        if (!prompt) return;
        setIsRunning(true);
        setResults([]);

        // Mocking the simulation of 3 tools
        const mockTools = [
            { id: 1, name: 'GPT-4o', latency: '1.2s', status: 'Optimal', output: 'The results for your prompt indicate a high level of efficiency in the specified domain.' },
            { id: 2, name: 'Claude 3.5 Sonnet', latency: '0.9s', status: 'Fast', output: 'Based on the context provided, the most effective approach would be to implement a structured workflow.' },
            { id: 3, name: 'Gemini 1.5 Pro', latency: '2.1s', status: 'Deep Scan', output: 'Analysis of the requested parameters shows a 98% correlation with existing high-performance architectures.' }
        ];

        setTimeout(() => {
            setResults(mockTools);
            setIsRunning(false);
        }, 2000);
    };

    return (
        <div className="w-full min-h-screen pt-24 pb-24 rtl animate-in fade-in duration-700 bg-black text-white" dir="rtl">
            <main className="max-w-7xl mx-auto px-6">
                
                {/* Header Section */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12 border-b border-white/10 pb-12">
                    <div>
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 bg-emerald-500 rounded-lg">
                                <Box className="w-6 h-6 text-black" />
                            </div>
                            <span className="text-emerald-400 font-black uppercase tracking-tighter text-sm">
                                Commander Environment
                            </span>
                        </div>
                        <h1 className="text-4xl md:text-5xl font-black tracking-tight mb-2">
                            Aether <span className="text-emerald-500">Playground</span>
                        </h1>
                        <p className="text-white/50 font-medium">
                            אל תקנה חתול בשק – תראה את התוצאות של כולם על המסך שלך בבת אחת.
                        </p>
                    </div>
                    <div className="flex bg-white/5 backdrop-blur-md p-2 rounded-2xl border border-white/10">
                        <div className="px-4 py-2 bg-emerald-500 text-black rounded-xl font-bold text-sm shadow-lg shadow-emerald-500/20">
                            Multi-Model Sandbox
                        </div>
                        <div className="px-4 py-2 text-white/40 font-bold text-sm">
                            Stress Test Mode
                        </div>
                    </div>
                </div>

                {/* Input Area */}
                <div className="relative mb-16">
                    <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-[2.5rem] blur opacity-20"></div>
                    <div className="relative bg-white/[0.03] backdrop-blur-3xl border border-white/20 rounded-[2.5rem] p-8 md:p-12 shadow-2xl">
                        <div className="flex flex-col gap-6">
                            <div className="flex items-center gap-3 text-white/40">
                                <Terminal className="w-5 h-5" />
                                <span className="text-xs font-black uppercase tracking-widest">Global Prompt Entry</span>
                            </div>
                            <textarea 
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                placeholder="הזן כאן את הפרומפט שלך להשוואה בין המודלים..."
                                className="w-full bg-transparent border-none focus:ring-0 text-2xl md:text-3xl font-bold placeholder:text-white/10 min-h-[150px] resize-none leading-tight"
                            />
                            <div className="flex flex-col md:flex-row justify-between items-center gap-4 pt-6 border-t border-white/5">
                                <div className="flex gap-4">
                                    <div className="flex items-center gap-2 text-white/30 text-xs font-bold bg-white/5 px-4 py-2 rounded-full border border-white/10">
                                        <Layers className="w-4 h-4" /> 3 מודלים במקביל
                                    </div>
                                    <div className="flex items-center gap-2 text-white/30 text-xs font-bold bg-white/5 px-4 py-2 rounded-full border border-white/10">
                                        <Sparkles className="w-4 h-4" /> Pro Credits Active
                                    </div>
                                </div>
                                <button 
                                    onClick={runSimulation}
                                    disabled={isRunning || !prompt}
                                    className={`flex items-center gap-3 px-10 py-5 rounded-2xl font-black text-lg transition-all ${isRunning || !prompt ? 'bg-white/5 text-white/20' : 'bg-emerald-500 text-black hover:bg-emerald-400 shadow-[0_10px_40px_rgba(16,185,129,0.3)] hover:-translate-y-1'}`}
                                >
                                    {isRunning ? 'מריץ סימולציה...' : 'שגר השוואה'} 
                                    <Send className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Results Grid */}
                {results.length > 0 && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 animate-in slide-in-from-bottom-10 fade-in duration-1000">
                        {results.map((tool) => (
                            <div key={tool.id} className="group flex flex-col h-full bg-white/[0.02] border border-white/10 rounded-[2rem] overflow-hidden hover:border-emerald-500/50 transition-all hover:bg-white/[0.04]">
                                <div className="p-6 border-b border-white/5 bg-white/[0.02]">
                                    <div className="flex justify-between items-center mb-4">
                                        <h3 className="text-xl font-black text-white">{tool.name}</h3>
                                        <span className={`px-2 py-1 rounded text-[10px] font-black uppercase tracking-tighter ${tool.status === 'Optimal' ? 'bg-emerald-500/20 text-emerald-400' : tool.status === 'Fast' ? 'bg-blue-500/20 text-blue-400' : 'bg-purple-500/20 text-purple-400'}`}>
                                            {tool.status}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-4 text-xs font-bold text-white/30">
                                        <div className="flex items-center gap-1">
                                            <Zap className="w-3 h-3 text-emerald-500" /> {tool.latency}
                                        </div>
                                        <div>Tokens: 248</div>
                                        <div>Precision: 99%</div>
                                    </div>
                                </div>
                                <div className="p-8 flex-1">
                                    <p className="text-white/70 italic text-lg leading-relaxed">
                                        "{tool.output}"
                                    </p>
                                </div>
                                <div className="p-6 mt-auto">
                                    <button className="w-full py-4 rounded-xl border border-white/10 text-white/50 font-bold text-xs hover:text-white hover:border-white/20 transition-all flex items-center justify-center gap-2">
                                        ראה דוח מלא בכספת <ChevronRight className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Empty State / Loading */}
                {!results.length && !isRunning && (
                    <div className="text-center py-20 border-2 border-dashed border-white/5 rounded-[3rem]">
                        <Box className="w-16 h-16 text-white/10 mx-auto mb-6" />
                        <h2 className="text-2xl font-black text-white/30">ממתין לפקודה שלך</h2>
                        <p className="text-white/20 font-medium">הכנס פרומפט למעלה כדי להתחיל בסימולציה</p>
                    </div>
                )}
                
                {isRunning && (
                    <div className="text-center py-20">
                        <div className="relative w-24 h-24 mx-auto mb-8">
                            <div className="absolute inset-0 border-t-4 border-emerald-500 rounded-full animate-spin"></div>
                            <Box className="absolute inset-0 m-auto w-10 h-10 text-emerald-500 animate-pulse" />
                        </div>
                        <h2 className="text-2xl font-black text-white animate-pulse">מחבר מנועי AI...</h2>
                        <p className="text-white/40 font-medium mt-2">מסנכרן API ודוגם ביצועים בזמן אמת</p>
                    </div>
                )}

            </main>
        </div>
    );
}
