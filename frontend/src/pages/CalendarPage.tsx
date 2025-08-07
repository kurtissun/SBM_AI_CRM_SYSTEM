import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Calendar, ChevronLeft, ChevronRight, Plus, Filter, Download,
  Target, Users, Flag, Gift, Sparkles, Clock, MapPin
} from 'lucide-react'
import { toast } from 'react-hot-toast'
import { useTranslation } from '@/contexts/TranslationContext'
import { useCampaignStore } from '@/stores/campaignStore'

interface CalendarEvent {
  id: string
  title: string
  date: string
  type: 'campaign' | 'holiday' | 'event'
  status?: 'active' | 'paused' | 'completed'
  description?: string
  color: string
  isNational?: boolean
}

const chineseHolidays2024: CalendarEvent[] = [
  {
    id: 'ny2024',
    title: '元旦 (New Year\'s Day)',
    date: '2024-01-01',
    type: 'holiday',
    description: 'National holiday - New Year celebrations',
    color: 'bg-red-500',
    isNational: true
  },
  {
    id: 'cny2024',
    title: '春节 (Spring Festival)',
    date: '2024-02-10',
    type: 'holiday',
    description: 'Chinese New Year - Year of the Dragon',
    color: 'bg-red-600',
    isNational: true
  },
  {
    id: 'qingming2024',
    title: '清明节 (Qingming Festival)',
    date: '2024-04-04',
    type: 'holiday',
    description: 'Tomb Sweeping Day',
    color: 'bg-green-600',
    isNational: true
  },
  {
    id: 'labor2024',
    title: '劳动节 (Labor Day)',
    date: '2024-05-01',
    type: 'holiday',
    description: 'International Workers\' Day',
    color: 'bg-blue-600',
    isNational: true
  },
  {
    id: 'dragon2024',
    title: '端午节 (Dragon Boat Festival)',
    date: '2024-06-10',
    type: 'holiday',
    description: 'Traditional dragon boat racing festival',
    color: 'bg-green-500',
    isNational: true
  },
  {
    id: 'midautumn2024',
    title: '中秋节 (Mid-Autumn Festival)',
    date: '2024-09-17',
    type: 'holiday',
    description: 'Moon cake festival',
    color: 'bg-yellow-500',
    isNational: true
  },
  {
    id: 'national2024',
    title: '国庆节 (National Day)',
    date: '2024-10-01',
    type: 'holiday',
    description: 'National Day Golden Week',
    color: 'bg-red-500',
    isNational: true
  },
  {
    id: 'singles2024',
    title: '双十一 (Singles\' Day)',
    date: '2024-11-11',
    type: 'event',
    description: 'Biggest shopping festival',
    color: 'bg-purple-500',
    isNational: false
  },
  {
    id: 'black-friday-2024',
    title: 'Black Friday',
    date: '2024-11-29',
    type: 'event',
    description: 'International shopping event',
    color: 'bg-gray-700',
    isNational: false
  },
  {
    id: '1212-2024',
    title: '双十二 (Double 12)',
    date: '2024-12-12',
    type: 'event',
    description: 'Year-end shopping festival',
    color: 'bg-purple-600',
    isNational: false
  }
]

