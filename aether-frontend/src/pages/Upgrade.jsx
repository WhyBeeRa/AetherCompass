import React from 'react';
import { ArrowLeft, CheckCircle, Shield, Zap, Rocket, Box, Activity } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Upgrade() {
    const navigate = useNavigate();

    return (
        <div className="w-full flex flex-col items-center pt-16 pb-24 rtl animate-in fade-in duration-700" dir="rtl">
            <main className="w-full max-w-4xl px-6 flex flex-col md:flex-row gap-12 items-center">

                {/* Visual / Info Column */}
                <div className="flex-1 flex flex-col pt-8 md:pr-4">
                    <button onClick={() => navigate(-1)} className="self-start text-white/50 hover:text-white mb-8 transition-colors flex items-center gap-2 text-sm font-bold">
                        <ArrowLeft className="w-4 h-4" /> חזרה למסלולים
                    </button>

                    <h1 className="text-4xl md:text-5xl font-black text-white mb-6 tracking-tight leading-tight">
                        הופך ל-<span className="text-emerald-500">Commander</span>
                    </h1>
                    <p className="text-white/70 font-medium leading-relaxed mb-8 text-lg">
                        אל תסתפק בחיפוש כלים. תתחיל לבנות מערכות. ה-Pro נותן לך את השליטה המלאה ב-ROI של ה-AI שלך.
                    </p>

                    <div className="space-y-6 mb-12">
                        {[
                            { text: 'Aether Playground: השוואה חיה של מודלים (Sandbox)', icon: Box },
                            { text: 'Cost Optimizer: זיהוי כפילויות וחיסכון במנויים', icon: Rocket },
                            { text: 'the Pulse: דאטה חי על Latency וביצועי API', icon: Zap },
                            { text: 'AI Architect: בניית תהליכי עבודה (Workflows) מורכבים', icon: Activity }
                        ].map((feature, idx) => (
                            <div key={idx} className="flex items-center gap-4 group">
                                <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 group-hover:bg-emerald-500/20 transition-all">
                                    <feature.icon className="w-5 h-5 text-emerald-500" />
                                </div>
                                <span className="text-white/90 font-bold group-hover:text-white transition-colors">{feature.text}</span>
                            </div>
                        ))}
                    </div>

                    <div className="mt-auto flex items-center gap-4 p-5 bg-white/[0.03] backdrop-blur-md rounded-2xl border border-white/10">
                        <Shield className="w-8 h-8 text-emerald-500/50 shrink-0" />
                        <p className="text-xs text-white/50 font-medium leading-relaxed">
                            התשלום מאובטח ומוצפן. מחיר מיוחד להשקה: $2.99 בלבד. ניתן לבטל בכל עת בלחיצת כפתור אחת. ללא אותיות קטנות.
                        </p>
                    </div>
                </div>

                {/* Checkout Column */}
                <div className="flex-1 flex justify-center md:justify-end w-full">
                    <div className="w-full max-w-sm flex flex-col p-10 rounded-[2.5rem] bg-gradient-to-br from-white/[0.08] to-transparent backdrop-blur-3xl border border-white/20 shadow-2xl relative overflow-hidden">
                        {/* Status Bar */}
                        <div className="absolute top-0 left-0 w-full h-1.5 bg-emerald-500"></div>

                        <div className="flex justify-between items-end mb-10 pb-10 border-b border-white/10">
                            <div>
                                <h3 className="font-black text-white text-2xl mb-1">Commander Plan</h3>
                                <p className="text-sm text-emerald-400 font-bold">גישה מיידית להכל</p>
                            </div>
                            <div className="text-right">
                                <span className="text-4xl font-black text-white">$2.99</span>
                                <p className="text-[10px] text-white/40 uppercase font-bold tracking-widest mt-1">per month</p>
                            </div>
                        </div>

                        {/* Payment Flow Visual */}
                        <div className="space-y-8 mb-10 text-center">
                            <div className="relative inline-block">
                                <div className="w-20 h-20 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto border border-emerald-500/20 animate-pulse">
                                    <Zap className="w-10 h-10 text-emerald-400 fill-emerald-400" />
                                </div>
                                <div className="absolute -top-2 -right-2 bg-white text-black text-[10px] px-2 py-0.5 rounded-md font-black">SECURE</div>
                            </div>
                            
                            <p className="text-white/60 text-sm font-medium leading-relaxed px-2">
                                שדרוג המנוי מתבצע דרך שער תשלום מאובטח. מיד לאחר האישור, חשבונך ישתנה ל-<span className="text-white font-bold italic">Commander Status</span> וכל הפיצ'רים ייפתחו.
                            </p>
                        </div>

                        <button className="w-full py-5 rounded-2xl bg-emerald-500 text-black font-black text-sm hover:bg-emerald-400 transition-all duration-300 shadow-[0_10px_30px_rgba(16,185,129,0.3)] hover:-translate-y-1 active:scale-[0.98] flex items-center justify-center gap-3">
                            מעבר לתשלום מאובטח <Zap className="w-4 h-4 fill-current" />
                        </button>

                        <div className="mt-6 flex flex-col items-center gap-4">
                            <div className="flex gap-4 opacity-30 invert grayscale">
                                <img src="https://upload.wikimedia.org/wikipedia/commons/b/b5/PayPal.svg" alt="PayPal" className="h-4" />
                                <img src="https://upload.wikimedia.org/wikipedia/commons/0/04/Visa.svg" alt="Visa" className="h-4" />
                                <img src="https://upload.wikimedia.org/wikipedia/commons/5/5e/Mastercard-logo.svg" alt="Mastercard" className="h-4" />
                            </div>
                            <p className="text-[10px] text-white/30 font-bold uppercase tracking-[0.2em]">Verified by Aether Lab</p>
                        </div>
                    </div>
                </div>

            </main>
        </div>
    );
}

