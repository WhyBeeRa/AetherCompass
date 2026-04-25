import React, { useState, useEffect } from 'react';
import { Shield, Target, Trophy, Zap, Users, Star, CheckCircle } from 'lucide-react';
import { useAuth } from '../AuthContext';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

const AetherInsiders = ({ setAppError }) => {
  const { currentUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showScoutModal, setShowScoutModal] = useState(false);
  const [scoutData, setScoutData] = useState({ name: '', url: '', description: '' });
  const [scouting, setScouting] = useState(false);
  const [scoutSuccess, setScoutSuccess] = useState(false);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const leaderboardRes = await fetch(`${import.meta.env.VITE_API_URL}/community/leaderboard`);
        if (leaderboardRes.ok) {
          const lbData = await leaderboardRes.json();
          setLeaderboard(lbData);
        }
      } catch (err) {
        console.error("Error fetching leaderboard data:", err);
      } finally {
        setLoading(false);
      }
    };

    const fetchProfile = async () => {
      try {
        const idToken = await currentUser.getIdToken();
        const profileRes = await fetch(`${import.meta.env.VITE_API_URL}/community/profile`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${idToken}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (profileRes.ok) {
          const profileData = await profileRes.json();
          setProfile(profileData);
        }
      } catch (err) {
        console.error("Error fetching profile:", err);
        if (setAppError) setAppError("Failed to load user profile");
      }
    };

    fetchLeaderboard();
    if (currentUser) {
      fetchProfile();
    }
  }, [currentUser, setAppError]);

  const handleScoutSubmit = async (e) => {
    e.preventDefault();
    setScouting(true);
    try {
      const idToken = await currentUser.getIdToken();
      const res = await fetch(`${import.meta.env.VITE_API_URL}/community/contribute`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${idToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(scoutData)
      });
      
      if (res.ok) {
        const data = await res.json();
        setProfile(data.user);
        setScoutSuccess(true);
        setScoutData({ name: '', url: '', description: '' });
        // Refresh leaderboard to show new points
        const lbRes = await fetch(`${import.meta.env.VITE_API_URL}/community/leaderboard`);
        if (lbRes.ok) setLeaderboard(await lbRes.json());
        
        // Close modal after 3 seconds
        setTimeout(() => {
            setShowScoutModal(false);
            setScoutSuccess(false);
        }, 3000);
      } else {
        const errorData = await res.json();
        if (setAppError) setAppError(errorData.detail || "Failed to submit tool for audit.");
      }
    } catch (err) {
      console.error(err);
      if (setAppError) setAppError("Server communication error.");
    } finally {
      setScouting(false);
    }
  };

  if (loading) return <div className="min-h-[50vh] flex items-center justify-center text-white/40">Processing network data...</div>;

  return (
    <div className="w-full max-w-5xl mx-auto space-y-12 animate-in fade-in duration-700">
      {/* Hero Section */}
      <section className="text-center space-y-4">
        <h1 className="text-5xl font-black bg-gradient-to-r from-cyan-400 via-indigo-400 to-purple-500 bg-clip-text text-transparent italic tracking-tighter">
          AETHER INSIDERS
        </h1>
        <p className="text-xl text-white/60 max-w-2xl mx-auto font-medium">
          Community is not a forum; it's the verification mechanism of the future. Join the architects shaping the Truth Score.
        </p>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* User Status Card */}
        <div className="lg:col-span-1 space-y-6">
          {currentUser ? (
            <>
              <div className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 blur-3xl -mr-16 -mt-16 group-hover:bg-cyan-500/20 transition-all duration-500" />
                
                <div className="flex flex-col items-center text-center space-y-6 relative z-10">
                  <div className="relative">
                    <div className="w-24 h-24 rounded-full bg-gradient-to-br from-cyan-500 to-indigo-600 p-1">
                      <div className="w-full h-full rounded-full bg-[#040914] flex items-center justify-center text-3xl font-black text-white italic">
                        {currentUser?.displayName?.[0] || currentUser?.email?.[0]}
                      </div>
                    </div>
                    <div className="absolute -bottom-2 -right-2 bg-yellow-500 text-[#040914] p-1.5 rounded-lg shadow-lg">
                      <Star className="w-4 h-4 fill-current" />
                    </div>
                  </div>

                  <div>
                    <h3 className="text-2xl font-bold tracking-tight text-white italic">
                      {profile?.display_name || "Agent Scout"}
                    </h3>
                    <p className="text-white/40 text-sm font-medium uppercase tracking-widest mt-1">
                       {profile?.badges?.[profile?.badges?.length - 1] || "New Member"}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 w-full gap-4">
                    <div className="bg-white/5 rounded-2xl p-4 border border-white/5 flex items-center justify-center">
                      <span className="text-[10px] text-white/40 uppercase font-black block">COMMUNITY MEMBER</span>
                    </div>
                  </div>


                  
                  <button 
                    onClick={() => setShowScoutModal(true)}
                    className="w-full py-4 bg-white/5 border border-white/10 rounded-2xl text-white/80 font-bold hover:bg-white/10 transition-all flex items-center justify-center gap-2"
                  >
                    <Target className="w-4 h-4 text-cyan-400" />
                    SCOUT NEW TOOL
                  </button>
                </div>
              </div>

              {/* Badges Display */}
              <div className="bg-white/5 border border-white/10 rounded-3xl p-6">
                <h4 className="text-sm font-black text-white/40 uppercase tracking-widest mb-4 flex items-center gap-2">
                  <Trophy className="w-4 h-4" />
                  BADGES EARNED
                </h4>
                <div className="flex flex-wrap gap-2">
                  {profile?.badges?.map((badge, idx) => (
                    <span key={idx} className="px-3 py-1.5 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded-full text-xs font-bold">
                      {badge}
                    </span>
                  ))}
                  {!profile?.badges?.length && <p className="text-white/20 text-sm italic">Start rating tools to earn badges...</p>}
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-xl relative overflow-hidden group flex flex-col items-center text-center space-y-6">
              <div className="w-24 h-24 rounded-full bg-white/5 flex items-center justify-center">
                <Shield className="w-10 h-10 text-white/20" />
              </div>
              <div>
                <h3 className="text-2xl font-bold tracking-tight text-white italic">
                  JOIN THE INSIDERS
                </h3>
                <p className="text-white/40 text-sm font-medium mt-2">
                  Log in to earn XP, discover new tools, and shape the community's truth ratings.
                </p>
              </div>
              <Link to="/activation" className="w-full py-4 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded-2xl font-black italic tracking-tight hover:bg-cyan-500/20 transition-all flex items-center justify-center gap-2">
                <Zap className="w-5 h-5" />
                LOG IN TO PARTICIPATE
              </Link>
            </div>
          )}
        </div>

        {/* Global Leaderboard */}
        <div className="lg:col-span-2 bg-[#040914]/50 border border-white/10 rounded-3xl p-8 backdrop-blur-xl">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-black text-white italic tracking-tight flex items-center gap-3">
              <Trophy className="w-6 h-6 text-yellow-500" />
              THE INSIDERS BOARD
            </h2>
            <div className="text-[10px] text-white/40 font-bold uppercase tracking-widest px-3 py-1 border border-white/10 rounded-full">
              GLOBAL RANKINGS
            </div>
          </div>

          <div className="space-y-4">
            {leaderboard.map((user, idx) => (
              <div key={idx} className={`flex items-center justify-between p-4 rounded-2xl transition-all ${idx < 3 ? 'bg-white/10 border border-white/20' : 'bg-white/5 border border-white/5'}`}>
                <div className="flex items-center gap-4">
                  <span className={`text-xl font-black w-6 ${idx === 0 ? 'text-yellow-500' : idx === 1 ? 'text-slate-400' : idx === 2 ? 'text-amber-700' : 'text-white/20'}`}>
                    {idx + 1}
                  </span>
                  <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center font-bold text-white/60">
                    {user.display_name?.[0] || user.email?.[0]}
                  </div>
                  <div>
                    <div className="font-bold text-white text-lg">{user.display_name}</div>
                    <div className="text-[10px] text-cyan-400/60 uppercase font-black flex gap-2">
                       {JSON.parse(user.badges_json || '[]').slice(-1)[0] || "Scout"}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xl font-black text-white">{user.points}</div>
                  <div className="text-[10px] text-white/40 font-bold uppercase">Points</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Scout Modal */}
      <AnimatePresence>
        {showScoutModal && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowScoutModal(false)}
              className="absolute inset-0 bg-[#040914]/80 backdrop-blur-md"
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="relative w-full max-w-lg bg-[#0a1120] border border-white/10 rounded-3xl p-8 shadow-2xl z-10"
            >
              <div className="flex items-center gap-3 mb-6">
                 <div className="p-3 bg-cyan-500/10 rounded-2xl">
                    <Target className="w-6 h-6 text-cyan-400" />
                 </div>
                 <div>
                    <h3 className="text-xl font-black text-white italic">TOOL SCOUTING</h3>
                    <p className="text-xs text-white/40 uppercase font-bold tracking-widest leading-none">Add a tool to the Aether ecosystem</p>
                 </div>
              </div>

              {scoutSuccess ? (
                <div className="py-12 text-center space-y-4 animate-in zoom-in duration-500">
                  <div className="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto border border-emerald-500/30">
                    <CheckCircle className="w-10 h-10 text-emerald-400" />
                  </div>
                  <h3 className="text-xl font-bold text-white italic">SCOUTING SUCCESSFUL!</h3>
                  <p className="text-white/60 text-sm">Mission received. An AI agent is currently conducting an in-depth scan of the tool. It will appear for admin approval once the report is finalized.</p>
                  <p className="text-cyan-400 font-black text-xs uppercase tracking-widest">+50 XP AWARDED</p>
                </div>
              ) : (
                <form onSubmit={handleScoutSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-xs font-black text-white/40 uppercase tracking-widest mr-1">Tool Name</label>
                    <input 
                      required
                      value={scoutData.name}
                      onChange={(e) => setScoutData({...scoutData, name: e.target.value})}
                      placeholder="e.g. Cursor AI"
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 focus:border-cyan-500/50 outline-none transition-all"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-black text-white/40 uppercase tracking-widest mr-1">Website URL</label>
                    <input 
                      required
                      type="url"
                      value={scoutData.url}
                      onChange={(e) => setScoutData({...scoutData, url: e.target.value})}
                      placeholder="https://..."
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 focus:border-cyan-500/50 outline-none transition-all"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-black text-white/40 uppercase tracking-widest mr-1">Brief Description</label>
                    <textarea 
                      required
                      value={scoutData.description}
                      onChange={(e) => setScoutData({...scoutData, description: e.target.value})}
                      placeholder="Why should this be in the vault?"
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 focus:border-cyan-500/50 outline-none transition-all h-24 resize-none"
                    />
                  </div>
                  
                  <button 
                    disabled={scouting}
                    type="submit"
                    className="w-full py-4 bg-cyan-500 text-[#040914] font-black italic rounded-2xl hover:bg-cyan-400 transition-all shadow-[0_0_30px_rgba(6,182,212,0.3)] disabled:opacity-50"
                  >
                    {scouting ? "SUBMITTING TO AUDITOR..." : "SUBMIT FOR VERIFICATION"}
                  </button>
                </form>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AetherInsiders;
