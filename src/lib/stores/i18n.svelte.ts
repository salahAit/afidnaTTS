
import { browser } from '$app/environment';
import { translations } from '../i18n/translations';

export type Language = 'ar' | 'en' | 'fr';

function getInitialLang(): Language {
    if (browser) {
        const saved = localStorage.getItem('lang');
        if (saved === 'ar' || saved === 'en' || saved === 'fr') return saved as Language;
        
        // Try to detect browser language
        const browserLang = navigator.language.split('-')[0];
        if (browserLang === 'ar' || browserLang === 'en' || browserLang === 'fr') return browserLang as Language;
    }
    return 'en';
}

let current = $state<Language>(getInitialLang());

export const i18n = {
    get lang() { return current; },
    get dir() { return current === 'ar' ? 'rtl' : 'ltr'; },
    
    setLang(lang: Language) {
        current = lang;
        if (browser) {
            localStorage.setItem('lang', lang);
            document.documentElement.lang = lang;
            document.documentElement.dir = this.dir;
        }
    },
    
    t(key: keyof typeof translations.en, params: Record<string, any> = {}) {
        let text = translations[current][key] || translations['en'][key] || key;
        
        // Replace params like {n}
        Object.keys(params).forEach(param => {
            text = text.replace(`{${param}}`, params[param].toString());
        });
        
        return text;
    },
    
    init() {
        if (browser) {
            document.documentElement.lang = current;
            document.documentElement.dir = this.dir;
        }
    }
};
