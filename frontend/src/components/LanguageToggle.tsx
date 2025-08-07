import React from 'react'
import { Languages } from 'lucide-react'
import { useTranslation } from '@/contexts/TranslationContext'

export const LanguageToggle: React.FC = () => {
  const { language, setLanguage } = useTranslation()

  return (
    <div className="flex items-center space-x-2">
      <Languages className="w-4 h-4 text-gray-600" />
      <div className="flex items-center bg-gray-100 rounded-lg p-1">
        <button
          onClick={() => setLanguage('en')}
          className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
            language === 'en'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          EN
        </button>
        <button
          onClick={() => setLanguage('zh')}
          className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
            language === 'zh'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          中文
        </button>
      </div>
    </div>
  )
}