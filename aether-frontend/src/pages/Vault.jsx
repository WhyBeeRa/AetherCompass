import React, { useState, useEffect } from 'react';
import { Shield, Clock, TrendingUp, CheckCircle, Search, Layers, Server, AlertCircle, Trash2, Loader2, Eye, EyeOff, Edit2, Check, Activity } from 'lucide-react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import LiveMonitorWidget from '../components/LiveMonitorWidget';
import { apiFetch } from '../api';
import { useTranslation } from 'react-i18next';

// Search Analytics Logger Component
const SearchLogger = ({ query }) => {
    useEffect(() => {
        if (!query || query.trim().length < 2) return;
        
        const timeoutId = setTimeout(() => {
            apiFetch(`/vault/search?q=${encodeURIComponent(query)}`)
                .catch(err => console.warn("Analytics log failed", err));
        }, 1500);

        return () => clearTimeout(timeoutId);
    }, [query]);
    
    return null;
};

const Vault = ({ setAppError }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const { t, i18n } = useTranslation();

    const queryParams = new URLSearchParams(location.search);
    const initialQuery = queryParams.get("q") || "";

    const { currentUser, isAdmin } = useAuth();
    const [tools, setTools] = useState([]);
    const [stats, setStats] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState(initialQuery);
    const [confirmDelete, setConfirmDelete] = useState(null);
    const [isDeleting, setIsDeleting] = useState(false);
    const [editingPricing, setEditingPricing] = useState(null);
    const [newPricingValue, setNewPricingValue] = useState("");
    const [isUpdating, setIsUpdating] = useState(false);

    useEffect(() => {
        const fetchVaultData = async () => {
            try {
                setIsLoading(true);
                const statsRes = await apiFetch('/vault/stats');
                if (!statsRes.ok) throw new Error("Failed to fetch vault stats");
                const statsData = await statsRes.json();
                setStats(statsData);

                const toolsRes = await apiFetch('/vault/search?q=');
                if (!toolsRes.ok) throw new Error("Failed to fetch vault data");
                const toolsData = await toolsRes.json();
                setTools(toolsData);
            } catch (err) {
                console.error("Vault fetch error:", err);
                if (setAppError) setAppError(t('vault.error_load'));
            } finally {
                setIsLoading(false);
            }
        };

        fetchVaultData();
    }, [setAppError, t]);

    const handleToggleStatus = async (toolName, currentStatus) => {
        try {
            setIsUpdating(true);
            const token = await currentUser.getIdToken();
            const res = await apiFetch(`/admin/vault/toggle/${encodeURIComponent(toolName.toLowerCase())}?active=${!currentStatus}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw new Error("Toggle failed");
            
            setTools(prev => prev.map(t => t.tool_name === toolName ? { ...t, is_active: !currentStatus } : t));
        } catch (err) {
            if (setAppError) setAppError(t('vault.error_toggle'));
        } finally {
            setIsUpdating(false);
        }
    };

    const handleUpdatePricing = async (toolName) => {
        try {
            setIsUpdating(true);
            const token = await currentUser.getIdToken();
            const res = await apiFetch(`/admin/vault/pricing/${encodeURIComponent(toolName.toLowerCase())}?pricing=${encodeURIComponent(newPricingValue)}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw new Error("Pricing update failed");
            
            setTools(prev => prev.map(t => t.tool_name === toolName ? { 
                ...t, 
                analysis: { ...t.analysis, metrics: { ...t.analysis.metrics, pricing: newPricingValue } } 
            } : t));
            setEditingPricing(null);
        } catch (err) {
            if (setAppError) setAppError(t('vault.error_pricing'));
        } finally {
            setIsUpdating(false);
        }
    };

    const handleDelete = async (toolName) => {
        if (!window.confirm(t('vault.confirm_delete_tool', { name: toolName }))) {
            return;
        }
        
        try {
            setIsDeleting(true);
            const token = await currentUser.getIdToken();
            const res = await apiFetch(`/admin/vault/tool/${encodeURIComponent(toolName.toLowerCase())}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!res.ok) {
                const errorData = await res.json();
                throw new Error(errorData.detail || t('vault.error_delete_failed'));
            }

            setTools(prev => prev.filter(t => t.tool_name !== toolName));
            setConfirmDelete(null);
        } catch (err) {
            if (setAppError) setAppError(err.message || t('vault.error_delete'));
        } finally {
            setIsDeleting(false);
        }
    };

    const categoryKeywords = {
        'code development': ['code', 'dev', 'react', 'tailwind', 'program', 'cursor', 'v0', 'github'],
        'image creation & design': ['image', 'design', 'midjourney', 'art', 'creative', 'ui', 'dall-e', 'luma'],
        'writing & text': ['text', 'write', 'content', 'chat', 'perplexity', 'claude', 'knowledge', 'gpt', 'model'],
        'video editing': ['video', 'film', 'edit', 'heygen', 'runway'],
        'voiceover & audio': ['audio', 'music', 'vocal', 'sound', 'suno', 'elevenlabs'],
        'marketing & seo': ['marketing', 'seo', 'sales', 'brand', 'campaign'],
        'investor decks': ['present', 'gamma', 'slide', 'deck', 'pitch'],
        'enterprise tools': ['enterprise', 'automat', 'zapier', 'workflow', 'make', 'task', 'api'],
    };

    const filteredTools = tools.filter(tool => {
        if (!searchQuery.trim()) return true;

        const qLower = searchQuery.toLowerCase().trim();
        const keywords = categoryKeywords[qLower];

        if (keywords) {
            const intents = tool.analysis?.intents_mapped || [];
            const jobs = tool.analysis?.job_to_be_done || [];
            const text_corpus = (
                tool.tool_name + " " +
                intents.map(i => i.intent_description || "").join(" ") + " " +
                jobs.join(" ")
            ).toLowerCase();
            return keywords.some(k => text_corpus.includes(k));
        }

        return tool.tool_name.toLowerCase().includes(qLower) ||
            tool.analysis?.intents_mapped?.some(intent => (intent.intent_description || "").toLowerCase().includes(qLower));
    });

    const dir = 'ltr';

    return (
        <div className="w-full relative flex justify-center pb-24 px-4 sm:px-6 lg:px-8 mt-12 animate-in fade-in duration-700">
            <div className="w-full max-w-5xl">

                {/* Header Section */}
                <div className="mb-12 text-center md:text-left">
                    <div className="inline-flex items-center justify-center p-3 bg-cyan-500/10 rounded-2xl border border-cyan-500/20 mb-6 drop-shadow-[0_0_15px_rgba(6,182,212,0.15)]">
                        <Server className="w-8 h-8 text-cyan-400" />
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold text-white mb-6 tracking-tight">
                        {t('vault.title')} <span className="text-transparent bg-clip-text bg-gradient-to-l from-cyan-400 to-blue-500 font-light mx-2">the-vault</span>
                    </h1>
                    <p className="text-lg text-white/60 max-w-2xl text-center md:text-left">
                        {t('vault.subtitle')}
                    </p>
                </div>

                {/* Live Monitoring Widget */}
                <LiveMonitorWidget />

                {/* Stats Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
                    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md relative overflow-hidden group">
                        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                        <Layers className="w-5 h-5 text-cyan-400 mb-4" />
                        <div className="text-3xl font-bold text-white mb-1">{stats?.verified_tools_count || 0}</div>
                        <div className="text-xs text-white/50 uppercase tracking-widest font-medium">{t('vault.verified_tools')}</div>
                    </div>

                    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md relative overflow-hidden group">
                        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                        <Shield className="w-5 h-5 text-blue-400 mb-4" />
                        <div className="text-3xl font-bold text-white mb-1">{stats?.average_trust_score?.toFixed(1) || "0.0"}</div>
                        <div className="text-xs text-white/50 uppercase tracking-widest font-medium">{t('vault.avg_trust')}</div>
                    </div>

                    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md relative overflow-hidden group">
                        <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                        <CheckCircle className="w-5 h-5 text-indigo-400 mb-4" />
                        <div className="text-3xl font-bold text-white mb-1">{stats?.total_intents_mapped || 0}</div>
                        <div className="text-xs text-white/50 uppercase tracking-widest font-medium">{t('vault.intents_mapped')}</div>
                    </div>

                    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md relative overflow-hidden group">
                        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                        <Clock className="w-5 h-5 text-emerald-400 mb-4" />
                        <div className="text-lg font-bold text-white mb-1 mt-2 tracking-wider">
                            {stats?.last_scan_date ? new Date(stats.last_scan_date).toLocaleDateString('en-US') : "N/A"}
                        </div>
                        <div className="text-xs text-white/50 uppercase tracking-widest font-medium mt-2">{t('vault.last_scan')}</div>
                    </div>
                </div>

                {/* Data Table Section */}
                <div className="bg-[#040914]/80 border border-white/10 rounded-3xl backdrop-blur-xl overflow-hidden shadow-2xl">
                    <div className="p-6 border-b border-white/5 flex flex-col md:flex-row items-center justify-between gap-4">
                        <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.6)] animate-pulse" />
                            {t('vault.live_database')}
                        </h2>
                        <div className="relative w-full md:w-64">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
                            <input
                                type="text"
                                placeholder={t('vault.search_placeholder')}
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-lg py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-cyan-500/50 focus:bg-white/10 transition-all text-white placeholder-white/30"
                            />
                        </div>
                    </div>
                    
                    {/* Search Analytics Logger (Background) */}
                    <SearchLogger query={searchQuery} />
                    
                    {isAdmin && (
                        <div className="p-4 bg-red-500/5 border-b border-red-500/10 flex items-center justify-between">
                            <div className="flex items-center gap-2 text-red-400 text-xs font-bold uppercase tracking-wider">
                                <Shield className="w-4 h-4" />
                                {t('vault.admin_panel')}
                            </div>
                            <button 
                                onClick={() => {
                                    if(window.confirm(t('vault.confirm_delete_all'))) {
                                        filteredTools.forEach(t => handleDelete(t.tool_name));
                                    }
                                }}
                                className="px-4 py-1.5 bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg text-xs font-bold hover:bg-red-500/30 transition-all"
                            >
                                {t('vault.delete_selected', { count: filteredTools.length })}
                            </button>
                        </div>
                    )}

                    <div className="overflow-x-auto">
                        {isLoading ? (
                            <div className="p-12 text-center text-white/50 animate-pulse text-sm">{t('vault.loading')}</div>
                        ) : filteredTools.length === 0 ? (
                            <div className="p-12 text-center text-white/50 text-sm">{t('vault.no_results')}</div>
                        ) : (
                            <table className="w-full text-sm text-left">
                                <thead>
                                    <tr className="bg-white/[0.02] border-b border-white/5 text-white/40 uppercase tracking-widest text-[0.65rem] font-medium">
                                        {isAdmin && <th className="px-6 py-4 font-medium">{t('vault.col_manage')}</th>}
                                        <th className="px-6 py-4 font-medium">{t('vault.col_tool_name')}</th>
                                        <th className="px-6 py-4 font-medium">{t('vault.col_trust_score')}</th>
                                        <th className="px-6 py-4 font-medium hidden md:table-cell">{t('vault.col_intents')}</th>
                                        <th className="px-6 py-4 font-medium hidden sm:table-cell">{t('vault.col_pricing')}</th>
                                        <th className="px-6 py-4 font-medium lg:text-center">{t('vault.col_status')}</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    {filteredTools.map((tool, idx) => (
                                        <tr key={idx} className={`hover:bg-white/[0.02] transition-colors group cursor-pointer ${!tool.is_active ? 'opacity-50' : ''}`} onClick={() => navigate(`/tool/${tool.tool_name.toLowerCase().replace(/\s+/g, '-')}`)}>
                                            {isAdmin && (
                                                <td className="px-6 py-4" onClick={(e) => e.stopPropagation()}>
                                                    <div className="flex items-center gap-2">
                                                        <button 
                                                            onClick={() => handleToggleStatus(tool.tool_name, tool.is_active)}
                                                            className={`p-2 rounded-lg transition-all ${tool.is_active ? 'text-emerald-400 hover:bg-emerald-400/10' : 'text-red-400 hover:bg-red-400/10'}`}
                                                            title={tool.is_active ? t('vault.toggle_active_title') : t('vault.toggle_inactive_title')}
                                                        >
                                                            {tool.is_active ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
                                                        </button>

                                                        {confirmDelete === tool.tool_name ? (
                                                            <div className="flex items-center gap-2">
                                                                <button 
                                                                    onClick={() => handleDelete(tool.tool_name)}
                                                                    disabled={isDeleting}
                                                                    className="px-3 py-1 bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg text-xs font-bold hover:bg-red-500/30 transition-all flex items-center gap-1"
                                                                >
                                                                    {isDeleting ? <Loader2 className="w-3 h-3 animate-spin" /> : t('vault.yes')}
                                                                </button>
                                                                <button 
                                                                    onClick={() => setConfirmDelete(null)}
                                                                    className="text-white/40 hover:text-white transition-colors text-xs"
                                                                >
                                                                    {t('vault.no')}
                                                                </button>
                                                            </div>
                                                        ) : (
                                                            <button 
                                                                onClick={() => setConfirmDelete(tool.tool_name)}
                                                                className="p-2 text-white/30 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-all"
                                                                title={t('vault.delete_title')}
                                                            >
                                                                <Trash2 className="w-3.5 h-3.5" />
                                                            </button>
                                                        )}
                                                    </div>
                                                </td>
                                            )}
                                            <td className="px-6 py-4 font-medium text-white flex items-center gap-3">
                                                <div className="flex flex-col">
                                                    <Link to={`/tool/${tool.tool_name.toLowerCase().replace(/\s+/g, '-')}`} className="hover:text-cyan-400 transition-colors">
                                                        {tool.tool_name.charAt(0).toUpperCase() + tool.tool_name.slice(1)}
                                                    </Link>
                                                    {!tool.is_active && <span className="text-[10px] text-red-400 uppercase font-bold">{t('vault.inactive')}</span>}
                                                </div>
                                                {tool.trust_score >= 90 && (
                                                    <span className="px-2 py-0.5 rounded text-[0.6rem] uppercase tracking-wider bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                                                        {t('vault.elite')}
                                                    </span>
                                                )}
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-2">
                                                    <div className={`font-bold ${tool.trust_score >= 85 ? "text-emerald-400" :
                                                        tool.trust_score >= 70 ? "text-amber-400" : "text-red-400"
                                                        }`}>
                                                        {tool.trust_score.toFixed(1)}
                                                    </div>
                                                    <div className="w-16 h-1.5 bg-white/10 rounded-full overflow-hidden hidden sm:block">
                                                        <div
                                                            className={`h-full rounded-full ${tool.trust_score >= 85 ? "bg-emerald-400" :
                                                                tool.trust_score >= 70 ? "bg-amber-400" : "bg-red-400"
                                                                }`}
                                                            style={{ width: `${tool.trust_score}%` }}
                                                        />
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 hidden md:table-cell text-white/60">
                                                <div className="flex flex-wrap gap-1">
                                                    {tool.analysis?.intents_mapped?.slice(0, 2).map((intent, i) => (
                                                        <span key={i} className="text-xs bg-white/5 px-2 py-1 rounded truncate max-w-[150px]" title={intent.intent_description}>
                                                            {intent.intent_description}
                                                        </span>
                                                    ))}
                                                    {tool.analysis?.intents_mapped?.length > 2 && (
                                                        <span className="text-xs text-white/30 px-1 py-1">+{tool.analysis.intents_mapped.length - 2}</span>
                                                    )}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 hidden sm:table-cell text-white/50 text-xs">
                                                {editingPricing?.name === tool.tool_name ? (
                                                    <div className="flex items-center gap-2" onClick={e => e.stopPropagation()}>
                                                        <input 
                                                            type="text" 
                                                            value={newPricingValue}
                                                            onChange={e => setNewPricingValue(e.target.value)}
                                                            className="bg-white/10 border border-white/20 rounded px-2 py-1 w-24 text-white text-xs"
                                                            autoFocus
                                                        />
                                                        <button 
                                                            onClick={() => handleUpdatePricing(tool.tool_name)}
                                                            className="p-1 hover:text-emerald-400"
                                                        >
                                                            <Check className="w-3 h-3" />
                                                        </button>
                                                    </div>
                                                ) : (
                                                    <div className="flex items-center gap-2">
                                                        <span>{tool.analysis?.metrics?.pricing || "N/A"}</span>
                                                        {isAdmin && (
                                                            <button 
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    setEditingPricing({ name: tool.tool_name });
                                                                    setNewPricingValue(tool.analysis?.metrics?.pricing || "");
                                                                }}
                                                                className="opacity-0 group-hover:opacity-100 p-1 hover:text-cyan-400 transition-all"
                                                                title={t('vault.edit_pricing_title')}
                                                            >
                                                                <Edit2 className="w-3 h-3" />
                                                            </button>
                                                        )}
                                                    </div>
                                                )}
                                            </td>
                                            <td className="px-6 py-4 lg:text-center">
                                                <div className="inline-flex items-center gap-1.5">
                                                    {tool.trust_score >= 70 ? (
                                                        <Shield className="w-4 h-4 text-cyan-400" />
                                                    ) : (
                                                        <AlertCircle className="w-4 h-4 text-red-400" />
                                                    )}
                                                    <span className="text-xs text-white/40">
                                                        {new Date(tool.audit_log?.timestamp || Date.now()).toLocaleDateString('en-US')}
                                                    </span>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
};

export default Vault;
