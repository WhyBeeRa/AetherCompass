import React, { useState, useEffect } from 'react';
import { Activity, Zap, ShieldAlert, Clock, Sparkles } from 'lucide-react';
import { apiFetch } from '../api';
import { useTranslation } from 'react-i18next';

const LiveMonitorWidget = () => {
    const { t } = useTranslation();
    const [benchmarks, setBenchmarks] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchBenchmarks = async () => {
            try {
                const res = await apiFetch('/benchmarks/live');
                if (res.ok) {
                    const data = await res.json();
                    setBenchmarks(data);
                }
            } catch (err) {
                console.error("Failed to fetch benchmarks:", err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchBenchmarks();
        const interval = setInterval(fetchBenchmarks, 30000);
        return () => clearInterval(interval);
    }, []);

    const [isScanning, setIsScanning] = useState(false);
    const [scanMessage, setScanMessage] = useState("");

    const handleTriggerScan = async () => {
        setIsScanning(true);
        setScanMessage(t('live_monitor.start_scan'));
        try {
            const res = await apiFetch('/admin/live-metrics/trigger', {
                method: 'POST'
            });
            if (res.ok) {
                setScanMessage(t('live_monitor.scan_success'));
                setTimeout(() => {
                    setScanMessage("");
                    setIsScanning(false);
                }, 3000);
            } else {
                setScanMessage(t('live_monitor.scan_error'));
                setTimeout(() => setIsScanning(false), 3000);
            }
        } catch (err) {
            console.error("Scan trigger failed:", err);
            setScanMessage(t('live_monitor.connection_failed'));
            setTimeout(() => setIsScanning(false), 3000);
        }
    };

    if (benchmarks.length === 0 && isLoading) return (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col items-center justify-center min-h-[140px] mb-12">
            <div className="flex items-center gap-3 text-cyan-400/50 text-sm font-medium animate-pulse mb-2">
                <div className="relative">
                    <Activity className="w-5 h-5" />
                    <div className="absolute inset-0 bg-cyan-400/20 blur-lg rounded-full" />
                </div>
                {t('live_monitor.connecting')}
            </div>
            <p className="text-[10px] text-white/30 uppercase tracking-[0.2em]">Aether Live Benchmarking Protocol</p>
        </div>
    );

    const lastChecked = benchmarks.length > 0 ? new Date(benchmarks[0].timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : null;

    return (
        <div className="mb-12 relative">
            {/* Soft Refresh Loading Overlay */}
            {isLoading && benchmarks.length > 0 && (
                <div className="absolute top-0 right-10 z-10 flex items-center gap-2 px-3 py-1 bg-cyan-500/20 border border-cyan-500/30 rounded-full animate-pulse transition-all">
                    <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-spin" />
                    <span className="text-[9px] font-bold text-cyan-400 uppercase tracking-widest">Refreshing Cached Data...</span>
                </div>
            )}

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
                <div className="flex items-center gap-2">
                    <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
                        <Activity className="w-4 h-4 text-cyan-400" />
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-white">Live Monitoring</h3>
                        <p className="text-[10px] text-white/40 uppercase tracking-widest">
                            {t('live_monitor.response_health')} {lastChecked && t('live_monitor.last_received', { time: lastChecked })}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {scanMessage && (
                        <span className="text-[10px] font-bold text-cyan-400 animate-pulse uppercase tracking-wider">
                            {scanMessage}
                        </span>
                    )}
                    <button 
                        onClick={handleTriggerScan}
                        disabled={isScanning}
                        className={`group relative flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all overflow-hidden
                            ${isScanning 
                                ? 'bg-white/5 text-white/20 border border-white/10 cursor-not-allowed' 
                                : 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 hover:bg-cyan-500/20 hover:border-cyan-500/40 active:scale-95'
                            }`}
                    >
                        <Zap className={`w-3.5 h-3.5 ${isScanning ? 'animate-spin' : ''}`} />
                        <span>{isScanning ? t('live_monitor.scanning') : t('live_monitor.update_pulse')}</span>
                    </button>

                    <div className="flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full h-8">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                        <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-tight">Active Pulse</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {benchmarks.map((m, idx) => (
                    <div key={`benchmark-${idx}`} className={`bg-[#050b1a] border rounded-2xl p-5 hover:border-cyan-500/30 transition-all group relative overflow-hidden ${
                        m.status === 'protected' ? 'border-indigo-500/30 shadow-[inset_0_0_20px_rgba(99,102,241,0.05)]' : 'border-white/5'
                    }`}>
                        <div className={`absolute top-0 right-0 w-24 h-24 blur-[40px] rounded-full pointer-events-none ${
                            m.status === 'protected' ? 'bg-indigo-500/10' : 'bg-cyan-500/5'
                        }`} />
                        
                        <div className="flex items-center justify-between mb-4">
                            <span className="text-xs font-bold text-white/90 tracking-tight">{m.tool_name}</span>
                            <span className={`text-[9px] font-medium px-1.5 py-0.5 rounded-md border uppercase ${
                                m.status === 'protected' ? 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20' : 'text-white/30 bg-white/5 border-white/10'
                            }`}>
                                {m.status === 'protected' ? 'Protected' : m.provider}
                            </span>
                        </div>
                        
                        <div className="flex items-end justify-between">
                            <div>
                                <div className="flex items-baseline gap-1 mb-1">
                                    <span className={`text-2xl font-bold tabular-nums ${m.status === 'protected' ? 'text-indigo-300' : 'text-white'}`}>
                                        {m.status === 'protected' ? '--' : m.latency_ms}
                                    </span>
                                    {m.status !== 'protected' && <span className="text-[10px] font-medium text-white/30 uppercase">ms</span>}
                                </div>
                                <div className={`flex items-center gap-1 text-[10px] font-bold tracking-tight px-2 py-0.5 rounded-sm ${
                                    m.status === 'protected' ? 'bg-indigo-500/10 text-indigo-400' :
                                    m.comparison_vs_avg < 0 
                                    ? 'bg-emerald-500/10 text-emerald-400' 
                                    : 'bg-red-500/10 text-red-400'
                                }`}>
                                    {m.status === 'protected' ? <ShieldAlert className="w-3 h-3" /> : (m.comparison_vs_avg < 0 ? <Zap className="w-3 h-3" /> : <Clock className="w-3 h-3" />)}
                                    {m.status === 'protected' ? 'Anti-Bot Secure' : `${Math.abs(m.comparison_vs_avg)}% ${m.comparison_vs_avg < 0 ? t('live_monitor.faster') : t('live_monitor.slower')}`}
                                </div>
                            </div>
                            
                            <div className="text-right">
                                <div className="inline-flex flex-col items-end">
                                    <div className={`flex items-center gap-1.5 font-bold text-xs mb-1 ${m.status === 'protected' ? 'text-indigo-300' : 'text-white/80'}`}>
                                        <Sparkles className={`w-3.5 h-3.5 ${m.status === 'protected' ? 'text-indigo-400' : 'text-amber-400'}`} />
                                        {m.hallucination_score}<span className="text-[8px] opacity-30">%</span>
                                    </div>
                                    <div className="text-[9px] text-white/20 uppercase font-medium leading-none">{t('live_monitor.reliability')}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default LiveMonitorWidget;
