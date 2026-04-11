import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Check, X, ExternalLink, Activity, Clock, AlertTriangle, Search } from 'lucide-react';
import { useAuth } from '../AuthContext';
import { apiFetch } from '../api';

const AdminRequests = () => {
  const { currentUser, isAdmin } = useAuth();
  const [pendingTools, setPendingTools] = useState([]);
  const [liveScans, setLiveScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('ready'); // 'ready' or 'scanning'

  const fetchAll = async () => {
    try {
      if (!currentUser) return;
      const idToken = await currentUser.getIdToken();
      
      // Fetch Ready for Review
      const resPending = await apiFetch('/admin/pending', {
        headers: { 'Authorization': `Bearer ${idToken}` }
      });
      const dataPending = await resPending.json();
      setPendingTools(dataPending);

      // Fetch Live Scans
      const resLive = await apiFetch('/admin/live-scans', {
        headers: { 'Authorization': `Bearer ${idToken}` }
      });
      const dataLive = await resLive.json();
      setLiveScans(dataLive);

    } catch (error) {
      console.error("Error fetching admin data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (currentUser && isAdmin) {
      fetchAll();
      // Poll live scans every 5 seconds
      const interval = setInterval(fetchAll, 5000);
      return () => clearInterval(interval);
    }
  }, [currentUser, isAdmin]);

  const handleAction = async (toolName, action) => {
    try {
      const idToken = await currentUser.getIdToken();
      const endpoint = action === 'approve' ? '/admin/approve' : '/admin/reject';
      
      const res = await apiFetch(`${endpoint}?tool_name=${encodeURIComponent(toolName)}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${idToken}` }
      });

      if (res.ok) {
        fetchAll();
      }
    } catch (error) {
      console.error(`Error ${action}ing tool:`, error);
    }
  };

  if (!currentUser || !isAdmin) return <div className="p-20 text-center text-white/50 font-bold uppercase tracking-widest">Access Denied • Admin Protocol Required</div>;

  return (
    <div className="min-h-screen pt-24 px-6 pb-20 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Shield className="text-cyan-400 w-10 h-10" />
            Admin Command Center
          </h1>
          <p className="text-white/60">Review and verify community-scouted AI assets.</p>
        </div>

        <div className="flex bg-white/5 p-1 rounded-xl border border-white/10">
          <button 
            onClick={() => setActiveTab('ready')}
            className={`px-6 py-2 rounded-lg transition-all flex items-center gap-2 ${activeTab === 'ready' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'text-white/50 hover:text-white'}`}
          >
            Ready for Review
            <span className="bg-white/10 px-2 rounded-md text-xs">{pendingTools.length}</span>
          </button>
          <button 
            onClick={() => setActiveTab('scanning')}
            className={`px-6 py-2 rounded-lg transition-all flex items-center gap-2 ${activeTab === 'scanning' ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30' : 'text-white/50 hover:text-white'}`}
          >
            Live AI Scans
            <span className="bg-white/10 px-2 rounded-md text-xs">{liveScans.filter(s => s.status !== 'completed').length}</span>
          </button>
        </div>
      </div>

      {loading && pendingTools.length === 0 && (
        <div className="flex items-center justify-center p-20">
          <Activity className="text-cyan-400 animate-spin w-12 h-12" />
        </div>
      )}

      <AnimatePresence mode="wait">
        {activeTab === 'ready' ? (
          <motion.div 
            key="ready"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="grid grid-cols-1 gap-6"
          >
            {pendingTools.length === 0 ? (
              <div className="text-center p-20 bg-white/5 rounded-2xl border border-dashed border-white/10">
                <Clock className="w-12 h-12 text-white/20 mx-auto mb-4" />
                <p className="text-white/40">No tools waiting for review.</p>
              </div>
            ) : (
              pendingTools.map((tool) => (
                <div key={tool.tool_name} className="bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col md:flex-row gap-6 items-start">
                  <div className="flex-1 w-full">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-bold text-white uppercase tracking-wider">{tool.tool_name}</h3>
                      <span className="px-3 py-1 bg-cyan-500/10 text-cyan-400 text-xs rounded-full border border-cyan-500/20">
                        {tool.analysis?.metrics?.trust_score}/100 Trust
                      </span>
                    </div>
                    
                    <p className="text-white/60 mb-4 line-clamp-2">{tool.analysis?.executive_summary}</p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                      <div className="bg-white/5 p-3 rounded-lg border border-white/5">
                        <span className="block text-white/30 mb-1">Pricing</span>
                        <span className="text-white font-medium">{tool.analysis?.metrics?.pricing}</span>
                      </div>
                      <div className="bg-white/5 p-3 rounded-lg border border-white/5">
                        <span className="block text-white/30 mb-1">Category</span>
                        <span className="text-white font-medium">{tool.analysis?.job_to_be_done?.[0]}</span>
                      </div>
                      <div className="bg-white/5 p-3 rounded-lg border border-white/5">
                        <span className="block text-white/30 mb-1">Ease of Use</span>
                        <span className="text-white font-medium">{tool.analysis?.metrics?.ease_of_use}/5</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex md:flex-col gap-3 w-full md:w-auto">
                    <button 
                      onClick={() => handleAction(tool.tool_name, 'approve')}
                      className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-green-500/10 hover:bg-green-500/20 text-green-400 rounded-xl border border-green-500/30 transition-all font-bold"
                    >
                      <Check className="w-5 h-5" />
                      APPROVE
                    </button>
                    <button 
                      onClick={() => handleAction(tool.tool_name, 'reject')}
                      className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-xl border border-red-500/30 transition-all font-bold"
                    >
                      <X className="w-5 h-5" />
                      REJECT
                    </button>
                  </div>
                </div>
              ))
            )}
          </motion.div>
        ) : (
          <motion.div 
            key="scanning"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="grid grid-cols-1 gap-4"
          >
            {liveScans.length === 0 ? (
              <div className="text-center p-20 bg-white/5 rounded-2xl border border-dashed border-white/10">
                <Search className="w-12 h-12 text-white/20 mx-auto mb-4" />
                <p className="text-white/40">No active AI scans right now.</p>
              </div>
            ) : (
              liveScans.map((task) => (
                <div key={task.task_id} className="bg-white/5 border border-white/10 rounded-2xl p-5 flex items-center justify-between group overflow-hidden relative">
                  {/* Progress Glow Background */}
                  {task.status === 'scanning' && (
                    <motion.div 
                      className="absolute inset-0 bg-purple-500/5"
                      animate={{ opacity: [0, 1, 0] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  )}
                  
                  <div className="flex items-center gap-4 relative z-10">
                    <div className={`p-3 rounded-xl ${
                      task.status === 'failed' ? 'bg-red-500/10 text-red-400' : 
                      task.status === 'completed' ? 'bg-green-500/10 text-green-400' :
                      'bg-purple-500/10 text-purple-400'
                    }`}>
                      {task.status === 'failed' ? <AlertTriangle className="w-6 h-6" /> : 
                       task.status === 'completed' ? <Check className="w-6 h-6" /> :
                       <Activity className="w-6 h-6 animate-pulse" />}
                    </div>
                    
                    <div>
                      <h3 className="font-bold text-white flex items-center gap-2">
                        {task.tool_name}
                        <span className="text-white/20 text-xs font-normal">({task.url})</span>
                      </h3>
                      <p className="text-xs text-white/40">Requested by: {task.submitter_email} • {new Date(task.created_at).toLocaleTimeString()}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-6 relative z-10">
                    <div className="text-right">
                      <span className={`text-xs font-bold px-3 py-1 rounded-full border ${
                        task.status === 'failed' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 
                        task.status === 'completed' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
                        'bg-purple-500/10 text-purple-400 border-purple-500/20'
                      }`}>
                        {task.status.toUpperCase()}
                      </span>
                      {task.error_message && (
                        <p className="text-[10px] text-red-400/60 mt-1 max-w-[200px] truncate">{task.error_message}</p>
                      )}
                    </div>
                    
                    <a 
                      href={task.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="p-2 hover:bg-white/10 rounded-lg text-white/30 hover:text-white transition-colors"
                    >
                      <ExternalLink className="w-5 h-5" />
                    </a>
                  </div>
                </div>
              ))
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AdminRequests;
