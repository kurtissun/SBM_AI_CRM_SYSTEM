import React from 'react'
import { Globe } from 'lucide-react'
import { useLanguageStore, Language } from '@/stores/languageStore'

interface LanguageSwitcherProps {
  variant?: 'default' | 'minimal'
  className?: string
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ 
  variant = 'default',
  className = '' 
}) => {
  const { language, setLanguage, t } = useLanguageStore()

  const languages: { code: Language; name: string; flag: string }[] = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'zh', name: '中文', flag: '🇨🇳' },
  ]

  if (variant === 'minimal') {
    return (
      <div className={`flex items-center space-x-1 ${className}`}>
        {languages.map((lang) => (
          <button
            key={lang.code}
            onClick={() => setLanguage(lang.code)}
            className={`px-2 py-1 rounded text-sm transition-colors ${
              language === lang.code
                ? 'bg-blue-100 text-blue-600 font-medium'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {lang.flag}
          </button>
        ))}
      </div>
    )
  }

  return (
    <div className={`relative group ${className}`}>
      <button className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors">
        <Globe className="w-4 h-4 text-gray-600" />
        <span className="text-sm text-gray-600">
          {languages.find(l => l.code === language)?.flag}
        </span>
        <span className="text-sm text-gray-600">
          {languages.find(l => l.code === language)?.name}
        </span>
      </button>
      
      <div className="absolute right-0 top-full mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
        <div className="py-1">
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => setLanguage(lang.code)}
              className={`w-full flex items-center space-x-3 px-4 py-2 text-left hover:bg-gray-50 transition-colors ${
                language === lang.code ? 'bg-blue-50 text-blue-600' : 'text-gray-700'
              }`}
            >
              <span className="text-lg">{lang.flag}</span>
              <span className="text-sm font-medium">{lang.name}</span>
              {language === lang.code && (
                <span className="ml-auto text-blue-600">✓</span>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}