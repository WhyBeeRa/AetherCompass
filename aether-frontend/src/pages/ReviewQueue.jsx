import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Check, X, ExternalLink, Activity, Clock, AlertTriangle, Search, 
         Edit3, ChevronDown, ChevronUp, BarChart3, Package, Zap, Filter, CheckSquare } from 'lucide-react';
import { useAuth } from '../AuthContext';
import { apiFetch } from '../api';

const CATEGORIES = [
  "Text & Productivity", "Design & Images", "Dev & Code", "Video & Audio",
  "Automation", "Data & Analytics", "Marketing & SEO", "Education & Research",
  "Customer Support", "Other"
];

const ReviewQueue = () => {
  const { currentUser, isAdmin } = useAuth();
  const [stagingTools, setStagingTools] = useState([]);
  const [pendingTools, setPendingTools] = useState([]);
  const [liveScans, setLiveScans] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('staging');
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [expandedId, setExpandedId] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [editData, setEditData] = useState({});
  const [filterCategory, setFilterCategory] = useState('');
  const [actionLoading, setActionLoading] = useState(null);

  const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

  const getToken = useCallback(async () => {
    return isLocal ? "dev-admin-token" : await currentUser?.getIdToken();
  }, [isLocal, currentUser]);

  const fetchAll = useCallback(async () => {
    try {
      if (!isLocal && !currentUser) return;
      const idToken = await getToken();
      const headers = { 'Authorization': `Bearer ${idToken}`, 'Content-Type': 'application/json' };

      // Fetch Staging Queue (processed, ready for review)
      const resStaging = await apiFetch('/admin/staging/queue?status=processed&limit=200', { headers });
      if (resStaging.ok) {
        const data = await resStaging.json();
        setStagingTools(Array.isArray(data) ? data : []);
      }

      // Fetch Staging Stats
      const resStats = await apiFetch('/admin/staging/stats', { headers });
      if (resStats.ok) setStats(await resStats.json());

      // Fetch Legacy Pending (is_active=0)
      const resPending = await apiFetch('/admin/requests', { headers });
      if (resPending.ok) {
        const dataPending = await resPending.json();
        setPendingTools(Array.isArray(dataPending.requests) ? dataPending.requests : []);
      }

      // Fetch Live Scans
      const resLive = await apiFetch('/admin/live-scans', { headers });
      if (resLive.ok) {
        const dataLive = await resLive.json();
        setLiveScans(Array.isArray(dataLive) ? dataLive : []);
      }

    } catch (error) {
      console.error("Error fetching admin data:", error);
    } finally {
      setLoading(false);
    }
  }, [isLocal, currentUser, getToken]);

  useEffect(() => {
    if (isLocal || (currentUser && isAdmin)) {
      fetchAll();
      const interval = setInterval(fetchAll, 8000);
      return () => clearInterval(interval);
    } else if (currentUser && !isAdmin) {
      setLoading(false);
    }
  }, [currentUser, isAdmin, isLocal, fetchAll]);

  // --- Actions ---

  const handleStagingAction = async (id, action, payload = {}) => {
    setActionLoading(id);
    try {
      const idToken = await getToken();
      const headers = { 'Authorization': `Bearer ${idToken}`, 'Content-Type': 'application/json' };
      
      let endpoint, method, body;
      if (action === 'approve') {
        endpoint = `/admin/staging/approve/${id}`;
        method = 'POST';
        body = JSON.stringify(payload);
      } else if (action === 'reject') {
        endpoint = `/admin/staging/reject/${id}?reason=${encodeURIComponent(payload.reason || '')}`;
        method = 'POST';
      } else if (action === 'edit') {
        endpoint = `/admin/staging/edit/${id}`;
        method = 'PUT';
        body = JSON.stringify(payload);
      }

      const res = await apiFetch(endpoint, { method, headers, body });
      if (res.ok) {
        setEditingId(null);
        setSelectedIds(prev => { const next = new Set(prev); next.delete(id); return next; });
        fetchAll();
      }
    } catch (error) {
      console.error(`Error ${action}ing staging tool:`, error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleBatchAction = async (action) => {
    if (selectedIds.size === 0) return;
    setActionLoading('batch');
    try {
      const idToken = await getToken();
      const headers = { 'Authorization': `Bearer ${idToken}`, 'Content-Type': 'application/json' };
      const endpoint = action === 'approve' ? '/admin/staging/approve-batch' : '/admin/staging/reject-batch';
      
      await apiFetch(endpoint, {
        method: 'POST', headers,
        body: JSON.stringify({ staging_ids: Array.from(selectedIds), reason: 'Batch action' })
      });
      
      setSelectedIds(new Set());
      fetchAll();
    } catch (error) {
      console.error(`Batch ${action} failed:`, error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleLegacyAction = async (toolName, action) => {
    try {
      const idToken = await getToken();
      const endpoint = action === 'approve' ? '/admin/approve' : '/admin/reject';
      await apiFetch(`${endpoint}?tool_name=${encodeURIComponent(toolName)}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${idToken}`, 'Content-Type': 'application/json' }
      });
      fetchAll();
    } catch (error) {
      console.error(`Error ${action}ing tool:`, error);
    }
  };

  const toggleSelect = (id) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const selectAll = () => {
    const filtered = filteredStagingTools();
    if (selectedIds.size === filtered.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filtered.map(t => t.id)));
    }
  };

  const startEdit = (tool) => {
    setEditingId(tool.id);
    setEditData({
      trust_score: tool.trust_score || 70,
      executive_summary: tool.analysis?.executive_summary || '',
      category: tool.category || tool.analysis?.job_to_be_done?.[0] || 'Other'
    });
  };

  const filteredStagingTools = () => {
    if (!filterCategory) return stagingTools;
    return stagingTools.filter(t => 
      (t.category || t.analysis?.job_to_be_done?.[0] || '').toLowerCase() === filterCategory.toLowerCase()
    );
  };

  // --- Score Color ---
  const scoreColor = (score) => {
    if (score >= 85) return 'text-green-400';
    if (score >= 70) return 'text-cyan-400';
    if (score >= 50) return 'text-yellow-400';
    return 'text-red-400';
  };

  const scoreBg = (score) => {
    if (score >= 85) return 'bg-green-500/10 border-green-500/20';
    if (score >= 70) return 'bg-cyan-500/10 border-cyan-500/20';
    if (score >= 50) return 'bg-yellow-500/10 border-yellow-500/20';
    return 'bg-red-500/10 border-red-500/20';
  };

  return (
    <div className="animate-in fade-in slide-in-from-bottom-5 duration-700">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Shield className="text-cyan-400 w-10 h-10" />
            Admin Command Center
          </h1>
          <p className="text-white/60">Review, edit, and publish AI tools from the staging pipeline.</p>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        {[
          { label: 'Pending Processing', value: stats.pending || 0, icon: Package, color: 'text-orange-400', bg: 'bg-orange-500/10' },
          { label: 'Ready for Review', value: stats.processed || 0, icon: Zap, color: 'text-cyan-400', bg: 'bg-cyan-500/10' },
          { label: 'Approved (Total)', value: stats.approved || 0, icon: Check, color: 'text-green-400', bg: 'bg-green-500/10' },
          { label: 'Approved Today', value: stats.approved_today || 0, icon: BarChart3, color: 'text-purple-400', bg: 'bg-purple-500/10' },
          { label: 'Rejected', value: stats.rejected || 0, icon: X, color: 'text-red-400', bg: 'bg-red-500/10' },
        ].map(({ label, value, icon: Icon, color, bg }) => (
          <div key={label} className={`${bg} rounded-xl p-4 border border-white/5`}>
            <div className="flex items-center gap-2 mb-1">
              <Icon className={`w-4 h-4 ${color}`} />
              <span className="text-white/40 text-xs">{label}</span>
            </div>
            <span className={`text-2xl font-bold ${color}`}>{value}</span>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex bg-white/5 p-1 rounded-xl border border-white/10 mb-6 overflow-x-auto">
        {[
          { key: 'staging', label: 'Staging Queue', count: stagingTools.length, color: 'cyan' },
          { key: 'legacy', label: 'Legacy Review', count: pendingTools.length, color: 'yellow' },
          { key: 'scanning', label: 'Live AI Scans', count: liveScans.filter(s => s.status !== 'completed').length, color: 'purple' },
        ].map(({ key, label, count, color }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`px-5 py-2 rounded-lg transition-all flex items-center gap-2 whitespace-nowrap text-sm ${
              activeTab === key 
                ? `bg-${color}-500/20 text-${color}-400 border border-${color}-500/30` 
                : 'text-white/50 hover:text-white'
            }`}
          >
            {label}
            <span className="bg-white/10 px-2 rounded-md text-xs">{count}</span>
          </button>
        ))}
      </div>

      {loading && stagingTools.length === 0 && (
        <div className="flex items-center justify-center p-20">
          <Activity className="text-cyan-400 animate-spin w-12 h-12" />
        </div>
      )}

      <AnimatePresence mode="wait">
        {/* ===================== STAGING QUEUE TAB ===================== */}
        {activeTab === 'staging' && (
          <motion.div key="staging" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
            
            {/* Toolbar */}
            {stagingTools.length > 0 && (
              <div className="flex flex-wrap items-center gap-3 mb-6">
                {/* Select All */}
                <button onClick={selectAll}
                  className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 text-white/60 text-sm transition-colors">
                  <CheckSquare className="w-4 h-4" />
                  {selectedIds.size === filteredStagingTools().length ? 'Deselect All' : 'Select All'}
                </button>

                {/* Batch Actions */}
                {selectedIds.size > 0 && (
                  <>
                    <button onClick={() => handleBatchAction('approve')}
                      disabled={actionLoading === 'batch'}
                      className="flex items-center gap-2 px-4 py-2 bg-green-500/10 hover:bg-green-500/20 text-green-400 rounded-lg border border-green-500/30 text-sm font-bold transition-all">
                      <Check className="w-4 h-4" />
                      Approve {selectedIds.size} Selected
                    </button>
                    <button onClick={() => handleBatchAction('reject')}
                      disabled={actionLoading === 'batch'}
                      className="flex items-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg border border-red-500/30 text-sm font-bold transition-all">
                      <X className="w-4 h-4" />
                      Reject {selectedIds.size}
                    </button>
                  </>
                )}

                <div className="flex-1" />

                {/* Category Filter */}
                <div className="flex items-center gap-2">
                  <Filter className="w-4 h-4 text-white/30" />
                  <select value={filterCategory} onChange={e => setFilterCategory(e.target.value)}
                    className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white/80 outline-none focus:border-cyan-500/30">
                    <option value="">All Categories</option>
                    {CATEGORIES.map(cat => <option key={cat} value={cat}>{cat}</option>)}
                  </select>
                </div>
              </div>
            )}

            {/* Tool Cards */}
            <div className="grid grid-cols-1 gap-4">
              {filteredStagingTools().length === 0 ? (
                <div className="text-center p-20 bg-white/5 rounded-2xl border border-dashed border-white/10">
                  <Package className="w-12 h-12 text-white/20 mx-auto mb-4" />
                  <p className="text-white/40 mb-2">No tools waiting for review.</p>
                  <p className="text-white/20 text-sm">Run the batch processor to populate this queue.</p>
                </div>
              ) : (
                filteredStagingTools().map((tool) => {
                  const isExpanded = expandedId === tool.id;
                  const isEditing = editingId === tool.id;
                  const isSelected = selectedIds.has(tool.id);
                  const analysis = tool.analysis || {};

                  return (
                    <motion.div key={tool.id} layout
                      className={`bg-white/5 border rounded-2xl overflow-hidden transition-all ${
                        isSelected ? 'border-cyan-500/40 bg-cyan-500/5' : 'border-white/10'
                      }`}>
                      
                      {/* Main Row */}
                      <div className="p-5 flex flex-col md:flex-row gap-4 items-start">
                        {/* Checkbox */}
                        <button onClick={() => toggleSelect(tool.id)}
                          className={`mt-1 w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-all ${
                            isSelected ? 'bg-cyan-500 border-cyan-500' : 'border-white/20 hover:border-white/40'
                          }`}>
                          {isSelected && <Check className="w-3 h-3 text-white" />}
                        </button>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-2 flex-wrap">
                            <h3 className="text-lg font-bold text-white">{tool.tool_name}</h3>
                            <span className={`px-3 py-0.5 text-xs rounded-full border font-medium ${scoreBg(tool.trust_score)} ${scoreColor(tool.trust_score)}`}>
                              {Math.round(tool.trust_score || 0)}/100
                            </span>
                            <span className="px-2 py-0.5 bg-white/5 text-white/40 text-xs rounded-full border border-white/5">
                              {tool.category || analysis.job_to_be_done?.[0] || 'Uncategorized'}
                            </span>
                            <span className="text-white/20 text-xs">{tool.source}</span>
                          </div>
                          
                          <p className="text-white/50 text-sm line-clamp-2 mb-3">
                            {analysis.executive_summary || 'No summary available.'}
                          </p>

                          {/* Quick Info Chips */}
                          <div className="flex flex-wrap gap-2 text-xs">
                            {analysis.pricing && (
                              <span className="bg-white/5 px-2 py-1 rounded text-white/40 border border-white/5">
                                {analysis.pricing}
                              </span>
                            )}
                            {analysis.learning_curve && (
                              <span className="bg-white/5 px-2 py-1 rounded text-white/40 border border-white/5">
                                {analysis.learning_curve}
                              </span>
                            )}
                            {(analysis.pros || []).length > 0 && (
                              <span className="bg-green-500/5 px-2 py-1 rounded text-green-400/60 border border-green-500/10">
                                {analysis.pros.length} pros
                              </span>
                            )}
                            {(analysis.cons || []).length > 0 && (
                              <span className="bg-red-500/5 px-2 py-1 rounded text-red-400/60 border border-red-500/10">
                                {analysis.cons.length} cons
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-2 flex-shrink-0">
                          <button onClick={() => setExpandedId(isExpanded ? null : tool.id)}
                            className="p-2 hover:bg-white/10 rounded-lg text-white/30 hover:text-white transition-colors"
                            title="Expand details">
                            {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                          </button>
                          <button onClick={() => startEdit(tool)}
                            className="p-2 hover:bg-white/10 rounded-lg text-white/30 hover:text-cyan-400 transition-colors"
                            title="Edit before approve">
                            <Edit3 className="w-5 h-5" />
                          </button>
                          <button onClick={() => handleStagingAction(tool.id, 'approve')}
                            disabled={actionLoading === tool.id}
                            className="flex items-center gap-1.5 px-4 py-2 bg-green-500/10 hover:bg-green-500/20 text-green-400 rounded-xl border border-green-500/30 transition-all font-bold text-sm">
                            <Check className="w-4 h-4" /> Approve
                          </button>
                          <button onClick={() => handleStagingAction(tool.id, 'reject')}
                            disabled={actionLoading === tool.id}
                            className="flex items-center gap-1.5 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-xl border border-red-500/30 transition-all font-bold text-sm">
                            <X className="w-4 h-4" /> Reject
                          </button>
                        </div>
                      </div>

                      {/* Expanded Details */}
                      <AnimatePresence>
                        {isExpanded && (
                          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                            <div className="px-5 pb-5 pt-2 border-t border-white/5">
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {/* Metrics */}
                                {analysis.metrics && (
                                  <div className="bg-white/5 rounded-lg p-3 border border-white/5">
                                    <h4 className="text-white/40 text-xs mb-2 uppercase tracking-wider">Metrics</h4>
                                    <div className="grid grid-cols-2 gap-2 text-sm">
                                      {Object.entries(analysis.metrics).filter(([k]) => ['accuracy','speed','value','ease_of_use'].includes(k)).map(([key, val]) => (
                                        <div key={key} className="flex justify-between">
                                          <span className="text-white/40 capitalize">{key.replace(/_/g, ' ')}</span>
                                          <span className="text-white font-medium">{val}/5</span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Pros & Cons */}
                                <div className="bg-white/5 rounded-lg p-3 border border-white/5">
                                  <h4 className="text-white/40 text-xs mb-2 uppercase tracking-wider">Pros & Cons</h4>
                                  {(analysis.pros || []).map((pro, i) => (
                                    <p key={`pro-${i}`} className="text-green-400/70 text-sm mb-1">+ {pro}</p>
                                  ))}
                                  {(analysis.cons || []).map((con, i) => (
                                    <p key={`con-${i}`} className="text-red-400/70 text-sm mb-1">− {con}</p>
                                  ))}
                                </div>
                              </div>

                              {/* Use Cases */}
                              {(analysis.use_cases || []).length > 0 && (
                                <div className="mt-3 flex flex-wrap gap-2">
                                  {analysis.use_cases.map((uc, i) => (
                                    <span key={i} className="bg-purple-500/10 px-3 py-1 rounded-full text-purple-400 text-xs border border-purple-500/20">
                                      {uc}
                                    </span>
                                  ))}
                                </div>
                              )}

                              {/* Processing Log */}
                              {tool.processing_log && (
                                <div className="mt-3 bg-black/20 rounded-lg p-3 border border-white/5">
                                  <h4 className="text-white/30 text-xs mb-1 uppercase tracking-wider">Processing Log</h4>
                                  <p className="text-white/20 text-xs font-mono">{tool.processing_log}</p>
                                </div>
                              )}
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>

                      {/* Inline Edit Panel */}
                      <AnimatePresence>
                        {isEditing && (
                          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                            <div className="px-5 pb-5 pt-2 border-t border-cyan-500/20 bg-cyan-500/5">
                              <h4 className="text-cyan-400 text-xs uppercase tracking-wider mb-3 font-bold">Quick Edit</h4>
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {/* Trust Score */}
                                <div>
                                  <label className="text-white/40 text-xs block mb-1">Trust Score</label>
                                  <input type="number" min="10" max="100" value={editData.trust_score}
                                    onChange={e => setEditData({...editData, trust_score: Number(e.target.value)})}
                                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm outline-none focus:border-cyan-500/50" />
                                </div>
                                {/* Category */}
                                <div>
                                  <label className="text-white/40 text-xs block mb-1">Category</label>
                                  <select value={editData.category} onChange={e => setEditData({...editData, category: e.target.value})}
                                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm outline-none focus:border-cyan-500/50">
                                    {CATEGORIES.map(cat => <option key={cat} value={cat}>{cat}</option>)}
                                  </select>
                                </div>
                                {/* Actions */}
                                <div className="flex items-end gap-2">
                                  <button onClick={() => {
                                    handleStagingAction(tool.id, 'edit', editData).then(() => {
                                      handleStagingAction(tool.id, 'approve', editData);
                                    });
                                  }}
                                    className="flex-1 px-4 py-2 bg-green-500/10 hover:bg-green-500/20 text-green-400 rounded-lg border border-green-500/30 text-sm font-bold transition-all">
                                    Save & Approve
                                  </button>
                                  <button onClick={() => setEditingId(null)}
                                    className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white/40 rounded-lg border border-white/10 text-sm transition-all">
                                    Cancel
                                  </button>
                                </div>
                              </div>
                              {/* Summary Edit */}
                              <div className="mt-3">
                                <label className="text-white/40 text-xs block mb-1">Executive Summary</label>
                                <textarea value={editData.executive_summary}
                                  onChange={e => setEditData({...editData, executive_summary: e.target.value})}
                                  rows={2}
                                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm outline-none focus:border-cyan-500/50 resize-none" />
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  );
                })
              )}
            </div>
          </motion.div>
        )}

        {/* ===================== LEGACY REVIEW TAB ===================== */}
        {activeTab === 'legacy' && (
          <motion.div key="legacy" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
            className="grid grid-cols-1 gap-6">
            {pendingTools.length === 0 ? (
              <div className="text-center p-20 bg-white/5 rounded-2xl border border-dashed border-white/10">
                <Clock className="w-12 h-12 text-white/20 mx-auto mb-4" />
                <p className="text-white/40">No tools waiting for legacy review.</p>
              </div>
            ) : (
              pendingTools.map((tool) => (
                <div key={tool.tool_name} className="bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col md:flex-row gap-6 items-start">
                  <div className="flex-1 w-full">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-bold text-white uppercase tracking-wider">{tool.tool_name}</h3>
                      <span className="px-3 py-1 bg-cyan-500/10 text-cyan-400 text-xs rounded-full border border-cyan-500/20">
                        {tool.trust_score}/100 Trust
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
                    <button onClick={() => handleLegacyAction(tool.tool_name, 'approve')}
                      className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-green-500/10 hover:bg-green-500/20 text-green-400 rounded-xl border border-green-500/30 transition-all font-bold">
                      <Check className="w-5 h-5" /> APPROVE
                    </button>
                    <button onClick={() => handleLegacyAction(tool.tool_name, 'reject')}
                      className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-xl border border-red-500/30 transition-all font-bold">
                      <X className="w-5 h-5" /> REJECT
                    </button>
                  </div>
                </div>
              ))
            )}
          </motion.div>
        )}

        {/* ===================== LIVE SCANS TAB ===================== */}
        {activeTab === 'scanning' && (
          <motion.div key="scanning" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
            className="grid grid-cols-1 gap-4">
            {liveScans.length === 0 ? (
              <div className="text-center p-20 bg-white/5 rounded-2xl border border-dashed border-white/10">
                <Search className="w-12 h-12 text-white/20 mx-auto mb-4" />
                <p className="text-white/40">No active AI scans right now.</p>
              </div>
            ) : (
              liveScans.map((task) => (
                <div key={task.task_id} className="bg-white/5 border border-white/10 rounded-2xl p-5 flex items-center justify-between group overflow-hidden relative">
                  {task.status === 'scanning' && (
                    <motion.div className="absolute inset-0 bg-purple-500/5"
                      animate={{ opacity: [0, 1, 0] }} transition={{ duration: 2, repeat: Infinity }} />
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
                      }`}>{task.status.toUpperCase()}</span>
                      {task.error_message && (
                        <p className="text-[10px] text-red-400/60 mt-1 max-w-[200px] truncate">{task.error_message}</p>
                      )}
                    </div>
                    <a href={task.url} target="_blank" rel="noopener noreferrer"
                      className="p-2 hover:bg-white/10 rounded-lg text-white/30 hover:text-white transition-colors">
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

export default ReviewQueue;
