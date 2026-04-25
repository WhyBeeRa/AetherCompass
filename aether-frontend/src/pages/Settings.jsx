import React, { useState } from 'react';
import { User, Bell, Shield, Wallet, LogOut, ChevronLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export default function Settings() {
    const navigate = useNavigate();
    const { t } = useTranslation();
    const [activeTab, setActiveTab] = useState('profile');

    const tabs = [
        { id: 'profile', label: t('settings.tab_profile'), icon: User },
        { id: 'notifications', label: t('settings.tab_notifications'), icon: Bell },
        { id: 'security', label: t('settings.tab_security'), icon: Shield },
        { id: 'support', label: t('settings.tab_support'), icon: Wallet },
    ];

    return (
        <div className="flex flex-col md:flex-row w-full max-w-5xl mx-auto min-h-[80vh] gap-8 animate-in fade-in duration-700 ltr" dir="ltr">

            {/* Sidebar Navigation */}
            <aside className="w-full md:w-64 flex flex-col gap-2">
                <div className="mb-6 px-4">
                    <h1 className="text-2xl font-bold text-white">{t('settings.title')}</h1>
                    <p className="text-sm text-white/60 mt-1">{t('settings.subtitle')}</p>
                </div>

                <nav className="flex flex-row md:flex-col gap-1 overflow-x-auto md:overflow-hidden pb-4 md:pb-0 px-4 md:px-0 scrollbar-hide">
                    {tabs.map(tab => {
                        const Icon = tab.icon;
                        const isActive = activeTab === tab.id;
                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all whitespace-nowrap ${isActive
                                        ? 'bg-white/20 backdrop-blur-md text-white shadow-md'
                                        : 'text-white/70 hover:bg-white/10 backdrop-blur-md hover:text-white'
                                    }`}
                            >
                                <Icon className="w-5 h-5" />
                                {tab.label}
                            </button>
                        );
                    })}
                </nav>

                <div className="mt-auto px-4 pt-8 border-t border-white/10 hidden md:block">
                    <button onClick={() => navigate('/')} className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-red-500 hover:bg-red-50 rounded-xl transition-colors w-full">
                        <LogOut className="w-5 h-5" />
                        {t('settings.logout')}
                    </button>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 bg-white/5 backdrop-blur-md border border-white/20 rounded-3xl p-6 md:p-10 shadow-sm animate-in slide-in-from-left-4 duration-500">

                {activeTab === 'profile' && (
                    <div className="max-w-xl animate-in fade-in duration-300">
                        <h2 className="text-xl font-bold text-white mb-6 border-b border-white/10 pb-4">{t('settings.profile_title')}</h2>

                        <div className="flex items-center gap-6 mb-8">
                            <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600 text-2xl font-bold uppercase ring-4 ring-white shadow-sm">
                                YB
                            </div>
                            <div className="flex flex-col gap-2">
                                <button className="px-4 py-2 bg-white/10 backdrop-blur-md text-white text-sm font-medium rounded-lg hover:bg-white/20 backdrop-blur-md transition-colors">
                                    {t('settings.change_photo')}
                                </button>
                                <button className="text-xs text-white/60 hover:text-red-500 transition-colors text-left">
                                    {t('settings.remove_photo')}
                                </button>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div className="flex flex-col gap-2">
                                <label className="text-sm font-semibold text-white/80">{t('settings.full_name')}</label>
                                <input type="text" defaultValue="Yuval Blank" className="w-full bg-white/5 backdrop-blur-md border border-white/20 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-neutral-900/10 focus:border-white/20 transition-all" />
                            </div>
                            <div className="flex flex-col gap-2">
                                <label className="text-sm font-semibold text-white/80">{t('settings.email')}</label>
                                <input type="email" defaultValue="yuval@example.com" disabled className="w-full bg-white/10 backdrop-blur-md border border-white/20 text-white/60 rounded-xl px-4 py-3 cursor-not-allowed" dir="ltr" />
                                <span className="text-xs text-white/50">{t('settings.email_help')}</span>
                            </div>
                            <div className="flex flex-col gap-2">
                                <label className="text-sm font-semibold text-white/80">{t('settings.role')}</label>
                                <input type="text" placeholder={t('settings.role_placeholder')} className="w-full bg-white/5 backdrop-blur-md border border-white/20 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-neutral-900/10 focus:border-white/20 transition-all" />
                            </div>
                        </div>

                        <div className="mt-10 pt-6 border-t border-white/10 flex justify-end">
                            <button className="px-6 py-3 bg-white/20 backdrop-blur-md text-white text-sm font-medium rounded-xl hover:bg-white/10 backdrop-blur-md transition-all shadow-md">
                                {t('settings.save_changes')}
                            </button>
                        </div>
                    </div>
                )}

                {activeTab === 'notifications' && (
                    <div className="max-w-xl animate-in fade-in duration-300">
                        <h2 className="text-xl font-bold text-white mb-6 border-b border-white/10 pb-4">{t('settings.notifications_title')}</h2>
                        <div className="space-y-6">
                            {[
                                { title: t('settings.notif_stack'), desc: t('settings.notif_stack_desc') },
                                { title: t('settings.notif_newsletter'), desc: t('settings.notif_newsletter_desc') },
                                { title: t('settings.notif_security'), desc: t('settings.notif_security_desc') }
                            ].map((item, i) => (
                                <div key={i} className="flex items-center justify-between p-4 border border-white/10 rounded-2xl">
                                    <div className="flex flex-col">
                                        <span className="font-semibold text-white mb-1">{item.title}</span>
                                        <span className="text-sm text-white/60">{item.desc}</span>
                                    </div>
                                    <label className="relative inline-flex items-center cursor-pointer">
                                        <input type="checkbox" className="sr-only peer" defaultChecked={i !== 1} />
                                        <div className="w-11 h-6 bg-white/20 backdrop-blur-md peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white/5 backdrop-blur-md after:border-white/30 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
                                    </label>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'security' && (
                    <div className="max-w-xl animate-in fade-in duration-300">
                        <h2 className="text-xl font-bold text-white mb-6 border-b border-white/10 pb-4">{t('settings.security_title')}</h2>
                        <div className="p-6 bg-amber-50 border border-amber-200 rounded-2xl flex items-start gap-4 mb-8">
                            <Shield className="w-6 h-6 text-amber-600 shrink-0 mt-1" />
                            <div>
                                <h3 className="font-semibold text-amber-900 mb-1">{t('settings.security_info_title')}</h3>
                                <p className="text-sm text-amber-700 leading-relaxed">{t('settings.security_info_desc')}</p>
                            </div>
                        </div>
                        <button className="flex justify-between items-center w-full px-5 py-4 border border-white/20 rounded-xl hover:bg-white/5 backdrop-blur-md transition-colors text-left">
                            <div className="flex flex-col">
                                <span className="font-medium text-white">{t('settings.login_history')}</span>
                                <span className="text-sm text-white/60">{t('settings.login_history_desc')}</span>
                            </div>
                            <ChevronLeft className="w-5 h-5 text-white/50 rotate-180" />
                        </button>
                    </div>
                )}

                {activeTab === 'support' && (
                    <div className="max-w-xl animate-in fade-in duration-300">
                        <h2 className="text-xl font-bold text-white mb-6 border-b border-white/10 pb-4">{t('settings.support_title')}</h2>
                        <div className="p-8 border border-white/20 rounded-3xl bg-white/5 backdrop-blur-md flex flex-col md:flex-row justify-between items-center gap-6 mb-8">
                            <div>
                                <span className="inline-block px-3 py-1 bg-white/20 backdrop-blur-md text-white/80 text-xs font-bold uppercase tracking-wider rounded-lg mb-3">{t('settings.current_plan')}</span>
                                <h3 className="text-2xl font-bold text-white mb-1">{t('settings.current_plan')}</h3>
                                <p className="text-white/60 text-sm leading-relaxed">{t('settings.support_desc')}</p>
                            </div>
                            <button onClick={() => navigate('/support')} className="px-6 py-3 bg-cyan-600 text-white font-medium rounded-xl hover:bg-cyan-700 transition-colors shadow-lg whitespace-nowrap">
                                {t('settings.support_btn')}
                            </button>
                        </div>
                    </div>
                )}

            </main>
        </div>
    );
}
