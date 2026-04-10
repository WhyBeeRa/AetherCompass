import React from 'react';
import { ShieldCheck, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Privacy() {
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
                        <ShieldCheck className="w-3 h-3" /> מדיניות פרטיות
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight mb-4">
                        מדיניות שמירת נתונים
                    </h1>
                    <p className="text-lg text-white/50 font-medium">עודכן לאחרונה: 1 לפברואר, 2026</p>
                </div>

                {/* Content */}
                <div className="prose prose-neutral prose-lg max-w-none text-white/70 space-y-8 leading-loose">
                    <div className="p-6 bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl mb-8">
                        <p className="text-sm text-white/70 font-bold m-0 leading-relaxed">
                            תקציר מנהלים: בנינו את Aether סביב האמת, וכך גם לגבי הפרטיות שלך. אנחנו לא מוכרים את בסיס הנתונים שלנו לגופי צד-שלישי. המידע נשמר על שרתינו באופן מאובטח ומוצפן ומשמש אך ורק לשיפור מנוע החיפוש שלנו ושמירת הכלים האישית שלך.
                        </p>
                    </div>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">1. המידע שאנו אוספים</h2>
                        <p className="text-white/50">כאשר אתה משתמש בשירות, אנו אוספים את סוגי המידע הבאים:</p>
                        <ul className="list-disc pr-6 space-y-2 text-white/50 marker:text-white/30">
                            <li><strong className="text-white/80">מידע שסופק על ידך:</strong> כתובת דוא״ל, פרופיל משתמש (במידה ונרשמת ל-Aether Pro או יצרת My Stack).</li>
                            <li><strong className="text-white/80">מידע חיפוש:</strong> האינטנטים (Intents) שהזנת בתיבת החיפוש. נתונים אלו נשמרים באופן אנונימי (ללא קשר לזהות המשתמש) כדי להבין אילו צרכים חסרים לקהל שלנו ולשלוח את הסוכנים שלנו לחקור אותם.</li>
                            <li><strong className="text-white/80">מידע טכני אוטומטי:</strong> כתובת IP, סוג דפדפן ונתוני שימוש אנליטיים סטנדרטיים (למשל לצורך מניעת תקיפות DDoS).</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">2. השימוש שאנו עושים במידע</h2>
                        <p className="text-white/50">מטרתנו היחידה היא לשפר את שירות מציאת האמת של Aether. אנו לא עוסקים בפרסום ריטרגטינג. השימושים העיקריים הינם:</p>
                        <ul className="list-disc pr-6 space-y-2 text-white/50 marker:text-white/30">
                            <li>אחסון וסנכרון רשימות ה-My Stack שלך.</li>
                            <li>אבטחת המערכת ומניעת ניצול לרעה של ה-API.</li>
                            <li>יצירת סטטיסטיקה אגרגטיבית ואנונימית.</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">3. צדדים שלישיים שאנו חולקים עמם מידע</h2>
                        <p className="text-white/50">Aether אינה מוכרת מידע אישי. אנו משתפים מידע באופן מינימלי רק עם ספקי תשתית הכרחיים לפעילות האתר (כגון ספקי ענן ושרתי מסד נתונים), וזאת בכפוף לכל דרישות אבטחת המידע המחמירות.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">4. הזכויות שלך</h2>
                        <p className="text-white/50">המרחב הדיגיטלי שלך שייך לך. אתה רשאי בכל עת לפנות אלינו למחיקה או ייצוא של הנתונים האישיים שלך על ידי פנייה לעמוד "צור קשר". עקב ארכיטקטורת המערכת אנחנו מבצעים מחיקה קשה (Hard Delete) מבסיס הנתונים תוך 48 שעות מיום קבלת הבקשה.</p>
                    </section>
                </div>

            </main>
        </div>
    );
}
