import React, { useRef } from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, Zap, Target, ShieldAlert, Cpu, CheckCircle2, ArrowRight } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

export default function Discover() {
    const { t } = useTranslation();
    const containerRef = useRef(null);

    // Fade-in animation variants
    const fadeIn = {
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
    };

    const staggerContainer = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
        }
    };

    return (
        <div ref={containerRef} className="w-full flex flex-col items-center justify-center pt-32 pb-40 overflow-hidden relative" dir="ltr">
            
            {/* HERO SPOTLIGHT SECTION */}
            <section className="relative w-full max-w-6xl mx-auto px-6 text-center flex flex-col items-center justify-center mb-32 z-10">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/10 blur-[120px] rounded-full pointer-events-none" />
                
                <motion.div 
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="bg-white/5 border border-white/10 px-4 py-1.5 rounded-full text-cyan-400 text-xs font-bold uppercase tracking-[0.2em] mb-8 backdrop-blur-md inline-flex items-center gap-2 shadow-[0_0_20px_rgba(34,211,238,0.15)]"
                >
                    <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                    {t('about.aether_lab')}
                </motion.div>
                
                <motion.h1 
                    initial="hidden" animate="visible" variants={fadeIn}
                    className="text-5xl md:text-7xl lg:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-b from-white to-white/40 tracking-tighter mb-8 max-w-4xl leading-tight"
                >
                    {t('about.objective_compass')}
                </motion.h1>
                
                <motion.p 
                    initial="hidden" animate="visible" variants={fadeIn}
                    className="text-lg md:text-xl text-white/50 max-w-2xl leading-relaxed mb-10 mx-auto"
                >
                    {t('about.noise_subtitle')}
                </motion.p>
                
                <motion.div initial="hidden" animate="visible" variants={fadeIn} className="flex items-center justify-center gap-4">
                    <Link to="/" className="px-8 py-4 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-[#02050a] font-bold tracking-tight transition-all shadow-[0_0_30px_rgba(34,211,238,0.3)] hover:shadow-[0_0_50px_rgba(34,211,238,0.5)] flex items-center gap-2">
                        Try the Engine <ArrowRight className="w-4 h-4" />
                    </Link>
                </motion.div>
            </section>

            {/* BENTO GRID (THE PILLARS) */}
            <section className="w-full max-w-6xl mx-auto px-6 mb-40 relative z-10">
                <motion.div 
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-100px" }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <span className="text-cyan-500 font-bold tracking-[0.4em] uppercase text-[10px] mb-4 block">
                        {t('about.quality_promise')}
                    </span>
                    <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">{t('about.three_pillars')}</h2>
                    <p className="text-white/40 max-w-2xl mx-auto leading-relaxed">{t('about.problem_subtitle')}</p>
                </motion.div>

                <motion.div 
                    variants={staggerContainer}
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, margin: "-100px" }}
                    className="grid grid-cols-1 md:grid-cols-3 gap-6"
                >
                    {/* Large Card 1 - Zero API */}
                    <motion.div variants={fadeIn} className="col-span-1 md:col-span-2 p-8 md:p-10 rounded-[2rem] bg-white/[0.02] border border-white/5 backdrop-blur-xl hover:border-cyan-500/30 transition-all group relative overflow-hidden flex flex-col justify-between min-h-[300px]">
                        <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-30 group-hover:scale-110 transition-all duration-700">
                            <Cpu className="w-40 h-40 text-cyan-400" />
                        </div>
                        <div className="relative z-10">
                            <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mb-6">
                                <Cpu className="w-6 h-6 text-cyan-400" />
                            </div>
                            <h3 className="text-2xl font-bold text-white mb-3">{t('about.zero_api_title')}</h3>
                            <p className="text-white/50 leading-relaxed max-w-md">
                                {t('about.zero_api_subtitle')}
                            </p>
                        </div>
                    </motion.div>

                    {/* Square Card 1 - Brand Agnostic */}
                    <motion.div variants={fadeIn} className="col-span-1 p-8 md:p-10 rounded-[2rem] bg-white/[0.02] border border-white/5 backdrop-blur-xl hover:border-indigo-500/30 transition-all group relative overflow-hidden min-h-[300px]">
                         <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-30 group-hover:scale-110 transition-all duration-700">
                            <ShieldCheck className="w-32 h-32 text-indigo-400" />
                        </div>
                        <div className="relative z-10">
                            <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-6">
                                <ShieldCheck className="w-6 h-6 text-indigo-400" />
                            </div>
                            <h3 className="text-xl font-bold text-white mb-3">{t('about.pillar_brand_title')}</h3>
                            <p className="text-white/50 leading-relaxed text-sm">
                                {t('about.pillar_brand_desc')}
                            </p>
                        </div>
                    </motion.div>

                    {/* Square Card 2 - Verified Intent */}
                     <motion.div variants={fadeIn} className="col-span-1 p-8 md:p-10 rounded-[2rem] bg-white/[0.02] border border-white/5 backdrop-blur-xl hover:border-emerald-500/30 transition-all group relative overflow-hidden min-h-[300px]">
                         <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-30 group-hover:scale-110 transition-all duration-700">
                            <Target className="w-32 h-32 text-emerald-400" />
                        </div>
                        <div className="relative z-10">
                            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-6">
                                <Target className="w-6 h-6 text-emerald-400" />
                            </div>
                            <h3 className="text-xl font-bold text-white mb-3">{t('about.pillar_intent_title')}</h3>
                            <p className="text-white/50 leading-relaxed text-sm">
                                {t('about.pillar_intent_desc')}
                            </p>
                        </div>
                    </motion.div>

                    {/* Large Card 2 - Privacy */}
                    <motion.div variants={fadeIn} className="col-span-1 md:col-span-2 p-8 md:p-10 rounded-[2rem] bg-white/[0.02] border border-white/5 backdrop-blur-xl hover:border-purple-500/30 transition-all group relative overflow-hidden flex flex-col justify-between min-h-[300px]">
                        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                        <div className="relative z-10">
                            <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mb-6">
                                <ShieldAlert className="w-6 h-6 text-purple-400" />
                            </div>
                            <h3 className="text-2xl font-bold text-white mb-3">Absolute Privacy Guarantees</h3>
                            <ul className="space-y-3 mt-6">
                                <li className="flex items-center gap-3 text-white/60 text-sm"><CheckCircle2 className="w-5 h-5 text-purple-400" /> No server-side tracking logs</li>
                                <li className="flex items-center gap-3 text-white/60 text-sm"><CheckCircle2 className="w-5 h-5 text-purple-400" /> Your queries never leave your device</li>
                                <li className="flex items-center gap-3 text-white/60 text-sm"><CheckCircle2 className="w-5 h-5 text-purple-400" /> Local Vector embeddings using WASM ONNX</li>
                            </ul>
                        </div>
                    </motion.div>
                </motion.div>
            </section>

            {/* TIMELINE / ABOUT US */}
            <section id="how-it-works" className="w-full max-w-4xl mx-auto px-6 mb-20 relative z-10">
                <motion.div 
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-100px" }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-20"
                >
                    <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">About Us</h2>
                    <p className="text-white/40">The anatomy of an objective search.</p>
                </motion.div>

                <div className="relative border-l-2 border-white/10 ml-4 md:ml-0 md:pl-0 md:border-l-0">
                    {/* Vertical line for desktop */}
                    <div className="hidden md:block absolute left-1/2 top-0 bottom-0 w-0.5 bg-white/10 -translate-x-1/2"></div>
                    
                    {/* Step 1 */}
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-50px" }}
                        className="relative flex flex-col md:flex-row items-center justify-between mb-24 md:mb-32"
                    >
                        <div className="absolute left-[-21px] md:left-1/2 md:-translate-x-1/2 w-10 h-10 rounded-full bg-[#040914] border-4 border-cyan-500 flex items-center justify-center z-10 shadow-[0_0_15px_rgba(34,211,238,0.5)]">
                            <span className="text-cyan-400 font-bold text-sm">1</span>
                        </div>
                        <div className="w-full md:w-5/12 pl-8 md:pl-0 md:text-right md:pr-12">
                            <h3 className="text-2xl font-bold text-white mb-2">Articulate Your Intent</h3>
                            <p className="text-white/50 text-sm leading-relaxed">Describe what you are trying to build or solve in plain English. No need to keyword stuff or use specific terminology.</p>
                        </div>
                        <div className="hidden md:block w-5/12 pl-12">
                            <div className="w-full p-6 rounded-2xl bg-white/[0.02] border border-white/5 backdrop-blur-md hover:border-cyan-500/30 transition-colors">
                                <div className="h-4 w-32 bg-white/10 rounded mb-3"></div>
                                <div className="h-2 w-full bg-white/5 rounded mb-2"></div>
                                <div className="h-2 w-3/4 bg-white/5 rounded"></div>
                            </div>
                        </div>
                    </motion.div>

                    {/* Step 2 */}
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-50px" }}
                        className="relative flex flex-col md:flex-row items-center justify-between mb-24 md:mb-32"
                    >
                        <div className="absolute left-[-21px] md:left-1/2 md:-translate-x-1/2 w-10 h-10 rounded-full bg-[#040914] border-4 border-indigo-500 flex items-center justify-center z-10 shadow-[0_0_15px_rgba(99,102,241,0.5)]">
                            <span className="text-indigo-400 font-bold text-sm">2</span>
                        </div>
                        <div className="hidden md:block w-5/12 pr-12 text-right">
                             <div className="w-full p-6 rounded-2xl bg-white/[0.02] border border-white/5 backdrop-blur-md flex items-center justify-center hover:border-indigo-500/30 transition-colors">
                                <Zap className="w-10 h-10 text-indigo-400 animate-pulse" />
                             </div>
                        </div>
                        <div className="w-full md:w-5/12 pl-8 md:pl-12">
                            <h3 className="text-2xl font-bold text-white mb-2">Local Embedding Generation</h3>
                            <p className="text-white/50 text-sm leading-relaxed">Your browser instantly converts your prompt into a dense mathematical vector representation using our lightweight ONNX model.</p>
                        </div>
                    </motion.div>

                    {/* Step 3 */}
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-50px" }}
                        className="relative flex flex-col md:flex-row items-center justify-between"
                    >
                        <div className="absolute left-[-21px] md:left-1/2 md:-translate-x-1/2 w-10 h-10 rounded-full bg-[#040914] border-4 border-emerald-500 flex items-center justify-center z-10 shadow-[0_0_15px_rgba(16,185,129,0.5)]">
                            <span className="text-emerald-400 font-bold text-sm">3</span>
                        </div>
                        <div className="w-full md:w-5/12 pl-8 md:pl-0 md:text-right md:pr-12">
                            <h3 className="text-2xl font-bold text-white mb-2">Vector Similarity Search</h3>
                            <p className="text-white/50 text-sm leading-relaxed">We compare your intent vector against thousands of categorized tools in milliseconds, returning only the purest matches.</p>
                        </div>
                        <div className="hidden md:block w-5/12 pl-12">
                             <div className="w-full p-6 rounded-2xl bg-gradient-to-br from-emerald-500/10 to-cyan-500/5 border border-emerald-500/20 backdrop-blur-md flex flex-col gap-3">
                                <div className="h-10 w-full bg-emerald-500/20 rounded border border-emerald-500/30"></div>
                                <div className="h-10 w-full bg-white/5 rounded border border-white/10"></div>
                             </div>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* FINAL CTA */}
            <section className="w-full max-w-4xl mx-auto px-6 mt-20 mb-10 relative z-10 text-center">
                <motion.div 
                    initial={{ opacity: 0, scale: 0.95 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true, margin: "-50px" }}
                    transition={{ duration: 0.6 }}
                    className="p-12 md:p-16 rounded-[2.5rem] bg-gradient-to-b from-white/[0.05] to-transparent border border-white/10 backdrop-blur-xl relative overflow-hidden flex flex-col items-center"
                >
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-cyan-500/10 blur-[100px] pointer-events-none" />
                    <h2 className="text-4xl md:text-6xl font-black text-white mb-6 tracking-tight relative z-10">
                        Ready to find your <br className="hidden md:block"/> perfect match?
                    </h2>
                    <p className="text-white/50 mb-10 text-lg max-w-xl mx-auto relative z-10">
                        Stop searching. Start building. Let our objective engine find exactly what you need in seconds.
                    </p>
                    <Link to="/" className="relative z-10 inline-flex items-center justify-center gap-2 px-10 py-5 rounded-2xl bg-white text-black font-black uppercase tracking-widest hover:bg-cyan-400 hover:scale-105 transition-all shadow-[0_0_40px_rgba(255,255,255,0.2)]">
                        Launch Engine <ArrowRight className="w-5 h-5" />
                    </Link>
                </motion.div>
            </section>
            
        </div>
    );
}
