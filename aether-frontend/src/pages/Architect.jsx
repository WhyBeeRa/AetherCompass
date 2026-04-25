import React, { useState } from 'react';
import { Activity, GitBranch, ArrowRight, Save, Plus, Trash2, Settings, Zap, Play } from 'lucide-react';

export default function Architect() {
    const [workflowName, setWorkflowName] = useState('New Blueprint');
    const [steps, setSteps] = useState([
        { id: 1, tool: 'Whisper Large V3', action: 'Transcribe Podcast to Text', config: 'Precision Mode' },
        { id: 2, tool: 'GPT-4o', action: 'Summarize to Key Points', config: 'Concise' }
    ]);

    const addStep = () => {
        const newStep = {
            id: Date.now(),
            tool: 'Select Tool...',
            action: 'Select Action...',
            config: 'Default'
        };
        setSteps([...steps, newStep]);
    };

    const removeStep = (id) => {
        setSteps(steps.filter(s => s.id !== id));
    };

    return (
        <div className="w-full min-h-screen pt-24 pb-24 ltr animate-in fade-in duration-700 bg-black text-white" dir="ltr">
            <main className="max-w-7xl mx-auto px-6">
                
                {/* Header Section */}
                <div className="flex flex-col md:flex-row justify-between items-center gap-6 mb-16">
                    <div>
                        <div className="flex items-center gap-3 mb-4 justify-center md:justify-start">
                            <div className="p-2 bg-emerald-500 rounded-lg">
                                <Activity className="w-6 h-6 text-black" />
                            </div>
                            <span className="text-emerald-400 font-black uppercase tracking-tighter text-sm">
                                AI Architecture Lab
                            </span>
                        </div>
                        <h1 className="text-4xl md:text-5xl font-black tracking-tight mb-2 text-center md:text-left">
                            AI <span className="text-emerald-500">Architect</span>
                        </h1>
                        <p className="text-white/50 font-medium text-center md:text-left">
                            Don't just collect tools—build machines. We provide the full architectural blueprint.
                        </p>
                    </div>
                    
                    <div className="flex gap-4">
                        <button className="flex items-center gap-2 px-6 py-3 bg-white/5 border border-white/10 rounded-xl font-bold text-sm hover:bg-white/10 transition-all">
                            <Save className="w-4 h-4" /> Save Blueprint
                        </button>
                        <button className="flex items-center gap-2 px-8 py-3 bg-emerald-500 text-black rounded-xl font-black text-sm hover:bg-emerald-400 shadow-lg shadow-emerald-500/20 transition-all">
                            <Play className="w-4 h-4 fill-current" /> Execute Workflow
                        </button>
                    </div>
                </div>

                {/* Workflow Builder Grid */}
                <div className="grid grid-cols-1 md:grid-cols-12 gap-12">
                    
                    {/* Sidebar / Tools */}
                    <div className="md:col-span-3 space-y-6">
                        <div className="bg-white/[0.03] border border-white/10 rounded-2xl p-6">
                            <h3 className="text-xs font-black text-white/30 uppercase tracking-[0.2em] mb-6">Component Library</h3>
                            <div className="space-y-3">
                                {['Audio Translation', 'Language Processing', 'Image Generation', 'Video Editing', 'Automation (Zapier)'].map((cat, i) => (
                                    <div key={i} className="p-4 bg-white/[0.02] border border-white/5 rounded-xl text-sm font-bold text-white/70 hover:bg-white/5 hover:border-emerald-500/30 cursor-pointer transition-all flex justify-between items-center group">
                                        {cat}
                                        <Plus className="w-4 h-4 text-white/20 group-hover:text-emerald-500" />
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="bg-gradient-to-br from-emerald-500/20 to-transparent border border-emerald-500/20 rounded-2xl p-6">
                            <h3 className="text-sm font-black text-emerald-400 mb-2 flex items-center gap-2">
                                <Zap className="w-4 h-4 fill-current" /> Smart Optimize
                            </h3>
                            <p className="text-[10px] text-white/50 font-medium leading-relaxed mb-4">
                                System detected a potential $5.20 monthly saving in this chain by swapping Whisper for Groq API.
                            </p>
                            <button className="w-full py-2 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-lg text-[10px] font-black uppercase tracking-widest hover:bg-emerald-500/30 transition-all">
                                Execute Optimization
                            </button>
                        </div>
                    </div>

                    {/* Main Canvas */}
                    <div className="md:col-span-9 relative">
                        <div className="mb-6 flex justify-between items-center">
                            <input 
                                value={workflowName}
                                onChange={(e) => setWorkflowName(e.target.value)}
                                className="bg-transparent border-none focus:ring-0 text-2xl font-black text-white p-0"
                            />
                            <div className="flex gap-2">
                                <div className="p-2 bg-white/5 rounded-lg border border-white/10 text-white/40">
                                    <Settings className="w-4 h-4" />
                                </div>
                            </div>
                        </div>

                        <div className="space-y-8 relative">
                            {/* Connection Line */}
                            <div className="absolute top-10 left-1/2 w-0.5 h-[calc(100%-80px)] bg-gradient-to-b from-emerald-500/50 to-transparent pointer-events-none hidden md:block"></div>

                            {steps.map((step, idx) => (
                                <div key={step.id} className="relative z-10">
                                    <div className="bg-white/[0.03] backdrop-blur-3xl border border-white/10 rounded-[2rem] p-8 hover:bg-white/[0.05] transition-all group border-l-4 border-l-emerald-500/50">
                                        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                                            <div className="flex gap-6 items-center">
                                                <div className="w-12 h-12 rounded-2xl bg-black border border-white/10 flex items-center justify-center font-black text-emerald-500 shadow-xl">
                                                    {idx + 1}
                                                </div>
                                                <div>
                                                    <p className="text-[10px] font-black text-white/30 uppercase tracking-widest mb-1">Step {idx + 1}</p>
                                                    <div className="flex items-center gap-3">
                                                        <h4 className="text-xl font-black text-white">{step.tool}</h4>
                                                        <ArrowRight className="w-4 h-4 text-white/20" />
                                                        <span className="text-emerald-400 font-bold">{step.action}</span>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="flex items-center gap-4 w-full md:w-auto">
                                                <div className="flex-1 md:flex-none px-4 py-2 bg-white/5 rounded-xl border border-white/5 text-xs font-bold text-white/40">
                                                    {step.config}
                                                </div>
                                                <button 
                                                    onClick={() => removeStep(step.id)}
                                                    className="p-3 text-white/20 hover:text-red-500 transition-colors"
                                                >
                                                    <Trash2 className="w-5 h-5" />
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    {idx < steps.length - 1 && (
                                        <div className="flex justify-center my-4">
                                            <div className="p-2 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                                                <GitBranch className="w-4 h-4 text-emerald-500 rotate-90" />
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}

                            <button 
                                onClick={addStep}
                                className="w-full py-6 border-2 border-dashed border-white/10 rounded-[2rem] text-white/30 font-black flex items-center justify-center gap-3 hover:border-emerald-500/30 hover:text-emerald-400 hover:bg-emerald-500/5 transition-all"
                            >
                                <Plus className="w-6 h-6" /> Add Step to Chain
                            </button>
                        </div>
                    </div>

                </div>

            </main>
        </div>
    );
}
