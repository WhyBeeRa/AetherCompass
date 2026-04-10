import React, { useState } from 'react';
import { Coins, ShieldCheck, Zap, ArrowRight, TrendingDown, Layers, Sparkles } from 'lucide-react';

export default function Optimizer() {
    const [isScanning, setIsScanning] = useState(false);
    const [scanResults, setScanResults] = useState(null);

    const startScan = () => {
        setIsScanning(true);
        setTimeout(() => {
            setScanResults({
                potentialSavings: '$24.50',
                duplicates: [
                    { name: 'Midjourney', reason: 'You are also paying for ChatGPT Plus which includes DALL-E 3.', savings: '$20/mo' },
                    { name: 'Jasper', reason: 'Claude 3.5 Sonnet (Free/Pro) produces similar results for your use case.', savings: '$4.50/mo' }
                ],
                recommendations: [
                    { title: 'Bundling Strategy', text: 'Consolidate your image generation tools into a single Enterprise API.' }
                ]
            });
            setIsScanning(false);
        }, 2500);
    };

    return (
        <div className="w-full min-h-screen pt-24 pb-24 rtl animate-in fade-in duration-700 bg-black text-white" dir="rtl">
            <main className="max-w-7xl mx-auto px-6">
                
                {/* Header */}
                <div className="mb-16 text-center md:text-right">
                    <div className="flex items-center gap-3 mb-4 justify-center md:justify-start">
                        <div className="p-2 bg-emerald-500 rounded-lg shadow-lg shadow-emerald-500/20">
                            <Coins className="w-6 h-6 text-black" />
                        </div>
                        <span className="text-emerald-400 font-black uppercase tracking-tighter text-sm">
                            Financial Intelligence Layer
                        </span>
                    </div>
                    <h1 className="text-4xl md:text-6xl font-black tracking-tight mb-4">
                        Cost <span className="text-emerald-500">Optimizer</span>
                    </h1>
                    <p className="text-white/50 text-lg font-medium max-w-2xl">
                        אנחנו סורקים את ה-"Stack" שלך ומזהים כפילויות. תפסיק לשלם פעמיים על אותו ה-Intelligence.
                    </p>
                </div>

                {/* Hero Action Card */}
                {!scanResults && !isScanning && (
                    <div className="relative group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-[3rem] blur opacity-25 group-hover:opacity-40 transition-all duration-700"></div>
                        <div className="relative bg-white/[0.03] backdrop-blur-3xl border border-white/20 rounded-[3rem] p-12 md:p-20 flex flex-col items-center text-center shadow-2xl">
                            <div className="w-24 h-24 bg-emerald-500/10 rounded-full flex items-center justify-center border border-emerald-500/20 mb-8">
                                <Zap className="w-12 h-12 text-emerald-400 fill-emerald-400/20" />
                            </div>
                            <h2 className="text-3xl font-black mb-6">מוכן לחסוך?</h2>
                            <p className="text-white/40 mb-10 max-w-md font-medium leading-relaxed">
                                המערכת תנתח את הכלים השמורים במחסנית שלך ותשווה אותם למחירונים העדכניים ביותר בשוק.
                            </p>
                            <button 
                                onClick={startScan}
                                className="px-12 py-5 bg-emerald-500 text-black font-black text-xl rounded-2xl hover:bg-emerald-400 transition-all shadow-xl shadow-emerald-500/30 hover:-translate-y-1 active:scale-95"
                            >
                                התחל סריקת סטאק (Deep Scan)
                            </button>
                        </div>
                    </div>
                )}

                {/* Scanning Animation */}
                {isScanning && (
                    <div className="py-20 flex flex-col items-center">
                        <div className="relative w-40 h-40 mb-12">
                            <div className="absolute inset-0 border-4 border-emerald-500/20 rounded-full"></div>
                            <div className="absolute inset-0 border-t-4 border-emerald-500 rounded-full animate-spin"></div>
                            <div className="absolute inset-0 flex items-center justify-center font-black text-emerald-500 text-3xl">
                                %{Math.floor(Math.random() * 100)}
                            </div>
                        </div>
                        <h2 className="text-2xl font-black animate-pulse">מנתח כפילויות ב-API...</h2>
                        <div className="mt-8 space-y-3 w-full max-w-xs">
                            <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                                <div className="h-full bg-emerald-500 w-2/3"></div>
                            </div>
                            <div className="flex justify-between text-[10px] font-black text-white/30 uppercase tracking-widest">
                                <span>Comparing Latency</span>
                                <span>Bundling Check</span>
                            </div>
                        </div>
                    </div>
                )}

                {/* Results Screen */}
                {scanResults && (
                    <div className="space-y-8 animate-in slide-in-from-bottom-10 fade-in duration-1000">
                        {/* Summary Header */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="bg-emerald-500 text-black p-10 rounded-[2.5rem] flex flex-col justify-between shadow-2xl shadow-emerald-500/20">
                                <TrendingDown className="w-10 h-10 mb-6" />
                                <div>
                                    <p className="text-xs font-black uppercase tracking-widest opacity-60">Potential Monthly Savings</p>
                                    <h2 className="text-6xl font-black">{scanResults.potentialSavings}</h2>
                                </div>
                            </div>
                            
                            <div className="md:col-span-2 bg-white/[0.03] border border-white/10 p-10 rounded-[2.5rem] flex items-center gap-8">
                                <div className="p-6 bg-white/5 rounded-full border border-white/10">
                                    <ShieldCheck className="w-10 h-10 text-emerald-400" />
                                </div>
                                <div>
                                    <h3 className="text-2xl font-black mb-2">מסלול ה-Commander מאושר</h3>
                                    <p className="text-white/50 font-medium leading-relaxed">
                                        הסריקה הושלמה בהצלחה. מצאנו {scanResults.duplicates.length} כפילויות בסטאק שלך שיכולות להיפסק באופן מיידי ללא פגיעה בביצועים.
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Duplicates List */}
                        <div className="bg-white/[0.02] border border-white/10 rounded-[2.5rem] overflow-hidden">
                            <div className="p-8 border-b border-white/10 bg-white/[0.02]">
                                <h3 className="text-xl font-black flex items-center gap-3">
                                    <Layers className="w-5 h-5 text-emerald-400" />
                                    כפילויות שזוהו (Redundancies)
                                </h3>
                            </div>
                            <div className="divide-y divide-white/5">
                                {scanResults.duplicates.map((dup, idx) => (
                                    <div key={idx} className="p-10 flex flex-col md:flex-row md:items-center justify-between gap-8 hover:bg-white/[0.02] transition-all group">
                                        <div className="flex-1">
                                            <h4 className="text-2xl font-bold text-white mb-2">{dup.name}</h4>
                                            <p className="text-white/40 font-medium">{dup.reason}</p>
                                        </div>
                                        <div className="flex items-center gap-8 shrink-0">
                                            <div className="text-right">
                                                <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">Savings</p>
                                                <p className="text-3xl font-black text-white">{dup.savings}</p>
                                            </div>
                                            <button className="p-4 bg-white/5 rounded-2xl border border-white/10 hover:border-emerald-500/50 transition-all text-emerald-400">
                                                <ArrowRight className="w-6 h-6" />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* CTA Section */}
                        <div className="p-10 bg-gradient-to-br from-emerald-500/10 to-transparent border border-emerald-500/20 rounded-[2.5rem] flex flex-col md:flex-row items-center justify-between gap-8">
                            <div className="flex gap-6 items-center">
                                <div className="p-4 bg-emerald-500 rounded-2xl">
                                    <Sparkles className="w-8 h-8 text-black" />
                                </div>
                                <div>
                                    <h4 className="text-xl font-black">ייצוא דוח ROI מלא</h4>
                                    <p className="text-white/50 text-sm font-medium">קבל PDF מעוצב לבוס או למנהל הכספים עם כל ההמלצות.</p>
                                </div>
                            </div>
                            <button className="px-8 py-4 bg-white/5 border border-white/10 rounded-2xl font-black text-sm hover:bg-white/10 transition-all">
                                הורד דוח Commander
                            </button>
                        </div>
                    </div>
                )}

            </main>
        </div>
    );
}
