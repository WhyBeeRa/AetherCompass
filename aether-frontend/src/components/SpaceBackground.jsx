import React from 'react';

export default function SpaceBackground() {
    return (
        <div className="fixed inset-0 w-screen h-screen pointer-events-none -z-10 bg-[#02050a] overflow-hidden">
            {/* Enhanced Nebula Glows (Slightly more vivid and expansive) */}
            <div className="absolute top-[5%] left-[10%] w-[40vw] h-[40vw] rounded-full bg-cyan-500/10 blur-[130px] mix-blend-screen animate-pulse duration-[8000ms]" />
            <div className="absolute bottom-[10%] right-[5%] w-[50vw] h-[50vw] rounded-full bg-emerald-500/10 blur-[160px] mix-blend-screen animate-pulse duration-[10000ms]" />
            <div className="absolute top-[40%] left-[60%] w-[30vw] h-[30vw] rounded-full bg-blue-600/5 blur-[120px] mix-blend-screen" />

            {/* Enhanced Minimalist Twinkling Starfield */}
            <div className="absolute inset-0 opacity-[0.35]">
                <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <pattern id="star-pattern-1" width="100" height="100" patternUnits="userSpaceOnUse">
                            <circle cx="15" cy="20" r="1.5" fill="#ffffff" opacity="0.8" />
                            <circle cx="60" cy="40" r="1.8" fill="#cffafe" opacity="0.4" />
                            <circle cx="45" cy="85" r="1.0" fill="#ffffff" opacity="0.6" />
                            <circle cx="90" cy="10" r="2.2" fill="#ffffff" opacity="0.3" />
                            <circle cx="25" cy="70" r="0.8" fill="#bae6fd" opacity="0.5" />
                        </pattern>
                        <pattern id="star-pattern-2" width="150" height="150" patternUnits="userSpaceOnUse">
                            <circle cx="20" cy="110" r="1.2" fill="#ffffff" opacity="0.7" />
                            <circle cx="120" cy="65" r="2.5" fill="#bae6fd" opacity="0.5" />
                            <circle cx="75" cy="25" r="0.8" fill="#ffffff" opacity="0.9" />
                            <circle cx="140" cy="130" r="1.8" fill="#ffffff" opacity="0.4" />
                            <circle cx="95" cy="100" r="1.0" fill="#ccfbf1" opacity="0.6" />
                        </pattern>
                        <pattern id="star-pattern-3" width="250" height="250" patternUnits="userSpaceOnUse">
                            <circle cx="50" cy="50" r="2.0" fill="#ffffff" opacity="0.3" />
                            <circle cx="180" cy="190" r="1.5" fill="#a5f3fc" opacity="0.4" />
                            <circle cx="220" cy="30" r="1.0" fill="#ffffff" opacity="0.8" />
                        </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#star-pattern-1)" />
                    <rect width="100%" height="100%" fill="url(#star-pattern-2)" />
                    <rect width="100%" height="100%" fill="url(#star-pattern-3)" />
                </svg>
            </div>
        </div>
    );
}
