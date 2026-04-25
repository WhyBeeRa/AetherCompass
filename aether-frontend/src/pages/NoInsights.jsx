import { useTranslation } from 'react-i18next';

export default function NoInsights() {
    const { t } = useTranslation();
    return (
        <div className="flex flex-col items-center justify-center min-h-[50vh] w-full pt-16">
            <h1 className="text-3xl font-bold text-white mb-4">{t('no_insights.title')}</h1>
            <p className="text-white/50">Aether Architecture Placeholder</p>
        </div>
    );
}
