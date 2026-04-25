import React, { useState, useEffect } from 'react';
import { Cpu, Search, Sparkles, Database } from 'lucide-react';

const PremiumSearchSkeleton = () => {
    const [statusIndex, setStatusIndex] = useState(0);
    const statuses = [
        "Architecting matching results based on user intent...",
        "Cross-referencing Vault data for verified performance...",
        "Calculating alignment and trust-score weights...",
        "Finalizing top 3 architectural matches...",
    ];

    useEffect(() => {
        const interval = setInterval(() => {
            setStatusIndex((prev) => (prev + 1) % statuses.length);
        }, 3000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="w-full flex flex-col gap-6 mt-4 mb-20 animate-in fade-in duration-700">
            {/* Main Status Message */}
            <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
                <div className="relative mb-6">
                    <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center animate-pulse">
                        <Cpu className="w-8 h-8 text-cyan-400" />
                    </div>
                    <div className="absolute -inset-2 bg-cyan-400/20 blur-xl rounded-full -z-10 animate-pulse delay-75"></div>
                    <div className="absolute top-0 right-0 w-3 h-3 bg-indigo-500 rounded-full animate-ping"></div>
                </div>
                <h3 className="text-xl font-medium text-white mb-2 transition-all duration-500">
                    {statuses[statusIndex]}
                </h3>
                <p className="text-white/40 text-sm tracking-widest uppercase font-bold">
                    Aether Intelligence Engine
                </p>
            </div>

            {/* Skeleton Cards */}
            {[1, 2, 3].map((i) => (
                <div key={i} className="flex flex-col p-8 rounded-3xl bg-white/5 backdrop-blur-md border border-white/10 relative overflow-hidden">
                    {/* Shimmer Effect */}
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full animate-[shimmer_2s_infinite]"></div>
                    
                    <div className="flex justify-between items-start mb-6">
                        <div className="flex flex-col gap-3 w-2/3">
                            <div className="h-8 bg-white/10 rounded-lg w-1/2 animate-pulse"></div>
                            <div className="h-4 bg-emerald-500/10 rounded w-1/3 animate-pulse"></div>
                            <div className="space-y-2 mt-4">
                                <div className="h-3 bg-white/5 rounded w-full animate-pulse"></div>
                                <div className="h-3 bg-white/5 rounded w-5/6 animate-pulse"></div>
                            </div>
                        </div>
                        <div className="w-20 h-8 bg-white/10 rounded-md animate-pulse"></div>
                    </div>

                    <div className="grid grid-cols-3 gap-6 py-5 my-5 border-t border-b border-white/5">
                        {[1, 2, 3].map((j) => (
                            <div key={j} className={`flex flex-col gap-2 ${j > 1 ? 'border-r border-white/10 pr-6' : ''}`}>
                                <div className="h-2 bg-white/5 rounded w-1/2 animate-pulse"></div>
                                <div className="h-4 bg-white/10 rounded w-3/4 animate-pulse"></div>
                            </div>
                        ))}
                    </div>

                    <div className="flex justify-between items-center mt-2">
                        <div className="h-6 bg-white/5 rounded w-32 animate-pulse"></div>
                        <div className="h-10 bg-white/10 rounded-xl w-40 animate-pulse"></div>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default PremiumSearchSkeleton;
