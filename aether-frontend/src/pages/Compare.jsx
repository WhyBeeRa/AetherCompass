import React, { useState, useEffect } from 'react';
import { Search, X, Plus, Zap, DollarSign, Share2, ShieldCheck, Scale, Image as ImageIcon, Code, AlignLeft, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Compare = ({ setAppError }) => {
    const [selectedTools, setSelectedTools] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [isSearching, setIsSearching] = useState(false);
    const [viewMode, setViewMode] = useState('specs'); // 'specs' or 'outputs'

    // Fetch tools for search
    useEffect(() => {
        const searchTools = async () => {
            if (!searchQuery.trim()) {
                setSearchResults([]);
                return;
            }
            try {
                setIsSearching(true);
                const res = await fetch(`http://127.0.0.1:8000/vault/search?q=${encodeURIComponent(searchQuery)}`);
                if (!res.ok) throw new Error("Search failed");
                const data = await res.json();
                setSearchResults(data);
            } catch (err) {
                console.error("Search error:", err);
            } finally {
                setIsSearching(false);
            }
        };

        const timer = setTimeout(searchTools, 300);
        return () => clearTimeout(timer);
    }, [searchQuery]);

    const addTool = (tool) => {
        if (selectedTools.length >= 3) {
            if (setAppError) setAppError("ניתן להשוות עד 3 כלים בו-זמנית.");
            return;
        }
        if (selectedTools.find(t => t.tool_name === tool.tool_name)) {
            return;
        }
        setSelectedTools([...selectedTools, tool]);
        setSearchQuery('');
        setSearchResults([]);
    };

    const removeTool = (toolName) => {
        setSelectedTools(selectedTools.filter(t => t.tool_name !== toolName));
    };

    const renderSpecRow = (label, icon, key, formatter = (v) => v || 'N/A') => {
        return (
            <div className="grid grid-cols-[1fr_repeat(3,1fr)] gap-4 py-4 border-b border-white/5 items-center">
                <div className="flex items-center gap-2 text-white/50 text-sm font-medium">
                    {icon}
                    <span>{label}</span>
                </div>
                {selectedTools.map((tool, idx) => (
                    <div key={idx} className="text-center text-white font-medium">
                        {formatter(tool.analysis?.metrics?.[key] || tool.analysis?.[key])}
                    </div>
                ))}
                {/* Fill empty slots */}
                {[...Array(3 - selectedTools.length)].map((_, idx) => (
                    <div key={idx + selectedTools.length} className="text-center text-white/10 italic text-xs">ממתין לבחירה...</div>
                ))}
            </div>
        );
    };

    return (
        <div className="w-full max-w-6xl mx-auto px-4 py-12 animate-in fade-in slide-in-from-bottom-4 duration-700" dir="rtl">
            {/* Header */}
            <div className="text-center mb-16">
                <motion.div 
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="inline-flex items-center justify-center p-3 bg-indigo-500/10 rounded-2xl border border-indigo-500/20 mb-6 group hover:border-indigo-500/40 transition-all duration-500"
                >
                    <Scale className="w-8 h-8 text-indigo-400 group-hover:rotate-12 transition-transform" />
                </motion.div>
                <h1 className="text-4xl md:text-6xl font-black text-white mb-6 tracking-tighter">
                    מטריצת ההשוואה <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">Comparison Matrix</span>
                </h1>
                <p className="text-white/50 text-lg max-w-2xl mx-auto leading-relaxed">
                    קבלו החלטות מבוססות דאטה. השוו בין היכולות הטכניות, העלויות והביצועים של כלי ה-AI המובילים בשוק ראש בראש.
                </p>
            </div>

            {/* Selection Area */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                {selectedTools.map((tool, idx) => (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        key={idx}
                        className="relative bg-white/5 border border-white/10 rounded-3xl p-6 backdrop-blur-xl group hover:border-indigo-500/30 transition-all duration-300"
                    >
                        <button 
                            onClick={() => removeTool(tool.tool_name)}
                            className="absolute top-4 left-4 p-2 bg-white/5 hover:bg-red-500/10 text-white/40 hover:text-red-400 rounded-full transition-all"
                        >
                            <X className="w-4 h-4" />
                        </button>
                        <div className="flex items-center gap-4 mb-4">
                            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 flex items-center justify-center border border-white/10 text-xl font-bold text-white">
                                {tool.tool_name.charAt(0)}
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-white">{tool.tool_name}</h3>
                                <p className="text-xs text-white/40 uppercase tracking-widest">{tool.analysis?.metrics?.pricing || 'Freemium'}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2 mt-4">
                            <div className="px-3 py-1 bg-cyan-400/10 text-cyan-400 border border-cyan-400/20 rounded-lg text-xs font-bold">
                                {tool.trust_score.toFixed(1)} Trust Score
                            </div>
                        </div>
                    </motion.div>
                ))}

                {selectedTools.length < 3 && (
                    <div className="relative group">
                        <div className="h-full min-h-[160px] bg-white/[0.02] border-2 border-dashed border-white/10 rounded-3xl flex flex-col items-center justify-center p-6 hover:bg-white/[0.04] hover:border-indigo-500/20 transition-all group-hover:cursor-text">
                            <div className="relative w-full">
                                <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/20 group-hover:text-indigo-400 transition-colors" />
                                <input 
                                    type="text"
                                    placeholder="חפש כלי להשוואה..."
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pr-12 pl-4 text-white focus:outline-none focus:border-indigo-500/30 transition-all text-center"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                />
                            </div>
                            <div className="mt-4 flex items-center gap-2 text-white/30 text-xs">
                                <Plus className="w-4 h-4" />
                                <span>הוסף כלי ({3 - selectedTools.length} נותרו)</span>
                            </div>
                        </div>

                        {/* Search Results Dropdown */}
                        <AnimatePresence>
                            {searchResults.length > 0 && (
                                <motion.div 
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: 10 }}
                                    className="absolute top-full left-0 right-0 mt-4 bg-[#0A0F1D] border border-white/10 rounded-2xl shadow-2xl z-50 p-2 max-h-[300px] overflow-y-auto backdrop-blur-2xl"
                                >
                                    {searchResults.map((tool, idx) => (
                                        <button 
                                            key={idx}
                                            onClick={() => addTool(tool)}
                                            className="w-full flex items-center justify-between p-3 hover:bg-white/5 rounded-xl transition-all group text-right"
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-xs font-bold text-white group-hover:bg-indigo-500/20 transition-all">
                                                    {tool.tool_name.charAt(0)}
                                                </div>
                                                <span className="font-medium text-white">{tool.tool_name}</span>
                                            </div>
                                            <div className="text-[10px] text-white/30 font-bold uppercase tracking-wider">{tool.analysis?.metrics?.pricing || 'AI'}</div>
                                        </button>
                                    ))}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                )}
            </div>

            {/* View Toggle */}
            <div className="flex justify-center mb-8">
                <div className="inline-flex bg-white/5 p-1 rounded-2xl border border-white/10 backdrop-blur-md">
                    <button 
                        onClick={() => setViewMode('specs')}
                        className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center gap-2 ${viewMode === 'specs' ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/20' : 'text-white/40 hover:text-white'}`}
                    >
                        <Zap className="w-4 h-4" />
                        נתונים טכניים (Specs)
                    </button>
                    <button 
                        onClick={() => setViewMode('outputs')}
                        className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center gap-2 ${viewMode === 'outputs' ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/20' : 'text-white/40 hover:text-white'}`}
                    >
                        <ImageIcon className="w-4 h-4" />
                        השוואת פלטים (Side-by-Side)
                    </button>
                </div>
            </div>

            {/* Comparison Logic */}
            <div className="bg-[#040914]/80 border border-white/10 rounded-[2.5rem] p-8 backdrop-blur-3xl shadow-2xl">
                {selectedTools.length === 0 ? (
                    <div className="py-20 text-center flex flex-col items-center justify-center">
                        <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mb-6">
                            <Info className="w-8 h-8 text-white/20" />
                        </div>
                        <h3 className="text-xl font-bold text-white/60 mb-2">המטריצה ריקה</h3>
                        <p className="text-white/30 max-w-xs leading-relaxed">בחר לפחות כלי אחד כדי להתחיל להשוות נתונים וביצועים.</p>
                    </div>
                ) : (
                    <>
                        {viewMode === 'specs' ? (
                            <div className="space-y-2">
                                {/* Header Row */}
                                <div className="grid grid-cols-[1fr_repeat(3,1fr)] gap-4 pb-8 mb-4 border-b border-white/10 items-end">
                                    <div className="text-xs text-white/30 font-bold uppercase tracking-widest pb-1">פרמטרים</div>
                                    {selectedTools.map((tool, idx) => (
                                        <div key={idx} className="text-center">
                                            <div className="text-xs font-black text-indigo-400 uppercase tracking-tighter mb-1">Tool 0{idx+1}</div>
                                            <div className="text-lg font-bold text-white truncate">{tool.tool_name}</div>
                                        </div>
                                    ))}
                                    {[...Array(3 - selectedTools.length)].map((_, idx) => (
                                        <div key={idx + selectedTools.length} className="text-center opacity-20 filter grayscale">
                                            <div className="text-xs font-black text-white/30 uppercase tracking-tighter mb-1">Empty</div>
                                            <div className="text-lg font-bold text-white/30">N/A</div>
                                        </div>
                                    ))}
                                </div>

                                {/* Dynamic Rows */}
                                {renderSpecRow("Latency (זמן תגובה)", <Clock className="w-4 h-4" />, "latency_label", (v) => v || '2.4s')}
                                {renderSpecRow("מחיר למשימה (Est.)", <DollarSign className="w-4 h-4" />, "cost_label", (v) => v || '$0.01 / task')}
                                {renderSpecRow("אינטגרציות", <Share2 className="w-4 h-4" />, "integration", (v) => v || 'Web / API')}
                                {renderSpecRow("דרגת פרטיות", <ShieldCheck className="w-4 h-4" />, "privacy_grade", (v) => v || 'Enterprise Safe')}
                                {renderSpecRow("עקומת למידה", <AlignLeft className="w-4 h-4" />, "learning_curve")}
                                {renderSpecRow("רמת דיוק", <Zap className="w-4 h-4" />, "accuracy", (v) => `${v}/5`)}
                                
                                <div className="mt-12 p-6 bg-white/5 rounded-3xl border border-white/10">
                                    <h4 className="flex items-center gap-2 text-white font-bold mb-4">
                                        <Zap className="w-4 h-4 text-amber-400" />
                                        ניתוח המומחים (System Insight)
                                    </h4>
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                                        {selectedTools.map((tool, idx) => (
                                            <div key={idx} className="space-y-3">
                                                <div className="text-indigo-400 text-xs font-bold uppercase tracking-widest">{tool.tool_name}</div>
                                                <p className="text-sm text-white/60 leading-relaxed italic">"{tool.analysis?.executive_summary}"</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-12 py-8">
                                {/* Side-by-Side Outputs Section */}
                                <div className="space-y-16">
                                    {/* Image Gen Sample */}
                                    <div className="space-y-6">
                                        <div className="flex items-center justify-between border-b border-white/5 pb-4">
                                            <div className="flex items-center gap-3">
                                                <div className="p-2 bg-indigo-500/20 rounded-lg">
                                                    <ImageIcon className="w-5 h-5 text-indigo-400" />
                                                </div>
                                                <div>
                                                    <h3 className="text-xl font-bold text-white">Image Generation</h3>
                                                    <p className="text-xs text-white/40">Prompt: "Cyberpunk City, ultra-detailed, 8k, futuristic aesthetics"</p>
                                                </div>
                                            </div>
                                            <div className="px-3 py-1 bg-white/5 rounded-full text-[10px] text-white/50 uppercase font-black">100% Zoom Check</div>
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                                            {selectedTools.map((tool, idx) => (
                                                <div key={idx} className="space-y-4">
                                                    <div className="aspect-[4/3] rounded-2xl bg-white/5 overflow-hidden border border-white/10 group cursor-zoom-in relative">
                                                        <img 
                                                            src={tool.gallery?.[0]?.media_url || "https://images.unsplash.com/photo-1614850523296-d8c1af93d400?q=80&w=800&auto=format"} 
                                                            alt={`${tool.tool_name} sample`}
                                                            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-150"
                                                        />
                                                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                                                            <div className="text-[10px] text-white font-bold uppercase tracking-widest">Detail Check Mode</div>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-sm font-bold text-white/80">{tool.tool_name}</span>
                                                        <span className="text-[10px] font-black px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded">HIGH FIDELITY</span>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Coding Sample */}
                                    <div className="space-y-6">
                                        <div className="flex items-center justify-between border-b border-white/5 pb-4">
                                            <div className="flex items-center gap-3">
                                                <div className="p-2 bg-indigo-500/20 rounded-lg">
                                                    <Code className="w-5 h-5 text-indigo-400" />
                                                </div>
                                                <div>
                                                    <h3 className="text-xl font-bold text-white">Coding Logic</h3>
                                                    <p className="text-xs text-white/40">Task: "Create a React Hook for handling multi-step forms with validation"</p>
                                                </div>
                                            </div>
                                            <div className="px-3 py-1 bg-white/5 rounded-full text-[10px] text-white/50 uppercase font-black">Clean vs Boilerplate</div>
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                                            {selectedTools.map((tool, idx) => (
                                                <div key={idx} className="space-y-4">
                                                    <div className="rounded-2xl bg-[#010409] p-4 font-mono text-xs text-white/80 border border-white/10 h-[300px] overflow-hidden relative">
                                                        <pre className="leading-relaxed">
                                                            {idx === 0 ? (
                                                                <code>
{`const useForm = () => {
  const [step, setStep] = useState(1);
  const [data, setData] = useState({});
  
  const next = () => setStep(s => s + 1);
  const back = () => setStep(s => s - 1);
  
  return { step, data, next, back };
};`}
                                                                </code>
                                                            ) : (
                                                                <code>
{`// Auto-generated hook
export function useMultiStepForm(initial) {
  const [current, setCurrent] = useState(0);
  const [steps, setSteps] = useState(initial);

  if (steps.length === 0) {
    throw new Error("Empty steps");
  }
  
  // Boilerplate validation logic
  useEffect(() => {
     console.log("Mounted");
  }, []);
  
  // ... extra lines ...
}`}
                                                                </code>
                                                            )}
                                                        </pre>
                                                        <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-[#010409] to-transparent" />
                                                    </div>
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-sm font-bold text-white/80">{tool.tool_name}</span>
                                                        <span className={`text-[10px] font-black px-2 py-0.5 rounded ${idx === 0 ? 'bg-indigo-500/20 text-indigo-400' : 'bg-red-500/20 text-red-500'}`}>
                                                            {idx === 0 ? 'CLEAN CODE' : 'HEAVY BOILERPLATE'}
                                                        </span>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

export default Compare;
