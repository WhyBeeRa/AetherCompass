import { useTranslation } from 'react-i18next';

export default function NotFound() {
    const { t } = useTranslation();
    return (
        <div className="flex flex-col items-center justify-center min-h-[50vh] w-full pt-16">
            <h1 className="text-3xl font-bold text-white mb-4">{t('not_found.title')}</h1>
            <p className="text-white/50">{t('not_found.subtitle')}</p>
        </div>
    );
}
