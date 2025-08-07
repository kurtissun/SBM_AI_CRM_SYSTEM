import React from 'react'
import { useTranslation } from '@/contexts/TranslationContext'
import { useTheme } from '@/contexts/ThemeContext'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  RadialLinearScale
} from 'chart.js'
import { Line, Bar, Doughnut, Pie, Radar, PolarArea } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  RadialLinearScale
)

// Theme-aware chart color palettes
export const getChartColors = (isDark: boolean, theme?: string) => {
  const isPureBlack = theme === 'pure-black'
  const isPureWhite = theme === 'pure-white'
  
  return {
  primary: [
    isDark ? 'rgba(96, 165, 250, 0.8)' : 'rgba(59, 130, 246, 0.8)',  // Blue
    isDark ? 'rgba(52, 211, 153, 0.8)' : 'rgba(16, 185, 129, 0.8)',  // Green
    isDark ? 'rgba(251, 191, 36, 0.8)' : 'rgba(245, 158, 11, 0.8)',  // Orange
    isDark ? 'rgba(167, 139, 250, 0.8)' : 'rgba(139, 92, 246, 0.8)', // Purple
    isDark ? 'rgba(248, 113, 113, 0.8)' : 'rgba(239, 68, 68, 0.8)',  // Red
    isDark ? 'rgba(34, 211, 238, 0.8)' : 'rgba(6, 182, 212, 0.8)',   // Cyan
    isDark ? 'rgba(244, 114, 182, 0.8)' : 'rgba(236, 72, 153, 0.8)', // Pink
    isDark ? 'rgba(74, 222, 128, 0.8)' : 'rgba(34, 197, 94, 0.8)',   // Emerald
  ],
  primarySolid: [
    isDark ? 'rgb(96, 165, 250)' : 'rgb(59, 130, 246)',  // Blue
    isDark ? 'rgb(52, 211, 153)' : 'rgb(16, 185, 129)',  // Green
    isDark ? 'rgb(251, 191, 36)' : 'rgb(245, 158, 11)',  // Orange
    isDark ? 'rgb(167, 139, 250)' : 'rgb(139, 92, 246)', // Purple
    isDark ? 'rgb(248, 113, 113)' : 'rgb(239, 68, 68)',  // Red
    isDark ? 'rgb(34, 211, 238)' : 'rgb(6, 182, 212)',   // Cyan
    isDark ? 'rgb(244, 114, 182)' : 'rgb(236, 72, 153)', // Pink
    isDark ? 'rgb(74, 222, 128)' : 'rgb(34, 197, 94)',   // Emerald
  ],
  background: isPureBlack ? 'rgba(0, 0, 0, 0.9)' : isPureWhite ? 'rgba(255, 255, 255, 0.9)' : isDark ? 'rgba(31, 41, 55, 0.8)' : 'rgba(255, 255, 255, 0.8)',
  gridColor: isPureBlack ? 'rgba(51, 51, 51, 0.5)' : isPureWhite ? 'rgba(229, 231, 235, 0.5)' : isDark ? 'rgba(75, 85, 99, 0.3)' : 'rgba(0, 0, 0, 0.1)',
  textColor: isPureBlack ? '#ffffff' : isPureWhite ? '#000000' : isDark ? '#e5e7eb' : '#374151'
}}

// Theme-aware common chart options
export const getCommonOptions = (isDark: boolean, theme?: string) => {
  const colors = getChartColors(isDark, theme)
  
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
          color: colors.textColor,
          font: {
            size: 12,
          }
        }
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: colors.textColor,
          font: {
            size: 12,
          }
        }
      },
      y: {
        grid: {
          color: colors.gridColor,
        },
        ticks: {
          color: colors.textColor,
          font: {
            size: 12,
          }
        }
      }
    }
  }
}

// Theme-aware Demo Data Generators
export const generateRevenueData = (isDark: boolean, theme?: string) => {
  const colors = getChartColors(isDark, theme)
  
  return {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: 'Revenue (¥)',
        data: [385000, 426000, 398000, 512000, 478000, 534000, 612000, 589000, 645000, 698000, 756000, 823000],
        borderColor: colors.primarySolid[0],
        backgroundColor: colors.primary[0],
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: colors.primarySolid[0],
        pointBorderColor: isDark ? '#374151' : '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
      },
      {
        label: 'Target (¥)',
        data: [400000, 420000, 440000, 460000, 480000, 500000, 520000, 540000, 560000, 580000, 600000, 620000],
        borderColor: colors.primarySolid[1],
        backgroundColor: colors.primary[1],
        borderWidth: 2,
        borderDash: [5, 5],
        fill: false,
        tension: 0.4,
      }
    ]
  }
}

