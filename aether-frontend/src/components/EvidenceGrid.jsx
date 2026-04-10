import { TrustCard } from "./TrustCard";
import { SponsoredCard } from "./SponsoredCard";
import { PulseFeedback } from "./PulseFeedback";

export function EvidenceGrid({ items, isLoading }) {
    if (isLoading) {
        return (
            <div className="relative w-full max-w-3xl mx-auto flex flex-col gap-4">
                {/* Live Feedback Area */}
                <div className="mb-4">
                    <PulseFeedback />
                </div>

                <div className="w-full space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="w-full h-32 rounded-xl bg-white/20 backdrop-blur-md/40 border border-white/5 animate-pulse relative overflow-hidden shadow-[0_0_15px_rgba(6,182,212,0.05)]" />
                    ))}
                </div>
            </div>
        );
    }

    if (!items || items.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center p-12 text-center text-white/60">
                <p>No insights found yet. Try searching for a tool.</p>
            </div>
        );
    }

    return (
        <div className="w-full max-w-3xl mx-auto flex flex-col gap-4">
            {items.map((item, index) => (
                <div key={index} className="w-full">
                    {/* Logic Gate: Sponsored vs Organic */}
                    {item.is_sponsored ? (
                        <SponsoredCard
                            title={item.title}
                            source={item.source}
                            summary={item.summary}
                            trust_score={item.trust_score}
                            media_url={item.media_url}
                            style_tags={item.style_tags}
                        />
                    ) : (
                        <TrustCard
                            title={item.title}
                            source={item.source}
                            reliability={item.trust_score}
                            summary={item.summary}
                            type={item.type || "evidence"}
                            toolName={item.tool_name}
                        />
                    )}
                </div>
            ))}
        </div>
    );
}
