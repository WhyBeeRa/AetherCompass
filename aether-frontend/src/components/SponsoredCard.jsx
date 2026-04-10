import { motion } from "framer-motion";
import { Shield, ExternalLink, Sparkles, Zap } from "lucide-react";

export function SponsoredCard({ title, source, summary, trust_score, media_url }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="group flex flex-col gap-3 p-4 rounded-xl bg-white/20 backdrop-blur-md/40 border border-emerald-500/30 hover:border-emerald-500/60 hover:shadow-[0_0_25px_rgba(16,185,129,0.2)] hover:bg-white/20 backdrop-blur-md/70 transition-all cursor-pointer overflow-hidden backdrop-blur-sm relative"
        >
            {/* Header */}
            <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-white/50 tracking-wide">
                    {source || "Sponsored"}
                </span>

                {/* Minimal Promoted Badge */}
                <div className="flex items-center gap-1 text-[10px] font-bold text-emerald-400 tracking-widest uppercase drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]">
                    <Zap className="w-3 h-3 fill-emerald-400/20" />
                    Promoted
                </div>
            </div>

            {/* Content */}
            <div className="space-y-1 mt-1">
                <h3 className="text-base font-medium text-white leading-tight group-hover:text-emerald-300 transition-colors">
                    {title}
                </h3>
                <p className="text-sm text-white/50 line-clamp-2 leading-relaxed font-light mt-2">
                    {summary}
                </p>
            </div>

            {/* Media Preview Thumbnail (If URL exists) */}
            {media_url && (
                <div className="w-full h-24 rounded-lg overflow-hidden mt-2 border border-white/10 opacity-90 group-hover:opacity-100 transition-opacity">
                    <img src={media_url} alt={title} className="w-full h-full object-cover" />
                </div>
            )}

            {/* Footer / Tags */}
            <div className="mt-auto pt-3 flex items-center justify-between border-t border-white/5">
                <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1.5 px-2 py-0.5 rounded border border-emerald-500/30 text-[10px] font-medium text-emerald-400 bg-emerald-500/10 tracking-wide">
                        <Shield className="w-3 h-3" />
                        {trust_score}% Trust
                    </div>
                </div>
                <ExternalLink className="w-4 h-4 text-white/70 group-hover:text-emerald-400 transition-colors" />
            </div>
        </motion.div>
    );
}
