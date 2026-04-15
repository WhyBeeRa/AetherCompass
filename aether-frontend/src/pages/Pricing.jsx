import React, { useState } from 'react';
import { CheckCircle2, Zap, Rocket, Activity, Box, Search, ShieldCheck } from 'lucide-react';

export default function Pricing() {
    const [billingCycle, setBillingCycle] = useState('monthly'); // 'monthly' | 'yearly'

    return (
        <div className="w-full flex flex-col items-center pt-24 pb-24 rtl animate-in fade-in duration-700" dir="rtl">
            <main className="w-full max-w-5xl px-6 flex flex-col items-center">

                {/* Header */}
                <div className="text-center mb-16 max-w-2xl">
                    <span className="text-emerald-400 font-bold tracking-widest uppercase text-xs mb-4 block">
                        Aether Pro Strategy
                    </span>
                    <h1 className="text-4xl md:text-6xl font-black text-white tracking-tight mb-6 leading-tight">
                        ה-AI שלך בחלק מהמחיר.<br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-500">בלי פשרות.</span>
                    </h1>
                    <p className="text-lg text-white/70 font-medium leading-relaxed">
                        תמורת פחות ממחיר של מנוי AI אחד, אנחנו עוזרים לך לחסוך מאות דולרים על כל השאר. לא קונים חתול בשק – בונים מכונות.
                    </p>
                </div>

                {/* Billing Toggle */}
                <div className="flex items-center gap-3 bg-white/5 backdrop-blur-md p-1 rounded-2xl mb-16 border border-white/10 shadow-sm transition-all hover:border-white/20">
                    <button
                        onClick={() => setBillingCycle('monthly')}
                        className={`px-8 py-3 rounded-xl text-sm font-bold transition-all ${billingCycle === 'monthly' ? 'bg-white/10 text-white shadow-lg' : 'text-white/40 hover:text-white/70'}`}
                    >
                        תשלום חודשי
                    </button>
                    <button
                        onClick={() => setBillingCycle('yearly')}
                        className={`px-8 py-3 rounded-xl text-sm font-bold transition-all flex items-center gap-2 ${billingCycle === 'yearly' ? 'bg-white/10 text-white shadow-lg' : 'text-white/40 hover:text-white/70'}`}
                    >
                        תשלום שנתי
                        <span className="bg-emerald-500/20 text-emerald-400 text-[10px] px-2 py-1 rounded-lg border border-emerald-500/30 uppercase tracking-widest font-black">20% OFF</span>
                    </button>
                </div>

                {/* Pricing Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-4xl mx-auto items-stretch">

                    {/* Free Tier: The Scout */}
                    <div className="flex flex-col p-8 md:p-10 rounded-[2.5rem] bg-white/[0.02] backdrop-blur-3xl border border-white/10 shadow-sm transition-all hover:bg-white/[0.04] relative">
                        <div className="mb-8 border-b border-white/5 pb-8 relative">
                            <h3 className="text-xl font-bold text-white/90 mb-2 flex items-center gap-2">
                                <Search className="w-5 h-5 text-white/40" />
                                ה-Scout
                            </h3>
                            <p className="text-white/50 text-sm h-10 leading-relaxed italic">למי שרק מתחיל לגשש בעולם ה-AI.</p>
                            <div className="mt-8 flex items-baseline gap-1">
                                <span className="text-5xl font-black text-white">$0</span>
                                <span className="text-white/30 font-medium tracking-wide">/ mo</span>
                            </div>
                        </div>
                        <ul className="space-y-5 mb-12 flex-1">
                            {[
                                { text: 'חיפוש והשוואה בסיסיים', icon: CheckCircle2 },
                                { text: 'התראות שבועיות (Newsletter)', icon: CheckCircle2 },
                                { text: 'ניהול "My Stack" (עד 3 כלים)', icon: CheckCircle2 },
                                { text: 'גישה לקהילת ה-Insiders (Limited)', icon: CheckCircle2 }
                            ].map((item, idx) => (
                                <li key={idx} className="flex items-center gap-4">
                                    <item.icon className="w-5 h-5 text-white/30 shrink-0" />
                                    <span className="text-white/70 font-medium text-sm">{item.text}</span>
                                </li>
                            ))}
                        </ul>
                        <button className="w-full py-5 rounded-2xl border border-white/10 text-white/70 font-bold text-sm bg-white/5 hover:bg-white/10 transition-all duration-300">
                            התחל בחינם
                        </button>
                    </div>

                    {/* Pro Tier: The Commander */}
                    <div className="flex flex-col p-8 md:p-10 rounded-[2.5rem] bg-gradient-to-b from-white/[0.08] to-transparent backdrop-blur-3xl border border-white/20 shadow-[0_0_50px_rgba(16,185,129,0.1)] relative overflow-hidden group">
                        {/* Interactive Sparkle Effect Placeholder */}
                        <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2 pointer-events-none group-hover:bg-emerald-500/20 transition-all duration-700"></div>

                        <div className="mb-8 border-b border-white/10 pb-8 relative">
                            <div className="absolute top-0 left-0 bg-emerald-500 text-black text-[10px] px-3 py-1 rounded-full font-black uppercase tracking-tighter transform -translate-y-12">מבוקש ביותר</div>
                            <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                                <Zap className="w-5 h-5 text-emerald-400 fill-emerald-400/20" />
                                ה-Commander (Pro)
                            </h3>
                            <p className="text-emerald-100/60 text-sm h-10 leading-relaxed italic">הכוח לבנות, לייעל ולשלוט ב-Workflow שלך.</p>
                            <div className="mt-8 flex items-baseline gap-1">
                                <div className="relative">
                                    <span className="text-5xl font-black text-white">
                                        {billingCycle === 'monthly' ? '$2.99' : '$2.41'}
                                    </span>
                                </div>
                                <span className="text-emerald-400/50 font-medium tracking-wide">/ mo</span>
                            </div>
                            {billingCycle === 'yearly' && (
                                <p className="text-emerald-400 text-xs mt-3 font-bold bg-emerald-500/10 inline-block px-2 py-1 rounded-md border border-emerald-500/20">חיוב שנתי של $29 בלבד</p>
                            )}
                        </div>
                        <ul className="space-y-4 mb-12 flex-1 relative">
                            {[
                                { text: 'Aether Playground (Sandbox חי)', icon: Box },
                                { text: 'Cost Optimizer (חיסכון בכסף)', icon: Rocket },
                                { text: 'AI Architect (בונה שרשראות)', icon: Activity },
                                { text: 'the Pulse (מדד ביצועים חי)', icon: Zap },
                                { text: 'Unlimited Stack + Memory', icon: CheckCircle2 },
                                { text: 'סקירה מוקדמת של כלי "Hunt"', icon: ShieldCheck },
                                { text: 'גישת VIP לקהילת ה-Insiders', icon: CheckCircle2 }
                            ].map((item, idx) => (
                                <li key={idx} className="flex items-center gap-4">
                                    <item.icon className="w-5 h-5 text-emerald-400 shrink-0" />
                                    <span className="text-neutral-200 font-bold text-sm">{item.text}</span>
                                </li>
                            ))}
                        </ul>
                        <a href="/upgrade" className="w-full py-5 text-center rounded-2xl bg-emerald-500 text-black font-black text-sm hover:bg-emerald-400 transition-all duration-300 shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:shadow-[0_0_40px_rgba(16,185,129,0.5)] transform hover:-translate-y-1 active:scale-[0.98] block">
                            שדרג עכשיו - No-brainer
                        </a>
                    </div>

                </div>

                {/* Proof Section */}
                <div className="mt-20 text-center max-w-lg">
                    <p className="text-white/40 text-sm font-medium leading-relaxed italic">
                        "הצלחתי לחסוך $20 בחודש כבר בסריקה הראשונה של ה-Cost Optimizer. המנוי שילם על עצמו לשנה כבר ביום הראשון."
                    </p>
                    <div className="mt-4 flex flex-col items-center">
                        <div className="flex gap-1 mb-2">
                            {[1, 2, 3, 4, 5].map(i => <Zap key={i} className="w-3 h-3 text-emerald-400 fill-emerald-400" />)}
                        </div>
                        <span className="text-white/70 text-xs font-bold">— אדריכל מערכות, תל אביב</span>
                    </div>
                </div>

            </main>
        </div>
    );
}
