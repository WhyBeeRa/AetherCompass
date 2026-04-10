import { useState, useRef, useEffect } from "react";
import { Loader2 } from "lucide-react";

export function SearchBar({ onSearch, isLoading, statusText }) {
    const [isFocused, setIsFocused] = useState(false);
    const [query, setQuery] = useState("");
    const textareaRef = useRef(null);

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
        }
    }, [query]);

    const handleSubmit = (e) => {
        if (e) e.preventDefault();
        if (!query.trim() || isLoading) return;
        onSearch(query);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    return (
        <div className="w-full relative group">
            <div className="flex flex-col gap-2">
                <form
                    onSubmit={handleSubmit}
                    className={`relative flex flex-col p-2 bg-white/20 backdrop-blur-md/40 backdrop-blur-sm transition-all duration-300 rounded-[32px] border ${isFocused
                        ? "border-cyan-500/50 shadow-[0_0_20px_rgba(6,182,212,0.15)] bg-white/20 backdrop-blur-md/60"
                        : "border-white/10 hover:border-white/20 hover:bg-white/20 backdrop-blur-md/50"
                        }`}
                    dir="rtl"
                >
                    {/* Top: Input Area */}
                    <div className="w-full px-4 pt-4 pb-2">
                        <textarea
                            ref={textareaRef}
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onFocus={() => setIsFocused(true)}
                            onBlur={() => setIsFocused(false)}
                            onKeyDown={handleKeyDown}
                            placeholder="לדוגמה: אני מחפש כלי חינמי לבניית מצגות משקיעים מטקסט..."
                            disabled={isLoading}
                            rows={1}
                            className="w-full bg-transparent border-none outline-none text-white placeholder-slate-500 text-lg font-normal tracking-wide disabled:opacity-50 disabled:cursor-not-allowed resize-none overflow-hidden"
                            style={{ minHeight: "32px", maxHeight: "200px" }}
                        />
                    </div>

                    {/* Bottom: Action Row - Focused on matching */}
                    <div className="flex justify-end px-2 pb-1 w-full">
                        {isLoading ? (
                            <div className="px-6 py-2 rounded-xl bg-white/10 backdrop-blur-md border border-white/5 text-cyan-400 shadow-sm flex items-center justify-center">
                                <Loader2 className="w-5 h-5 animate-spin" />
                            </div>
                        ) : (
                            <button
                                type="submit"
                                disabled={!query.trim()}
                                className={`px-6 py-2 rounded-xl transition-all font-medium text-sm shadow-sm flex items-center gap-2 ${query.trim()
                                    ? "bg-gradient-to-r from-cyan-600 to-emerald-600 text-white hover:from-cyan-500 hover:to-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.3)] border border-transparent"
                                    : "bg-white/10 backdrop-blur-md border border-white/5 text-white/60 cursor-not-allowed"
                                    }`}
                            >
                                התאם לי כלי
                            </button>
                        )}
                    </div>
                </form>
                {statusText && (
                    <div className="text-center text-xs text-cyan-400 animate-pulse font-mono tracking-wider mt-2 drop-shadow-[0_0_5px_rgba(6,182,212,0.5)]">
                        {statusText}
                    </div>
                )}
            </div>
        </div>
    );
}
