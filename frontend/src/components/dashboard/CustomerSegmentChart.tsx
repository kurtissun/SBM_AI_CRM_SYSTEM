import React from 'react'
import { Doughnut } from 'react-chartjs-2'
import { useQuery } from '@tanstack/react-query'
import { Users, ChevronRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '@/lib/api'

export const CustomerSegmentChart: React.FC = () => {
  const { data: segmentData, isLoading } = useQuery({
    queryKey: ['customer-segments'],
    queryFn: () => api.get('/segmentation/overview'),
  })

  const chartData = {
    labels: segmentData?.labels || ['VIP Members', 'Regular Customers', 'New Visitors', 'Inactive'],
    datasets: [
      {
        data: segmentData?.values || [25, 45, 20, 10],
        backgroundColor: [
          '#3B82F6',
          '#10B981',
          '#F59E0B',
          '#EF4444',
        ],
        borderColor: [
          '#2563EB',
          '#059669',
          '#D97706',
          '#DC2626',
        ],
        borderWidth: 2,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 20,
          usePointStyle: true,
        },
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.label || ''
            const value = context.parsed || 0
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0)
            const percentage = ((value / total) * 100).toFixed(1)
            return `${label}: ${value.toLocaleString()} (${percentage}%)`
          }
        }
      },
    },
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-48 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Customer Segments</h2>
          <p className="text-sm text-gray-600">Distribution by customer type</p>
        </div>
        <Link
          to="/segmentation"
          className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
        >
          Manage
          <ChevronRight className="w-4 h-4 ml-1" />
        </Link>
      </div>
      
      <div className="h-48 mb-4">
        <Doughnut data={chartData} options={options} />
      </div>

      <div className="space-y-3">
        {Array.isArray(segmentData?.segments) && segmentData.segments.map((segment: any, index: number) => (
          <div key={segment.name} className="flex items-center justify-between">
            <div className="flex items-center">
              <div
                className="w-3 h-3 rounded-full mr-3"
                style={{ backgroundColor: chartData.datasets[0].backgroundColor[index] }}
              ></div>
              <span className="text-sm font-medium text-gray-700">{segment.name}</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">{segment.count}</span>
              <span className="text-xs text-gray-500">({segment.percentage}%)</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Users className="w-5 h-5 text-gray-500 mr-2" />
            <span className="text-sm font-medium text-gray-700">Total Customers</span>
          </div>
          <span className="text-lg font-bold text-gray-900">
            {segmentData?.total?.toLocaleString() || '0'}
          </span>
        </div>
      </div>
    </div>
  )
}