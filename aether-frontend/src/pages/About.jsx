import React, { useRef } from 'react';
import { motion, useScroll, useTransform, useSpring } from 'framer-motion';
import { ShieldCheck, Database, Zap, AlertCircle, GitBranch, Activity, Compass, Target, Info } from 'lucide-react';
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

    // Phase 1: The Noise (0 - 0.25)
    const noiseOpacity = useTransform(smoothProgress, [0, 0.2], [1, 0]);
    const noiseScale = useTransform(smoothProgress, [0, 0.2], [1, 1.5]);
    const noiseBlur = useTransform(smoothProgress, [0, 0.15], ["0px", "20px"]);

    // Phase 2: The Problem (0.25 - 0.5)
    const problemOpacity = useTransform(smoothProgress, [0.15, 0.25, 0.45, 0.5], [0, 1, 1, 0]);
    const problemY = useTransform(smoothProgress, [0.15, 0.5], [100, -100]);

    // Phase 3: The Aether Lab / Compass (0.5 - 0.75)
    const compassOpacity = useTransform(smoothProgress, [0.45, 0.55, 0.7, 0.8], [0, 1, 1, 0]);
    const compassScale = useTransform(smoothProgress, [0.45, 0.6, 0.75], [0.5, 1, 0.8]);
    const compassRotate = useTransform(smoothProgress, [0.5, 0.75], [0, 360]);

    // Phase 4: The Pillars (0.75 - 1)
    const pillarsOpacity = useTransform(smoothProgress, [0.75, 0.85], [0, 1]);
    const pillarsY = useTransform(smoothProgress, [0.75, 1], [50, 0]);

    return (
        <div ref={containerRef} className="relative w-full bg-[#040914]" style={{ height: '500vh' }}>
            
            {/* STICKY CANVAS FOR ANIMATIONS */}
            <div className="sticky top-0 h-screen w-full flex items-center justify-center overflow-hidden">
                
                {/* SECTION 1: THE NOISE (ENTROPY) */}
                <motion.div 
                    style={{ opacity: noiseOpacity, scale: noiseScale, filter: `blur(${noiseBlur})` }}
                    className="absolute inset-0 flex flex-col items-center justify-center px-6 text-center z-10"
                >
                    <div className="flex flex-wrap gap-8 justify-center opacity-30 absolute inset-0 pt-40 pointer-events-none">
                        {[AlertCircle, GitBranch, Activity, Database, Zap, Info].map((Icon, i) => (
                            <motion.div
                                key={i}
                                animate={{ 
                                    y: [0, Math.random() * 100 - 50],
                                    rotate: [0, 360],
                                    opacity: [0.1, 0.5, 0.1]
                                }}
                                transition={{ duration: 5 + i, repeat: Infinity, ease: "linear" }}
                            >
                                <Icon className="w-12 h-12 text-white/40" />
                            </motion.div>
                        ))}
                    </div>
                    <h1 className="text-5xl md:text-7xl font-bold text-white tracking-tighter mb-6 relative">
                        עידן של רעש <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500/50 to-orange-500/50">אלגוריתמי.</span>
                    </h1>
                    <p className="max-w-xl text-white/50 text-xl font-medium leading-relaxed">
                        האינטרנט הוצפה באינדקסים שטחיים. <br className="hidden md:block" />
                        תוצאות שנקנות בכסף, לא באיכות.
                    </p>
                </motion.div>

                {/* SECTION 2: THE PROBLEM (DECEPTION) */}
                <motion.div 
                    style={{ opacity: problemOpacity, y: problemY }}
                    className="absolute inset-0 flex flex-col items-center justify-center px-6 text-center z-20"
                >
                    <div className="bg-red-500/10 border border-red-500/20 px-4 py-1 rounded-full text-red-500 text-xs font-bold uppercase tracking-widest mb-6">
                        The Core Issue
                    </div>
                    <h2 className="text-4xl md:text-6xl font-bold text-white mb-8">
                        הינדוס תודעה.
                    </h2>
                    <p className="max-w-2xl text-white/70 text-lg md:text-xl leading-loose">
                        כשאתה מחפש פתרון AI למשימה אמיתית, התוצאות הראשונות הן כבר מזמן לא הטובות ביותר. הן של החברות להן יש את תקציב השיווק הגדול ביותר.
                    </p>
                </motion.div>

                {/* SECTION 3: THE SOLUTION (THE COMPASS) */}
                <motion.div 
                    style={{ opacity: compassOpacity }}
                    className="absolute inset-0 flex flex-col items-center justify-center px-6 text-center z-30"
                >
                    <motion.div 
                        style={{ scale: compassScale, rotate: compassRotate }}
                        className="relative mb-12"
                    >
                        <div className="absolute inset-0 bg-cyan-500/20 blur-[100px] rounded-full scale-150"></div>
                        <img 
                            src={compassImg} 
                            alt="Aether Compass" 
                            className="w-48 h-48 md:w-80 md:h-80 object-contain drop-shadow-[0_0_50px_rgba(34,211,238,0.4)]"
                        />
                    </motion.div>
                    <div className="bg-cyan-500/10 border border-cyan-500/20 px-4 py-1 rounded-full text-cyan-400 text-xs font-bold uppercase tracking-widest mb-6">
                        The Aether Lab
                    </div>
                    <h2 className="text-4xl md:text-6xl font-bold text-white mb-6">
                        המצפן האובייקטיבי שלך.
                    </h2>
                    <p className="max-w-2xl text-white/70 text-lg md:text-xl leading-relaxed">
                        בנינו רשת אוטונומית של סוכנים (Agents) שיורדים לשטח כדי בדיוק ולעמת את ההבטחות של חברות הטכנולוגיה.
                    </p>
                </motion.div>

                {/* SECTION 4: THE PILLARS (OBJECTIVE TRUTH) */}
                <motion.div 
                    style={{ opacity: pillarsOpacity, y: pillarsY }}
                    className="absolute inset-0 flex flex-col items-center justify-center px-6 z-40"
                >
                    <div className="text-center mb-16">
                        <span className="text-cyan-400 font-bold tracking-widest uppercase text-xs mb-4 block">
                            הבטחת האיכות שלנו
                        </span>
                        <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                            שלושה עמודי תווך.
                        </h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl w-full">
                        <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl hover:border-white/20 transition-all group">
                            <ShieldCheck className="w-10 h-10 text-cyan-400 mb-6 group-hover:scale-110 transition-transform" />
                            <h3 className="text-xl font-bold text-white mb-3">נטול הטיות מותג</h3>
                            <p className="text-white/50 text-sm leading-relaxed">
                                הפרדנו לחלוטין את מנגנון הדירוג שלנו (Trust Score) מהשפעות מסחריות. הכל מתמטי.
                            </p>
                        </div>
                        <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl hover:border-white/20 transition-all group">
                            <Database className="w-10 h-10 text-indigo-400 mb-6 group-hover:scale-110 transition-transform" />
                            <h3 className="text-xl font-bold text-white mb-3">מידע מאומת-שטח</h3>
                            <p className="text-white/50 text-sm leading-relaxed">
                                הסוכנים שלנו בודקים תרחישי שימוש מציאותיים כדי לוודא שאין הבדל בין השיווק למציאות.
                            </p>
                        </div>
                        <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl hover:border-white/20 transition-all group">
                            <Target className="w-10 h-10 text-emerald-400 mb-6 group-hover:scale-110 transition-transform" />
                            <h3 className="text-xl font-bold text-white mb-3">מיקוד בכוונת הליבה</h3>
                            <p className="text-white/50 text-sm leading-relaxed">
                                חיפוש אדריכלי שמבין מה אתה רוצה לעשות (Intent), ולא רק מילות מפתח.
                            </p>
                        </div>
                    </div>
                </motion.div>

            </div>
            
            {/* SCROLL PROGRESS INDICATOR */}
            <div className="fixed left-8 top-1/2 -translate-y-1/2 flex flex-col gap-4 z-50">
                {[0, 1, 2, 3].map(i => {
                    const isActive = useTransform(smoothProgress, [i * 0.25, (i + 1) * 0.25], [1, 0.3]);
                    return (
                        <motion.div 
                            key={i}
                            style={{ opacity: isActive }}
                            className="w-1 h-8 bg-cyan-500 rounded-full"
                        />
                    );
                })}
            </div>

        </div>
    );
}
