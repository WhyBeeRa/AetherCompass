import React, { useState, useEffect } from 'react';
import { Swords, CheckCircle2, AlertCircle, RefreshCcw, TrendingUp, ShieldCheck } from 'lucide-react';
import { useAuth } from '../AuthContext';
import { useNavigate } from 'react-router-dom';

const EloBattle = ({ setAppError }) => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [voted, setVoted] = useState(false);
  const [winner, setWinner] = useState(null);
  const [showStats, setShowStats] = useState(false);
  const [userUpdate, setUserUpdate] = useState(null);
  const [reason, setReason] = useState("");
  const [submissionLoading, setSubmissionLoading] = useState(false);

  const fetchPair = async () => {
    setLoading(true);
    setVoted(false);
    setShowStats(false);
    setWinner(null);
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/community/battle/pair`);
      if (res.ok) {
        const data = await res.json();
        setTools(data);
      }
    } catch (err) {
      console.error(err);
      if (setAppError) setAppError("נכשל בטעינת קרב Elo");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPair();
  }, []);

  const handleVote = async (toolName) => {
    if (voted) return;
    setVoted(true);
    setWinner(toolName);
    // We'll show the reason selection before final submission or just use a default
    // Actually, let's make it so they click, then they can optionally add a reason, then "Confirm"
  };

  const submitVote = async (selectedReason = "") => {
    if (submissionLoading) return;
    setSubmissionLoading(true);
    
    try {
      const idToken = await currentUser.getIdToken();
      const res = await fetch(`${import.meta.env.VITE_API_URL}/community/battle/vote`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${idToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool_a: tools[0].tool_name,
          tool_b: tools[1].tool_name,
          winner: winner,
          category: tools[0].analysis.job_to_be_done?.[0] || "General",
          reason: selectedReason || reason
        })
      });

      if (res.ok) {
        const data = await res.json();
        setUserUpdate(data);
        setShowStats(true);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSubmissionLoading(false);
    }
  };

  if (loading) return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center gap-6 text-white/40">
      <RefreshCcw className="w-12 h-12 animate-spin text-cyan-400" />
      <p className="text-xl font-black italic tracking-tighter">PREPARING ARENA...</p>
    </div>
  );

  return (
    <div className="w-full max-w-6xl mx-auto space-y-8 animate-in fade-in zoom-in-95 duration-500">
      <div className="text-center space-y-2">
        <h2 className="text-sm font-black text-cyan-400 uppercase tracking-[0.3em]">The Arena</h2>
        <h1 className="text-4xl font-black text-white italic tracking-tighter">CHOOSE THE SUPERIOR INTELLIGENCE</h1>
        <p className="text-white/40 max-w-xl mx-auto text-sm">בחן את הפלטים וקבע מי מהכלים מספק תוצאה איכותית, אמינה ושימושית יותר. הצבעתך מעדכנת את ה-Trust Score בזמן אמת.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 relative items-stretch">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20 hidden md:flex items-center justify-center w-16 h-16 bg-[#040914] border-4 border-white/10 rounded-full shadow-[0_0_30px_rgba(0,0,0,0.5)]">
           <Swords className="w-8 h-8 text-white/20 italic" />
        </div>

        {tools.map((tool, idx) => (
          <div 
            key={idx}
            onClick={() => !voted && handleVote(tool.tool_name)}
            className={`relative flex flex-col bg-white/5 border-2 rounded-[2rem] p-8 transition-all duration-500 cursor-pointer overflow-hidden group
              ${voted ? (winner === tool.tool_name ? 'border-cyan-500 shadow-[0_0_40px_rgba(6,182,212,0.2)]' : 'border-white/5 opacity-40') : 'border-white/10 hover:border-white/30 hover:bg-white/[0.08] hover:scale-[1.02]'}
            `}
          >
            {/* Tool Label (Hidden until voted) */}
            <div className={`absolute top-6 left-1/2 -translate-x-1/2 px-6 py-2 bg-white/10 border border-white/20 rounded-full backdrop-blur-md z-10 transition-all duration-700
              ${voted ? 'translate-y-0 opacity-100' : '-translate-y-12 opacity-0'}
            `}>
              <span className="text-lg font-black text-white italic tracking-tight">{tool.tool_name}</span>
            </div>

            {/* Content Slot */}
            <div className="flex-1 space-y-6 mt-4">
              <div className="space-y-4">
                <div className="h-1.5 w-12 bg-cyan-500 rounded-full" />
                <h3 className="text-2xl font-bold text-white leading-tight">
                  {voted ? tool.analysis.executive_summary : "Model Output Review"}
                </h3>
                <p className="text-white/60 leading-relaxed min-h-[100px]">
                  {tool.analysis.job_to_be_done?.[0] || "General AI task performance"} evaluation.
                  {!voted && " Please examine the technical consistency, tone, and practical utility of this model's logic based on its general performance profile."}
                </p>
              </div>

              {/* Mock Model Output Simulation (Placeholder for real data if we had it) */}
              <div className="bg-[#020617] rounded-2xl p-6 border border-white/5 font-mono text-xs text-white/50 space-y-3">
                <div className="flex gap-2">
                   <div className="w-3 h-3 rounded-full bg-rose-500/30" />
                   <div className="w-3 h-3 rounded-full bg-amber-500/30" />
                   <div className="w-3 h-3 rounded-full bg-emerald-500/30" />
                </div>
                <div className="p-3 bg-white/5 rounded-lg border border-white/5 italic">
                   {tool.analysis.pros?.[0] || "Optimized for logical reasoning"}
                </div>
                <div className="opacity-40">
                   {tool.analysis.use_cases?.[0] || "Advanced Content Synthesis"}
                </div>
              </div>
            </div>

            {/* Selection UI */}
            <div className={`mt-8 flex items-center justify-center transition-all duration-500 ${voted ? 'h-12' : 'h-16'}`}>
              {voted ? (
                winner === tool.tool_name ? (
                  <div className="flex items-center gap-2 text-cyan-400 font-black italic">
                    <CheckCircle2 className="w-6 h-6" />
                    WINNER SELECTED
                  </div>
                ) : null
              ) : (
                <div className="px-8 py-3 bg-white/5 border border-white/10 rounded-2xl font-black text-white/40 uppercase tracking-widest group-hover:text-cyan-400 group-hover:border-cyan-500/30 group-hover:bg-cyan-500/10 transition-all">
                  Click to Vote
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {voted && !showStats && (
        <div className="bg-white/5 border border-white/10 rounded-[2rem] p-8 animate-in fade-in slide-in-from-top-4 duration-500">
          <div className="max-w-2xl mx-auto space-y-6">
            <div className="text-center space-y-2">
              <h3 className="text-xl font-bold text-white">למה בחרת ב-{winner}?</h3>
              <p className="text-white/40 text-sm">המשוב שלך עוזר למפתחים להבין מה לשפר.</p>
            </div>
            
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {["דיוק גבוה יותר", "מהירות תגובה", "טון טבעי", "מבנה ברור", "יצירתיות", "אחר"].map((r) => (
                <button
                  key={r}
                  disabled={submissionLoading}
                  onClick={() => {
                    setReason(r);
                    submitVote(r);
                  }}
                  className={`px-4 py-3 rounded-xl border transition-all text-sm font-bold
                    ${reason === r ? 'bg-cyan-500 border-cyan-400 text-[#040914]' : 'bg-white/5 border-white/10 text-white/60 hover:border-white/30 hover:bg-white/10'}
                  `}
                >
                  {r}
                </button>
              ))}
            </div>

            <div className="flex justify-center pt-4">
              <button 
                disabled={submissionLoading}
                onClick={() => submitVote()}
                className="text-white/30 text-xs hover:text-white/60 transition-all underline underline-offset-4 disabled:opacity-50"
              >
                {submissionLoading ? "שולח..." : "דלג ושלח בכל זאת"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Post-Vote Feedback */}
      {showStats && (
        <div className="bg-gradient-to-r from-cyan-500/10 to-indigo-500/10 border border-cyan-500/20 rounded-[2.5rem] p-10 animate-in slide-in-from-bottom-10 duration-700">
           <div className="flex flex-col md:flex-row items-center justify-between gap-8">
             <div className="flex items-center gap-6">
                <div className="w-20 h-20 bg-cyan-500/20 rounded-full flex items-center justify-center text-cyan-400 border border-cyan-500/30 shadow-[0_0_30px_rgba(6,182,212,0.2)]">
                   <TrendingUp className="w-10 h-10" />
                </div>
                <div className="space-y-1">
                   <h4 className="text-2xl font-black text-white italic tracking-tight">VOTE RECORDED!</h4>
                   <p className="text-white/60 font-medium">+10 XP EARNED • TRUST SCORE UPDATED</p>
                </div>
             </div>
             
             {userUpdate?.new_badges?.length > 0 && (
               <div className="flex items-center gap-4 px-6 py-4 bg-yellow-500/10 border border-yellow-500/20 rounded-2xl animate-bounce">
                  <ShieldCheck className="w-8 h-8 text-yellow-500" />
                  <div className="text-left">
                     <p className="text-[10px] text-yellow-500 font-black uppercase tracking-widest">New Badge Unlocked!</p>
                     <p className="font-bold text-white">{userUpdate.new_badges[0]}</p>
                  </div>
               </div>
             )}

             <div className="flex flex-wrap gap-4">
               <button 
                 onClick={fetchPair}
                 className="px-8 py-4 bg-white text-[#040914] font-black italic rounded-2xl hover:scale-105 transition-all shadow-xl"
               >
                 NEXT BATTLE
               </button>
               <button 
                 onClick={() => navigate('/insiders')}
                 className="px-8 py-4 bg-white/5 border border-white/10 text-white font-black italic rounded-2xl hover:bg-white/10 transition-all"
               >
                 COMMUNITY HUB
               </button>
             </div>
           </div>
        </div>
      )}
    </div>
  );
};

export default EloBattle;
