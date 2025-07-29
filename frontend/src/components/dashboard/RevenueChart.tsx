import React from 'react'
import { Line } from 'react-chartjs-2'
import { useQuery } from '@tanstack/react-query'
import { TrendingUp, DollarSign } from 'lucide-react'
import { api } from '@/lib/api'

interface RevenueChartProps {
  period: string
}

export const RevenueChart: React.FC<RevenueChartProps> = ({ period }) => {
  const { data: revenueData, isLoading } = useQuery({
    queryKey: ['revenue-chart', period],
    queryFn: () => api.get(`/analytics/revenue?period=${period}`),
  })

  const chartData = {
    labels: revenueData?.labels || [],
    datasets: [
      {
        label: 'Revenue',
        data: revenueData?.revenue || [],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Predicted',
        data: revenueData?.predicted || [],
        borderColor: 'rgb(168, 85, 247)',
        backgroundColor: 'rgba(168, 85, 247, 0.1)',
        borderWidth: 2,
        borderDash: [5, 5],
        fill: false,
        tension: 0.4,
      }
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: ¥${context.parsed.y.toLocaleString()}`
          }
        }
      },
    },
    scales: {
      x: {
        display: true,
        grid: {
          display: false,
        },
      },
      y: {
        display: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
        ticks: {
          callback: function(value: any) {
            return '¥' + value.toLocaleString()
          },
        },
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Revenue Analytics</h2>
          <p className="text-sm text-gray-600">Track revenue performance and predictions</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <DollarSign className="w-5 h-5 text-green-600 mr-2" />
            <span className="text-sm font-medium text-gray-700">
              Total: ¥{revenueData?.total?.toLocaleString() || '0'}
            </span>
          </div>
          <div className="flex items-center">
            <TrendingUp className="w-5 h-5 text-blue-600 mr-2" />
            <span className="text-sm font-medium text-gray-700">
              Growth: {revenueData?.growth || '0'}%
            </span>
          </div>
        </div>
      </div>
      <div className="h-64">
        <Line data={chartData} options={options} />
      </div>
    </div>
  )
}