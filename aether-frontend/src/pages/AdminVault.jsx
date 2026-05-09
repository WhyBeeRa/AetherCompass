import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ArrowLeft, ArrowRight, Check, Image as ImageIcon, Activity, Box, Search, ExternalLink, SlidersHorizontal, Layers, Percent, Server } from 'lucide-react';
import { apiFetch } from '../api';

// Live Preview Component (Mock of Sponsored/Feed Card)
const LivePreview = ({ formData }) => {
    return (
        <div className="sticky top-24 w-full h-max">
            <div className="flex items-center gap-2 mb-4 text-white/50 text-sm font-medium uppercase tracking-wider px-2">
                <Search className="w-4 h-4" />
                Live Feed Preview
            </div>
            
            <div className="bg-aether-black border border-white/5 rounded-2xl overflow-hidden hover:border-white/10 transition-colors duration-500 relative group animate-in fade-in zoom-in duration-500">
                {/* Media Container */}
                <div className="relative h-48 w-full overflow-hidden bg-white/[0.02]">
                    <div className="absolute inset-0 bg-gradient-to-t from-aether-black via-aether-black/50 to-transparent z-10" />
                    {formData.image_url ? (
                        <img 
                            src={formData.image_url} 
                            alt={formData.name || "Preview"} 
                            className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity duration-700"
                        />
                    ) : (
                        <div className="w-full h-full flex flex-col items-center justify-center text-white/20">
                            <ImageIcon className="w-8 h-8 mb-2 opacity-50" />
                            <span className="text-xs uppercase tracking-widest">No Image Asset</span>
                        </div>
                    )}

                    {/* Trust Badge overlay */}
                    <div className="absolute top-4 right-4 z-20 flex flex-col gap-2">
                         <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-xs font-medium text-white/90">
                            {formData.trust_score >= 85 ? (
                                <ShieldAlert className="w-3.5 h-3.5 text-emerald-400" />
                            ) : formData.trust_score >= 70 ? (
                                <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
                            ) : (
                                <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                            )}
                            Score: {formData.trust_score || "0"}
                        </div>
                    </div>
                </div>

                {/* Content Container */}
                <div className="p-6 relative z-20 -mt-6">
                    <div className="flex items-start justify-between mb-3">
                        <div>
                             <div className="text-[10px] font-bold tracking-widest text-cyan-400/80 uppercase mb-1 flex items-center gap-1.5">
                                <Box className="w-3 h-3" />
                                {formData.intent_category || "Category"}
                            </div>
                            <h3 className="text-xl font-bold text-white tracking-tight">
                                {formData.name || "Tool Name"}
                            </h3>
                        </div>
                    </div>
                    
                    <p className="text-sm text-white/60 leading-relaxed mb-6 line-clamp-2 min-h-[40px]">
                        {formData.description || "Execution summary and short description of the tool's main capability."}
                    </p>

                    {/* Metrics Preview */}
                    <div className="grid grid-cols-2 gap-3 mb-6">
                        <div className="flex flex-col gap-1">
                            <span className="text-[10px] text-white/40 uppercase tracking-wider">Ease of Use</span>
                            <div className="flex gap-1">
                                {[1,2,3,4,5].map(i => (
                                    <div key={i} className={`h-1 flex-1 rounded-full ${i <= formData.ease_of_use ? 'bg-white/40' : 'bg-white/10'}`} />
                                ))}
                            </div>
                        </div>
                         <div className="flex flex-col gap-1">
                            <span className="text-[10px] text-white/40 uppercase tracking-wider">Speed</span>
                            <div className="flex gap-1">
                                {[1,2,3,4,5].map(i => (
                                    <div key={i} className={`h-1 flex-1 rounded-full ${i <= formData.speed ? 'bg-cyan-400/50' : 'bg-white/10'}`} />
                                ))}
                            </div>
                        </div>
                    </div>
                    
                    <div className="pt-4 border-t border-white/5 flex items-center justify-between">
                        <span className="text-xs text-white/40 font-medium tracking-wide">
                            {formData.pricing || "Pricing"} • {formData.learning_curve || "Learning"}
                        </span>
                        <div className="flex items-center justify-center p-2 rounded-full bg-white/5 text-white/40">
                             <ExternalLink className="w-4 h-4" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};


export default function AdminVault() {
    const { currentUser, isAdmin } = useAuth();
    const navigate = useNavigate();
    const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
    
    // Step state

    const [step, setStep] = useState(1);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitResult, setSubmitResult] = useState(null);

    const [formData, setFormData] = useState({
        name: '',
        intent_category: 'Code Development',
        description: '',
        pros: '',
        cons: '',
        use_cases: '',
        trust_score: 85,
        accuracy: 4,
        speed: 4,
        value: 4,
        ease_of_use: 4,
        pricing: 'Freemium',
        learning_curve: 'Moderate',
        visual_quality: 'Mid',
        image_url: '',
        latency_label: '2.4s',
        cost_label: '$0.01 / task',
        privacy_grade: 'Enterprise Safe',
        skill_multiplier: 3,
        hallucination_score: 4,
        integration: 'Web / API'
    });

    if (!isLocal && (!currentUser || !isAdmin)) return null;

    const handleInput = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: ['trust_score', 'accuracy', 'speed', 'value', 'ease_of_use', 'skill_multiplier', 'hallucination_score'].includes(name) 
                ? Number(value) 
                : value
        }));
    };

    const nextStep = () => setStep(s => Math.min(3, s + 1));
    const prevStep = () => setStep(s => Math.max(1, s - 1));

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        setSubmitResult(null);

        try {
            const token = isLocal ? "dev-admin-token" : await currentUser.getIdToken();
            
            // BUG-10 fix: Split comma-separated strings into arrays for backend
            const payload = {
                ...formData,
                pros: typeof formData.pros === 'string' ? formData.pros.split(',').map(s => s.trim()).filter(Boolean) : formData.pros,
                cons: typeof formData.cons === 'string' ? formData.cons.split(',').map(s => s.trim()).filter(Boolean) : formData.cons,
                use_cases: typeof formData.use_cases === 'string' ? formData.use_cases.split(',').map(s => s.trim()).filter(Boolean) : formData.use_cases,
            };

            const response = await apiFetch('/admin/vault/tool', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to save tool");
            }

            setSubmitResult({ type: 'success', message: `Tool ${formData.name} successfully added to the Vault.` });
            
            // Reset form after success
            setTimeout(() => {
                setStep(1);
                setFormData({
                    name: '', intent_category: 'Code Development', description: '', pros: '', cons: '', use_cases: '',
                    trust_score: 85, accuracy: 4, speed: 4, value: 4, ease_of_use: 4, pricing: 'Freemium',
                    image_url: '',
                    latency_label: '2.4s', cost_label: '$0.01 / task', privacy_grade: 'Enterprise Safe', 
                    skill_multiplier: 3, hallucination_score: 4,
                    integration: 'Web / API'
                });
                setSubmitResult(null);
            }, 3000);

        } catch (error) {
            console.error(error);
            setSubmitResult({ type: 'error', message: error.message });
        } finally {
            setIsSubmitting(false);
        }
    };

    const triggerLiveBenchmark = async () => {
        try {
            setIsSubmitting(true);
            const token = isLocal ? "dev-admin-token" : await currentUser.getIdToken();
            const response = await apiFetch('/api/agents/metrics/run', {
                method: 'POST',
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                setSubmitResult({ 
                    type: 'success', 
                    message: "Performance scan (Live Scan) successfully triggered in background. Metrics will update shortly." 
                });
                // Clear message after 5 seconds
                setTimeout(() => setSubmitResult(null), 5000);
            } else {
                throw new Error("Failed to trigger performance scan");
            }
        } catch (err) {
            setSubmitResult({ 
                type: 'error', 
                message: "Error triggering performance scan: " + err.message 
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const triggerDiscoveryScan = async () => {
        try {
            setIsSubmitting(true);
            const token = isLocal ? "dev-admin-token" : await currentUser.getIdToken();
            const response = await apiFetch('/api/agents/scout/run?intent=Hot%20new%20AI%20tools', {
                method: 'POST',
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                setSubmitResult({ 
                    type: 'success', 
                    message: "Autonomous scout initiated! Searching Reddit, GitHub, and major AI repositories. Results will populate shortly." 
                });
                setTimeout(() => setSubmitResult(null), 8000);
            } else {
                throw new Error("Failed to trigger discovery scout");
            }
        } catch (err) {
            setSubmitResult({ type: 'error', message: "Error: " + err.message });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="w-full animate-in fade-in slide-in-from-bottom-5 duration-700" dir="ltr">
            
            <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white mb-2 flex items-center gap-3">
                        <ShieldAlert className="w-8 h-8 text-cyan-400" />
                        Aether Admin Protocol
                    </h1>
                    <p className="text-white/50 text-sm">Manual Vault Entry System • Logged in as <span className="text-white/80">{currentUser?.email || 'Local Admin'}</span></p>
                </div>
                
                <div className="flex flex-wrap items-center gap-3">
                    <button 
                        onClick={triggerDiscoveryScan}
                        disabled={isSubmitting}
                        className="flex items-center gap-2 px-6 py-2.5 bg-purple-500/10 border border-purple-500/20 text-purple-400 rounded-xl text-sm font-bold hover:bg-purple-500/20 transition-all shadow-[0_0_15px_rgba(168,85,247,0.1)]"
                    >
                        <Search className={`w-4 h-4 ${isSubmitting ? 'animate-pulse' : ''}`} />
                        Discovery Scan (Reddit Scout)
                    </button>

                    <button 
                        onClick={triggerLiveBenchmark}
                        disabled={isSubmitting}
                        className="flex items-center gap-2 px-6 py-2.5 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded-xl text-sm font-bold hover:bg-cyan-500/20 transition-all"
                    >
                        <Activity className={`w-4 h-4 ${isSubmitting ? 'animate-pulse' : ''}`} />
                        Benchmark Test (Live Metrics)
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
                
                {/* Form Section (Takes up 2/3) */}
                <div className="lg:col-span-2">
                    
                    {/* Stepper Header */}
                    <div className="flex items-center gap-4 mb-8">
                        {[
                            { num: 1, label: "Basic Info", icon: Box },
                            { num: 2, label: "Metrics", icon: Activity },
                            { num: 3, label: "Assets", icon: ImageIcon }
                        ].map((s, i) => (
                            <React.Fragment key={s.num}>
                                <div className={`flex items-center gap-2 ${step === s.num ? 'text-cyan-400' : step > s.num ? 'text-white/80' : 'text-white/30'}`}>
                                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border ${step === s.num ? 'bg-cyan-500/10 border-cyan-500/30' : step > s.num ? 'bg-white/10 border-white/20' : 'border-white/10'}`}>
                                        {step > s.num ? <Check className="w-4 h-4" /> : s.num}
                                    </div>
                                    <span className="text-sm font-medium hidden sm:block">{s.label}</span>
                                </div>
                                {i < 2 && <div className={`h-px flex-1 ${step > s.num ? 'bg-white/20' : 'bg-white/5'}`} />}
                            </React.Fragment>
                        ))}
                    </div>

                    <form onSubmit={handleSubmit} className="bg-white/[0.02] border border-white/5 p-8 rounded-3xl backdrop-blur-sm relative">
                        
                        {submitResult && (
                            <div className={`mb-6 p-4 rounded-xl border ${submitResult.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-red-500/10 border-red-500/30 text-red-400'} text-sm animate-in fade-in slide-in-from-top-2`}>
                                {submitResult.message}
                            </div>
                        )}
                        {step === 1 && (
                            <div className="space-y-6 animate-in slide-in-from-right fade-in">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="space-y-2">
                                        <label className="text-xs uppercase tracking-widest text-white/50 font-medium">Tool Name</label>
                                        <input required name="name" value={formData.name} onChange={handleInput} 
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-cyan-500/50 transition-colors" 
                                            placeholder="e.g. Midjourney v6" />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs uppercase tracking-widest text-white/50 font-medium">Category / Intent</label>
                                        <select name="intent_category" value={formData.intent_category} onChange={handleInput}
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-500/50 transition-colors">
                                            <option value="Code Development">Code Development</option>
                                            <option value="Image Creation & Design">Image Creation & Design</option>
                                            <option value="Writing & Text">Writing & Text</option>
                                            <option value="Video Editing">Video Editing</option>
                                            <option value="Voiceover & Audio">Voiceover & Audio</option>
                                            <option value="Marketing & SEO">Marketing & SEO</option>
                                            <option value="Investor Decks">Investor Decks</option>
                                            <option value="Enterprise Tools">Enterprise Tools</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-xs uppercase tracking-widest text-white/50 font-medium">Executive Summary</label>
                                    <textarea required name="description" value={formData.description} onChange={handleInput} rows={3}
                                        className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-cyan-500/50 transition-colors"
                                        placeholder="Sentence 1: The Peak Capability. Sentence 2: The Core Catch." />
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="space-y-2">
                                        <label className="text-xs uppercase tracking-widest text-white/50 font-medium">Pros (Comma Separated)</label>
                                        <textarea name="pros" value={formData.pros} onChange={handleInput} rows={2}
                                            className="w-full bg-black/40 border border-emerald-500/20 rounded-xl px-4 py-3 text-emerald-100 placeholder-emerald-900/50 focus:outline-none focus:border-emerald-500/50 transition-colors"
                                            placeholder="Extremely fast API, High quality generation" />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs uppercase tracking-widest text-white/50 font-medium">Cons (Comma Separated)</label>
                                        <textarea name="cons" value={formData.cons} onChange={handleInput} rows={2}
                                            className="w-full bg-black/40 border border-rose-500/20 rounded-xl px-4 py-3 text-rose-100 placeholder-rose-900/50 focus:outline-none focus:border-rose-500/50 transition-colors"
                                            placeholder="Expensive, Requires coding knowledge" />
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-xs uppercase tracking-widest text-white/50 font-medium">Use Cases (Comma Separated Tags)</label>
                                    <input name="use_cases" value={formData.use_cases} onChange={handleInput}
                                        className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-cyan-500/50 transition-colors"
                                        placeholder="UI Design, Ad Creatives, Concept Art" />
                                </div>
                            </div>
                        )}

                        {/* --- STEP 2: METRICS --- */}
                        {step === 2 && (
                            <div className="space-y-8 animate-in slide-in-from-right fade-in">
                                
                                <div className="p-6 rounded-2xl bg-white/[0.02] border border-cyan-500/20 mb-6">
                                    <div className="flex items-center justify-between mb-2">
                                        <label className="text-sm uppercase tracking-widest text-cyan-400 font-bold flex items-center gap-2">
                                            <Percent className="w-4 h-4" /> Global Trust Score
                                        </label>
                                        <span className="text-2xl font-black text-white">{formData.trust_score}</span>
                                    </div>
                                    <input type="range" name="trust_score" min="10" max="100" value={formData.trust_score} onChange={handleInput}
                                        className="w-full h-2 bg-black/50 rounded-lg appearance-none cursor-pointer accent-cyan-400" />
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                    {[
                                        { name: 'accuracy', label: 'Accuracy / Quality' },
                                        { name: 'speed', label: 'Speed & Latency' },
                                        { name: 'value', label: 'Value for Money' },
                                        { name: 'ease_of_use', label: 'Ease of Use' }
                                    ].map(metric => (
                                        <div key={metric.name} className="space-y-3">
                                            <div className="flex justify-between items-center text-xs uppercase tracking-widest text-white/60 font-medium">
                                                <label>{metric.label}</label>
                                                <span>{formData[metric.name]} / 5</span>
                                            </div>
                                            <input type="range" name={metric.name} min="1" max="5" value={formData[metric.name]} onChange={handleInput}
                                                className="w-full h-1.5 bg-white/10 rounded-lg appearance-none cursor-pointer accent-white" />
                                            <div className="flex justify-between text-[10px] text-white/30">
                                                <span>Poor</span><span>Excellent</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6 border-t border-white/5">
                                     <div className="space-y-2">
                                        <label className="text-xs uppercase tracking-widest text-white/50 font-medium">Pricing Model</label>
                                        <select name="pricing" value={formData.pricing} onChange={handleInput}
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-cyan-500/50">
                                            <option>Free</option>
                                            <option>Freemium</option>
                                            <option>Paid (Monthly)</option>
                                            <option>Enterprise / Custom</option>
                                            <option>Pay as you go (API)</option>
                                        </select>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs uppercase tracking-widest text-white/50 font-medium">Learning Curve</label>
                                        <select name="learning_curve" value={formData.learning_curve} onChange={handleInput}
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-cyan-500/50">
                                            <option>Very Easy (No Code)</option>
                                            <option>Moderate</option>
                                            <option>Hard</option>
                                            <option>Developers Only</option>
                                        </select>
                                    </div>
                                     <div className="space-y-2">
                                        <label className="text-xs uppercase tracking-widest text-white/50 font-medium">Visual Quality</label>
                                        <select name="visual_quality" value={formData.visual_quality} onChange={handleInput}
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-cyan-500/50">
                                            <option>High</option>
                                            <option>Mid</option>
                                            <option>Low</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6 border-t border-white/5">
                                    <div className="space-y-2">
                                        <label className="text-xs uppercase tracking-widest text-white/50 font-medium text-indigo-400">Latency Label (Comparison)</label>
                                        <input name="latency_label" value={formData.latency_label} onChange={handleInput}
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-cyan-500/50"
                                            placeholder="e.g. 1.2s or 500ms" />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs uppercase tracking-widest text-white/50 font-medium text-indigo-400">Cost Label (Comparison)</label>
                                        <input name="cost_label" value={formData.cost_label} onChange={handleInput}
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-cyan-500/50"
                                            placeholder="e.g. $0.002 / image" />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs uppercase tracking-widest text-white/50 font-medium text-indigo-400">Privacy Grade</label>
                                        <input name="privacy_grade" value={formData.privacy_grade} onChange={handleInput}
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-cyan-500/50"
                                            placeholder="e.g. Enterprise Ready, B+, SOC2" />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs uppercase tracking-widest text-white/50 font-medium text-indigo-400">Integrations</label>
                                        <input name="integration" value={formData.integration} onChange={handleInput}
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-cyan-500/50"
                                            placeholder="e.g. Slack, Zapier, API" />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs uppercase tracking-widest text-white/50 font-medium text-cyan-400">Skill Multiplier (1-5)</label>
                                        <input type="number" name="skill_multiplier" min="1" max="5" value={formData.skill_multiplier} onChange={handleInput}
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-cyan-500/50" />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs uppercase tracking-widest text-white/50 font-medium text-cyan-400">Hallucination Score (1-5)</label>
                                        <input type="number" name="hallucination_score" min="1" max="5" value={formData.hallucination_score} onChange={handleInput}
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-cyan-500/50" />
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* --- STEP 3: ASSETS --- */}
                        {step === 3 && (
                            <div className="space-y-6 animate-in slide-in-from-right fade-in min-h-[300px]">
                                <div className="space-y-2">
                                    <label className="text-xs uppercase tracking-widest text-white/50 font-medium">Primary Image Asset (URL)</label>
                                    <input name="image_url" value={formData.image_url} onChange={handleInput}
                                        className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-cyan-500/50 transition-colors"
                                        placeholder="https://images.unsplash.com/photo-..." />
                                </div>
                                <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-200 text-sm">
                                    <p className="flex items-start gap-3">
                                        <ShieldAlert className="w-5 h-5 flex-shrink-0 mt-0.5" />
                                        You are about to inject raw data into the Aether Vault. Ensure all metrics and assessments are objective and free of marketing hype. This action will be logged under your administrative identity.
                                    </p>
                                </div>
                            </div>
                        )}

                        {/* Navigation Buttons */}
                        <div className="mt-10 flex items-center justify-between pt-6 border-t border-white/5">
                            <button type="button" onClick={prevStep} disabled={step === 1 || isSubmitting}
                                className="px-6 py-2.5 rounded-full text-sm font-medium text-white/60 hover:text-white hover:bg-white/5 disabled:opacity-30 flex items-center gap-2 transition-all">
                                <ArrowLeft className="w-4 h-4" /> Back
                            </button>
                            
                            {step < 3 ? (
                                <button type="button" onClick={nextStep}
                                    className="px-6 py-2.5 bg-white text-black hover:bg-white/90 rounded-full text-sm font-bold flex items-center gap-2 transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5">
                                    Next Phase <ArrowRight className="w-4 h-4" />
                                </button>
                            ) : (
                                <button type="submit" disabled={isSubmitting || !formData.name}
                                    className="px-8 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full text-sm font-bold flex items-center gap-2 hover:shadow-[0_0_20px_rgba(6,182,212,0.4)] hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:hover:shadow-none disabled:hover:translate-y-0">
                                    {isSubmitting ? (
                                        <><Layers className="w-4 h-4 animate-spin" /> Committing...</>
                                    ) : (
                                        <><Server className="w-4 h-4" /> Inject to Vault</>
                                    )}
                                </button>
                            )}
                        </div>

                    </form>
                </div>

                {/* Live Preview Section (Takes up 1/3) */}
                <div className="hidden lg:block lg:col-span-1">
                    <LivePreview formData={formData} />
                </div>
            </div>
        </div>
    );
}
