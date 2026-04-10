import React, { useState } from 'react';
import { Terminal, Code2, Server, KeySquare } from 'lucide-react';

export default function ApiDocs() {
    const [email, setEmail] = useState('');
    const [useCase, setUseCase] = useState('');
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (email && useCase) {
            setSubmitted(true);
        }
    };

    return (
        <div className="w-full flex flex-col items-center pt-24 pb-24 rtl animate-in fade-in duration-700" dir="rtl">
            <main className="w-full max-w-4xl px-6">

                {/* Developer Header */}
                <div className="mb-16 border-b border-white/20 pb-12">
                    <div className="inline-flex items-center gap-2 px-3 py-1 mb-6 rounded-md bg-white/10 backdrop-blur-md border border-white/20 text-white/70 text-xs font-bold tracking-widest font-mono uppercase">
                        <Terminal className="w-3 h-3" /> API Endpoint
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight mb-4">
                        Aether Vault API <span className="text-neutral-300">/ Waitlist</span>
                    </h1>
                    <p className="text-xl text-white/70 leading-relaxed font-medium max-w-2xl">
                        גישה ישירה למסד הנתונים הקליני של Aether. אנחנו פותחים גישה מוקדמת למפתחים שבונים יישומים מבוססי-המלצות אובייקטיביות, סוכני קנייה, ופלטפורמות מחקר.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                    {/* Left: Technical Features */}
                    <div className="space-y-8 pr-4">
                        <h3 className="text-sm font-bold text-white uppercase tracking-widest mb-6 border-b border-white/10 pb-2">Technical Capabilities</h3>

                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-white/5 backdrop-blur-md border border-white/20 rounded-xl shrink-0">
                                <KeySquare className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h4 className="font-bold text-white mb-1">RESTful & GraphQL</h4>
                                <p className="text-sm text-white/70 leading-relaxed font-medium">שאילתות גמישות בכל מודלי הנתונים - עקומת למידה, תמחור סתרים, ודירוגי אמינות (Trust Score).</p>
                            </div>
                        </div>

                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-white/5 backdrop-blur-md border border-white/20 rounded-xl shrink-0">
                                <Server className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h4 className="font-bold text-white mb-1">Intent Resolution Engine</h4>
                                <p className="text-sm text-white/70 leading-relaxed font-medium">עקיפת ה-API המסורתי לחיפוש טקסט חופשי. שלח מסר חופשי (Intent) וקבל מערך מסודר של כלים שעברו הערכת הצלחה מתמטית.</p>
                            </div>
                        </div>

                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-white/5 backdrop-blur-md border border-white/20 rounded-xl shrink-0">
                                <Code2 className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h4 className="font-bold text-white mb-1">Zero-Bias Architecture</h4>
                                <p className="text-sm text-white/70 leading-relaxed font-medium">מובטח בחוזה ה-SLA: אין קידום ממומן במענה ה-API האורגני. הנתונים תמיד נשארים טהורים וחסינים לקניית כוח.</p>
                            </div>
                        </div>
                    </div>

                    {/* Right: Waitlist Form */}
                    <div className="bg-white/5 backdrop-blur-md border border-white/20 rounded-3xl p-8 relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-2 h-full bg-white/20 backdrop-blur-md rounded-r-3xl"></div>

                        {submitted ? (
                            <div className="h-full flex flex-col items-center justify-center text-center animate-in zoom-in-95 duration-500 py-10">
                                <Terminal className="w-12 h-12 text-emerald-500 mb-4" />
                                <h3 className="text-xl font-bold text-white mb-2">הבקשה נקלטה במערכת.</h3>
                                <p className="text-white/60 text-sm font-medium">צוות האדריכלים שלנו יבחן את הפרטים, ונחזור אליך ברגע שנשחרר מפתחות API נוספים.</p>
                            </div>
                        ) : (
                            <form onSubmit={handleSubmit} className="flex flex-col h-full">
                                <h3 className="text-lg font-bold text-white mb-2">Request API Access</h3>
                                <p className="text-sm text-white/60 font-medium mb-8">
                                    מספר המפתחות מוגבל מאוד בשלב הבטא הראשוני לצורך הבטחת יציבות השרתים.
                                </p>

                                <div className="space-y-5 mb-8">
                                    <div>
                                        <label className="text-xs font-bold text-white/60 uppercase tracking-widest mb-2 block">Company / Developer Email</label>
                                        <input
                                            type="email"
                                            required
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="dev@company.com"
                                            className="w-full p-3 bg-white/5 backdrop-blur-md border border-white/20 rounded-xl text-white font-medium font-mono text-sm focus:ring-2 focus:ring-neutral-900 outline-none transition-all placeholder:text-white/50"
                                            dir="ltr"
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs font-bold text-white/60 uppercase tracking-widest mb-2 block">Proposed Use Case</label>
                                        <textarea
                                            required
                                            value={useCase}
                                            onChange={(e) => setUseCase(e.target.value)}
                                            placeholder="What are you building with Aether?"
                                            className="w-full p-3 bg-white/5 backdrop-blur-md border border-white/20 rounded-xl text-white font-medium focus:ring-2 focus:ring-neutral-900 outline-none transition-all placeholder:text-white/50 resize-none h-24 text-sm"
                                            dir="ltr"
                                        ></textarea>
                                    </div>
                                </div>

                                <div className="mt-auto">
                                    <button type="submit" className="w-full py-3.5 rounded-xl bg-white/20 backdrop-blur-md hover:bg-white/10 backdrop-blur-md text-white font-bold text-sm shadow-md transition-all active:scale-[0.98]">
                                        Submit Request
                                    </button>
                                </div>
                            </form>
                        )}
                    </div>
                </div>

            </main>
        </div>
    );
}
