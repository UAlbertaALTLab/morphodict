import i18next from 'i18next';
import creeTranslation from '../locals/cree/creeTranslations.json';
import syllabicTranslation from '../locals/syllabics/syllabicTranslations.json';
import enTranslation from '../locals/en/enTranslations.json';
import LanguageDetector from 'i18next-browser-languagedetector';

    i18next
    //.use(LanguageDetector)
    .init({
        lng: 'en',
        fallbackLng: 'en',
        debug: true,
        resources: {
            cree: {
                translation: creeTranslation
            },
            en: {
                translation: enTranslation
            },
            syllabic: {
                translation: syllabicTranslation
            }

          }
    });

export default i18next;