import React from 'react';
import { ShieldCheck, Database, Zap } from 'lucide-react';

export default function About() {
    return (
        <div className="min-h-screen w-full flex flex-col items-center bg-[#0a0a0c] pt-24 pb-24 rtl animate-in fade-in duration-700" dir="rtl">
            <main className="w-full max-w-3xl px-6">

                {/* Header Section */}
                <div className="mb-16">
                    <span className="text-white/50 font-bold tracking-widest uppercase text-xs mb-4 block">
                        החזון שלנו (The Manifesto)
                    </span>
                    <h1 className="text-4xl md:text-5xl font-bold text-white leading-tight tracking-tight mb-8">
                        אנחנו בונים מצפן אובייקטיבי
                        <br className="hidden md:block" />
                        בעידן של רעש אלגוריתמי.
                    </h1>
                    <p className="text-xl text-white/70 leading-relaxed font-medium">
                        רשת האינטרנט הוצפה באינדקסים שטחיים של כלי בינה מלאכותית. רובם מונעים מקידום ממומן (SEO), תוכניות שותפים מוסוות, וביקורות חסרות משמעות של יוצרי תוכן שמעולם לא השתמשו בכלי שהם מקדמים. אנחנו כאן כדי לפתור את זה.
                    </p>
                </div>

                {/* The Core Problem */}
                <div className="prose prose-neutral prose-lg max-w-none text-white/70 mb-16 space-y-6 leading-loose">
                    <p>
                        <strong className="text-white">הבעיה: הינדוס תודעה.</strong> כשאתה מחפש פתרון AI למשימה אמיתית (כמו בניית אפליקציה, או תמלול וידאו בעברית), התוצאות הראשונות בגוגל הן כבר מזמן לא התוצאות הטובות ביותר. הן התוצאות של החברות להן יש את תקציב השיווק הגדול ביותר.
                    </p>
                    <p>
                        <strong className="text-white">הפתרון: The Aether Lab.</strong> בנינו רשת אוטונומית של טיפוסי-סוכנים (Agents) שיורדים לשטח כדי לבדוק ולעמת את ההבטחות של חברות הטכנולוגיה. אנחנו מחפשים שקיפות בתמחור, במדיניות המידע, ובעיקר - במבחן התוצאה אל מול הצרכים המדויקים (Intents) שלך.
                    </p>
                    <p>
                        Aether לא רק זורק עליך רשימת כלים. הוא מחבר את המשימה הספציפית שלך ישירות לפתרונות שעברו בקרת איכות קלינית. בלי רעש, בלי הסחות דעת, ואך ורק עם האמת כפי שהיא התבררה במעבדה האדריכלית שלנו.
                    </p>
                </div>

                {/* Core Pillars */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-10 border-t border-white/10">
                    <div className="flex flex-col">
                        <ShieldCheck className="w-6 h-6 text-white mb-4" />
                        <h3 className="text-lg font-bold text-white mb-2">נטול הטיות מותג</h3>
                        <p className="text-sm text-white/50 leading-relaxed">
                            הפרדנו לחלוטין את מנגנון הדירוג שלנו (Trust Score) מהשפעות מסחריות. הוא מחושב באופן מתמטי וקליני בלבד.
                        </p>
                    </div>
                    <div className="flex flex-col">
                        <Database className="w-6 h-6 text-white mb-4" />
                        <h3 className="text-lg font-bold text-white mb-2">מידע מאומת-שטח</h3>
                        <p className="text-sm text-white/50 leading-relaxed">
                            הסוכנים שלנו בודקים תרחישי שימוש מציאותיים (Use Cases) כדי לוודא שאין הבדל בין ההבטחה השיווקית ליכולת האמיתית.
                        </p>
                    </div>
                    <div className="flex flex-col">
                        <Zap className="w-6 h-6 text-white mb-4" />
                        <h3 className="text-lg font-bold text-white mb-2">מיקוד בכוונת הליבה</h3>
                        <p className="text-sm text-white/50 leading-relaxed">
                            חיפוש אדריכלי שמבין *מה* אתה רוצה לעשות (האינטנט), ולא מחפש רק התאמה של מילות מפתח עיוורות.
                        </p>
                    </div>
                </div>

            </main>
        </div>
    );
}
