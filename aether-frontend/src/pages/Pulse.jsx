import React from 'react';
import { Activity, Zap, Shield, BarChart3, Clock, AlertTriangle, TrendingUp, Cpu } from 'lucide-react';

export default function Pulse() {
    // Mock data for the dashboard
    const metrics = [
        { name: 'OpenAI (GPT-4o)', latency: 850, uptime: '99.98%', load: 'Medium', status: 'stable' },
        { name: 'Anthropic (Claude 3.5)', latency: 1120, uptime: '99.95%', load: 'High', status: 'warning' },
        { name: 'Google (Gemini 1.5)', latency: 640, uptime: '99.99%', load: 'Low', status: 'stable' },
        { name: 'Mistral (Large)', latency: 910, uptime: '99.90%', load: 'Medium', status: 'stable' }
    ];

    return (
        <div className="w-full min-h-screen pt-24 pb-24 rtl animate-in fade-in duration-700 bg-black text-white" dir="rtl">
            <main className="max-w-7xl mx-auto px-6">
                
                {/* Header */}
                <div className="flex flex-col md:flex-row justify-between items-end gap-6 mb-12">
                    <div>
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 bg-emerald-500 rounded-lg animate-pulse">
                                <Activity className="w-6 h-6 text-black" />
                            </div>
                            <span className="text-emerald-400 font-black uppercase tracking-tighter text-sm">
                                Live Health Dashboard
                            </span>
                        </div>
                        <h1 className="text-4xl md:text-5xl font-black tracking-tight mb-2">
                            the <span className="text-emerald-500">Pulse</span>
                        </h1>
                        <p className="text-white/50 font-medium">
                            עקוב אחרי ה-Latency, הדיוק וה-Uptime של מנועי ה-AI המובילים בזמן אמת.
                        </p>
                    </div>
                    <div className="text-left font-mono text-emerald-500/50 text-xs">
                        LAST SCAN: {new Date().toLocaleTimeString()} <br />
                        GLOBAL STATUS: NOMINAL
                    </div>
                </div>

                {/* Main Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
                    {[
                        { label: 'Avg Latency', value: '874ms', icon: Clock, color: 'text-blue-400' },
                        { label: 'API Succes Rate', value: '99.92%', icon: Shield, color: 'text-emerald-400' },
                        { label: 'Market Volatility', value: 'Low', icon: TrendingUp, color: 'text-yellow-400' },
                        { label: 'Compute Power', value: 'Extensive', icon: Cpu, color: 'text-purple-400' }
                    ].map((stat, idx) => (
                        <div key={idx} className="bg-white/[0.03] border border-white/10 rounded-2xl p-6 flex flex-col gap-4">
                            <stat.icon className={`w-6 h-6 ${stat.color}`} />
                            <div>
                                <p className="text-white/40 text-xs font-bold uppercase tracking-widest">{stat.label}</p>
                                <p className="text-3xl font-black mt-1">{stat.value}</p>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Real-time Status List */}
                <div className="bg-white/[0.03] border border-white/10 rounded-3xl overflow-hidden shadow-2xl">
                    <div className="p-8 border-b border-white/5 flex justify-between items-center bg-white/[0.01]">
                        <h2 className="text-xl font-black flex items-center gap-3">
                            <BarChart3 className="w-5 h-5 text-emerald-500" />
                            סטטוס ספקים חי
                        </h2>
                        <div className="flex gap-2">
                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></div>
                            <span className="text-[10px] font-black text-emerald-500/70 uppercase">Monitoring Live Nodes</span>
                        </div>
                    </div>
                    
                    <div className="divide-y divide-white/5">
                        {metrics.map((m, idx) => (
                            <div key={idx} className="p-8 flex flex-col md:flex-row md:items-center justify-between gap-6 hover:bg-white/[0.02] transition-all group">
                                <div className="flex items-center gap-6">
                                    <div className={`w-12 h-12 rounded-full flex items-center justify-center border ${m.status === 'stable' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500' : 'bg-yellow-500/10 border-yellow-500/20 text-yellow-500'}`}>
                                        <Zap className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-bold group-hover:text-emerald-400 transition-colors">{m.name}</h3>
                                        <p className="text-white/30 text-xs font-bold">API Version: 2024-05-13</p>
                                    </div>
                                </div>
                                
                                <div className="grid grid-cols-2 md:grid-cols-3 gap-8 md:gap-16">
                                    <div>
                                        <p className="text-white/20 text-[10px] font-black uppercase tracking-widest mb-1">Latency</p>
                                        <p className={`text-xl font-black ${m.latency < 1000 ? 'text-emerald-400' : 'text-yellow-400'}`}>{m.latency}ms</p>
                                    </div>
                                    <div>
                                        <p className="text-white/20 text-[10px] font-black uppercase tracking-widest mb-1">Uptime</p>
                                        <p className="text-xl font-black text-white">{m.uptime}</p>
                                    </div>
                                    <div className="hidden md:block">
                                        <p className="text-white/20 text-[10px] font-black uppercase tracking-widest mb-1">Status</p>
                                        <div className="flex items-center gap-2 mt-2">
                                            <div className={`w-2 h-2 rounded-full ${m.status === 'stable' ? 'bg-emerald-500' : 'bg-yellow-500'}`}></div>
                                            <span className="text-xs font-bold uppercase">{m.status === 'stable' ? 'Stable' : 'Congested'}</span>
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="flex justify-end">
                                    <button className="px-6 py-3 rounded-xl bg-white/5 border border-white/10 text-white/50 font-bold text-xs hover:bg-white/10 hover:text-white transition-all">
                                        דוח ביצועים היסטורי
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Pro Insight Alert */}
                <div className="mt-12 p-8 rounded-[2.5rem] bg-gradient-to-r from-emerald-500/10 via-transparent to-transparent border border-emerald-500/20 flex flex-col md:flex-row items-center gap-8">
                    <div className="w-16 h-16 bg-emerald-500 rounded-2xl flex items-center justify-center shrink-0 shadow-lg shadow-emerald-500/20">
                        <AlertTriangle className="w-8 h-8 text-black" />
                    </div>
                    <div>
                        <h4 className="text-xl font-black text-white mb-2">תובנת Commander: Claude 3.5 חווה עומס</h4>
                        <p className="text-white/50 font-medium leading-relaxed">
                            זיהינו עלייה של 15% ב-Latency בשרתי אירופה של Anthropic. אנחנו ממליצים להעביר Workflows קריטיים ל-GPT-4o ב-30 הדקות הקרובות כדי לשמור על רציפות.
                        </p>
                    </div>
                    <button className="shrink-0 px-8 py-4 bg-emerald-500 text-black font-black rounded-2xl hover:bg-emerald-400 transition-all">
                        פעולה אוטומטית (Webhook)
                    </button>
                </div>

            </main>
        </div>
    );
}