export const CalendarPage: React.FC = () => {
  const { t } = useTranslation()
  const { campaigns } = useCampaignStore()
  const [currentDate, setCurrentDate] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState<Date | null>(null)
  const [filter, setFilter] = useState<'all' | 'campaigns' | 'holidays' | 'events'>('all')
  const [events, setEvents] = useState<CalendarEvent[]>([])

  // Generate calendar events from campaigns and holidays
  useEffect(() => {
    const campaignEvents: CalendarEvent[] = campaigns.map(campaign => ({
      id: campaign.id,
      title: campaign.name,
      date: campaign.schedule.startDate,
      type: 'campaign' as const,
      status: campaign.status,
      description: `${campaign.objective} campaign - Budget: ¥${campaign.budget.amount.toLocaleString()}`,
      color: campaign.status === 'active' ? 'bg-blue-500' : 
             campaign.status === 'paused' ? 'bg-yellow-500' : 'bg-gray-500'
    }))

    // If no campaigns exist, generate some sample ones
    if (campaigns.length === 0) {
      const { generateMockCampaigns } = useCampaignStore.getState()
      generateMockCampaigns()
    } else {
      setEvents([...campaignEvents, ...chineseHolidays2024])
    }
  }, [campaigns])

  // Calendar grid generation
  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear()
    const month = date.getMonth()
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const daysInMonth = lastDay.getDate()
    const startingDayOfWeek = firstDay.getDay()

    const days = []
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null)
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day))
    }
    
    return days
  }

  const getEventsForDate = (date: Date) => {
    const dateString = date.toISOString().split('T')[0]
    return events.filter(event => {
      if (filter !== 'all') {
        if (filter === 'campaigns' && event.type !== 'campaign') return false
        if (filter === 'holidays' && event.type !== 'holiday') return false
        if (filter === 'events' && event.type !== 'event') return false
      }
      return event.date === dateString
    })
  }

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev)
      if (direction === 'prev') {
        newDate.setMonth(newDate.getMonth() - 1)
      } else {
        newDate.setMonth(newDate.getMonth() + 1)
      }
      return newDate
    })
  }

  const goToToday = () => {
    setCurrentDate(new Date())
    setSelectedDate(new Date())
  }

  const exportCalendar = () => {
    toast.success('Generating calendar export...')
    setTimeout(() => {
      const exportData = {
        month: currentDate.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long' }),
        events: events.map(event => ({
          title: event.title,
          date: event.date,
          type: event.type,
          status: event.status || 'N/A',
          description: event.description
        })),
        campaigns: campaigns.length,
        holidays: chineseHolidays2024.length,
        generated: new Date().toISOString()
      }
      
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `calendar-${currentDate.getFullYear()}-${currentDate.getMonth() + 1}.json`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Calendar exported successfully!')
    }, 1500)
  }

  const days = getDaysInMonth(currentDate)

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">营销日历 (Marketing Calendar)</h1>
          <p className="text-gray-600 mt-2">
            Campaign schedules, Chinese holidays, and important events
          </p>
        </div>
        <div className="flex items-center space-x-3">
          {/* Filter */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Events</option>
            <option value="campaigns">Campaigns Only</option>
            <option value="holidays">Holidays Only</option>
            <option value="events">Shopping Events</option>
          </select>

          <button
            onClick={goToToday}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Clock className="w-4 h-4 mr-2 inline" />
            Today
          </button>

          <button
            onClick={exportCalendar}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="w-4 h-4 mr-2 inline" />
            Export
          </button>
        </div>
      </div>

      {/* Calendar Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigateMonth('prev')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            </button>
            <h2 className="text-2xl font-bold text-gray-900">
              {currentDate.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long' })}
            </h2>
            <button
              onClick={() => navigateMonth('next')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronRight className="w-5 h-5 text-gray-600" />
            </button>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3 text-sm">
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-blue-500 rounded"></div>
                <span>Active Campaigns</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-red-500 rounded"></div>
                <span>National Holidays</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-purple-500 rounded"></div>
                <span>Shopping Events</span>
              </div>
            </div>
          </div>
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-1">
          {/* Week Headers */}
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="p-3 text-center text-sm font-semibold text-gray-500 border-b">
              {day}
            </div>
          ))}

          {/* Calendar Days */}
          {days.map((day, index) => {
            if (!day) {
              return <div key={index} className="h-24 border border-gray-100"></div>
            }

            const dayEvents = getEventsForDate(day)
            const isToday = day.toDateString() === new Date().toDateString()
            const isSelected = selectedDate?.toDateString() === day.toDateString()

            return (
              <motion.div
                key={index}
                whileHover={{ scale: 1.02 }}
                className={`h-24 border border-gray-100 p-1 cursor-pointer transition-colors ${
                  isToday ? 'bg-blue-50 border-blue-200' :
                  isSelected ? 'bg-gray-100' : 'hover:bg-gray-50'
                }`}
                onClick={() => setSelectedDate(day)}
              >
                <div className={`text-sm font-medium mb-1 ${
                  isToday ? 'text-blue-600' : 'text-gray-900'
                }`}>
                  {day.getDate()}
                </div>
                
                <div className="space-y-1">
                  {dayEvents.slice(0, 2).map(event => (
                    <div
                      key={event.id}
                      className={`${event.color} text-white text-xs px-1 py-0.5 rounded truncate`}
                      title={event.title}
                    >
                      {event.type === 'campaign' && <Target className="w-3 h-3 inline mr-1" />}
                      {event.type === 'holiday' && <Flag className="w-3 h-3 inline mr-1" />}
                      {event.type === 'event' && <Gift className="w-3 h-3 inline mr-1" />}
                      {event.title.length > 10 ? `${event.title.substring(0, 10)}...` : event.title}
                    </div>
                  ))}
                  {dayEvents.length > 2 && (
                    <div className="text-xs text-gray-500">
                      +{dayEvents.length - 2} more
                    </div>
                  )}
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* Event Details */}
      {selectedDate && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Events for {selectedDate.toLocaleDateString('zh-CN', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </h3>
          
          {getEventsForDate(selectedDate).length > 0 ? (
            <div className="space-y-4">
              {getEventsForDate(selectedDate).map(event => (
                <div key={event.id} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                  <div className={`w-12 h-12 ${event.color} rounded-lg flex items-center justify-center`}>
                    {event.type === 'campaign' && <Target className="w-6 h-6 text-white" />}
                    {event.type === 'holiday' && <Flag className="w-6 h-6 text-white" />}
                    {event.type === 'event' && <Gift className="w-6 h-6 text-white" />}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="font-semibold text-gray-900">{event.title}</h4>
                      {event.status && (
                        <span className={`px-2 py-0.5 text-xs rounded-full ${
                          event.status === 'active' ? 'bg-green-100 text-green-700' :
                          event.status === 'paused' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {event.status}
                        </span>
                      )}
                      {event.isNational && (
                        <span className="px-2 py-0.5 text-xs bg-red-100 text-red-700 rounded-full">
                          National Holiday
                        </span>
                      )}
                    </div>
                    {event.description && (
                      <p className="text-sm text-gray-600">{event.description}</p>
                    )}
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span>Type: {event.type}</span>
                      <span>Date: {event.date}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No events scheduled for this date</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default CalendarPage