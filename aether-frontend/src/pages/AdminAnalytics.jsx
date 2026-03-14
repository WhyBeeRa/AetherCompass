import React, { useState, useEffect } from 'react';
import { BarChart3, Search, Clock, CheckCircle2, XCircle, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';

const AdminAnalytics = ({ setAppError }) => {
    const { currentUser, isAdmin } = useAuth();
    const [queries, setQueries] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchAnalytics = async () => {
            if (!isAdmin) return;
            try {
                setIsLoading(true);
                const token = await currentUser.getIdToken();
                const res = await fetch('http://127.0.0.1:8000/admin/analytics', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!res.ok) throw new Error("Failed to fetch analytics");
                const data = await res.json();
                setQueries(data);
            } catch (err) {
                console.error(err);
                if (setAppError) setAppError("שגיאה בטעינת אנליטיקות.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchAnalytics();
    }, [isAdmin, currentUser, setAppError]);

    if (!isAdmin) {
        return (
            <div className="min-h-screen flex items-center justify-center text-white">
                <div className="text-center">
                    <h1 className="text-2xl font-bold mb-4">גישה למורשים בלבד</h1>
                    <Link to="/" className="text-cyan-400 hover:underline flex items-center justify-center gap-2">
                        <ArrowLeft className="w-4 h-4" /> חזרה לדף הבית
                    </Link>
                </div>
            </div>
        );
    }

    const matchCount = queries.filter(q => q.has_match).length;
    const missCount = queries.length - matchCount;
    const matchRate = queries.length > 0 ? (matchCount / queries.length * 100).toFixed(1) : 0;

    return (
        <div className="w-full flex justify-center pb-24 px-4 sm:px-6 lg:px-8 mt-12 animate-in fade-in duration-700">
            <div className="w-full max-w-5xl">
                
                <div className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6 text-right">
                    <div>
                        <div className="inline-flex items-center justify-center p-3 bg-indigo-500/10 rounded-2xl border border-indigo-500/20 mb-6">
                            <BarChart3 className="w-8 h-8 text-indigo-400" />
                        </div>
                        <h1 className="text-4xl font-bold text-white mb-4">Intent Analytics</h1>
                        <p className="text-white/60">מה המשתמשים באמת מחפשים? נתונים בזמן אמת על כוונות החיפוש.</p>
                    </div>
                    
                    <div className="flex gap-4">
                        <div className="bg-white/5 border border-white/10 rounded-2xl p-4 min-w-[120px]">
                            <div className="text-2xl font-bold text-emerald-400">{matchRate}%</div>
                            <div className="text-[10px] text-white/40 uppercase tracking-widest">Match Rate</div>
                        </div>
                        <div className="bg-white/5 border border-white/10 rounded-2xl p-4 min-w-[120px]">
                            <div className="text-2xl font-bold text-white">{queries.length}</div>
                            <div className="text-[10px] text-white/40 uppercase tracking-widest">Total Searches</div>
                        </div>
                    </div>
                </div>

                <div className="bg-[#040914]/80 border border-white/10 rounded-3xl backdrop-blur-xl overflow-hidden shadow-2xl">
                    <div className="p-6 border-b border-white/5">
                        <h2 className="text-xl font-bold text-white flex items-center gap-2">
                            <Clock className="w-5 h-5 text-cyan-400" />
                            Recent Queries
                        </h2>
                    </div>

                    <div className="overflow-x-auto">
                        {isLoading ? (
                            <div className="p-12 text-center text-white/50 animate-pulse">טוען נתונים...</div>
                        ) : queries.length === 0 ? (
                            <div className="p-12 text-center text-white/50">אין נתוני חיפוש עדיין.</div>
                        ) : (
                            <table className="w-full text-right text-sm">
                                <thead>
                                    <tr className="bg-white/[0.02] border-b border-white/5 text-white/40 uppercase tracking-widest text-[0.65rem] font-medium">
                                        <th className="px-6 py-4">פרומפט / חיפוש</th>
                                        <th className="px-6 py-4">זמן</th>
                                        <th className="px-6 py-4 text-center">סטטוס</th>
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
                                                {new Date(q.timestamp).toLocaleString('he-IL')}
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

                <div className="mt-8 flex justify-center">
                    <Link to="/vault" className="text-white/40 hover:text-white transition-colors text-sm flex items-center gap-2">
                        <ArrowLeft className="w-4 h-4" /> חזרה לכספת
                    </Link>
                </div>

            </div>
        </div>
    );
};

export default AdminAnalytics;
