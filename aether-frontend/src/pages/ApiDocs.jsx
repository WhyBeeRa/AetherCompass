import React, { useState } from 'react';
import { Terminal, Code2, Server, KeySquare } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function ApiDocs() {
    const { t, i18n } = useTranslation();
    const [email, setEmail] = useState('');
    const [useCase, setUseCase] = useState('');
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (email && useCase) {
            setSubmitted(true);
        }
    };

    const isRtl = i18n.dir() === 'rtl';

    return (
        <div className="w-full flex flex-col items-center pt-24 pb-24 animate-in fade-in duration-700">
            <main className="w-full max-w-4xl px-6">

                {/* Developer Header */}
                <div className={`mb-16 border-b border-white/20 pb-12 ${isRtl ? 'text-right' : 'text-left'}`}>
                    <div className="inline-flex items-center gap-2 px-3 py-1 mb-6 rounded-md bg-white/10 backdrop-blur-md border border-white/20 text-white/70 text-xs font-bold tracking-widest font-mono uppercase">
                        <Terminal className="w-3 h-3" /> API Endpoint
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight mb-4">
                        {t('api_docs.title_main')} <span className="text-neutral-300">{t('api_docs.title_sub')}</span>
                    </h1>
                    <p className="text-xl text-white/70 leading-relaxed font-medium max-w-2xl">
                        {t('api_docs.subtitle')}
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                    {/* Left: Technical Features */}
                    <div className={`space-y-8 ${isRtl ? 'pl-4' : 'pr-4'}`}>
                        <h3 className="text-sm font-bold text-white uppercase tracking-widest mb-6 border-b border-white/10 pb-2">{t('api_docs.tech_capabilities')}</h3>

                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-white/5 backdrop-blur-md border border-white/20 rounded-xl shrink-0">
                                <KeySquare className="w-5 h-5 text-white" />
                            </div>
                            <div className={isRtl ? 'text-right' : 'text-left'}>
                                <h4 className="font-bold text-white mb-1">RESTful & GraphQL</h4>
                                <p className="text-sm text-white/70 leading-relaxed font-medium">{t('api_docs.rest_graphql')}</p>
                            </div>
                        </div>

                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-white/5 backdrop-blur-md border border-white/20 rounded-xl shrink-0">
                                <Server className="w-5 h-5 text-white" />
                            </div>
                            <div className={isRtl ? 'text-right' : 'text-left'}>
                                <h4 className="font-bold text-white mb-1">Intent Resolution Engine</h4>
                                <p className="text-sm text-white/70 leading-relaxed font-medium">{t('api_docs.intent_engine')}</p>
                            </div>
                        </div>

                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-white/5 backdrop-blur-md border border-white/20 rounded-xl shrink-0">
                                <Code2 className="w-5 h-5 text-white" />
                            </div>
                            <div className={isRtl ? 'text-right' : 'text-left'}>
                                <h4 className="font-bold text-white mb-1">Zero-Bias Architecture</h4>
                                <p className="text-sm text-white/70 leading-relaxed font-medium">{t('api_docs.zero_bias')}</p>
                            </div>
                        </div>
                    </div>

                    {/* Right: Waitlist Form */}
                    <div className="bg-white/5 backdrop-blur-md border border-white/20 rounded-3xl p-8 relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-2 h-full bg-white/20 backdrop-blur-md rounded-r-3xl"></div>

                        {submitted ? (
                            <div className="h-full flex flex-col items-center justify-center text-center animate-in zoom-in-95 duration-500 py-10">
                                <Terminal className="w-12 h-12 text-emerald-500 mb-4" />
                                <h3 className="text-xl font-bold text-white mb-2">{t('api_docs.success_title')}</h3>
                                <p className="text-white/60 text-sm font-medium">{t('api_docs.success_subtitle')}</p>
                            </div>
                        ) : (
                            <form onSubmit={handleSubmit} className="flex flex-col h-full">
                                <h3 className={`text-lg font-bold text-white mb-2 ${isRtl ? 'text-right' : 'text-left'}`}>{t('api_docs.request_access')}</h3>
                                <p className={`text-sm text-white/60 font-medium mb-8 ${isRtl ? 'text-right' : 'text-left'}`}>
                                    {t('api_docs.limited_keys')}
                                </p>

                                <div className="space-y-5 mb-8">
                                    <div className={isRtl ? 'text-right' : 'text-left'}>
                                        <label className="text-xs font-bold text-white/60 uppercase tracking-widest mb-2 block">{t('api_docs.email_label')}</label>
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
                                    <div className={isRtl ? 'text-right' : 'text-left'}>
                                        <label className="text-xs font-bold text-white/60 uppercase tracking-widest mb-2 block">{t('api_docs.use_case_label')}</label>
                                        <textarea
                                            required
                                            value={useCase}
                                            onChange={(e) => setUseCase(e.target.value)}
                                            placeholder={t('api_docs.use_case_placeholder')}
                                            className="w-full p-3 bg-white/5 backdrop-blur-md border border-white/20 rounded-xl text-white font-medium focus:ring-2 focus:ring-neutral-900 outline-none transition-all placeholder:text-white/50 resize-none h-24 text-sm"
                                            dir="ltr"
                                        ></textarea>
                                    </div>
                                </div>

                                <div className="mt-auto">
                                    <button type="submit" className="w-full py-3.5 rounded-xl bg-white/20 backdrop-blur-md hover:bg-white/10 backdrop-blur-md text-white font-bold text-sm shadow-md transition-all active:scale-[0.98]">
                                        {t('api_docs.submit')}
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
