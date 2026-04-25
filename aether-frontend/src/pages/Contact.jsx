import React, { useState } from 'react';
import { Mail, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export default function Contact() {
    const navigate = useNavigate();
    const { t } = useTranslation();
    const [isSubmitted, setIsSubmitted] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        setIsSubmitted(true);
    };

    return (
        <div className="min-h-screen w-full flex flex-col items-center bg-[#0a0a0c] pt-24 pb-24 ltr animate-in fade-in duration-700" dir="ltr">
            <main className="w-full max-w-2xl px-6">

                {/* Header */}
                <div className="mb-16">
                    <button onClick={() => navigate(-1)} className="text-white/50 hover:text-white mb-8 transition-colors flex items-center gap-2 text-sm font-bold bg-white/5 backdrop-blur-md px-3 py-1.5 rounded-md border border-white/10 aspect-fit inline-flex w-auto">
                        <ArrowLeft className="w-4 h-4" /> {t('nav.back')}
                    </button>
                    <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight mb-4">
                        {t('contact.title')}
                    </h1>
                    <p className="text-lg text-white/50 font-medium leading-relaxed">
                        {t('contact.subtitle')}
                    </p>
                </div>

                {/* Form / Success State */}
                <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-3xl p-8 md:p-10 shadow-sm relative overflow-hidden">
                    {isSubmitted ? (
                        <div className="flex flex-col items-center justify-center py-12 animate-in fade-in zoom-in-95 duration-500 text-center">
                            <CheckCircle2 className="w-12 h-12 text-emerald-500 mb-6" />
                            <h3 className="text-2xl font-bold text-white mb-3">{t('contact.success_title')}</h3>
                            <p className="text-white/50 max-w-sm leading-relaxed">
                                {t('contact.success_subtitle')}
                            </p>
                            <button onClick={() => setIsSubmitted(false)} className="mt-8 text-sm text-white/50 hover:text-white transition-colors underline underline-offset-4">
                                {t('contact.send_another')}
                            </button>
                        </div>
                    ) : (
                        <form className="space-y-6 animate-in fade-in duration-500" onSubmit={handleSubmit}>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                 <div>
                                    <label className="text-xs font-bold text-white/50 uppercase tracking-widest mb-2 block">{t('contact.full_name')}</label>
                                    <input required type="text" placeholder="John Doe" className="w-full p-3.5 bg-white/5 backdrop-blur-md border border-white/10 rounded-xl text-white font-medium focus:ring-1 focus:ring-white/30 focus:border-white/30 outline-none transition-all placeholder:text-white/20" />
                                </div>
                                <div>
                                    <label className="text-xs font-bold text-white/50 uppercase tracking-widest mb-2 block">{t('contact.email')}</label>
                                    <input required type="email" placeholder="email@example.com" className="w-full p-3.5 bg-white/5 backdrop-blur-md border border-white/10 rounded-xl text-white font-medium font-mono text-sm focus:ring-1 focus:ring-white/30 focus:border-white/30 outline-none transition-all placeholder:text-white/20" dir="ltr" />
                                </div>
                            </div>

                             <div>
                                <label className="text-xs font-bold text-white/50 uppercase tracking-widest mb-2 block">{t('contact.subject')}</label>
                                <select className="w-full p-3.5 bg-white/5 backdrop-blur-md border border-white/10 rounded-xl text-white font-medium focus:ring-1 focus:ring-white/30 focus:border-white/30 outline-none transition-all appearance-none">
                                    <option className="bg-[#0a0a0c] text-white">{t('contact.subject_suggestion')}</option>
                                    <option className="bg-[#0a0a0c] text-white">{t('contact.subject_inaccuracy')}</option>
                                    <option className="bg-[#0a0a0c] text-white">{t('contact.subject_partnership')}</option>
                                    <option className="bg-[#0a0a0c] text-white">{t('contact.subject_other')}</option>
                                </select>
                            </div>

                            <div>
                                <label className="text-xs font-bold text-white/50 uppercase tracking-widest mb-2 block">{t('contact.label_content')}</label>
                                <textarea required placeholder={t('contact.placeholder_content')} className="w-full p-3.5 bg-white/5 backdrop-blur-md border border-white/10 rounded-xl text-white font-medium focus:ring-1 focus:ring-white/30 focus:border-white/30 outline-none transition-all placeholder:text-white/20 resize-none h-32 leading-relaxed text-sm"></textarea>
                            </div>

                            <div className="pt-2 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                                <span className="text-xs text-white/50 font-medium inline-flex items-center gap-1.5">
                                    <Mail className="w-3.5 h-3.5" /> {t('contact.fast_response')}
                                </span>
                                <button type="submit" className="w-full md:w-auto px-8 py-3.5 rounded-xl bg-white text-black hover:bg-neutral-200 font-bold text-sm shadow-md transition-all active:scale-[0.98]">
                                    {t('contact.submit')}
                                </button>
                            </div>
                        </form>
                    )}
                </div>

            </main>
        </div>
    );
}
