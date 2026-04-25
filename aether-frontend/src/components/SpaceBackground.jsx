import React from 'react';

export default function SpaceBackground() {
    return (
        <div className="fixed inset-0 w-screen h-screen pointer-events-none -z-10 bg-[#02050a] overflow-hidden">
            {/* 1. Deep Atmospheric Glows (The 'Premium' Layer) */}
            <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-cyan-500/10 blur-[120px] rounded-full animate-atmospheric" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] bg-indigo-600/10 blur-[150px] rounded-full animate-atmospheric [animation-delay:-5s]" />
            <div className="absolute top-[20%] right-[10%] w-[40%] h-[40%] bg-emerald-500/5 blur-[100px] rounded-full animate-atmospheric [animation-delay:-12s]" />

            {/* 2. Layered Twinkling Starfield */}
            <div className="absolute inset-0 opacity-[0.4]">
                <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <pattern id="star-pattern-rich-1" width="100" height="100" patternUnits="userSpaceOnUse">
                            <circle cx="15" cy="20" r="0.8" fill="#ffffff" opacity="0.8" />
                            <circle cx="85" cy="15" r="0.5" fill="#ffffff" opacity="0.4" />
                            <circle cx="60" cy="40" r="1.1" fill="#ffffff" opacity="0.6" />
                            <circle cx="25" cy="75" r="0.6" fill="#ffffff" opacity="0.3" />
                            <circle cx="70" cy="85" r="0.9" fill="#ffffff" opacity="0.5" />
                        </pattern>
                        <pattern id="star-pattern-rich-2" width="200" height="200" patternUnits="userSpaceOnUse">
                            <circle cx="40" cy="150" r="0.7" fill="#ffffff" opacity="0.4" />
                            <circle cx="160" cy="50" r="1.2" fill="#ffffff" opacity="0.6" />
                            <circle cx="100" cy="100" r="0.5" fill="#ffffff" opacity="0.3" />
                            <circle cx="180" cy="180" r="0.8" fill="#ffffff" opacity="0.5" />
                        </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#star-pattern-rich-1)" />
                    <rect width="100%" height="100%" fill="url(#star-pattern-rich-2)" />
                </svg>
            </div>
            
            {/* 3. Global Vignette for Depth */}
            <div className="absolute inset-0 bg-gradient-radial from-transparent via-[#02050a]/40 to-[#02050a] pointer-events-none" />
        </div>
    );
}

