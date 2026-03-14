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
            גישה לנתוני שוק בזמן אמת. הבן איפה הכלי שלך מנצח, איפה הוא מפסיד ב-Elo Battles ומה המשתמשים באמת מחפשים ולא מוצאים.
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
            {/* Top Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white/5 border border-white/10 rounded-[2rem] p-8 space-y-2 relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform">
                  <TrendingUp className="w-16 h-16" />
                </div>
                <p className="text-white/40 text-sm font-bold uppercase tracking-widest">ELO Win Rate</p>
                <div className="flex items-end gap-3">
                  <h2 className="text-5xl font-black italic text-cyan-400">{insights.win_rate}%</h2>
                  <div className={`flex items-center gap-1 mb-2 ${insights.win_rate > 50 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {insights.win_rate > 50 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                    <span className="text-xs font-bold">{insights.win_rate > 50 ? 'Above Avg' : 'Below Avg'}</span>
                  </div>
                </div>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-[2rem] p-8 space-y-2 relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform">
                  <Users className="w-16 h-16" />
                </div>
                <p className="text-white/40 text-sm font-bold uppercase tracking-widest">Total Battles</p>
                <h2 className="text-5xl font-black italic text-white">{insights.total_battles}</h2>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-[2rem] p-8 space-y-2 relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform">
                  <Target className="w-16 h-16" />
                </div>
                <p className="text-white/40 text-sm font-bold uppercase tracking-widest">Market Awareness</p>
                <h2 className="text-5xl font-black italic text-white">
                  {Math.round(insights.total_battles / 10 * (insights.win_rate / 100) * 10) / 10}/10
                </h2>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Loss Reasons (The "Why") */}
              <div className="bg-white/5 border border-white/10 rounded-[3rem] p-10 space-y-8">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <h3 className="text-2xl font-black italic">INTELLIGENCE: WHY YOU LOSE</h3>
                    <p className="text-white/40 text-sm">סיבות שבגללן משתמשים העדיפו את המתחרים בקרבות ראש בראש.</p>
                  </div>
                  <AlertCircle className="w-8 h-8 text-rose-500 opacity-50" />
                </div>

                <div className="space-y-4">
                  {insights.loss_reasons.length > 0 ? (
                    insights.loss_reasons.map((r, i) => (
                      <div key={i} className="flex items-center gap-6 group">
                        <div className="w-12 h-12 flex-shrink-0 bg-rose-500/10 border border-rose-500/20 rounded-2xl flex items-center justify-center text-rose-400 font-black italic">
                          #{i+1}
                        </div>
                        <div className="flex-1 space-y-1">
                          <div className="flex justify-between items-center">
                            <span className="font-bold text-lg">{r.reason}</span>
                            <span className="text-white/20 text-xs">Lost to {r.winner}</span>
                          </div>
                          <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                            <motion.div 
                               initial={{ width: 0 }}
                               animate={{ width: `${100 - (i * 15)}%` }}
                               className="h-full bg-rose-500/50"
                            />
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-12 text-white/20 italic">No loss data recorded yet.</div>
                  )}
                </div>
              </div>

              {/* Market Gaps (Missed Searches) */}
              <div className="bg-white/5 border border-white/10 rounded-[3rem] p-10 space-y-8">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <h3 className="text-2xl font-black italic text-cyan-400">MARKET GAPS: UNMET DEMAND</h3>
                    <p className="text-white/40 text-sm">משתמשים מחפשים את הדברים האלו ולא מוצאים תוצאות רלוונטיות.</p>
                  </div>
                  <Search className="w-8 h-8 text-cyan-400 opacity-50" />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
                    <div className="col-span-2 text-center py-12 text-white/20 italic">No market gaps identified.</div>
                  )}
                </div>
              </div>
            </div>

            {/* Competitor Analysis */}
            <div className="bg-gradient-to-r from-cyan-500/10 to-indigo-500/10 border border-cyan-500/20 rounded-[3rem] p-10">
               <div className="flex flex-col md:flex-row items-center justify-between gap-12">
                  <div className="space-y-4 text-center md:text-left">
                     <h3 className="text-3xl font-black italic tracking-tight uppercase">Primary Adversaries</h3>
                     <p className="text-white/60 max-w-sm">
                        אלו הכלים שהכי קשה לך לנצח. ניתוח של ה-Value Proposition שלהם יכול לחשוף נקודות תורפה.
                     </p>
                  </div>

                  <div className="flex-1 flex flex-wrap justify-center gap-6">
                    {insights.competitor_comparison.length > 0 ? (
                      insights.competitor_comparison.map((comp, i) => (
                        <div key={i} className="flex flex-col items-center gap-3">
                           <div className="w-24 h-24 bg-[#040914] border-4 border-white/10 rounded-full flex items-center justify-center font-black text-2xl group hover:border-cyan-500 transition-all duration-500 relative">
                              {comp.competitor[0].toUpperCase()}
                              <div className="absolute -top-2 -right-2 bg-rose-500 text-white text-[10px] font-black px-2 py-1 rounded-full shadow-lg">
                                 {comp.win_count} L
                              </div>
                           </div>
                           <span className="font-bold text-sm text-white/60">{comp.competitor}</span>
                        </div>
                      ))
                    ) : (
                      <div className="text-white/20 italic">Insufficient data for competitor analysis.</div>
                    )}
                  </div>

                  <div className="p-8 bg-white/5 border border-white/10 rounded-3xl backdrop-blur-xl space-y-4">
                     <div className="flex items-center gap-3">
                        <Info className="w-6 h-6 text-cyan-400" />
                        <span className="font-black italic">STRATEGY ADVISOR</span>
                     </div>
                     <p className="text-white/50 text-xs leading-relaxed max-w-[200px]">
                        נראה שהכלי שלך מתקשה מול {insights.competitor_comparison[0]?.competitor || 'המתחרים'}. 
                        מומלץ להתמקד בשיפור {insights.loss_reasons[0]?.reason || 'הדיוק'} כדי לסגור את הפער.
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
