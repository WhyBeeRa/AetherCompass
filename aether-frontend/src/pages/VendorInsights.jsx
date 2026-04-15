import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Target, 
  Users, 
  BarChart3, 
  AlertCircle, 
  Search, 
  Zap, 
  ArrowUpRight, 
  ArrowDownRight,
  ChevronRight,
  Info
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const VendorInsights = () => {
  const [tools, setTools] = useState([]);
  const [selectedTool, setSelectedTool] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Fetch list of tools available for insights
  useEffect(() => {
    const fetchTools = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/vendor/tools`);
        if (res.ok) {
          const data = await res.json();
          setTools(data);
        }
      } catch (err) {
        console.error("Failed to fetch tools", err);
      }
    };
    fetchTools();
  }, []);

  // Fetch insights when a tool is selected
  const fetchInsights = async (toolName) => {
    setLoading(true);
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/vendor/insights/${toolName}`);
      if (res.ok) {
        const data = await res.json();
        setInsights(data);
      }
    } catch (err) {
      console.error("Failed to fetch insights", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectTool = (tool) => {
    setSelectedTool(tool);
    fetchInsights(tool.name);
    setSearchQuery("");
  };

  const filteredTools = searchQuery 
    ? tools.filter(t => t.name.toLowerCase().includes(searchQuery.toLowerCase()))
    : tools.slice(0, 5);

  return (
    <div className="min-h-screen bg-[#040914] text-white p-6 md:p-12 space-y-12">
      {/* Header */}
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div className="space-y-4">
          <div className="flex items-center gap-2 px-3 py-1 bg-cyan-500/10 border border-cyan-500/20 rounded-full w-fit">
            <Zap className="w-4 h-4 text-cyan-400" />
            <span className="text-[10px] font-black uppercase tracking-widest text-cyan-400">B2B Intelligence Portal</span>
          </div>
          <h1 className="text-5xl font-black italic tracking-tighter">AETHER INSIGHTS</h1>
          <p className="text-white/40 max-w-xl">
            גישה לנתוני שוק בזמן אמת. הבן מה המשתמשים באמת מחפשים ואיפה נמצאים פערי השוק שהכלי שלך יכול למלא.
          </p>
        </div>

        {/* Tool Selector */}
        <div className="relative w-full md:w-72 group">
          <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
            <Search className="w-5 h-5 text-white/20 group-focus-within:text-cyan-400 transition-colors" />
          </div>
          <input
            type="text"
            placeholder="Search your tool..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-white placeholder:text-white/20 focus:outline-none focus:border-cyan-500/50 focus:bg-white/10 transition-all font-bold"
          />
          
          <AnimatePresence>
            {searchQuery && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="absolute top-full left-0 right-0 mt-2 bg-[#0a0f1e] border border-white/10 rounded-2xl overflow-hidden z-50 shadow-2xl"
              >
                {filteredTools.length > 0 ? (
                  filteredTools.map(tool => (
                    <button
                      key={tool.id}
                      onClick={() => handleSelectTool(tool)}
                      className="w-full text-left px-6 py-4 hover:bg-white/5 transition-colors flex items-center justify-between group"
                    >
                      <span className="font-bold">{tool.name}</span>
                      <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-all text-cyan-400" />
                    </button>
                  ))
                ) : (
                  <div className="px-6 py-4 text-white/40 text-sm italic">No tools found</div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <div className="max-w-7xl mx-auto">
        {!selectedTool ? (
          <div className="h-[50vh] flex flex-col items-center justify-center border-2 border-dashed border-white/5 rounded-[3rem] gap-6 text-white/20">
            <BarChart3 className="w-16 h-16 opacity-20" />
            <p className="font-black italic text-xl tracking-tighter">SELECT A TOOL TO REVEAL MARKET DATA</p>
          </div>
        ) : loading ? (
          <div className="h-[50vh] flex flex-col items-center justify-center gap-6 text-white/40">
            <div className="w-16 h-16 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin" />
            <p className="font-black italic text-xl tracking-tighter">CRUNCHING DATA FOR {selectedTool.name.toUpperCase()}...</p>
          </div>
        ) : insights ? (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-6 duration-700">
            {/* Top Stats - Replaced with general placeholders since Battles are gone */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white/5 border border-white/10 rounded-[2rem] p-8 space-y-2 relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform">
                  <TrendingUp className="w-16 h-16" />
                </div>
                <p className="text-white/40 text-sm font-bold uppercase tracking-widest">Aether Market Score</p>
                <div className="flex items-end gap-3">
                  <h2 className="text-5xl font-black italic text-cyan-400">Stable</h2>
                </div>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-[2rem] p-8 space-y-2 relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform">
                  <Target className="w-16 h-16" />
                </div>
                <p className="text-white/40 text-sm font-bold uppercase tracking-widest">Opportunity Index</p>
                <h2 className="text-5xl font-black italic text-white">
                  {insights.missed_searches.length}/10
                </h2>
              </div>
            </div>

            <div className="w-full">
              {/* Market Gaps (Missed Searches) - Keeping this as it's useful B2B insight */}
              <div className="bg-white/5 border border-white/10 rounded-[3rem] p-10 space-y-8">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <h3 className="text-2xl font-black italic text-cyan-400">MARKET GAPS: UNMET DEMAND</h3>
                    <p className="text-white/40 text-sm">משתמשים מחפשים את הדברים האלו ולא מוצאים תוצאות רלוונטיות.</p>
                  </div>
                  <Search className="w-8 h-8 text-cyan-400 opacity-50" />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {insights.missed_searches.length > 0 ? (
                    insights.missed_searches.map((m, i) => (
                      <div key={i} className="bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-cyan-500/5 hover:border-cyan-500/30 transition-all group">
                         <div className="flex justify-between items-start mb-2">
                            <span className="font-black italic text-lg truncate max-w-[150px]">{m.query_text}</span>
                            <div className="px-2 py-0.5 bg-cyan-500/20 rounded text-[10px] font-black text-cyan-400">
                               {m.count} SEARCHES
                            </div>
                         </div>
                         <p className="text-white/40 text-xs">High opportunity for feature development or SEO targeting.</p>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-12 text-white/20 italic col-span-full">No market gaps identified.</div>
                  )}
                </div>
              </div>
            </div>

            {/* Strategy Section */}
            <div className="bg-gradient-to-r from-cyan-500/10 to-indigo-500/10 border border-cyan-500/20 rounded-[3rem] p-10">
               <div className="flex flex-col md:flex-row items-center justify-between gap-12">
                  <div className="space-y-4 text-center md:text-left">
                     <h3 className="text-3xl font-black italic tracking-tight uppercase">Strategic Posture</h3>
                     <p className="text-white/60 max-w-sm">
                        מיקוד במענה על פערי החיפוש שזוהו יאפשר לכלי שלך להשיג יתרון משמעותי על פני המתחרים בשוק.
                     </p>
                  </div>

                  <div className="p-8 bg-white/5 border border-white/10 rounded-3xl backdrop-blur-xl space-y-4">
                     <div className="flex items-center gap-3">
                        <Info className="w-6 h-6 text-cyan-400" />
                        <span className="font-black italic">STRATEGY ADVISOR</span>
                     </div>
                     <p className="text-white/50 text-xs leading-relaxed max-w-[200px]">
                        נראה שיש ביקוש גבוה ל "{insights.missed_searches[0]?.query_text || 'פיצ'רים חדשים'}". 
                        שקול להוסיף יכולות אלו למוצר שלך כדי להרחיב את נתח השוק.
                     </p>
                  </div>
               </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default VendorInsights;

