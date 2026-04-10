import React from 'react';
import { FileText, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Terms() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen w-full flex flex-col items-center bg-[#0a0a0c] pt-24 pb-24 rtl animate-in fade-in duration-700" dir="rtl">
            <main className="w-full max-w-3xl px-6">

                {/* Header */}
                <div className="mb-16">
                    <button onClick={() => navigate(-1)} className="text-white/50 hover:text-white mb-8 transition-colors flex items-center gap-2 text-sm font-bold bg-white/5 backdrop-blur-md px-3 py-1.5 rounded-md border border-white/10 aspect-fit inline-flex w-auto">
                        <ArrowLeft className="w-4 h-4" /> חזרה
                    </button>
                    <div className="inline-flex items-center gap-2 px-3 py-1 mb-6 rounded-md bg-white/5 backdrop-blur-md border border-white/10 text-white/50 text-xs font-bold tracking-widest uppercase">
                        <FileText className="w-3 h-3" /> מסמך משפטי
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight mb-4">
                        תנאי שימוש
                    </h1>
                    <p className="text-lg text-white/50 font-medium">עודכן לאחרונה: 1 לפברואר, 2026</p>
                </div>

                {/* Content */}
                <div className="prose prose-neutral prose-lg max-w-none text-white/50 space-y-8 leading-loose">
                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">1. מבוא</h2>
                        <p>ברוכים הבאים ל-Aether Lab ("החברה", "אנחנו", "שלנו"). תקנון זה מגדיר את תנאי השימוש בפלטפורמת Aether, לרבות אתר האינטרנט, שירותי ה-API, וכלים נלווים. השימוש במערכת מהווה הסכמה מלאה לתנאים אלו.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">2. מהות השירות והעדר אחריות מוחלטת</h2>
                        <p>Aether מספקת פלטפורמה לאינדקס ולניתוח כלי בינה מלאכותית על בסיס מבחני מעבדה עצמאיים. עם זאת:</p>
                        <ul className="list-disc pr-6 space-y-2 marker:text-white/30">
                            <li>המידע מוגש as-is ללא אחריות לדיוק מוחלט, בהתחשב באופי הדינמי של כלי AI.</li>
                            <li>Aether אינה נושאת באחריות לכל נזק, ישיר או עקיף, שייגרם כתוצאה מהסתמכות על נתוני המעבדה.</li>
                            <li>האחריות לבדיקת תנאי השימוש ורישיונות של כל כלי AI שמוצג בפלטפורמה חלה על המשתמש בלבד.</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">3. נתונים ואובייקטיביות</h2>
                        <p>אנו מתחייבים כי מדד ה-Trust Score ותוצאות מנוע ה-Intent Resolution אינם נתונים למניפולציות פיננסיות מטעם חברות מסחריות (Pay-to-Play). במקרים של תוכן ממומן, הוא יסומן בצורה מפורשת ובולטת כ"Promoted".</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">4. שימוש ב-API</h2>
                        <p>משתמשים בעלי גישה ל-Vault API מחויבים לשמור על סודיות מפתחות הגישה. Aether שומרת את הזכות להשעות או לחסום גישה ל-API במקרים של עומס חריג או שימוש לרעה שאינו עומד בתנאי ה-SLA.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">5. שינויים בתנאים</h2>
                        <p>החברה רשאית לעדכן תנאים אלו מעת לעת ללא הודעה מוקדמת. המשך השימוש בשירות לאחר פרסום העדכון מהווה הסכמה לתנאים החדשים. עדכונים מהותיים יישלחו למשתמשים רשומים במייל הדואר.</p>
                    </section>
                </div>

            </main>
        </div>
    );
}