export const generateCustomerSegmentData = (isDark: boolean, theme?: string) => {
  const colors = getChartColors(isDark, theme)
  
  return {
    labels: ['VIP Customers', 'Regular Customers', 'New Customers', 'Inactive Customers'],
    datasets: [
      {
        data: [156, 342, 98, 67],
        backgroundColor: [
          colors.primary[2], // Orange
          colors.primary[0], // Blue
          colors.primary[1], // Green
          colors.primary[3], // Purple
        ],
        borderColor: [
          colors.primarySolid[2], // Orange
          colors.primarySolid[0], // Blue
          colors.primarySolid[1], // Green
          colors.primarySolid[3], // Purple
        ],
        borderWidth: 2,
        hoverOffset: 4,
      }
    ]
  }
}

export const generateCampaignPerformanceData = (isDark: boolean, theme?: string) => {
  const colors = getChartColors(isDark, theme)
  
  return {
    labels: ['Email Marketing', 'Social Media', 'SMS Campaigns', 'Display Ads', 'Search Ads'],
    datasets: [
      {
        label: 'ROI (%)',
        data: [245, 189, 298, 167, 203],
        backgroundColor: colors.primary,
        borderColor: colors.primarySolid,
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      }
    ]
  }
}

export const generateEngagementRadarData = (isDark: boolean, theme?: string) => {
  const colors = getChartColors(isDark, theme)
  
  return {
    labels: ['Email Opens', 'Click Rate', 'Social Shares', 'Website Visits', 'App Usage', 'Purchase Rate'],
    datasets: [
      {
        label: 'Current Month',
        data: [85, 72, 68, 91, 76, 83],
        borderColor: colors.primarySolid[0],
        backgroundColor: colors.primary[0].replace('0.8', '0.2'),
        borderWidth: 2,
        pointBackgroundColor: colors.primarySolid[0],
        pointBorderColor: isDark ? '#374151' : '#fff',
        pointHoverBackgroundColor: isDark ? '#374151' : '#fff',
        pointHoverBorderColor: colors.primarySolid[0],
      },
      {
        label: 'Previous Month',
        data: [78, 68, 62, 87, 71, 79],
        borderColor: colors.primarySolid[1],
        backgroundColor: colors.primary[1].replace('0.8', '0.2'),
        borderWidth: 2,
        pointBackgroundColor: colors.primarySolid[1],
        pointBorderColor: isDark ? '#374151' : '#fff',
        pointHoverBackgroundColor: isDark ? '#374151' : '#fff',
        pointHoverBorderColor: colors.primarySolid[1],
      }
    ]
  }
}

export const generateChurnAnalysisData = (isDark: boolean, theme?: string) => {
  const colors = getChartColors(isDark, theme)
  
  return {
    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
    datasets: [
      {
        label: 'Customer Retention (%)',
        data: [94.5, 92.8, 95.2, 93.7],
        borderColor: colors.primarySolid[1],
        backgroundColor: colors.primary[1].replace('0.8', '0.1'),
        borderWidth: 3,
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Churn Rate (%)',
        data: [5.5, 7.2, 4.8, 6.3],
        borderColor: colors.primarySolid[4],
        backgroundColor: colors.primary[4].replace('0.8', '0.1'),
        borderWidth: 3,
        fill: true,
        tension: 0.4,
      }
    ]
  }
}

export const generateGeographicData = (isDark: boolean, theme?: string) => {
  const colors = getChartColors(isDark, theme)
  
  return {
    labels: ['Shanghai', 'Beijing', 'Shenzhen', 'Guangzhou', 'Hangzhou', 'Chengdu', 'Others'],
    datasets: [
      {
        data: [285, 234, 198, 167, 134, 123, 156],
        backgroundColor: colors.primary,
        borderWidth: 0,
        hoverOffset: 8,
      }
    ]
  }
}

