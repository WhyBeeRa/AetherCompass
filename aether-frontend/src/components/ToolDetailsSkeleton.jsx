import React from 'react';

const ToolDetailsSkeleton = () => {
    return (
        <div className="w-full max-w-4xl flex flex-col items-center pb-24 animate-in fade-in duration-700 rtl" dir="rtl">
            {/* Nav Back Skeleton */}
            <div className="w-full flex justify-between items-center mb-8">
                <div className="h-4 bg-white/10 rounded w-32 animate-pulse"></div>
                <div className="h-10 bg-white/10 rounded-xl w-40 animate-pulse"></div>
            </div>

            {/* Header Skeleton */}
            <div className="w-full bg-white/5 backdrop-blur-md rounded-3xl p-8 mb-8 border border-white/10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 overflow-hidden relative">
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full animate-[shimmer_2s_infinite]"></div>
                <div className="flex flex-col gap-4 w-full md:w-2/3">
                    <div className="h-10 bg-white/10 rounded-lg w-3/4 animate-pulse"></div>
                    <div className="flex items-center gap-3">
                        <div className="h-4 bg-white/5 rounded w-24 animate-pulse"></div>
                        <div className="w-1 h-1 rounded-full bg-neutral-800"></div>
                        <div className="h-4 bg-emerald-500/10 rounded w-16 animate-pulse"></div>
                    </div>
                </div>
                <div className="w-32 h-24 bg-white/10 rounded-2xl animate-pulse"></div>
            </div>

            {/* Content Blocks Skeletons */}
            <div className="w-full bg-white/5 backdrop-blur-md rounded-3xl p-10 border border-white/10 shadow-xl mb-8 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full animate-[shimmer_2s_infinite]"></div>
                <div className="h-3 bg-white/5 rounded w-48 mb-6 animate-pulse"></div>
                <div className="space-y-4 mb-10">
                    <div className="h-6 bg-white/10 rounded w-full animate-pulse"></div>
                    <div className="h-6 bg-white/10 rounded w-5/6 animate-pulse"></div>
                    <div className="h-6 bg-white/10 rounded w-4/6 animate-pulse"></div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 pt-8 border-t border-white/5">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <div key={i} className="flex flex-col gap-2">
                            <div className="h-2 bg-white/5 rounded w-1/2 animate-pulse"></div>
                            <div className="h-4 bg-white/10 rounded w-3/4 animate-pulse"></div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
                {[1, 2].map((i) => (
                    <div key={i} className="h-64 bg-white/5 border border-white/10 rounded-3xl p-8 animate-pulse"></div>
                ))}
            </div>
        </div>
    );
};

export default ToolDetailsSkeleton;
