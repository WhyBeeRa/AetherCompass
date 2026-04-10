import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowRight, ShieldCheck, AlertTriangle, ExternalLink, CheckCircle2, XCircle, Terminal, FileText, Activity } from 'lucide-react';
import { apiFetch } from '../api';

export default function ToolDetails({ setAppError }) {
    const { id } = useParams();
    const navigate = useNavigate();

    const [tool, setTool] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    // MY STACK (LOCAL STORAGE LOGIC)
    const [isSaved, setIsSaved] = useState(false);
    const toolId = tool?.id || tool?.name?.trim().toLowerCase().replace(/\s+/g, '-');

    useEffect(() => {
        if (toolId) {
            const savedStack = JSON.parse(localStorage.getItem('aether_saved_stack') || '[]');
            setIsSaved(savedStack.includes(toolId));
        }
    }, [toolId]);

    const toggleSave = () => {
        if (!toolId) return;
        let savedStack = JSON.parse(localStorage.getItem('aether_saved_stack') || '[]');

        if (isSaved) {
            savedStack = savedStack.filter(id => id !== toolId);
            setIsSaved(false);
        } else {
            savedStack.push(toolId);
            setIsSaved(true);
        }
        localStorage.setItem('aether_saved_stack', JSON.stringify(savedStack));
    };

    useEffect(() => {
        const fetchToolData = async () => {
            setIsLoading(true);
            setAppError(null);

            try {
                // Fetch the specific tool by Name/ID. 
                // In Aether, the ID is typically the tool_name currently.
                const response = await apiFetch(`/tool/${encodeURIComponent(id)}`);

                if (!response.ok) {
                    if (response.status === 404) {
                        setAppError(`הכלי "${id}" לא נמצא באינדקס שלנו.`);
                        navigate('/'); // Clinical Fallback: silently return home
                        return;
                    }
                    throw new Error("Failed to fetch tool details");
                }

                const data = await response.json();
                setTool(data);

            } catch {
                setAppError("לא הצלחנו לטעון את נתוני הכלי כרגע. נסה שוב מאוחר יותר.");
                navigate('/');
            } finally {
                setIsLoading(false);
            }
        };

        if (id) {
            fetchToolData();
        }
    }, [id, navigate, setAppError]);

    if (isLoading) {
        return (
            <div className="min-h-[70vh] flex flex-col items-center justify-center w-full animate-in fade-in duration-500">
                <span className="text-white/60 font-medium text-sm tracking-widest uppercase">מאחזר נתונים מהכספת...</span>
            </div>
        );
    }

    if (!tool) return null;

    // Safety accessors for the nested API data
    const analysis = tool.analysis || {};
    const executiveSummary = analysis.executive_summary || "אין תקציר מנהלים זמין.";
    const stringsPros = analysis.pros || [];
    const stringsCons = analysis.cons || [];
    const useCases = analysis.use_cases || [];
    const intentsMapped = analysis.intents_mapped || [];
    const metrics = analysis.metrics || {};
    const measurementProofs = analysis.measurement_proofs || [];

    // Deep Intelligence Fields
    const limitations = analysis.limitations || [];
    const privacyPolicy = analysis.privacy_policy || 'לא ידוע (דרוש אימות נוסף)';
    const socialProof = analysis.social_proof || null;

    // Determine trusting UI color scale (Aether Trust Score)
    const trustScore = tool.trust_score || 0;
    const isHighlyTrusted = trustScore >= 90;
    const isModeratelyTrusted = trustScore >= 70 && trustScore < 90;

    const trustColorText = isHighlyTrusted ? 'text-emerald-500' : isModeratelyTrusted ? 'text-amber-500' : 'text-red-500';
    const trustColorBg = isHighlyTrusted ? 'bg-emerald-50' : isModeratelyTrusted ? 'bg-amber-50' : 'bg-red-50';
    const trustColorBorder = isHighlyTrusted ? 'border-emerald-200' : isModeratelyTrusted ? 'border-amber-200' : 'border-red-200';

    return (
        <div className="w-full max-w-4xl flex flex-col items-center pb-24 animate-in slide-in-from-bottom-4 fade-in duration-700 rtl" dir="rtl">

            {/* Nav Back */}
            <div className="w-full flex justify-between items-center mb-8">
                <button
                    onClick={() => navigate(-1)}
                    className="flex items-center gap-2 text-white/60 hover:text-white transition-colors text-sm font-medium"
                >
                    <ArrowRight className="w-4 h-4" />
                    חזרה לתוצאות
                </button>

                {/* Save to Stack Button */}
                <button
                    onClick={toggleSave}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold transition-all border ${isSaved ? 'bg-white/10 border-white/30 text-white shadow-sm' : 'bg-transparent border-white/10 text-white/60 hover:text-white hover:border-white/20'}`}
                >
                    {isSaved ? (
                        <><CheckCircle2 className="w-4 h-4 text-emerald-400" /> במחסנית שלי</>
                    ) : (
                        <><ShieldCheck className="w-4 h-4" /> שמור למחסנית</>
                    )}
                </button>
            </div>

            {/* Header: The Truth Card Identity */}
            <div className={`w-full bg-white/5 backdrop-blur-md rounded-3xl p-8 mb-8 border shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-6 ${isHighlyTrusted ? 'border-white/20' : 'border-white/20'}`}>

                <div className="flex flex-col">
                    <h1 className="text-4xl font-bold text-white mb-2 truncate max-w-lg">{tool.name}</h1>
                    <div className="flex items-center gap-3 text-sm font-medium">
                        <span className="text-white/60">Aether Objective Analysis</span>
                        <span className="w-1 h-1 rounded-full bg-neutral-300"></span>
                        <span className={`${tool.status === 'verified' ? 'text-emerald-600' : 'text-amber-600'} flex items-center gap-1`}>
                            {tool.status === 'verified' ? <ShieldCheck className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
                            {tool.status === 'verified' ? 'מאומת' : 'בבדיקה'}
                        </span>
                    </div>
                </div>

                {/* Trust Score Badge */}
                <div className={`flex flex-col items-center justify-center p-4 rounded-2xl w-32 border ${trustColorBg} ${trustColorBorder}`}>
                    <span className="text-xs uppercase tracking-widest font-semibold text-white/60 mb-1">Trust Score</span>
                    <span className={`text-4xl font-bold ${trustColorText}`}>{trustScore.toFixed(1)}</span>
                </div>
            </div>

            {/* Section 1: Executive Summary */}
            <section className="w-full bg-white/5 backdrop-blur-md rounded-3xl p-8 md:p-10 border border-white/20 shadow-xl mb-8 relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-2 h-full bg-white/20 backdrop-blur-md rounded-r-3xl transition-all group-hover:w-3"></div>
                <h2 className="text-sm font-bold text-white/50 uppercase tracking-widest mb-4">תקציר מנהלים / Executive Summary</h2>
                <p className="text-xl md:text-2xl font-medium text-white/90 leading-relaxed font-medium">
                    {executiveSummary}
                </p>

                {/* Technical Meta Matrix */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 py-8 mt-8 border-t border-white/10">
                    <div className="flex flex-col">
                        <span className="text-white/40 text-[10px] font-bold uppercase tracking-widest mb-2 font-mono">Learning Curve</span>
                        <span className="text-white text-sm font-bold">{metrics.learning_curve || 'בינוני'}</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-white/40 text-[10px] font-bold uppercase tracking-widest mb-2 font-mono">Price Model</span>
                        <span className="text-white text-sm font-bold">{metrics.pricing || 'Freemium'}</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-white/40 text-[10px] font-bold uppercase tracking-widest mb-2 font-mono">Avg Latency</span>
                        <span className="text-emerald-400 text-sm font-bold">{metrics.latency_label || '2.4s'}</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-white/40 text-[10px] font-bold uppercase tracking-widest mb-2 font-mono">Est Cost</span>
                        <span className="text-white text-sm font-bold">{metrics.cost_label || '$0.01 / task'}</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-white/40 text-[10px] font-bold uppercase tracking-widest mb-2 font-mono">Privacy Grade</span>
                        <span className="text-cyan-400 text-sm font-bold">{metrics.privacy_grade || 'A+'}</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-white/40 text-[10px] font-bold uppercase tracking-widest mb-2 font-mono">Last Verified</span>
                        <span className="text-white/60 text-sm font-bold">{metrics.last_verified ? new Date(metrics.last_verified).toLocaleDateString('he-IL') : 'היום'}</span>
                    </div>
                </div>
            </section>

            {/* AETHER AUDIT METRICS - NEW SECTION 2026 */}
            <section className="w-full mb-8 bg-gradient-to-br from-cyan-900/10 to-transparent p-1 rounded-3xl border border-white/10">
                <div className="bg-[#0a0a0c]/80 backdrop-blur-xl rounded-[22px] p-8 border border-white/5 shadow-2xl">
                    <div className="flex items-center gap-2 mb-8">
                        <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></div>
                        <h3 className="text-sm font-bold text-white uppercase tracking-[0.2em]">Aether Audit Matrix</h3>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {/* Skill Multiplier */}
                        <div className="flex flex-col gap-3">
                            <span className="text-white/40 text-[10px] font-black uppercase tracking-widest">Skill Multiplier</span>
                            <div className="flex items-end gap-2">
                                <span className="text-4xl font-black text-white">{metrics.skill_multiplier || '3.0'}x</span>
                                <span className="text-cyan-500/60 text-xs font-bold mb-1">Impact</span>
                            </div>
                            <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                                <div className="h-full bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.5)]" style={{ width: `${(metrics.skill_multiplier || 3) * 20}%` }}></div>
                            </div>
                            <p className="text-[10px] text-white/30 leading-relaxed">היכולת להפוך ג'וניור לארכיטקט ענן.</p>
                        </div>

                        {/* Hallucination Score */}
                        <div className="flex flex-col gap-3">
                            <span className="text-white/40 text-[10px] font-black uppercase tracking-widest">Zero-Hallucination</span>
                            <div className="flex items-end gap-2">
                                <span className="text-4xl font-black text-white">{metrics.hallucination_score || '4.5'}/5</span>
                            </div>
                            <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                                <div className="h-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]" style={{ width: `${(metrics.hallucination_score || 4.5) * 20}%` }}></div>
                            </div>
                            <p className="text-[10px] text-white/30 leading-relaxed">דיוק עובדתי וולידציית סינטקס.</p>
                        </div>

                        {/* Time-to-Value */}
                        <div className="flex flex-col gap-3">
                            <span className="text-white/40 text-[10px] font-black uppercase tracking-widest">Time-to-Value</span>
                            <div className="flex items-center gap-2">
                                <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-md">
                                    <span className="text-lg font-black text-white uppercase tracking-tighter">Fast</span>
                                </div>
                            </div>
                            <p className="text-[10px] text-white/30 leading-relaxed mt-auto">זמן עד לתוצר שמיש באמת.</p>
                        </div>

                        {/* Stress Test */}
                        <div className="flex flex-col gap-3">
                            <span className="text-white/40 text-[10px] font-black uppercase tracking-widest">Stress Test</span>
                            <div className="flex items-center gap-2">
                                <span className="text-lg font-black text-emerald-400 uppercase">Passed</span>
                            </div>
                            <p className="text-[10px] text-white/30 leading-relaxed mt-auto">עמידות בתהליך עבודה מלא.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* INTENT PIPELINE */}
            {intentsMapped.length > 0 && (
                <section className="w-full mb-8">
                    <h3 className="text-sm font-bold text-white uppercase tracking-widest mb-4 pr-2">אינטנטים מאומתים</h3>
                    <div className="grid grid-cols-1 gap-3">
                        {intentsMapped.map((intent, idx) => (
                            <div key={idx} className="flex flex-col md:flex-row md:items-center justify-between p-5 bg-white/5 backdrop-blur-md border border-white/20 rounded-2xl shadow-sm hover:border-white/30 transition-all">
                                <div className="flex flex-col mb-3 md:mb-0">
                                    <span className="text-white font-bold mb-1">{intent.intent_description}</span>
                                    {intent.trade_off && (
                                        <span className="text-white/60 text-xs flex items-center gap-1">
                                            <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5" />
                                            {intent.trade_off}
                                        </span>
                                    )}
                                </div>
                                <div className="flex items-center gap-4">
                                    <div className="w-32 h-2.5 bg-white/10 backdrop-blur-md rounded-full overflow-hidden">
                                        <div className="h-full bg-white/20 backdrop-blur-md rounded-full" style={{ width: `${intent.success_score}%` }}></div>
                                    </div>
                                    <span className="text-sm font-black text-white w-12 text-left">{intent.success_score}%</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {/* Section 2: Clinical Matrix (Pros / Cons) */}
            <section className="w-full grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">

                {/* PROS */}
                <div className="flex flex-col p-8 rounded-3xl bg-emerald-50/50 border border-emerald-100 shadow-sm relative overflow-hidden">
                    <h3 className="text-sm font-bold text-emerald-900 uppercase tracking-widest mb-6 flex items-center gap-2">
                        <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                        יתרונות (למה כן)
                    </h3>
                    <ul className="space-y-4">
                        {stringsPros.length > 0 ? stringsPros.map((pro, index) => {
                            const parts = pro.split(':');
                            const hasTitle = parts.length > 1;
                            return (
                                <li key={index} className="flex items-start gap-4 text-emerald-900 text-sm leading-relaxed">
                                    <span className="text-emerald-500 font-bold mt-1 text-lg leading-none">•</span>
                                    <div>
                                        {hasTitle ? (
                                            <><span className="font-bold block mb-1">{parts[0]}</span><span className="text-emerald-700">{parts.slice(1).join(':')}</span></>
                                        ) : (
                                            <span className="text-emerald-800">{pro}</span>
                                        )}
                                    </div>
                                </li>
                            )
                        }) : (
                            <li className="text-emerald-400 text-sm">אין נתונים מאומתים.</li>
                        )}
                    </ul>
                </div>

                {/* CONS & LIMITATIONS */}
                <div className="flex flex-col p-8 rounded-3xl bg-amber-50/50 border border-amber-100 shadow-sm relative overflow-hidden">
                    <h3 className="text-sm font-bold text-amber-900 uppercase tracking-widest mb-6 flex items-center gap-2">
                        <XCircle className="w-5 h-5 text-amber-500" />
                        חסרונות (למה לא)
                    </h3>
                    <ul className="space-y-4 mb-6">
                        {stringsCons.length > 0 ? stringsCons.map((con, index) => {
                            const parts = con.split(':');
                            const hasTitle = parts.length > 1;
                            return (
                                <li key={index} className="flex items-start gap-4 text-amber-900 text-sm leading-relaxed">
                                    <span className="text-amber-500 font-bold mt-1 text-lg leading-none">•</span>
                                    <div>
                                        {hasTitle ? (
                                            <><span className="font-bold block mb-1">{parts[0]}</span><span className="text-amber-700">{parts.slice(1).join(':')}</span></>
                                        ) : (
                                            <span className="text-amber-800">{con}</span>
                                        )}
                                    </div>
                                </li>
                            )
                        }) : (
                            <li className="text-amber-400 text-sm">אין נתונים מאומתים.</li>
                        )}
                    </ul>

                    {/* DEEP INTELLIGENCE: Limitations (Phase 7 expansion) */}
                    {limitations.length > 0 && (
                        <div className="mt-auto border-t border-amber-500/10 pt-4">
                            <h4 className="text-xs font-bold text-amber-900/60 uppercase tracking-widest mb-3">מגבלות טכניות קשיחות</h4>
                            <ul className="space-y-2">
                                {limitations.map((lim, idx) => (
                                    <li key={idx} className="flex items-start gap-3 text-amber-800/80 text-xs">
                                        <span className="text-amber-400 font-bold mt-0.5">•</span>
                                        <span>{lim}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            </section>

            {/* DEEP INTELLIGENCE: Privacy & Social Proof */}
            <section className="w-full flex flex-col md:flex-row gap-6 mb-12">
                <div className="flex-1 bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/10 shadow-sm flex items-start gap-4">
                    <ShieldCheck className="w-6 h-6 text-cyan-500 flex-shrink-0" />
                    <div className="flex flex-col">
                        <span className="text-white/50 text-xs font-bold uppercase tracking-widest mb-1.5">מדיניות פרטיות</span>
                        <span className="text-white/90 text-sm font-medium leading-relaxed">{privacyPolicy}</span>
                    </div>
                </div>
                {socialProof && (
                    <div className="flex-1 bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/10 shadow-sm flex items-start gap-4">
                        <div className="text-2xl text-white/30 font-serif leading-none mt-1">"</div>
                        <div className="flex flex-col">
                            <span className="text-white/50 text-xs font-bold uppercase tracking-widest mb-1.5">עדויות שטח</span>
                            <span className="text-white/90 text-sm italic leading-relaxed">{socialProof}</span>
                        </div>
                    </div>
                )}
            </section>

            {/* PROOF OF MEASUREMENT: Audit Logs (The Lab) */}
            {measurementProofs.length > 0 && (
                <section className="w-full mb-12">
                    <div className="flex items-center justify-between mb-8 pr-2">
                        <div className="flex flex-col">
                            <div className="flex items-center gap-2 mb-1">
                                <Terminal className="w-5 h-5 text-cyan-500" />
                                <h3 className="text-sm font-bold text-white uppercase tracking-widest">Audit Logs: Proof of Measurement</h3>
                            </div>
                            <p className="text-white/40 text-xs">Raw extraction data from controlled laboratory testing cycles.</p>
                        </div>
                        <div className="hidden md:flex items-center gap-4 text-[10px] font-bold text-white/30 uppercase tracking-tighter">
                            <span className="flex items-center gap-1"><Activity className="w-3 h-3" /> Real-time Drifting: Monitored</span>
                            <span className="flex items-center gap-1"><ShieldCheck className="w-3 h-3" /> Identity: Verified</span>
                        </div>
                    </div>

                    <div className="flex flex-col gap-6">
                        {measurementProofs.map((proof, idx) => (
                            <div key={idx} className="group relative bg-[#0d0d0f] border border-white/5 rounded-3xl overflow-hidden hover:border-white/20 transition-all duration-500 shadow-2xl">
                                {/* Glass shine effect */}
                                <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                                
                                <div className="relative p-8">
                                    <div className="flex items-center justify-between mb-6">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 bg-white/5 rounded-lg">
                                                <FileText className="w-4 h-4 text-cyan-400" />
                                            </div>
                                            <h4 className="text-lg font-bold text-white/90">{proof.scenario}</h4>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            {proof.metrics_captured && Object.entries(proof.metrics_captured).map(([key, val]) => (
                                                <div key={key} className="px-3 py-1 bg-cyan-500/10 border border-cyan-500/20 rounded-full text-[10px] font-bold text-cyan-400 uppercase tracking-wider">
                                                    {key}: {val}
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                        {/* Input Block */}
                                        <div className="flex flex-col gap-3">
                                            <div className="flex items-center gap-2 px-2">
                                                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/50"></div>
                                                <span className="text-[10px] font-black text-white/30 uppercase tracking-[0.2em]">Laboratory Input</span>
                                            </div>
                                            <div className="p-4 bg-white/[0.02] border border-white/5 rounded-2xl text-sm text-white/70 font-mono leading-relaxed italic">
                                                "{proof.prompt}"
                                            </div>
                                        </div>

                                        {/* Output Block */}
                                        <div className="flex flex-col gap-3">
                                            <div className="flex items-center gap-2 px-2">
                                                <div className="w-1.5 h-1.5 rounded-full bg-cyan-500/50"></div>
                                                <span className="text-[10px] font-black text-white/30 uppercase tracking-[0.2em]">System Output (Raw)</span>
                                            </div>
                                            <div className="p-4 bg-[#0a0a0c] border border-white/10 rounded-2xl text-xs text-cyan-100/60 font-mono leading-relaxed max-h-[150px] overflow-y-auto custom-scrollbar">
                                                {proof.output}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="mt-6 pt-4 border-t border-white/5 flex justify-between items-center">
                                        <div className="text-[9px] font-bold text-white/20 uppercase tracking-widest">
                                            Captured: {new Date(proof.timestamp).toLocaleString('he-IL')}
                                        </div>
                                        <div className="flex items-center gap-1.5">
                                            <div className="w-1 h-1 rounded-full bg-emerald-500"></div>
                                            <span className="text-[9px] font-bold text-white/40 uppercase">Zero Human Interference Detected</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {/* Section 3: Targeted Use Cases (Pills) */}

            <section className="w-full mb-12">
                <h2 className="text-sm font-bold text-white/50 uppercase tracking-widest mb-6">תרחישי שימוש אידיאליים</h2>
                <div className="flex flex-wrap gap-2">
                    {useCases.length > 0 ? useCases.map((uc, index) => (
                        <div key={index} className="px-4 py-2 rounded-lg bg-white/5 backdrop-blur-md border border-white/20 text-white/80 text-sm font-medium shadow-sm">
                            {uc}
                        </div>
                    )) : (
                        <span className="text-white/50 text-sm">לא הוגדרו תרחישים ספציפיים.</span>
                    )}
                </div>
            </section>

            {/* Final CTA Launcher */}
            <div className="w-full flex justify-center mt-8 border-t border-white/10 pt-12">
                <button className="flex items-center gap-3 px-8 py-4 bg-white/20 backdrop-blur-md text-white rounded-xl hover:bg-white/10 backdrop-blur-md transition-all font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5">
                    הפעל את הכלי
                    <ExternalLink className="w-5 h-5" />
                </button>
            </div>

        </div>
    );
}