export const generateAIInsightsData = (isDark: boolean, theme?: string) => {
  const colors = getChartColors(isDark, theme)
  
  return {
    labels: ['Prediction Accuracy', 'Data Quality', 'Model Performance', 'Insight Relevance', 'User Satisfaction'],
    datasets: [
      {
        data: [94, 89, 92, 87, 91],
        backgroundColor: colors.primary.slice(0, 5),
        borderWidth: 0,
      }
    ]
  }
}

// Chart Components
interface ChartProps {
  height?: number
  title?: string
  className?: string
}

export const RevenueChart: React.FC<ChartProps> = ({ height = 300, title, className = '' }) => {
  const { theme } = useTheme()
  const isDark = theme === 'dark' || theme === 'pure-black'
  
  return (
    <div className={`relative ${className}`} style={{ height }}>
      {title && <h3 className={`text-lg font-semibold mb-4 ${
        isDark ? 'text-gray-100' : 'text-gray-900'
      }`}>{title}</h3>}
      <Line data={generateRevenueData(isDark, theme)} options={getCommonOptions(isDark, theme)} />
    </div>
  )
}

export const CustomerSegmentChart: React.FC<ChartProps> = ({ height = 300, title, className = '' }) => {
  const { theme } = useTheme()
  const isDark = theme === 'dark' || theme === 'pure-black'
  const colors = getChartColors(isDark, theme)
  
  return (
    <div className={`relative ${className}`} style={{ height }}>
      {title && <h3 className={`text-lg font-semibold mb-4 ${
        isDark ? 'text-gray-100' : 'text-gray-900'
      }`}>{title}</h3>}
      <Doughnut 
        data={generateCustomerSegmentData(isDark, theme)} 
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom' as const,
              labels: {
                usePointStyle: true,
                padding: 20,
                color: colors.textColor,
                font: {
                  size: 12,
                }
              }
            },
          }
        }} 
      />
    </div>
  )
}

export const CampaignPerformanceChart: React.FC<ChartProps> = ({ height = 300, title, className = '' }) => {
  const { theme } = useTheme()
  const isDark = theme === 'dark' || theme === 'pure-black'
  
  return (
    <div className={`relative ${className}`} style={{ height }}>
      {title && <h3 className={`text-lg font-semibold mb-4 ${
        isDark ? 'text-gray-100' : 'text-gray-900'
      }`}>{title}</h3>}
      <Bar data={generateCampaignPerformanceData(isDark, theme)} options={getCommonOptions(isDark, theme)} />
    </div>
  )
}

export const EngagementRadarChart: React.FC<ChartProps> = ({ height = 300, title, className = '' }) => {
  const { theme } = useTheme()
  const isDark = theme === 'dark' || theme === 'pure-black'
  const colors = getChartColors(isDark, theme)
  
  return (
    <div className={`relative ${className}`} style={{ height }}>
      {title && <h3 className={`text-lg font-semibold mb-4 ${
        isDark ? 'text-gray-100' : 'text-gray-900'
      }`}>{title}</h3>}
      <Radar 
        data={generateEngagementRadarData(isDark, theme)} 
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top' as const,
              labels: {
                color: colors.textColor,
                font: {
                  size: 12,
                }
              }
            }
          },
          scales: {
            r: {
              beginAtZero: true,
              max: 100,
              ticks: {
                stepSize: 20,
                color: colors.textColor,
              },
              grid: {
                color: colors.gridColor,
              },
              angleLines: {
                color: colors.gridColor,
              }
            }
          }
        }} 
      />
    </div>
  )
}

export const ChurnAnalysisChart: React.FC<ChartProps> = ({ height = 300, title, className = '' }) => {
  const { theme } = useTheme()
  const isDark = theme === 'dark' || theme === 'pure-black'
  
  return (
    <div className={`relative ${className}`} style={{ height }}>
      {title && <h3 className={`text-lg font-semibold mb-4 ${
        isDark ? 'text-gray-100' : 'text-gray-900'
      }`}>{title}</h3>}
      <Line data={generateChurnAnalysisData(isDark, theme)} options={getCommonOptions(isDark, theme)} />
    </div>
  )
}

