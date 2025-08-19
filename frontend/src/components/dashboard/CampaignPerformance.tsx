import React from "react";
import { Bar } from "react-chartjs-2";
import { useQuery } from "@tanstack/react-query";
import {
  Target,
  TrendingUp,
  Users,
  DollarSign,
  ChevronRight,
} from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";

export const CampaignPerformance: React.FC = () => {
  const { data: campaignData, isLoading } = useQuery<any>({
    queryKey: ["campaign-performance"],
    queryFn: () => api.get("/campaigns/performance"),
  });

  const chartData = {
    labels: Array.isArray((campaignData as any)?.campaigns)
      ? (campaignData as any).campaigns.map((c: any) => c.name)
      : [],
    datasets: [
      {
        label: "Impressions",
        data: Array.isArray((campaignData as any)?.campaigns)
          ? (campaignData as any).campaigns.map((c: any) => c.impressions)
          : [],
        backgroundColor: "rgba(59, 130, 246, 0.8)",
        borderColor: "rgb(59, 130, 246)",
        borderWidth: 1,
        yAxisID: "y",
      },
      {
        label: "Conversions",
        data: Array.isArray(campaignData?.campaigns)
          ? campaignData.campaigns.map((c: any) => c.conversions)
          : [],
        backgroundColor: "rgba(16, 185, 129, 0.8)",
        borderColor: "rgb(16, 185, 129)",
        borderWidth: 1,
        yAxisID: "y1",
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top" as const,
      },
      tooltip: {
        mode: "index" as const,
        intersect: false,
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
        type: "linear" as const,
        display: true,
        position: "left" as const,
        grid: {
          color: "rgba(0, 0, 0, 0.1)",
        },
        ticks: {
          callback: function (value: any) {
            return value.toLocaleString();
          },
        },
      },
      y1: {
        type: "linear" as const,
        display: true,
        position: "right" as const,
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          callback: function (value: any) {
            return value.toLocaleString();
          },
        },
      },
    },
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            Campaign Performance
          </h2>
          <p className="text-sm text-gray-600">Track active campaign metrics</p>
        </div>
        <Link
          to="/campaigns"
          className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
        >
          Manage Campaigns
          <ChevronRight className="w-4 h-4 ml-1" />
        </Link>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <Target className="w-5 h-5 text-blue-600" />
            <span className="text-xs text-blue-600 font-medium">Active</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {campaignData?.summary?.active || 0}
          </p>
          <p className="text-sm text-gray-600">Campaigns</p>
        </div>

        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            <span className="text-xs text-green-600 font-medium">
              +{campaignData?.summary?.growth || 0}%
            </span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {campaignData?.summary?.totalImpressions?.toLocaleString() || 0}
          </p>
          <p className="text-sm text-gray-600">Total Impressions</p>
        </div>

        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <Users className="w-5 h-5 text-purple-600" />
            <span className="text-xs text-purple-600 font-medium">CVR</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {campaignData?.summary?.conversionRate || 0}%
          </p>
          <p className="text-sm text-gray-600">Conversion Rate</p>
        </div>

        <div className="bg-orange-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="w-5 h-5 text-orange-600" />
            <span className="text-xs text-orange-600 font-medium">ROI</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {campaignData?.summary?.roi || 0}%
          </p>
          <p className="text-sm text-gray-600">Return on Investment</p>
        </div>
      </div>

      {/* Chart */}
      <div className="h-64">
        <Bar data={chartData} options={options} />
      </div>

      {/* Top Campaigns Table */}
      <div className="mt-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">
          Top Performing Campaigns
        </h3>
        <div className="space-y-2">
          {Array.isArray(campaignData?.topCampaigns) &&
            campaignData.topCampaigns
              .slice(0, 3)
              .map((campaign: any, index: number) => (
                <div
                  key={campaign.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                      <span className="text-sm font-bold text-blue-600">
                        {index + 1}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {campaign.name}
                      </p>
                      <p className="text-xs text-gray-600">{campaign.type}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      {campaign.conversionRate}%
                    </p>
                    <p className="text-xs text-gray-600">CVR</p>
                  </div>
                </div>
              ))}
        </div>
      </div>
    </div>
  );
};
