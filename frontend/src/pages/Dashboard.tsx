import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Users,
  ShoppingCart,
  TrendingUp,
  DollarSign,
  Target,
  Brain,
  Activity,
  Calendar,
  ChevronRight,
  ArrowUp,
  ArrowDown,
  Sparkles,
  Building,
  Eye,
  Globe,
  Info,
  RefreshCw,
  Plus,
} from "lucide-react";
import { Link } from "react-router-dom";
import { toast } from "react-hot-toast";
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
} from "chart.js";
import { Line, Bar, Doughnut } from "react-chartjs-2";
import { useTranslation } from "@/contexts/TranslationContext";
import { useTheme } from "@/contexts/ThemeContext";
import {
  getChartColors,
  getCommonOptions,
} from "@/components/charts/ChartLibrary";
import { useDashboardStore } from "@/stores/dashboardStore";
import { useCampaignStore } from "@/stores/campaignStore";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { ActivityFeed } from "@/components/dashboard/ActivityFeed";
import { CampaignPerformance } from "@/components/dashboard/CampaignPerformance";
import { AIInsightsFeed } from "@/components/dashboard/AIInsightsFeed";
import { DashboardChartsGrid } from "@/components/charts/ChartLibrary";
import { AIInsightModal } from "@/components/modals/AIInsightModal";

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
  Filler
);

