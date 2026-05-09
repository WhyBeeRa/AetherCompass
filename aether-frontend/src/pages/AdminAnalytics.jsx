import React, { useState, useEffect } from 'react';
import { BarChart3, Search, Clock, CheckCircle2, XCircle, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { apiFetch } from '../api';
import { useTranslation } from 'react-i18next';

const AdminAnalytics = ({ setAppError }) => {
    const { t } = useTranslation();
    const { currentUser, isAdmin } = useAuth();
    const [queries, setQueries] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

    useEffect(() => {
        const fetchAnalytics = async () => {
            if (!isLocal && !isAdmin) return;
            try {
                setIsLoading(true);
                const token = isLocal ? "dev-admin-token" : await currentUser.getIdToken();
                const res = await apiFetch('/admin/analytics', {
                    headers: { 
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                if (!res.ok) throw new Error("Failed to fetch analytics");
                const data = await res.json();
                setQueries(data);
            } catch (err) {
                console.error(err);
                if (setAppError) setAppError(t('admin.analytics.error_fetch'));
            } finally {
                setIsLoading(false);
            }
        };

        fetchAnalytics();
    }, [isAdmin, currentUser, setAppError, isLocal, t]);

    const matchCount = queries.filter(q => q.has_match).length;
    const missCount = queries.length - matchCount;
    const matchRate = queries.length > 0 ? (matchCount / queries.length * 100).toFixed(1) : 0;

    return (
        <>
            <div className="w-full animate-in fade-in slide-in-from-bottom-5 duration-700">
                <div className="w-full">
                    
                    <div className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6 text-left">
                        <div>
                            <div className="inline-flex items-center justify-center p-3 bg-indigo-500/10 rounded-2xl border border-indigo-500/20 mb-6">
                                <BarChart3 className="w-8 h-8 text-indigo-400" />
                            </div>
                            <h1 className="text-4xl font-bold text-white mb-4">{t('admin.analytics.title')}</h1>
                            <p className="text-white/60">{t('admin.analytics.subtitle')}</p>
                        </div>
                        
                        <div className="flex gap-4">
                            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 min-w-[120px]">
                                <div className="text-2xl font-bold text-emerald-400">{matchRate}%</div>
                                <div className="text-[10px] text-white/40 uppercase tracking-widest">{t('admin.analytics.match_rate')}</div>
                            </div>
                            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 min-w-[120px]">
                                <div className="text-2xl font-bold text-white">{queries.length}</div>
                                <div className="text-[10px] text-white/40 uppercase tracking-widest">{t('admin.analytics.total_searches')}</div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-[#040914]/80 border border-white/10 rounded-3xl backdrop-blur-xl overflow-hidden shadow-2xl">
                        <div className="p-6 border-b border-white/5 text-left">
                            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                <Clock className="w-5 h-5 text-cyan-400" />
                                {t('admin.analytics.recent_queries')}
                            </h2>
                        </div>

                        <div className="overflow-x-auto">
                            {isLoading ? (
                                <div className="p-12 text-center text-white/50 animate-pulse">{t('admin.analytics.loading')}</div>
                            ) : queries.length === 0 ? (
                                <div className="p-12 text-center text-white/50">{t('admin.analytics.no_data')}</div>
                            ) : (
                                <table className="w-full text-left text-sm">
                                    <thead>
                                        <tr className="bg-white/[0.02] border-b border-white/5 text-white/40 uppercase tracking-widest text-[0.65rem] font-medium">
                                            <th className="px-6 py-4">{t('admin.analytics.col_query')}</th>
                                            <th className="px-6 py-4">{t('admin.analytics.col_time')}</th>
                                            <th className="px-6 py-4 text-center">{t('admin.analytics.col_status')}</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-white/5">
                                        {queries.map((q) => (
                                            <tr key={q.id} className="hover:bg-white/[0.02] transition-colors">
                                                <td className="px-6 py-4">
                                                    <div className="flex items-center gap-3">
                                                        <Search className="w-3 h-3 text-white/20" />
                                                        <span className="text-white font-medium">{q.query_text}</span>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 text-white/40 text-xs">
                                                    {new Date(q.timestamp).toLocaleString('en-US')}
                                                </td>
                                                <td className="px-6 py-4">
                                                    <div className="flex justify-center">
                                                        {q.has_match ? (
                                                            <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold uppercase tracking-tight">
                                                                <CheckCircle2 className="w-3 h-3" /> Match
                                                            </div>
                                                        ) : (
                                                            <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-red-500/10 text-red-400 border border-red-500/20 text-[10px] font-bold uppercase tracking-tight">
                                                                <XCircle className="w-3 h-3" /> Miss
                                                            </div>
                                                        )}
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
        </>
    );
};

export default AdminAnalytics;
