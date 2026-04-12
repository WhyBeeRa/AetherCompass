import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import translationEN from './locales/en/translation.json';
import translationHE from './locales/he/translation.json';

const resources = {
  en: {
    translation: translationEN
  },
  he: {
    translation: translationHE
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'he',
    interpolation: {
      escapeValue: false // react already safes from xss
    },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag', 'path', 'subdomain'],
      caches: ['localStorage']
    }
  });

// Handle RTL/LTR based on language
i18n.on('languageChanged', (lng) => {
  document.documentElement.dir = (lng === 'he') ? 'rtl' : 'ltr';
  document.documentElement.lang = lng;
});

// Initial direction setting
document.documentElement.dir = (i18n.language === 'he') ? 'rtl' : 'ltr';
document.documentElement.lang = i18n.language;

export default i18n;
