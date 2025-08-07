import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Search, X, Clock, Users, Target, BarChart3, ArrowRight } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { api } from '@/lib/api'
import { useTranslation } from '@/contexts/TranslationContext'

interface GlobalSearchProps {
  onClose: () => void
}

const getSearchCategories = (t: (key: string) => string) => [
  { id: 'customers', label: t('search.customers.category'), icon: Users, color: 'blue' },
  { id: 'campaigns', label: t('search.campaigns.category'), icon: Target, color: 'purple' },
  { id: 'reports', label: t('search.reports.category'), icon: BarChart3, color: 'green' },
]

export const GlobalSearch: React.FC<GlobalSearchProps> = ({ onClose }) => {
  const { t } = useTranslation()
  const [query, setQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const navigate = useNavigate()
  const searchCategories = getSearchCategories(t)

  const { data: searchResults, isLoading } = useQuery({
    queryKey: ['search', query, selectedCategory],
    queryFn: async () => {
      // Mock search results for demo
      await new Promise(resolve => setTimeout(resolve, 500)) // Simulate API delay
      
      const mockResults = [
        { id: '1', title: 'John Smith - Premium Customer', description: 'High-value customer, VIP status', category: 'customers', link: '/customers/1' },
        { id: '2', title: 'Summer Sale Campaign', description: 'Active campaign with 23% ROI', category: 'campaigns', link: '/campaigns/2' },
        { id: '3', title: 'Q4 Revenue Report', description: 'Quarterly performance analysis', category: 'reports', link: '/reports/3' },
        { id: '4', title: 'Sarah Johnson - New Lead', description: 'Recently engaged prospect', category: 'customers', link: '/customers/4' },
        { id: '5', title: 'Email Marketing Campaign', description: 'Automated email sequence', category: 'campaigns', link: '/campaigns/5' }
      ]
      
      return mockResults.filter(result => 
        result.title.toLowerCase().includes(query.toLowerCase()) ||
        result.description.toLowerCase().includes(query.toLowerCase())
      ).filter(result => 
        selectedCategory === 'all' || result.category === selectedCategory
      )
    },
    enabled: query.length > 2,
  })

  const { data: recentSearches } = useQuery({
    queryKey: ['recent-searches'],
    queryFn: async () => {
      // Mock recent searches
      return [
        { id: '1', query: 'VIP customers' },
        { id: '2', query: 'Campaign performance' },
        { id: '3', query: 'Revenue analytics' },
        { id: '4', query: 'Customer segments' }
      ]
    },
  })

  const handleResultClick = (result: any) => {
    navigate(result.link)
    onClose()
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose()
    }
  }

  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
      }
    }

    document.addEventListener('keydown', handleGlobalKeyDown)
    return () => document.removeEventListener('keydown', handleGlobalKeyDown)
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 z-50 flex items-start justify-center pt-20"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: -20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: -20 }}
        className="w-full max-w-2xl bg-white rounded-xl shadow-2xl mx-4"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={t('search.customers')}
              className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              autoFocus
            />
            <button
              onClick={onClose}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 hover:bg-gray-100 rounded"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>

          {/* Category Filters */}
          <div className="flex items-center space-x-2 mt-4">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                selectedCategory === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {t('search.all')}
            </button>
            {searchCategories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`flex items-center px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  selectedCategory === category.id
                    ? `bg-${category.color}-600 text-white`
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <category.icon className="w-4 h-4 mr-1" />
                {category.label}
              </button>
            ))}
          </div>
        </div>

        {/* Search Results */}
        <div className="max-h-96 overflow-y-auto">
          {query.length > 2 ? (
            isLoading ? (
              <div className="p-4">
                <div className="animate-pulse space-y-3">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gray-200 rounded"></div>
                      <div className="flex-1">
                        <div className="h-4 bg-gray-200 rounded w-3/4 mb-1"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : searchResults && searchResults.length > 0 ? (
              <div className="py-2">
                {searchResults.map((result: any) => (
                  <button
                    key={result.id}
                    onClick={() => handleResultClick(result)}
                    className="w-full flex items-center px-4 py-3 hover:bg-gray-50 text-left"
                  >
                    <div className={`w-8 h-8 rounded flex items-center justify-center mr-3 ${
                      result.category === 'customers' ? 'bg-blue-100 text-blue-600' :
                      result.category === 'campaigns' ? 'bg-purple-100 text-purple-600' :
                      'bg-green-100 text-green-600'
                    }`}>
                      {result.category === 'customers' && <Users className="w-4 h-4" />}
                      {result.category === 'campaigns' && <Target className="w-4 h-4" />}
                      {result.category === 'reports' && <BarChart3 className="w-4 h-4" />}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{result.title}</p>
                      <p className="text-sm text-gray-600">{result.description}</p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400" />
                  </button>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center">
                <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">{t('search.noResults')} "{query}"</p>
                <p className="text-sm text-gray-400 mt-1">{t('search.tryDifferent')}</p>
              </div>
            )
          ) : (
            /* Recent Searches */
            <div className="py-2">
              <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
                {t('search.recent')}
              </div>
              {recentSearches?.map((search: any) => (
                <button
                  key={search.id}
                  onClick={() => setQuery(search.query)}
                  className="w-full flex items-center px-4 py-2 hover:bg-gray-50 text-left"
                >
                  <Clock className="w-4 h-4 text-gray-400 mr-3" />
                  <span className="text-gray-700">{search.query}</span>
                </button>
              ))}
              
              {(!recentSearches || recentSearches.length === 0) && (
                <div className="px-4 py-8 text-center">
                  <p className="text-gray-500">{t('search.startTyping')}</p>
                  <p className="text-sm text-gray-400 mt-1">{t('search.searchAcross')}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-gray-200 bg-gray-50 rounded-b-xl">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center space-x-4">
              <span>{t('search.pressEnter')} <kbd className="px-1 py-0.5 bg-white border border-gray-300 rounded">↵</kbd> {t('search.toSelect')}</span>
              <span>{t('search.pressEsc')} <kbd className="px-1 py-0.5 bg-white border border-gray-300 rounded">Esc</kbd> {t('search.toClose')}</span>
            </div>
            <span>{t('search.poweredBy')}</span>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}