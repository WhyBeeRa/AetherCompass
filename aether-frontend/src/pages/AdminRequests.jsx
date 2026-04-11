import React, { useState, useEffect } from 'react';
import { ShieldCheck, XCircle, Clock, ExternalLink, ArrowLeft, RefreshCw, Trash2, CheckCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { apiFetch } from '../api';

const AdminRequests = ({ setAppError }) => {
    const { currentUser, isAdmin } = useAuth();
    const [pending, setPending] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(null);

    const fetchPending = async () => {
        if (!isAdmin) return;
        try {
            setIsLoading(true);
            const token = await currentUser.getIdToken();
            const res = await apiFetch('/admin/pending', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setPending(data);
            }
        } catch (err) {
            console.error(err);
            if (setAppError) setAppError("נכשל בטעינת בקשות ממתינות.");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchPending();
    }, [isAdmin, currentUser]);

    const handleAction = async (toolName, action) => {
        setActionLoading(toolName);
        try {
            const token = await currentUser.getIdToken();
            const endpoint = action === 'approve' ? '/admin/approve' : '/admin/reject';
            const res = await apiFetch(`${endpoint}?tool_name=${encodeURIComponent(toolName)}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (res.ok) {
                // Remove from local state
                setPending(prev => prev.filter(p => p.tool_name !== toolName));
            } else {
                throw new Error("Action failed");
            }
        } catch (err) {
            console.error(err);
            alert("שגיאה בביצוע הפעולה.");
        } finally {
            setActionLoading(null);
        }
    };

    if (!isAdmin) return <div className="text-white text-center mt-20">Access Denied.</div>;

    return (
        <div className="w-full max-w-6xl mx-auto px-4 py-12 pt-24 min-h-screen text-slate-200" dir="ltr">
            <div className="flex items-center justify-between mb-12">
                <div className="text-left">
                    <h1 className="text-3xl font-black italic text-white flex items-center gap-3">
                        <ShieldCheck className="w-8 h-8 text-cyan-400 font-normal" />
                        COMMUNITY REQUEST CENTER
                    </h1>
                    <p className="text-white/40 mt-1 uppercase text-[10px] tracking-widest font-black">Verify and deploy new AI tools scouted by the community</p>
                </div>
                <button 
                   onClick={fetchPending}
                   className="p-3 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/10 transition-all text-white/60"
                >
                    <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {isLoading ? (
                    [1,2,3].map(i => (
                        <div key={i} className="h-64 rounded-3xl bg-white/5 border border-white/10 animate-pulse" />
                    ))
                ) : pending.length === 0 ? (
                    <div className="col-span-full py-20 bg-white/[0.02] border border-dashed border-white/10 rounded-3xl text-center">
                        <CheckCircle className="w-12 h-12 text-emerald-500/20 mx-auto mb-4" />
                        <h3 className="text-white/40 font-bold italic uppercase tracking-wider">Queue is clear. No pending tools found.</h3>
                    </div>
                ) : (
                    pending.map((item) => (
                        <div key={item.id} className="group relative bg-[#0a1120] border border-white/10 rounded-3xl overflow-hidden hover:border-cyan-500/50 transition-all duration-500">
                            <div className="p-6 space-y-4">
                                <div className="flex items-start justify-between">
                                    <div className="text-left">
                                        <div className="text-[10px] font-black text-cyan-400/80 uppercase tracking-widest mb-1">{item.analysis.metrics.pricing}</div>
                                        <h3 className="text-xl font-bold text-white tracking-tight italic">{item.tool_name}</h3>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-lg font-black text-white">{item.trust_score}</div>
                                        <div className="text-[10px] text-white/40 uppercase font-black">Score</div>
                                    </div>
                                </div>

                                <div className="p-4 bg-white/5 border border-white/5 rounded-2xl text-xs text-white/60 leading-relaxed italic">
                                    "{item.analysis.executive_summary}"
                                </div>

                                <div className="flex items-center justify-between pt-4 border-t border-white/5">
                                    <div className="flex items-center gap-1.5 text-white/40 text-[10px] uppercase font-bold">
                                        <Clock className="w-3 h-3" />
                                        {new Date(item.last_updated).toLocaleDateString()}
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-3 pt-2">
                                     <button 
                                        disabled={actionLoading === item.tool_name}
                                        onClick={() => handleAction(item.tool_name, 'approve')}
                                        className="py-3 bg-emerald-500 text-black font-black italic rounded-2xl text-xs hover:bg-emerald-400 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                                    >
                                        <CheckCircle className="w-4 h-4" /> APPROVE
                                    </button>
                                    <button 
                                        disabled={actionLoading === item.tool_name}
                                        onClick={() => handleAction(item.tool_name, 'reject')}
                                        className="py-3 bg-white/5 border border-white/10 text-white font-black italic rounded-2xl text-xs hover:bg-rose-500/20 hover:text-rose-400 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                                    >
                                        <Trash2 className="w-4 h-4" /> REJECT
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))
                )
                }
            </div>

            <div className="mt-12 text-center text-white/20 text-[10px] uppercase font-bold tracking-[0.2em]">
                END OF AUDIT QUEUE
            </div>
        </div>
    );
};

export default AdminRequests;
