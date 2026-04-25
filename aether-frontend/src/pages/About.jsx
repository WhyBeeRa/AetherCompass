import React, { useRef } from 'react';
import { motion, useScroll, useTransform, useSpring } from 'framer-motion';
import { ShieldCheck, Database, Zap, AlertCircle, GitBranch, Activity, Compass, Target, Info, ShieldAlert, Cpu } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import compassImg from '../assets/compass-hero.png';

export default function About() {
    const { t } = useTranslation();
    const containerRef = useRef(null);
    
    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start start", "end end"]
    });

    const smoothProgress = useSpring(scrollYProgress, {
        stiffness: 100,
        damping: 30,
        restDelta: 0.001
    });

    // Phase 1: The Noise (0 - 0.2)
    const noiseOpacity = useTransform(smoothProgress, [0, 0.15, 0.2], [1, 1, 0]);
    const noiseScale = useTransform(smoothProgress, [0, 0.2], [1, 1.5]);
    const noiseBlur = useTransform(smoothProgress, [0, 0.15], ["0px", "20px"]);

    // Phase 2: The Problem (0.2 - 0.4)
    const problemOpacity = useTransform(smoothProgress, [0.15, 0.2, 0.35, 0.4], [0, 1, 1, 0]);
    const problemY = useTransform(smoothProgress, [0.15, 0.4], [100, -100]);

    // Phase 3: The Aether Lab / Compass (0.4 - 0.6)
    const compassOpacity = useTransform(smoothProgress, [0.35, 0.4, 0.55, 0.6], [0, 1, 1, 0]);
    const compassScale = useTransform(smoothProgress, [0.35, 0.5, 0.65], [0.5, 1, 0.8]);
    const compassRotate = useTransform(smoothProgress, [0.4, 0.6], [0, 360]);

    // Phase 4: The Pillars (0.6 - 0.8)
    const pillarsOpacity = useTransform(smoothProgress, [0.55, 0.6, 0.75, 0.8], [0, 1, 1, 0]);
    const pillarsY = useTransform(smoothProgress, [0.55, 0.8], [50, -50]);

    // Phase 5: Zero-API Philosophy (0.8 - 1.0)
    const zeroApiOpacity = useTransform(smoothProgress, [0.75, 0.85], [0, 1]);
    const zeroApiY = useTransform(smoothProgress, [0.75, 1], [50, 0]);

    return (
        <div ref={containerRef} className="relative w-full bg-[#040914] font-sans antialiased text-slate-200" style={{ height: '600vh' }} dir="ltr">
            
            {/* STICKY CANVAS FOR ANIMATIONS */}
            <div className="sticky top-0 h-screen w-full flex items-center justify-center overflow-hidden">
                
                {/* SECTION 1: THE NOISE (ENTROPY) */}
                <motion.div 
                    style={{ opacity: noiseOpacity, scale: noiseScale, filter: `blur(${noiseBlur})` }}
                    className="absolute inset-0 flex flex-col items-center justify-center px-6 text-center z-10"
                >
                    <div className="flex flex-wrap gap-8 justify-center opacity-10 absolute inset-0 pt-40 pointer-events-none z-0">
                        {[AlertCircle, GitBranch, Activity, Database, Zap, Info].map((Icon, i) => (
                            <motion.div
                                key={`noise-icon-${i}`}
                                animate={{ 
                                    y: [0, Math.random() * 100 - 50],
                                    rotate: [0, 360],
                                    opacity: [0.1, 0.3, 0.1]
                                }}
                                transition={{ duration: 8 + i, repeat: Infinity, ease: "linear" }}
                            >
                                <Icon className="w-12 h-12 text-white/40" />
                            </motion.div>
                        ))}
                    </div>
                    <div className="relative z-10">
                        <h1 className="text-5xl md:text-8xl font-bold text-white tracking-tighter mb-6 relative">
                            {t('about.era_of_noise')} <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-600">{t('about.algorithmic_noise')}</span>
                        </h1>
                        <p className="max-w-xl mx-auto text-white/50 text-xl font-medium leading-relaxed">
                            {t('about.noise_subtitle')}
                        </p>
                    </div>
                </motion.div>

                {/* SECTION 2: THE PROBLEM (ENGINEERED REALITY) */}
                <motion.div 
                    style={{ opacity: problemOpacity, y: problemY }}
                    className="absolute inset-0 flex flex-col items-center justify-center px-6 text-center z-20"
                >
                    <div className="bg-white/5 border border-white/10 px-4 py-1 rounded-full text-white/40 text-[10px] font-bold uppercase tracking-widest mb-6 backdrop-blur-md">
                        {t('about.core_disconnect')}
                    </div>
                    <h2 className="text-4xl md:text-7xl font-bold text-white mb-8 tracking-tight">
                        {t('about.engineered_reality')}
                    </h2>
                    <p className="max-w-2xl text-white/70 text-lg md:text-xl leading-relaxed">
                        {t('about.problem_subtitle')}
                    </p>
                </motion.div>

                {/* SECTION 3: THE SOLUTION (THE COMPASS) */}
                <motion.div 
                    id="how-it-works"
                    style={{ opacity: compassOpacity }}
                    className="absolute inset-0 flex flex-col items-center justify-center px-6 text-center z-30"
                >
                    <motion.div 
                        style={{ scale: compassScale, rotate: compassRotate }}
                        className="relative mb-12"
                    >
                        <div className="absolute inset-0 bg-cyan-500/10 blur-[120px] rounded-full scale-150"></div>
                        <img 
                            src={compassImg} 
                            alt="Aether Compass" 
                            className="w-56 h-56 md:w-96 md:h-96 object-contain drop-shadow-[0_0_80px_rgba(34,211,238,0.3)]"
                        />
                    </motion.div>
                    <div className="bg-cyan-500/10 border border-cyan-500/20 px-4 py-1 rounded-full text-cyan-400 text-[10px] font-bold uppercase tracking-[0.3em] mb-6">
                        {t('about.aether_lab')}
                    </div>
                    <h2 className="text-4xl md:text-7xl font-bold text-white mb-6 tracking-tight">
                        {t('about.objective_compass')}
                    </h2>
                    <p className="max-w-2xl text-white/70 text-lg md:text-xl leading-relaxed">
                        {t('about.solution_subtitle')}
                    </p>
                </motion.div>

                {/* SECTION 4: THE PILLARS (VERIFIED TRUTH) */}
                <motion.div 
                    style={{ opacity: pillarsOpacity, y: pillarsY }}
                    className="absolute inset-0 flex flex-col items-center justify-center px-6 z-40"
                    dir="ltr"
                >
                    <div className="text-center mb-16">
                        <span className="text-cyan-500 font-bold tracking-[0.4em] uppercase text-[10px] mb-4 block">
                            {t('about.quality_promise')}
                        </span>
                        <h2 className="text-4xl md:text-6xl font-bold text-white mb-4 tracking-tighter">
                            {t('about.three_pillars')}
                        </h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl w-full">
                        <div className="p-10 rounded-[2.5rem] bg-white/[0.02] border border-white/5 backdrop-blur-3xl hover:border-white/20 transition-all group relative overflow-hidden">
                            <div className="absolute -top-20 -right-20 w-40 h-40 bg-cyan-500/5 blur-3xl rounded-full"></div>
                            <ShieldCheck className="w-10 h-10 text-cyan-400 mb-8 group-hover:scale-110 transition-transform" />
                            <h3 className="text-xl font-bold text-white mb-4">{t('about.pillar_brand_title')}</h3>
                            <p className="text-white/40 text-sm leading-relaxed">
                                {t('about.pillar_brand_desc')}
                            </p>
                        </div>
                        <div className="p-10 rounded-[2.5rem] bg-white/[0.02] border border-white/5 backdrop-blur-3xl hover:border-white/20 transition-all group relative overflow-hidden">
                            <div className="absolute -top-20 -right-20 w-40 h-40 bg-indigo-500/5 blur-3xl rounded-full"></div>
                            <Database className="w-10 h-10 text-indigo-400 mb-8 group-hover:scale-110 transition-transform" />
                            <h3 className="text-xl font-bold text-white mb-4">{t('about.pillar_field_title')}</h3>
                            <p className="text-white/40 text-sm leading-relaxed">
                                {t('about.pillar_field_desc')}
                            </p>
                        </div>
                        <div className="p-10 rounded-[2.5rem] bg-white/[0.02] border border-white/5 backdrop-blur-3xl hover:border-white/20 transition-all group relative overflow-hidden">
                            <div className="absolute -top-20 -right-20 w-40 h-40 bg-emerald-500/5 blur-3xl rounded-full"></div>
                            <Target className="w-10 h-10 text-emerald-400 mb-8 group-hover:scale-110 transition-transform" />
                            <h3 className="text-xl font-bold text-white mb-4">{t('about.pillar_intent_title')}</h3>
                            <p className="text-white/40 text-sm leading-relaxed">
                                {t('about.pillar_intent_desc')}
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* SECTION 5: ZERO-API PHILOSOPHY */}
                <motion.div 
                    style={{ opacity: zeroApiOpacity, y: zeroApiY }}
                    className="absolute inset-0 flex flex-col items-center justify-center px-6 text-center z-50"
                >
                    <div className="bg-white/5 border border-white/10 px-4 py-1 rounded-full text-white/40 text-[10px] font-bold uppercase tracking-widest mb-6 backdrop-blur-md">
                         {t('about.zero_api_foundation')}
                    </div>
                    
                    <div className="relative mb-10">
                        <div className="absolute inset-0 bg-indigo-500/20 blur-[100px] rounded-full scale-150"></div>
                        <div className="w-24 h-24 md:w-32 md:h-32 bg-gradient-to-br from-indigo-500 to-cyan-500 rounded-3xl flex items-center justify-center shadow-2xl relative z-10 mx-auto transform rotate-12">
                            <Cpu className="w-12 h-12 md:w-16 md:h-16 text-white" />
                        </div>
                    </div>

                    <h2 className="text-4xl md:text-7xl font-bold text-white mb-8 tracking-tight">
                        {t('about.zero_api_title')}
                    </h2>
                    <p className="max-w-3xl text-white/70 text-lg md:text-xl leading-relaxed mx-auto">
                        {t('about.zero_api_subtitle')}
                    </p>

                    <div className="mt-12 flex items-center justify-center gap-12 text-white/40 font-bold tracking-widest uppercase text-[10px]">
                        <div className="flex items-center gap-2">
                            <ShieldAlert className="w-4 h-4 text-cyan-500" />
                            LOCAL PROCESSING
                        </div>
                        <div className="flex items-center gap-2">
                            <ShieldAlert className="w-4 h-4 text-cyan-500" />
                            NO DATA LEAKAGE
                        </div>
                        <div className="flex items-center gap-2">
                             <ShieldAlert className="w-4 h-4 text-cyan-500" />
                            ONNX RUNTIME
                        </div>
                    </div>
                </motion.div>

            </div>
            
            {/* SCROLL PROGRESS INDICATOR */}
            <div className="fixed right-8 top-1/2 -translate-y-1/2 flex flex-col gap-4 z-50">
                {[0, 1, 2, 3, 4].map(i => {
                    const isActive = useTransform(smoothProgress, [i * 0.2, (i + 1) * 0.2], [1, 0.2]);
                    return (
                        <motion.div 
                            key={`progress-dot-${i}`}
                            style={{ opacity: isActive }}
                            className="w-0.5 h-10 bg-cyan-500 rounded-full shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                        />
                    );
                })}
            </div>

        </div>
    );
}