export const GeographicChart: React.FC<ChartProps> = ({ height = 300, title, className = '' }) => {
  const { theme } = useTheme()
  const isDark = theme === 'dark' || theme === 'pure-black'
  const colors = getChartColors(isDark, theme)
  
  return (
    <div className={`relative ${className}`} style={{ height }}>
      {title && <h3 className={`text-lg font-semibold mb-4 ${
        isDark ? 'text-gray-100' : 'text-gray-900'
      }`}>{title}</h3>}
      <PolarArea 
        data={generateGeographicData(isDark, theme)} 
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom' as const,
              labels: {
                usePointStyle: true,
                padding: 15,
                color: colors.textColor,
                font: {
                  size: 12,
                }
              }
            }
          }
        }} 
      />
    </div>
  )
}

export const AIInsightsChart: React.FC<ChartProps> = ({ height = 300, title, className = '' }) => {
  const { theme } = useTheme()
  const isDark = theme === 'dark' || theme === 'pure-black'
  const colors = getChartColors(isDark, theme)
  
  return (
    <div className={`relative ${className}`} style={{ height }}>
      {title && <h3 className={`text-lg font-semibold mb-4 ${
        isDark ? 'text-gray-100' : 'text-gray-900'
      }`}>{title}</h3>}
      <Pie 
        data={generateAIInsightsData(isDark, theme)} 
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right' as const,
              labels: {
                usePointStyle: true,
                padding: 20,
                color: colors.textColor,
                font: {
                  size: 11,
                }
              }
            }
          }
        }} 
      />
    </div>
  )
}

// Enhanced Dashboard Chart Grid
export const DashboardChartsGrid: React.FC = () => {
  const { t } = useTranslation()
  const { theme } = useTheme()
  const isDark = theme === 'dark' || theme === 'pure-black'
  
  return (
  <div className="space-y-6">
    {/* Primary Charts Row */}
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="gradient-border">
        <div className={`gradient-border-content seamless-container p-6 rounded-xl shadow-lg`}>
          <RevenueChart title={t('dashboard.revenue')} height={300} />
        </div>
      </div>
      <div className="gradient-border">
        <div className={`gradient-border-content seamless-container p-6 rounded-xl shadow-lg`}>
          <CustomerSegmentChart title={t('dashboard.segments')} height={300} />
        </div>
      </div>
    </div>

    {/* Secondary Charts Row */}
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="gradient-border">
        <div className="gradient-border-content seamless-container p-6 rounded-xl shadow-lg">
          <CampaignPerformanceChart title={t('dashboard.campaigns')} height={250} />
        </div>
      </div>
      <div className="gradient-border">
        <div className="gradient-border-content seamless-container p-6 rounded-xl shadow-lg">
          <ChurnAnalysisChart title={t('customers.retentionRate')} height={250} />
        </div>
      </div>
      <div className="gradient-border">
        <div className="gradient-border-content seamless-container p-6 rounded-xl shadow-lg">
          <AIInsightsChart title={t('dashboard.insights')} height={250} />
        </div>
      </div>
    </div>

    {/* Advanced Analytics Row */}
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="gradient-border">
        <div className="gradient-border-content seamless-container p-6 rounded-xl shadow-lg">
          <EngagementRadarChart title={t('dashboard.engagement')} height={300} />
        </div>
      </div>
      <div className="gradient-border">
        <div className="gradient-border-content seamless-container p-6 rounded-xl shadow-lg">
          <GeographicChart title="Geographic Distribution" height={300} />
        </div>
      </div>
    </div>
  </div>
  )
}

// Real-time Chart Component
export const RealTimeChart: React.FC<{
  data: number[]
  labels: string[]
  title: string
  color?: string
}> = ({ data, labels, title, color = 'rgba(59, 130, 246, 0.8)' }) => {
  const chartData = {
    labels,
    datasets: [
      {
        label: title,
        data,
        borderColor: color,
        backgroundColor: color.replace('0.8', '0.1'),
        borderWidth: 2,
        fill: true,
        tension: 0.4,
      }
    ]
  }

  return (
    <div className="h-48">
      <Line 
        data={chartData} 
        options={{
          ...getCommonOptions(false),
          animation: {
            duration: 750,
          },
          scales: {
            ...getCommonOptions(false).scales,
            x: {
              ...getCommonOptions(false).scales.x,
              display: false,
            },
            y: {
              ...getCommonOptions(false).scales.y,
              display: false,
            }
          },
          plugins: {
            legend: {
              display: false,
            }
          }
        }} 
      />
    </div>
  )
}