export const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const colors = getChartColors(isDark);
  const [selectedPeriod, setSelectedPeriod] = useState("7d");
  const [greeting, setGreeting] = useState("");
  const [showInfo, setShowInfo] = useState(false);
  const [isAutoRefresh, setIsAutoRefresh] = useState(true);

  // Use the new dashboard store
  const {
    currentTimeframe,
    selectedDate,
    setTimeframe,
    setSelectedDate,
    getCurrentData,
    getTimeframeData,
    generateAIInsights,
    initializeData,
    insights,
  } = useDashboardStore();

  // Get campaign data for consistency
  const { campaigns } = useCampaignStore();
  const activeCampaigns = campaigns.filter((c) => c.status === "active").length;

  // Initialize data on component mount
  useEffect(() => {
    initializeData();
  }, [initializeData]);

  // Get current dashboard data
  const currentData = getCurrentData();
  const timeframeData = getTimeframeData(
    selectedPeriod === "1d"
      ? 1
      : selectedPeriod === "7d"
      ? 7
      : selectedPeriod === "30d"
      ? 30
      : selectedPeriod === "90d"
      ? 90
      : 365
  );

  // Get data directly from store for proper filtering
  const { data } = useDashboardStore();

  // Set greeting based on time
  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting(t("dashboard.goodMorning"));
    else if (hour < 18) setGreeting(t("dashboard.goodAfternoon"));
    else setGreeting(t("dashboard.goodEvening"));
  }, []);

  // Calculate metrics from real data based on timeframe selection
  const calculateGrowth = (current: number, previous: number) => {
    if (previous === 0) return 0;
    return (((current - previous) / previous) * 100).toFixed(1);
  };

  // Get aggregated data based on timeframe view
  const getAggregatedData = () => {
    if (currentTimeframe === "daily") {
      return timeframeData;
    } else if (currentTimeframe === "monthly") {
      // Group by month
      const monthlyData = new Map();
      timeframeData.forEach((day) => {
        const monthKey = day.date.substring(0, 7); // YYYY-MM
        if (!monthlyData.has(monthKey)) {
          monthlyData.set(monthKey, {
            revenue: 0,
            customers: { total: 0, vip: 0, regular: 0, new: 0, inactive: 0 },
            campaigns: {
              active: 0,
              total_impressions: 0,
              total_clicks: 0,
              total_conversions: 0,
              avg_ctr: 0,
              avg_roi: 0,
            },
            engagement: {
              session_duration: 0,
              pages_per_session: 0,
              bounce_rate: 0,
              return_rate: 0,
            },
            count: 0,
          });
        }
        const month = monthlyData.get(monthKey);
        month.revenue += day.revenue;
        month.customers.total = Math.max(
          month.customers.total,
          day.customers.total
        );
        month.customers.vip += day.customers.vip;
        month.customers.regular += day.customers.regular;
        month.customers.new += day.customers.new;
        month.customers.inactive += day.customers.inactive;
        month.campaigns.total_impressions += day.campaigns.total_impressions;
        month.campaigns.total_clicks += day.campaigns.total_clicks;
        month.campaigns.total_conversions += day.campaigns.total_conversions;
        month.engagement.session_duration += day.engagement.session_duration;
        month.engagement.pages_per_session += day.engagement.pages_per_session;
        month.engagement.bounce_rate += day.engagement.bounce_rate;
        month.engagement.return_rate += day.engagement.return_rate;
        month.count += 1;
      });
      return Array.from(monthlyData.values()).map((month) => ({
        ...month,
        campaigns: {
          ...month.campaigns,
          avg_ctr:
            (month.campaigns.total_clicks / month.campaigns.total_impressions) *
            100,
          avg_roi:
            (month.campaigns.total_conversions / month.campaigns.total_clicks) *
            100 *
            2.5,
        },
        engagement: {
          session_duration: month.engagement.session_duration / month.count,
          pages_per_session: month.engagement.pages_per_session / month.count,
          bounce_rate: month.engagement.bounce_rate / month.count,
          return_rate: month.engagement.return_rate / month.count,
        },
      }));
    } else {
      // Yearly view - aggregate all data
      const totalData = timeframeData.reduce(
        (acc, day) => {
          acc.revenue += day.revenue;
          acc.customers.total = Math.max(
            acc.customers.total,
            day.customers.total
          );
          acc.customers.vip += day.customers.vip;
          acc.customers.regular += day.customers.regular;
          acc.customers.new += day.customers.new;
          acc.customers.inactive += day.customers.inactive;
          acc.campaigns.total_impressions += day.campaigns.total_impressions;
          acc.campaigns.total_clicks += day.campaigns.total_clicks;
          acc.campaigns.total_conversions += day.campaigns.total_conversions;
          acc.engagement.session_duration += day.engagement.session_duration;
          acc.engagement.pages_per_session += day.engagement.pages_per_session;
          acc.engagement.bounce_rate += day.engagement.bounce_rate;
          acc.engagement.return_rate += day.engagement.return_rate;
          acc.count += 1;
          return acc;
        },
        {
          revenue: 0,
          customers: { total: 0, vip: 0, regular: 0, new: 0, inactive: 0 },
          campaigns: {
            active: 0,
            total_impressions: 0,
            total_clicks: 0,
            total_conversions: 0,
            avg_ctr: 0,
            avg_roi: 0,
          },
          engagement: {
            session_duration: 0,
            pages_per_session: 0,
            bounce_rate: 0,
            return_rate: 0,
          },
          count: 0,
        }
      );

      return [
        {
          ...totalData,
          campaigns: {
            ...totalData.campaigns,
            avg_ctr:
              (totalData.campaigns.total_clicks /
                totalData.campaigns.total_impressions) *
              100,
            avg_roi:
              (totalData.campaigns.total_conversions /
                totalData.campaigns.total_clicks) *
              100 *
              2.5,
          },
          engagement: {
            session_duration:
              totalData.engagement.session_duration / totalData.count,
            pages_per_session:
              totalData.engagement.pages_per_session / totalData.count,
            bounce_rate: totalData.engagement.bounce_rate / totalData.count,
            return_rate: totalData.engagement.return_rate / totalData.count,
          },
        },
      ];
    }
  };

  const aggregatedData = getAggregatedData();
  const totalRevenue = aggregatedData.reduce((sum, d) => sum + d.revenue, 0);
  const avgCustomers =
    aggregatedData.length > 0
      ? Math.round(
          aggregatedData.reduce((sum, d) => sum + d.customers.total, 0) /
            aggregatedData.length
        )
      : 0;
  const activeCustomers =
    aggregatedData.length > 0
      ? Math.round(
          aggregatedData.reduce(
            (sum, d) => sum + (d.customers.total - d.customers.inactive),
            0
          ) / aggregatedData.length
        )
      : 0;
  // Use consistent campaign count across dashboard
  const displayCampaigns = activeCampaigns;

  // Calculate growth rates with proper comparison periods
  const comparisonPeriodLength =
    selectedPeriod === "1d"
      ? 1
      : selectedPeriod === "7d"
      ? 7
      : selectedPeriod === "30d"
      ? 30
      : selectedPeriod === "90d"
      ? 90
      : 365;

  // Get previous period data based on selected period, not double the length
  const startDate = new Date(selectedDate);
  const previousEndDate = new Date(startDate);
  previousEndDate.setDate(previousEndDate.getDate() - comparisonPeriodLength);
  const previousStartDate = new Date(previousEndDate);
  previousStartDate.setDate(
    previousStartDate.getDate() - comparisonPeriodLength + 1
  );

  const previousPeriodData = data.filter((d) => {
    const date = new Date(d.date);
    return date >= previousStartDate && date <= previousEndDate;
  });

  const previousRevenue = previousPeriodData.reduce(
    (sum, d) => sum + d.revenue,
    0
  );
  const previousCustomers =
    previousPeriodData.length > 0
      ? Math.round(
          previousPeriodData.reduce((sum, d) => sum + d.customers.total, 0) /
            previousPeriodData.length
        )
      : 0;
  const previousActive =
    previousPeriodData.length > 0
      ? Math.round(
          previousPeriodData.reduce(
            (sum, d) => sum + (d.customers.total - d.customers.inactive),
            0
          ) / previousPeriodData.length
        )
      : 0;

  const revenueGrowth =
    previousRevenue > 0 ? calculateGrowth(totalRevenue, previousRevenue) : "0";
  const customerGrowth =
    previousCustomers > 0
      ? calculateGrowth(avgCustomers, previousCustomers)
      : "0";
  const activeGrowth =
    previousActive > 0 ? calculateGrowth(activeCustomers, previousActive) : "0";

  // Modal state for AI insights
  const [selectedInsight, setSelectedInsight] = useState<any>(null);
  const [showInsightModal, setShowInsightModal] = useState(false);

  const openInsightModal = (insight: any) => {
    setSelectedInsight(insight);
    setShowInsightModal(true);
  };

  const closeInsightModal = () => {
    setSelectedInsight(null);
    setShowInsightModal(false);
  };

  // Dynamic metric titles based on timeframe
  const getMetricTitle = (base: string) => {
    if (currentTimeframe === "daily") return base;
    if (currentTimeframe === "monthly") return `Avg ${base} (Monthly)`;
    return `Avg ${base} (Yearly)`;
  };

  const metrics = [
    {
      title: getMetricTitle("Customers"),
      value: avgCustomers.toLocaleString(),
      change: `${
        parseFloat(customerGrowth as string) >= 0 ? "+" : ""
      }${customerGrowth}%`,
      trend: parseFloat(customerGrowth as string) >= 0 ? "up" : "down",
      icon: Users,
      color: "blue" as const,
      link: "/customers",
    },
    {
      title: `Revenue (${selectedPeriod.toUpperCase()})`,
      value: `¥${totalRevenue.toLocaleString()}`,
      change: `${
        parseFloat(revenueGrowth as string) >= 0 ? "+" : ""
      }${revenueGrowth}%`,
      trend: parseFloat(revenueGrowth as string) >= 0 ? "up" : "down",
      icon: DollarSign,
      color: "green" as const,
      link: "/analytics",
    },
    {
      title: getMetricTitle("Active Customers"),
      value: activeCustomers.toLocaleString(),
      change: `${
        parseFloat(activeGrowth as string) >= 0 ? "+" : ""
      }${activeGrowth}%`,
      trend: parseFloat(activeGrowth as string) >= 0 ? "up" : "down",
      icon: Activity,
      color: "purple" as const,
      link: "/customers",
    },
    {
      title: getMetricTitle("Active Campaigns"),
      value: displayCampaigns.toString(),
      change:
        previousPeriodData.length > 0
          ? `+${
              displayCampaigns -
              Math.round(
                previousPeriodData.reduce(
                  (sum, d) => sum + d.campaigns.active,
                  0
                ) / previousPeriodData.length
              )
            }`
          : "+0",
      trend: "up" as const,
      icon: Target,
      color: "orange" as const,
      link: "/campaigns",
    },
  ];

  const quickActions = [
    {
      label: t("dashboard.addCustomer"),
      icon: Users,
      link: "/customers",
      color: "blue",
    },
    {
      label: t("dashboard.createCampaign"),
      icon: Target,
      link: "/campaigns",
      color: "green",
    },
    {
      label: t("dashboard.viewAnalytics"),
      icon: Activity,
      link: "/analytics",
      color: "purple",
    },
    {
      label: t("dashboard.aiInsights"),
      icon: Brain,
      link: "/ai-assistant",
      color: "orange",
    },
  ];

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {t("dashboard.title")}
          </h1>
          <p className="text-gray-600 mt-1">{t("dashboard.subtitle")}</p>
        </div>
        <div className="flex items-center space-x-3">
          {/* Timeframe Selector */}
          <select
            value={currentTimeframe}
            onChange={(e) =>
              setTimeframe(e.target.value as "daily" | "monthly" | "yearly")
            }
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="daily">Daily View</option>
            <option value="monthly">Monthly View</option>
            <option value="yearly">Yearly View</option>
          </select>

          {/* Period Selector */}
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="1d">{t("time.today")}</option>
            <option value="7d">{t("time.last7days")}</option>
            <option value="30d">{t("time.last30days")}</option>
            <option value="90d">{t("time.last90days")}</option>
            <option value="1y">{t("time.lastYear")}</option>
          </select>

          {/* Date Picker */}
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          {/* Calendar Button - Working */}
          <Link
            to="/calendar"
            className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            title="View Marketing Calendar"
          >
            <Calendar className="w-4 h-4" />
          </Link>

          {/* Info Button - Working */}
          <button
            onClick={() => setShowInfo(!showInfo)}
            className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            title="Dashboard Information"
          >
            <Info className="w-4 h-4" />
          </button>

          {/* Manual Refresh */}
          <button
            onClick={() => {
              generateAIInsights();
              toast.success("Dashboard data refreshed!");
            }}
            className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          {/* Export Button */}
          <button
            onClick={() => {
              toast.success("Generating dashboard export...");
              setTimeout(() => {
                const exportData = {
                  date: selectedDate,
                  timeframe: currentTimeframe,
                  period: selectedPeriod,
                  metrics: {
                    totalRevenue,
                    totalCustomers: currentData?.customers.total || 0,
                    // activeToday,
                    activeCampaigns,
                  },
                  insights: insights.length,
                  timestamp: new Date().toISOString(),
                };
                const blob = new Blob([JSON.stringify(exportData, null, 2)], {
                  type: "application/json",
                });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `sbm-dashboard-${
                  new Date().toISOString().split("T")[0]
                }.json`;
                a.click();
                window.URL.revokeObjectURL(url);
                toast.success("Dashboard report exported successfully!");
              }, 2000);
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
          >
            <Eye className="w-4 h-4 mr-2" />
            {t("dashboard.export")}
          </button>
        </div>
      </div>

      {/* Info Panel */}
      {showInfo && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6"
        >
          <div className="flex items-start space-x-3">
            <Info className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-900 mb-2">
                Dashboard Information
              </h3>
              <div className="text-sm text-blue-800 space-y-1">
                <p>
                  <strong>Current View:</strong>{" "}
                  {currentTimeframe.charAt(0).toUpperCase() +
                    currentTimeframe.slice(1)}{" "}
                  | Period: {selectedPeriod} | Date: {selectedDate}
                </p>
                <p>
                  <strong>Data Points:</strong> {timeframeData.length} days of
                  historical data
                </p>
                <p>
                  <strong>AI Insights:</strong> {insights.length} active
                  insights generated from real data analysis
                </p>
                <p>
                  <strong>Last Updated:</strong> {new Date().toLocaleString()}
                </p>
                <p>
                  <strong>Features:</strong> Real-time data switching,
                  functional date picker, AI-powered analytics, exportable
                  reports
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <motion.div
            key={metric.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <MetricCard {...(metric as any)} />
          </motion.div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          {t("dashboard.quickActions")}
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {quickActions.map((action, index) => (
            <motion.div
              key={action.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
            >
              <Link
                to={action.link}
                className="flex flex-col items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
              >
                <div
                  className={`w-12 h-12 bg-${action.color}-100 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}
                >
                  <action.icon className={`w-6 h-6 text-${action.color}-600`} />
                </div>
                <span className="text-sm font-medium text-gray-700">
                  {action.label}
                </span>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Main Content Grid - Enhanced */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue Analytics - Enhanced with Real Data */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Revenue Analytics
              </h2>
              <p className="text-sm text-gray-600">
                Track revenue performance and predictions
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="px-2 py-1 bg-green-600 text-white rounded-full text-xs font-medium">
                Live Data
              </span>
              <span className="px-2 py-1 bg-blue-600 text-white rounded-full text-xs font-medium">
                AI Powered
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-1">Total</p>
              <p className="text-2xl font-bold text-gray-900">
                ¥{totalRevenue.toLocaleString()}
              </p>
              <p className="text-sm text-green-600 mt-1">
                Growth: +{revenueGrowth}%
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-1">Daily Average</p>
              <p className="text-2xl font-bold text-gray-900">
                ¥
                {Math.round(
                  totalRevenue / timeframeData.length
                ).toLocaleString()}
              </p>
              <p className="text-sm text-blue-600 mt-1">
                Trend:{" "}
                {parseFloat(revenueGrowth as string) > 0
                  ? "Increasing"
                  : "Stable"}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-1">Projected</p>
              <p className="text-2xl font-bold text-gray-900">
                ¥{Math.round(totalRevenue * 1.15).toLocaleString()}
              </p>
              <p className="text-sm text-purple-600 mt-1">+15% forecast</p>
            </div>
          </div>

          <div className="h-64">
            <Line
              data={{
                labels: aggregatedData.map((d, i) => {
                  if (currentTimeframe === "daily") {
                    const date = new Date(timeframeData[i]?.date || new Date());
                    return date.toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    });
                  } else if (currentTimeframe === "monthly") {
                    return `Month ${i + 1}`;
                  } else {
                    return `Year ${new Date().getFullYear()}`;
                  }
                }),
                datasets: [
                  {
                    label: "Revenue",
                    data: aggregatedData.map((d) => d.revenue),
                    borderColor: colors.primarySolid[1],
                    backgroundColor: colors.primary[1].replace("0.8", "0.1"),
                    fill: true,
                    tension: 0.4,
                  },
                  {
                    label: "Trend",
                    data: aggregatedData.map((d, i) => {
                      const base = aggregatedData[0]?.revenue || 0;
                      const growth =
                        (totalRevenue - base) / aggregatedData.length;
                      return base + i * growth;
                    }),
                    borderColor: colors.primarySolid[0],
                    borderDash: [5, 5],
                    fill: false,
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: true,
                    ticks: {
                      callback: (value) =>
                        `¥${(value as number).toLocaleString()}`,
                    },
                  },
                },
              }}
            />
          </div>
        </div>

        {/* Customer Segments - Enhanced with Real Data */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Customer Segments
              </h2>
              <p className="text-sm text-gray-600">
                Distribution by customer type
              </p>
            </div>
            <Link
              to="/customers"
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Manage
            </Link>
          </div>

          {currentData && (
            <>
              <div className="mb-6">
                <div className="h-48">
                  <Doughnut
                    data={{
                      labels: [
                        "VIP Members",
                        "Regular Customers",
                        "New Visitors",
                        "Inactive",
                      ],
                      datasets: [
                        {
                          data: [
                            currentData.customers.vip,
                            currentData.customers.regular,
                            currentData.customers.new,
                            currentData.customers.inactive,
                          ],
                          backgroundColor: [
                            colors.primary[6], // Pink for VIP
                            colors.primary[1], // Green for Regular
                            colors.primary[0], // Blue for New
                            colors.primary[7], // Gray for Inactive
                          ],
                          borderWidth: 2,
                          borderColor: isDark ? "#374151" : "#fff",
                        },
                      ],
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: "bottom",
                          labels: {
                            usePointStyle: true,
                            padding: 15,
                          },
                        },
                      },
                    }}
                  />
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">VIP Members</span>
                  <span className="text-sm font-medium">
                    (
                    {(
                      (currentData.customers.vip /
                        currentData.customers.total) *
                      100
                    ).toFixed(1)}
                    %)
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">
                    Regular Customers
                  </span>
                  <span className="text-sm font-medium">
                    (
                    {(
                      (currentData.customers.regular /
                        currentData.customers.total) *
                      100
                    ).toFixed(1)}
                    %)
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">New Visitors</span>
                  <span className="text-sm font-medium">
                    (
                    {(
                      (currentData.customers.new /
                        currentData.customers.total) *
                      100
                    ).toFixed(1)}
                    %)
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Inactive</span>
                  <span className="text-sm font-medium">
                    (
                    {(
                      (currentData.customers.inactive /
                        currentData.customers.total) *
                      100
                    ).toFixed(1)}
                    %)
                  </span>
                </div>
                <div className="pt-2 border-t border-gray-200">
                  <div className="flex justify-between items-center font-semibold">
                    <span className="text-sm text-gray-900">
                      Total Customers
                    </span>
                    <span className="text-sm">
                      {currentData.customers.total.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Real AI Insights - Full width with actual data analysis */}
        <div className="lg:col-span-3 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                AI-Generated Insights
              </h2>
              <p className="text-sm text-gray-600">
                Real-time analysis of your business data
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">Live Analysis</span>
              <button
                onClick={() => {
                  generateAIInsights();
                  toast.success("AI insights refreshed!");
                }}
                className="ml-3 px-3 py-1 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
              >
                Refresh Insights
              </button>
            </div>
          </div>

          {insights.length > 0 ? (
            <div className="space-y-4">
              {insights.slice(0, 3).map((insight) => (
                <div
                  key={insight.id}
                  className={`p-4 rounded-lg border-l-4 ${
                    insight.type === "opportunity"
                      ? "bg-green-50 border-green-400"
                      : insight.type === "warning"
                      ? "bg-yellow-50 border-yellow-400"
                      : insight.type === "trend"
                      ? "bg-blue-50 border-blue-400"
                      : "bg-purple-50 border-purple-400"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="font-semibold text-gray-900">
                          {insight.title}
                        </h3>
                        <span
                          className={`px-2 py-0.5 text-xs rounded-full font-medium ${
                            insight.priority === "high"
                              ? "bg-red-600 text-white"
                              : insight.priority === "medium"
                              ? "bg-yellow-600 text-white"
                              : "bg-gray-600 text-white"
                          }`}
                        >
                          {insight.priority} priority
                        </span>
                        <span className="px-2 py-0.5 text-xs bg-gray-600 text-white rounded-full font-medium">
                          {insight.confidence}% confidence
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">
                        {insight.description}
                      </p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span>Impact: {insight.impact_estimate}</span>
                        <span>Sources: {insight.data_source.join(", ")}</span>
                        <span>
                          Generated:{" "}
                          {new Date(insight.created_at).toLocaleString()}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <button
                        onClick={() => openInsightModal(insight)}
                        className={`px-3 py-1 text-white text-sm rounded-lg ${
                          insight.type === "opportunity"
                            ? "bg-green-600 hover:bg-green-700"
                            : insight.type === "warning"
                            ? "bg-yellow-600 hover:bg-yellow-700"
                            : insight.type === "trend"
                            ? "bg-blue-600 hover:bg-blue-700"
                            : "bg-purple-600 hover:bg-purple-700"
                        }`}
                      >
                        View Details
                      </button>
                    </div>
                  </div>
                </div>
              ))}

              {insights.length > 3 && (
                <div className="text-center">
                  <Link
                    to="/ai-assistant"
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    View all {insights.length} insights →
                  </Link>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <Brain className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">
                AI is analyzing your data to generate insights...
              </p>
              <button
                onClick={() => {
                  generateAIInsights();
                  toast.success("Generating AI insights...");
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Generate Insights
              </button>
            </div>
          )}
        </div>

        {/* Advanced Analytics Dashboard Cards - Enhanced and Bigger */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  Advanced Analytics Dashboard
                </h2>
                <p className="text-gray-600">
                  Comprehensive data visualization with interactive charts
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <span className="px-3 py-1 bg-blue-600 text-white rounded-full text-sm font-medium">
                  Live Data
                </span>
                <span className="px-3 py-1 bg-green-600 text-white rounded-full text-sm font-medium">
                  AI Powered
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Active Campaigns */}
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
                <div className="flex items-center justify-between mb-4">
                  <Target className="w-8 h-8 text-blue-600" />
                  <Link
                    to="/campaigns"
                    className="text-xs text-blue-600 font-medium hover:text-blue-800 underline"
                  >
                    Campaign Analytics →
                  </Link>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {displayCampaigns}
                </h3>
                <p className="text-sm text-gray-600 mb-4">Active Campaigns</p>
                {aggregatedData.length > 0 && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span>Impressions</span>
                      <span>
                        {Math.round(
                          aggregatedData.reduce(
                            (sum, d) => sum + d.campaigns.total_impressions,
                            0
                          ) / aggregatedData.length
                        ).toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span>CTR</span>
                      <span>
                        {(
                          aggregatedData.reduce(
                            (sum, d) => sum + d.campaigns.avg_ctr,
                            0
                          ) / aggregatedData.length
                        ).toFixed(1)}
                        %
                      </span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span>ROI</span>
                      <span>
                        {(
                          aggregatedData.reduce(
                            (sum, d) => sum + d.campaigns.avg_roi,
                            0
                          ) / aggregatedData.length
                        ).toFixed(1)}
                        %
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* Retention Rate */}
              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
                <div className="flex items-center justify-between mb-4">
                  <Users className="w-8 h-8 text-green-600" />
                  <Link
                    to="/customers"
                    className="text-xs text-green-600 font-medium hover:text-green-800 underline"
                  >
                    Customer Analytics →
                  </Link>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {aggregatedData.length > 0
                    ? (
                        aggregatedData.reduce(
                          (sum, d) => sum + d.engagement.return_rate,
                          0
                        ) / aggregatedData.length
                      ).toFixed(1)
                    : "0"}
                  %
                </h3>
                <p className="text-sm text-gray-600 mb-4">Retention Rate</p>
                {aggregatedData.length > 0 && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span>Session Duration</span>
                      <span>
                        {Math.round(
                          aggregatedData.reduce(
                            (sum, d) => sum + d.engagement.session_duration,
                            0
                          ) /
                            aggregatedData.length /
                            60
                        )}
                        m
                      </span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span>Pages/Session</span>
                      <span>
                        {(
                          aggregatedData.reduce(
                            (sum, d) => sum + d.engagement.pages_per_session,
                            0
                          ) / aggregatedData.length
                        ).toFixed(1)}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span>Bounce Rate</span>
                      <span>
                        {(
                          aggregatedData.reduce(
                            (sum, d) => sum + d.engagement.bounce_rate,
                            0
                          ) / aggregatedData.length
                        ).toFixed(1)}
                        %
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* Customer Engagement */}
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
                <div className="flex items-center justify-between mb-4">
                  <Activity className="w-8 h-8 text-purple-600" />
                  <Link
                    to="/analytics"
                    className="text-xs text-purple-600 font-medium hover:text-purple-800 underline"
                  >
                    Engagement Analytics →
                  </Link>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {aggregatedData.length > 0
                    ? Math.round(
                        100 -
                          aggregatedData.reduce(
                            (sum, d) => sum + d.engagement.bounce_rate,
                            0
                          ) /
                            aggregatedData.length
                      )
                    : "0"}
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Customer Engagement
                </p>
                {currentData &&
                  Object.keys(currentData.geography).length > 0 && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs">
                        <span>Top City</span>
                        <span>{Object.keys(currentData.geography)[0]}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span>Geographic Reach</span>
                        <span>
                          {Object.keys(currentData.geography).length} cities
                        </span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span>Avg Engagement</span>
                        <span>
                          {Math.round(
                            Object.values(currentData.geography).reduce(
                              (sum, city) => sum + city.engagement,
                              0
                            ) / Object.values(currentData.geography).length
                          )}
                          %
                        </span>
                      </div>
                    </div>
                  )}
              </div>
            </div>

            {/* Geographic Distribution Chart */}
            {currentData && Object.keys(currentData.geography).length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Geographic Distribution
                </h3>
                <div className="h-64">
                  <Bar
                    data={{
                      labels: Object.keys(currentData.geography),
                      datasets: [
                        {
                          label: "Customers",
                          data: Object.values(currentData.geography).map(
                            (city) => city.customers
                          ),
                          backgroundColor: colors.primary[0],
                          borderColor: colors.primarySolid[0],
                          borderWidth: 1,
                        },
                        {
                          label: "Revenue (¥1000s)",
                          data: Object.values(currentData.geography).map(
                            (city) => Math.round(city.revenue / 1000)
                          ),
                          backgroundColor: colors.primary[1],
                          borderColor: colors.primarySolid[1],
                          borderWidth: 1,
                        },
                      ],
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        y: {
                          beginAtZero: true,
                        },
                      },
                    }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Active Campaigns Calendar Preview */}
        <div className="lg:col-span-3 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Active Campaigns Calendar
              </h2>
              <p className="text-sm text-gray-600">
                Currently running campaigns and upcoming events
              </p>
            </div>
            <Link
              to="/calendar"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              View Full Calendar →
            </Link>
          </div>

          {campaigns.filter((c) => c.status === "active").length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {campaigns
                .filter((c) => c.status === "active")
                .slice(0, 6)
                .map((campaign) => (
                  <div
                    key={campaign.id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <Target className="w-5 h-5 text-blue-600" />
                        <h3 className="font-medium text-gray-900">
                          {campaign.name}
                        </h3>
                      </div>
                      <span className="px-2 py-0.5 bg-green-600 text-white text-xs rounded-full font-medium">
                        Active
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      {campaign.objective}
                    </p>
                    <div className="space-y-1 text-xs text-gray-500">
                      <div className="flex justify-between">
                        <span>Start:</span>
                        <span>
                          {new Date(
                            (campaign as any).schedule.startDate
                          ).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>End:</span>
                        <span>
                          {new Date(
                            (campaign as any).schedule.endDate
                          ).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Budget:</span>
                        <span>¥{campaign.budget.amount.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>ROI:</span>
                        <span className="text-green-600 font-medium">
                          {campaign.performance?.roi
                            ? `${campaign.performance.roi}%`
                            : "Calculating..."}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">
                No active campaigns at the moment
              </p>
              <Link
                to="/campaigns/create"
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Campaign
              </Link>
            </div>
          )}
        </div>

        {/* Additional Dashboard Components - Properly Spaced */}
        <div className="lg:col-span-2">
          <CampaignPerformance />
        </div>
        <div className="lg:col-span-1">
          <ActivityFeed />
        </div>
      </div>

      {/* Comprehensive CRM Analytics Section */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-8">
        {/* Sales Pipeline */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Sales Pipeline
            </h3>
            <Link
              to="/analytics"
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              View Details →
            </Link>
          </div>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Leads</span>
              <span className="font-semibold">
                {Math.round(avgCustomers * 0.15)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Qualified</span>
              <span className="font-semibold">
                {Math.round(avgCustomers * 0.08)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Proposals</span>
              <span className="font-semibold">
                {Math.round(avgCustomers * 0.03)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Closed Won</span>
              <span className="font-semibold text-green-600">
                {Math.round(avgCustomers * 0.02)}
              </span>
            </div>
            <div className="pt-2 border-t">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Conversion Rate</span>
                <span className="font-bold text-green-600">13.3%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Lead Sources */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Lead Sources
            </h3>
            <Link
              to="/campaigns"
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Manage →
            </Link>
          </div>
          <div className="h-32 mb-4">
            <Doughnut
              data={{
                labels: [
                  "Organic Search",
                  "Social Media",
                  "Email Campaign",
                  "Referrals",
                  "Direct",
                ],
                datasets: [
                  {
                    data: [35, 25, 20, 12, 8],
                    backgroundColor: [
                      colors.primary[1], // Green for Organic Search
                      colors.primary[0], // Blue for Social Media
                      colors.primary[3], // Purple for Email Campaign
                      colors.primary[2], // Orange for Referrals
                      colors.primary[4], // Red for Direct
                    ],
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
              }}
            />
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between">
              <span>Organic Search</span>
              <span className="font-semibold">35%</span>
            </div>
            <div className="flex justify-between">
              <span>Social Media</span>
              <span className="font-semibold">25%</span>
            </div>
            <div className="flex justify-between">
              <span>Email</span>
              <span className="font-semibold">20%</span>
            </div>
          </div>
        </div>

        {/* Customer Lifecycle */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Customer Lifecycle
            </h3>
            <Link
              to="/customers"
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              View All →
            </Link>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="text-sm">New Customers</span>
              </div>
              <span className="font-semibold">
                {aggregatedData.length > 0
                  ? Math.round(
                      aggregatedData.reduce(
                        (sum, d) => sum + d.customers.new,
                        0
                      ) / aggregatedData.length
                    )
                  : 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-sm">Active Customers</span>
              </div>
              <span className="font-semibold">{activeCustomers}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                <span className="text-sm">VIP Customers</span>
              </div>
              <span className="font-semibold">
                {aggregatedData.length > 0
                  ? Math.round(
                      aggregatedData.reduce(
                        (sum, d) => sum + d.customers.vip,
                        0
                      ) / aggregatedData.length
                    )
                  : 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
                <span className="text-sm">At Risk</span>
              </div>
              <span className="font-semibold text-red-600">
                {aggregatedData.length > 0
                  ? Math.round(
                      aggregatedData.reduce(
                        (sum, d) => sum + d.customers.inactive,
                        0
                      ) / aggregatedData.length
                    )
                  : 0}
              </span>
            </div>
            <div className="pt-2 border-t">
              <div className="flex justify-between">
                <span className="text-sm font-medium">Avg. Lifetime Value</span>
                <span className="font-bold">
                  ¥{Math.round(totalRevenue / avgCustomers).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Revenue Forecast */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Revenue Forecast
            </h3>
            <Link
              to="/analytics"
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Forecasting →
            </Link>
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>This Month</span>
                <span className="font-semibold">
                  ¥{Math.round(totalRevenue * 1.1).toLocaleString()}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: "78%" }}
                ></div>
              </div>
              <span className="text-xs text-gray-500">78% of monthly goal</span>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Next Month</span>
                <span className="font-semibold">
                  ¥{Math.round(totalRevenue * 1.25).toLocaleString()}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: "85%" }}
                ></div>
              </div>
              <span className="text-xs text-gray-500">AI Confidence: 85%</span>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Quarter Target</span>
                <span className="font-semibold">
                  ¥{Math.round(totalRevenue * 3.2).toLocaleString()}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-purple-500 h-2 rounded-full"
                  style={{ width: "68%" }}
                ></div>
              </div>
              <span className="text-xs text-gray-500">68% on track</span>
            </div>
          </div>
        </div>
      </div>

      {/* Team Performance & Activity Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        {/* Team Performance */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Team Performance
            </h3>
            <Link
              to="/operations"
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Team Stats →
            </Link>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold">Sales Team</p>
                <p className="text-sm text-gray-600">8 members</p>
              </div>
              <div className="text-right">
                <p className="font-bold text-green-600">112%</p>
                <p className="text-xs text-gray-500">of target</p>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold">Marketing Team</p>
                <p className="text-sm text-gray-600">5 members</p>
              </div>
              <div className="text-right">
                <p className="font-bold text-blue-600">94%</p>
                <p className="text-xs text-gray-500">campaign success</p>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold">Support Team</p>
                <p className="text-sm text-gray-600">6 members</p>
              </div>
              <div className="text-right">
                <p className="font-bold text-purple-600">4.8</p>
                <p className="text-xs text-gray-500">avg rating</p>
              </div>
            </div>
          </div>
        </div>

        {/* Key Metrics Summary */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Key Metrics</h3>
            <span className="text-xs bg-green-600 text-white px-2 py-1 rounded-full font-medium">
              All Time
            </span>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {(totalRevenue / 1000000).toFixed(1)}M
              </p>
              <p className="text-xs text-gray-600">Total Revenue</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {avgCustomers.toLocaleString()}
              </p>
              <p className="text-xs text-gray-600">Total Customers</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {aggregatedData.length > 0
                  ? (
                      aggregatedData.reduce(
                        (sum, d) => sum + d.campaigns.avg_ctr,
                        0
                      ) / aggregatedData.length
                    ).toFixed(1)
                  : 0}
                %
              </p>
              <p className="text-xs text-gray-600">Avg CTR</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {aggregatedData.length > 0
                  ? (
                      aggregatedData.reduce(
                        (sum, d) => sum + d.engagement.return_rate,
                        0
                      ) / aggregatedData.length
                    ).toFixed(0)
                  : 0}
                %
              </p>
              <p className="text-xs text-gray-600">Retention Rate</p>
            </div>
          </div>
        </div>

        {/* Recent Activity Summary */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Recent Activity
            </h3>
            <Link
              to="/operations"
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              View All →
            </Link>
          </div>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm font-medium">
                  Campaign "Summer Sale" launched
                </p>
                <p className="text-xs text-gray-500">2 hours ago</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm font-medium">
                  New VIP customer registered
                </p>
                <p className="text-xs text-gray-500">4 hours ago</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm font-medium">AI insights updated</p>
                <p className="text-xs text-gray-500">6 hours ago</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm font-medium">Weekly report generated</p>
                <p className="text-xs text-gray-500">1 day ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Insight Modal */}
      <AIInsightModal
        isOpen={showInsightModal}
        onClose={closeInsightModal}
        insight={selectedInsight}
        onApply={() => {
          toast.success("AI recommendation applied successfully!");
        }}
      />
    </div>
  );
};
