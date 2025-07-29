import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Brain, Users, Zap, BarChart3, Target, Plus, Play, Settings } from 'lucide-react'

export const SegmentationStudio: React.FC = () => {
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('kmeans')

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Intelligent Segmentation Studio</h1>
          <p className="text-gray-600 mt-1">AI-powered customer segmentation and clustering</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          <Plus className="w-4 h-4 mr-2 inline" />
          Create Segment
        </button>
      </div>

      {/* Algorithm Selection */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">ML Algorithm Selection</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {['kmeans', 'dbscan', 'hierarchical'].map((algo) => (
            <button
              key={algo}
              onClick={() => setSelectedAlgorithm(algo)}
              className={`p-4 border rounded-lg text-left transition-colors ${
                selectedAlgorithm === algo
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <Brain className="w-5 h-5 text-blue-600" />
                {selectedAlgorithm === algo && (
                  <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                )}
              </div>
              <h3 className="font-medium text-gray-900 capitalize">{algo}</h3>
              <p className="text-sm text-gray-600">
                {algo === 'kmeans' && 'Centroid-based clustering'}
                {algo === 'dbscan' && 'Density-based clustering'}
                {algo === 'hierarchical' && 'Tree-based clustering'}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Segment Builder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Visual Segment Builder</h2>
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Drag and drop criteria here</p>
            </div>
            <div className="flex items-center space-x-2">
              <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
                <Play className="w-4 h-4 mr-2 inline" />
                Run Segmentation
              </button>
              <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                <Settings className="w-4 h-4 mr-2 inline" />
                Advanced Settings
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Segment Preview</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center">
                <Users className="w-5 h-5 text-blue-600 mr-2" />
                <span className="font-medium">High-Value Customers</span>
              </div>
              <span className="text-sm text-gray-600">2,543 customers</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div className="flex items-center">
                <Users className="w-5 h-5 text-green-600 mr-2" />
                <span className="font-medium">Frequent Shoppers</span>
              </div>
              <span className="text-sm text-gray-600">1,827 customers</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
              <div className="flex items-center">
                <Users className="w-5 h-5 text-orange-600 mr-2" />
                <span className="font-medium">At-Risk Customers</span>
              </div>
              <span className="text-sm text-gray-600">456 customers</span>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Segmentation Performance</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">0.73</div>
            <div className="text-sm text-gray-600">Silhouette Score</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">5</div>
            <div className="text-sm text-gray-600">Optimal Clusters</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">89%</div>
            <div className="text-sm text-gray-600">Classification Accuracy</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">12.4</div>
            <div className="text-sm text-gray-600">Davies-Bouldin Index</div>
          </div>
        </div>
      </div>
    </div>
  )
}