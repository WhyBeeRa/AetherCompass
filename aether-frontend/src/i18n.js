import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import translationEN from './locales/en/translation.json';

const resources = {
  en: {
    translation: translationEN
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en', // Force English
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false // react already safes from xss
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: [] // Disable caching to ensure it doesn't get stuck on Hebrew
    }
  });

// Force LTR for the entire app
document.documentElement.dir = 'ltr';
document.documentElement.lang = 'en';

// Handle language changes just in case, though it will be locked to en
i18n.on('languageChanged', (lng) => {
  document.documentElement.dir = 'ltr';
  document.documentElement.lang = 'en';
});

// Initial direction setting
document.documentElement.dir = 'ltr';
document.documentElement.lang = 'en';

export default i18n;
