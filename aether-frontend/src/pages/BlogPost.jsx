import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Clock, FlaskConical, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion } from 'framer-motion';

// Mock data to enrich the post (in a real app, this metadata could be loaded from an API or frontmatter)
const postsMetadata = {
    "the-seed-strategy": {
        title: "אסטרטגיית ה-Seed: איך להביא ניתוחים שוברי שוק?",
        date: "14 מרץ, 2026",
        readTime: "4 דק' קריאה"
    },
    "claude-3-5-sonnet-coding-test": {
        title: "Claude 3.5 Sonnet תחת המיקרוסקופ: האם מהפכת הקידוד באמת כאן?",
        date: "12 פברואר, 2026",
        readTime: "6 דק' קריאה"
    },
    "rise-of-autonomous-agents": {
        title: "עלייתם של סוכני ה-AI האוטונומיים: למה Agentic משנה את חוקי המשחק",
        date: "05 פברואר, 2026",
        readTime: "8 דק' קריאה"
    },
    "ai-writing-tools-turing-test": {
        title: "כלי כתיבה AI לעומת בני אדם: תוצאות מבחן הטורינג של Aether",
        date: "28 ינואר, 2026",
        readTime: "5 דק' קריאה"
    }
};

export default function BlogPost() {
    const { slug } = useParams();
    const navigate = useNavigate();
    const [content, setContent] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const postMetadata = postsMetadata[slug];

    useEffect(() => {
        const fetchPost = async () => {
            setLoading(true);
            try {
                // Fetch the markdown file from the public folder
                const response = await fetch(`/blog/${slug}.md`);
                if (!response.ok) {
                    throw new Error('Post not found');
                }
                const text = await response.text();
                setContent(text);
                setError(null);
            } catch (err) {
                console.error("Error fetching blog post:", err);
                setError("המאמר לא נמצא או שהייתה שגיאה בטעינתו.");
            } finally {
                setLoading(false);
            }
        };

        fetchPost();
    }, [slug]);

    return (
        <div className="min-h-screen w-full flex flex-col items-center bg-[#0a0a0c] pt-24 pb-24 rtl" dir="rtl">
            <main className="w-full max-w-3xl px-6">

                {/* Fixed Back Button */}
                <button onClick={() => navigate(-1)} className="text-white/50 hover:text-white mb-12 transition-colors flex items-center gap-2 text-sm font-bold bg-white/5 backdrop-blur-md px-3 py-1.5 rounded-md border border-white/10 aspect-fit inline-flex w-auto mt-4">
                    <ArrowLeft className="w-4 h-4" /> חזרה
                </button>

                {loading ? (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex flex-col items-center justify-center py-20"
                    >
                        <div className="w-8 h-8 border-2 border-white/20 border-t-white/80 rounded-full animate-spin mb-4"></div>
                        <span className="text-white/50 text-sm font-mono tracking-widest uppercase">טוען נתוני מעבדה...</span>
                    </motion.div>
                ) : error ? (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex flex-col items-center justify-center py-20 text-center bg-white/5 border border-white/10 rounded-2xl p-8"
                    >
                        <AlertCircle className="w-12 h-12 text-white/30 mb-4" />
                        <h2 className="text-2xl font-bold text-white mb-2">שגיאה (404)</h2>
                        <p className="text-white/50">{error}</p>
                    </motion.div>
                ) : (
                    <motion.article
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.7, ease: "easeOut" }}
                        className="prose prose-neutral prose-lg max-w-none prose-headings:text-white prose-p:text-white/70 prose-a:text-emerald-400 hover:prose-a:text-emerald-300 prose-strong:text-white prose-ul:text-white/70 prose-li:marker:text-white/30 prose-hr:border-white/10 prose-blockquote:text-white/50 prose-blockquote:border-white/20 prose-code:text-emerald-300 prose-code:bg-white/5 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-md leading-loose"
                    >
                        {postMetadata && (
                            <header className="mb-12 border-b border-white/10 pb-8">
                                <div className="inline-flex items-center gap-2 px-3 py-1 mb-6 rounded-md bg-white/5 backdrop-blur-md border border-white/10 text-white/50 text-xs font-bold tracking-widest font-mono uppercase">
                                    <FlaskConical className="w-3 h-3" /> דו״ח מעבדה
                                </div>
                                <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight mb-6">
                                    {postMetadata.title}
                                </h1>
                                <div className="flex items-center gap-4 text-sm text-white/50 font-mono tracking-wider uppercase">
                                    <time>{postMetadata.date}</time>
                                    <span className="w-1 h-1 rounded-full bg-white/20"></span>
                                    <span className="flex items-center gap-1.5"><Clock className="w-3 h-3" /> {postMetadata.readTime}</span>
                                </div>
                            </header>
                        )}

                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {content}
                        </ReactMarkdown>
                    </motion.article>
                )}
            </main>
        </div>
    );
}
