import React from 'react';
import { ArrowLeft, Heart, ShieldCheck, Zap, Globe, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export default function Support() {
    const navigate = useNavigate();
    const { t, i18n } = useTranslation();
    const isRtl = i18n.dir() === 'rtl';

    // Ko-fi Support Link
    const supportLink = "https://ko-fi.com/S6S71XVKL7";

    return (
        <div className="w-full flex flex-col items-center pt-16 pb-32 animate-in fade-in duration-1000 ltr" dir="ltr">
            <main className="w-full max-w-5xl px-6 flex flex-col items-center text-center">
                
                {/* Navigation Back */}
                <div className="w-full flex justify-start mb-12">
                    <button 
                        onClick={() => navigate('/')}
                        className="group flex items-center gap-2 text-white/40 hover:text-white transition-colors font-medium text-sm"
                    >
                        <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" /> 
                        {t('settings.back_home')}
                    </button>
                </div>

                {/* Hero Header */}
                <div className="mb-16 max-w-2xl">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-cyan-400 text-[10px] font-black uppercase tracking-[0.2em] mb-6">
                        <Sparkles className="w-3 h-3" /> Community Driven
                    </div>
                    <h1 className="text-5xl md:text-7xl font-black text-white mb-8 tracking-tighter leading-tight">
                        More Than a Product.<br /><span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-500">It's a Mission.</span>
                    </h1>
                    <p className="text-xl text-white/60 font-medium leading-relaxed">
                        {t('settings.support_desc')}
                    </p>
                </div>

                {/* The "Zero-API" & Privacy Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mb-20 text-left">
                    {[
                        { 
                            title: 'Zero-API Privacy', 
                            desc: 'We rebuilt our core to run AI locally. Your data never leaves your device, ensuring maximum speed and total privacy.',
                            icon: ShieldCheck,
                            color: 'text-emerald-400'
                        },
                        { 
                            title: 'No Ads or Paywalls', 
                            desc: 'We removed all "Pro" gates. Aether is 100% free for everyone, forever. No corporate manipulation, just open access.',
                            icon: Zap,
                            color: 'text-cyan-400'
                        },
                        { 
                            title: 'Human-Powered', 
                            desc: 'We are funded exclusively by our community. Your support directly powers our infrastructure and rapid development.',
                            icon: Globe,
                            color: 'text-indigo-400'
                        }
                    ].map((item, idx) => (
                        <div key={idx} className="p-8 rounded-[2rem] bg-white/[0.03] border border-white/10 hover:border-white/20 transition-all group">
                            <div className={`w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-6 border border-white/5 group-hover:scale-110 transition-transform`}>
                                <item.icon className={`w-6 h-6 ${item.color}`} />
                            </div>
                            <h3 className="text-xl font-black text-white mb-4">{item.title}</h3>
                            <p className="text-sm text-white/50 leading-relaxed font-medium">
                                {item.desc}
                            </p>
                        </div>
                    ))}
                </div>

                {/* The Support Action Card */}
                <div className="relative w-full max-w-3xl group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500 via-indigo-500 to-purple-600 rounded-[3rem] blur opacity-20 group-hover:opacity-40 transition-all duration-1000"></div>
                    <div className="relative bg-[#0a0a0c] border border-white/10 rounded-[3rem] p-10 md:p-16 flex flex-col items-center text-center shadow-2xl overflow-hidden">
                        
                        {/* Background subtle pattern */}
                        <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-[100px] pointer-events-none"></div>
                        <div className="absolute bottom-0 left-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-[100px] pointer-events-none"></div>

                        <div className="w-24 h-24 bg-white/5 rounded-full flex items-center justify-center border border-white/10 mb-8 relative">
                            <Heart className="w-10 h-10 text-rose-500 fill-rose-500/20" />
                            <div className="absolute -top-1 -right-1 w-8 h-8 bg-white text-black rounded-full flex items-center justify-center font-black text-xs animate-bounce shadow-lg">
                                +1
                            </div>
                        </div>

                        <h2 className="text-3xl md:text-4xl font-black text-white mb-6">
                            Support the Compass
                        </h2>
                        <p className="text-lg text-white/50 mb-12 max-w-lg font-medium leading-relaxed">
                            "We aren't just selling a product; we are building a future where AI works for you, not against you."
                        </p>

                        <div className="flex flex-col sm:flex-row gap-4 w-full justify-center items-center">
                            <a 
                                href={supportLink}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="px-10 py-5 bg-[#0a0a0c] border border-white/10 text-white font-black text-lg rounded-2xl hover:bg-white/5 transition-all flex items-center justify-center gap-3 shadow-2xl hover:-translate-y-1 active:scale-95 group/btn"
                            >
                                <img height='36' style={{border: '0px', height: '36px'}} src='https://storage.ko-fi.com/cdn/kofi6.png?v=6' border='0' alt='Support Aether on ko-fi.com' className="group-hover/btn:scale-105 transition-transform" />
                                <span className="ml-2">Support the Mission</span>
                            </a>
                            <button 
                                onClick={() => navigate('/')}
                                className="px-10 py-5 bg-white/5 border border-white/10 text-white font-black text-lg rounded-2xl hover:bg-white/10 transition-all"
                            >
                                Continue for Free
                            </button>
                        </div>

                        <div className="mt-12 flex items-center gap-3 py-3 px-6 bg-white/5 rounded-full border border-white/5">
                            <div className="flex -space-x-2">
                                {[1,2,3,4].map(i => (
                                    <div key={i} className="w-6 h-6 rounded-full border border-[#0a0a0c] overflow-hidden">
                                        <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=support${i}`} alt="supporter" />
                                    </div>
                                ))}
                            </div>
                            <span className="text-[10px] text-white/30 font-black uppercase tracking-widest leading-none">
                                Joined by 420+ Supporters this month
                            </span>
                        </div>
                    </div>
                </div>

                {/* Footer Quote */}
                <div className="mt-24 max-w-lg">
                    <p className="text-white/20 text-sm font-medium italic leading-relaxed">
                        "Aether's power comes from its independence. Your support ensures we remain the clearest lens into the AI world, free from external interests."
                    </p>
                </div>

            </main>
        </div>
    );
}
