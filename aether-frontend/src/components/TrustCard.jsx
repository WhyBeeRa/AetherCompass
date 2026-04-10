import { motion } from "framer-motion";
import { Shield, ExternalLink, Activity, AlertTriangle } from "lucide-react";

export function TrustCard({ title, source, reliability, summary, type = "evidence", toolName }) {
    const isRejected = reliability < 70; // Example threshold

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="group flex flex-col gap-3 p-4 rounded-xl bg-white/20 backdrop-blur-md/40 border border-white/5 hover:border-cyan-500/30 hover:bg-white/20 backdrop-blur-md/60 hover:shadow-[0_0_20px_rgba(6,182,212,0.15)] transition-all cursor-pointer overflow-hidden backdrop-blur-sm"
        >
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-white/50 tracking-wide">
                        {source || "Unknown"}
                    </span>
                </div>

                <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-medium tracking-wide border border-white/10 ${isRejected ? 'text-rose-400 bg-rose-500/10' : 'text-emerald-400 bg-emerald-500/10'}`}>
                    {isRejected ? <AlertTriangle className="w-3 h-3" /> : <Shield className="w-3 h-3" />}
                    <span>{reliability}%</span>
                </div>
            </div>

            {/* Content */}
            <div className="space-y-1.5 mt-1">
                <h3 className="text-base font-medium text-white leading-tight group-hover:text-cyan-300 transition-colors">
                    {title || toolName}
                </h3>
                <p className="text-sm text-white/50 line-clamp-3 leading-relaxed font-light">
                    {summary}
                </p>
            </div>

            {/* Footer */}
            <div className="mt-auto pt-3 flex items-center justify-between border-t border-white/5">
                <div className="flex items-center gap-2 text-xs text-white/60">
                    <Activity className="w-3 h-3 text-cyan-500/50" />
                    <span className="capitalize">{type}</span>
                </div>
                <ExternalLink className="w-4 h-4 text-white/70 group-hover:text-cyan-400 transition-colors" />
            </div>
        </motion.div>
    );
}
