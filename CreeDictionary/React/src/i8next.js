import i18next from 'i18next';
//import enLocalesTranslationJson from './locals/en/translation'
//import jaLocalesTranslationJson from './locals/ja/translation'
import jaLocalesTranslationJson from './locals/ja/jaTranslations.json'

/*i18next
    .init({
        fallbackLng: 'ja',
        debug: true,
        resources: {
            en: {
                translation: enLocalesTranslationJson
            },
            ja: {
                translation: jaLocalesTranslationJson
            }
        }
    });*/

    i18next.init({
        fallbackLng: 'ja',
        debug: true,
        resources: {
            ja: {
              translation: jaLocalesTranslationJson
            },
            en: {
                translation: {
                  "hello": "hello"
                }
              }

          }
    });

export default i18next;