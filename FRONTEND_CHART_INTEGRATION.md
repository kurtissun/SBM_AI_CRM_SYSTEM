# Frontend Chart Integration Guide
## SBM AI CRM System - Custom Reporting & Visualization Engine

This guide provides comprehensive information for integrating the backend chart engine with frontend applications for data visualization in CRM dashboards.

## 🚀 Overview

The SBM CRM system now includes a powerful **Custom Reporting & Chart Engine** that generates frontend-ready chart data for dashboards, reports, and analytics sections. The engine supports multiple chart types, real-time data, and export capabilities.

## 📊 Available Chart Types

### Standard Charts
- **Line Charts** - Time series, trends, continuous data
- **Bar/Column Charts** - Categorical comparisons, rankings
- **Pie/Doughnut Charts** - Percentages, composition analysis
- **Area Charts** - Volume trends, cumulative data
- **Scatter Plots** - Correlations, distributions, outliers

### Advanced Charts
- **Funnel Charts** - Conversion analysis, sales pipeline
- **Geographic Maps** - Location-based data, regional analysis
- **Heatmaps** - Data density, correlation matrices
- **Gauge Charts** - KPIs, performance targets
- **KPI Cards** - Dashboard metrics, key indicators

## 🔗 API Endpoints

### Base URL
```
https://your-crm-domain.com/api/charts
```

### Authentication
All endpoints require JWT authentication:
```javascript
headers: {
  'Authorization': 'Bearer YOUR_JWT_TOKEN',
  'Content-Type': 'application/json'
}
```

### Core Endpoints

#### 1. KPI Dashboard
```javascript
GET /api/charts/dashboard/kpi

// Response
{
  "chart_id": "uuid",
  "config": {
    "chart_type": "kpi",
    "title": "CRM Dashboard - Key Metrics",
    "custom_options": {
      "layout": "grid",
      "columns": 3,
      "show_trends": true
    }
  },
  "series": [{
    "name": "Key Performance Indicators",
    "data": [
      {
        "x": "Total Customers",
        "y": 15420,
        "metadata": {
          "format": "number",
          "trend": "+342 this month",
          "trend_direction": "up"
        }
      },
      {
        "x": "Total Revenue", 
        "y": 1250000,
        "metadata": {
          "format": "currency",
          "trend": "$81.12 per customer",
          "trend_direction": "up"
        }
      }
      // ... more KPIs
    ]
  }],
  "metadata": {
    "chart_category": "kpi_dashboard",
    "metrics": {
      "total_customers": 15420,
      "total_revenue": 1250000,
      "conversion_rate": 12.5
    }
  },
  "export_formats": ["png", "pdf", "json"]
}
```

#### 2. Customer Demographics
```javascript
GET /api/charts/customer/demographics?chart_type=pie

// Response - Pie Chart
{
  "chart_id": "uuid",
  "config": {
    "chart_type": "pie", 
    "title": "Customer Demographics",
    "subtitle": "Total customers analyzed: 15420"
  },
  "series": [{
    "name": "Age Groups",
    "data": [
      {
        "x": "25-34",
        "y": 4200,
        "label": "25-34: 4200",
        "color": "#3366CC"
      },
      {
        "x": "35-44", 
        "y": 3800,
        "label": "35-44: 3800",
        "color": "#DC3912"
      }
      // ... more age groups
    ]
  }]
}
```

#### 3. Revenue Trends
```javascript
GET /api/charts/revenue/trend?days=30&granularity=day

// Response - Multi-series Line Chart
{
  "chart_id": "uuid",
  "config": {
    "chart_type": "column",
    "title": "Revenue Trend Analysis",
    "x_axis_label": "Time Period",
    "y_axis_label": "Revenue ($)",
    "x_axis_type": "datetime"
  },
  "series": [
    {
      "name": "Daily Revenue",
      "data": [
        {
          "x": "2024-01-01",
          "y": 25420.50,
          "metadata": {"transactions": 45}
        },
        {
          "x": "2024-01-02", 
          "y": 31200.75,
          "metadata": {"transactions": 52}
        }
        // ... 30 days of data
      ],
      "color": "#3366CC"
    },
    {
      "name": "Cumulative Revenue",
      "data": [
        {"x": "2024-01-01", "y": 25420.50},
        {"x": "2024-01-02", "y": 56621.25}
        // ... cumulative data
      ],
      "color": "#DC3912",
      "type": "line"
    }
  ]
}
```

#### 4. Campaign Performance
```javascript
GET /api/charts/campaign/performance

// Response - Multi-metric Bar Chart
{
  "config": {
    "chart_type": "bar",
    "title": "Campaign Performance Comparison",
    "x_axis_label": "Campaign",
    "y_axis_label": "Performance Metrics (%)"
  },
  "series": [
    {
      "name": "CTR (%)",
      "data": [
        {"x": "Summer Sale 2024", "y": 3.2},
        {"x": "Holiday Campaign", "y": 4.1}
      ],
      "color": "#3366CC"
    },
    {
      "name": "Conversion Rate (%)", 
      "data": [
        {"x": "Summer Sale 2024", "y": 12.5},
        {"x": "Holiday Campaign", "y": 15.8}
      ],
      "color": "#DC3912"
    }
  ]
}
```

#### 5. Customer Segmentation
```javascript
GET /api/charts/customer/segmentation

// Response - Bubble Chart
{
  "config": {
    "chart_type": "scatter",
    "title": "Customer Segmentation Analysis",
    "subtitle": "Bubble size represents customer count",
    "x_axis_label": "Average Spending ($)",
    "y_axis_label": "Average Age",
    "x_axis_type": "numeric",
    "y_axis_type": "numeric"
  },
  "series": [{
    "name": "Customer Segments",
    "data": [
      {
        "x": 850.50,    // avg spending
        "y": 34.2,     // avg age
        "label": "Segment 1",
        "metadata": {
          "segment_id": 1,
          "customer_count": 2400,
          "bubble_size": 2400,
          "percentage": 15.6
        }
      }
      // ... more segments
    ]
  }],
  "metadata": {
    "alternative_charts": {
      "pie_chart": {
        "config": {...},
        "series": [...]
      }
    }
  }
}
```

#### 6. Conversion Funnel
```javascript
GET /api/charts/conversion/funnel

// Response - Funnel Chart
{
  "config": {
    "chart_type": "funnel",
    "title": "Customer Conversion Funnel",
    "custom_options": {
      "funnel_neck_width": 0.3,
      "show_percentages": true
    }
  },
  "series": [{
    "name": "Conversion Funnel",
    "data": [
      {
        "x": "Website Visitors",
        "y": 10000,
        "label": "Website Visitors: 10,000 (100.0%)",
        "metadata": {
          "stage_index": 0,
          "percentage": 100.0
        }
      },
      {
        "x": "Purchase Completed",
        "y": 900,
        "label": "Purchase Completed: 900 (9.0%)", 
        "metadata": {
          "stage_index": 4,
          "percentage": 9.0,
          "conversion_from_previous": 60.0
        }
      }
      // ... funnel stages
    ]
  }]
}
```

#### 7. Custom Charts
```javascript
POST /api/charts/custom

// Request Body
{
  "chart_type": "bar",
  "title": "Custom Revenue Analysis",
  "data_source": "customers",
  "x_field": "segment_id", 
  "y_field": "total_spent",
  "aggregation": "sum",
  "filters": {
    "created_at": {
      "min": "2024-01-01",
      "max": "2024-12-31"
    },
    "total_spent": {
      "min": 100
    }
  },
  "group_by": "segment_id",
  "x_axis_label": "Customer Segment",
  "y_axis_label": "Total Revenue ($)"
}

// Response
{
  "success": true,
  "data": {
    "chart_id": "uuid",
    "config": {...},
    "series": [...],
    "export_formats": ["png", "pdf", "csv", "json"]
  }
}
```

## 🎨 Frontend Integration Examples

### React with Chart.js
```jsx
import React, { useState, useEffect } from 'react';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';

const CRMChart = ({ endpoint, chartType, ...props }) => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchChartData();
  }, [endpoint]);

  const fetchChartData = async () => {
    try {
      const response = await fetch(`/api/charts/${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      setChartData(transformDataForChartJS(data));
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch chart data:', error);
      setLoading(false);
    }
  };

  const transformDataForChartJS = (apiData) => {
    const { series, config } = apiData;
    
    return {
      labels: series[0].data.map(point => point.x),
      datasets: series.map((serie, index) => ({
        label: serie.name,
        data: serie.data.map(point => point.y),
        backgroundColor: serie.color || `hsl(${index * 60}, 70%, 50%)`,
        borderColor: serie.color || `hsl(${index * 60}, 70%, 40%)`,
        borderWidth: 2,
        fill: config.chart_type === 'area'
      }))
    };
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: chartData?.config?.title
      },
      legend: {
        display: chartData?.config?.show_legend !== false
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: chartData?.config?.y_axis_label
        }
      },
      x: {
        title: {
          display: true,
          text: chartData?.config?.x_axis_label
        }
      }
    }
  };

  if (loading) return <div>Loading chart...</div>;
  if (!chartData) return <div>No data available</div>;

  const ChartComponent = {
    line: Line,
    bar: Bar,
    pie: Pie,
    doughnut: Doughnut
  }[chartType] || Bar;

  return (
    <div className="chart-container">
      <ChartComponent data={chartData} options={chartOptions} {...props} />
    </div>
  );
};

// Usage Examples
const DashboardCharts = () => {
  return (
    <div className="dashboard-grid">
      {/* KPI Cards */}
      <div className="kpi-section">
        <CRMChart 
          endpoint="dashboard/kpi" 
          chartType="kpi"
          className="kpi-cards" 
        />
      </div>

      {/* Revenue Trend */}
      <div className="revenue-chart">
        <CRMChart 
          endpoint="revenue/trend?days=30&granularity=day" 
          chartType="line"
          height={300}
        />
      </div>

      {/* Customer Demographics */}
      <div className="demographics-chart">
        <CRMChart 
          endpoint="customer/demographics?chart_type=pie" 
          chartType="pie"
          height={300}
        />
      </div>

      {/* Campaign Performance */}
      <div className="campaign-chart">
        <CRMChart 
          endpoint="campaign/performance" 
          chartType="bar"
          height={400}
        />
      </div>
    </div>
  );
};
```

### Vue.js with ApexCharts
```vue
<template>
  <div class="chart-wrapper">
    <apexchart
      v-if="chartOptions && chartSeries"
      :type="chartType"
      :options="chartOptions"
      :series="chartSeries"
      :height="height"
    />
    <div v-else-if="loading" class="loading">
      Loading chart...
    </div>
  </div>
</template>

<script>
import VueApexCharts from 'vue3-apexcharts';

export default {
  name: 'CRMChart',
  components: {
    apexchart: VueApexCharts
  },
  props: {
    endpoint: String,
    chartType: String,
    height: {
      type: Number,
      default: 350
    }
  },
  data() {
    return {
      chartOptions: null,
      chartSeries: null,
      loading: true
    };
  },
  async mounted() {
    await this.fetchChartData();
  },
  methods: {
    async fetchChartData() {
      try {
        const response = await this.$http.get(`/api/charts/${this.endpoint}`);
        const data = response.data;
        
        this.transformDataForApexCharts(data);
        this.loading = false;
      } catch (error) {
        console.error('Chart data fetch failed:', error);
        this.loading = false;
      }
    },
    
    transformDataForApexCharts(apiData) {
      const { series, config } = apiData;
      
      this.chartSeries = series.map(serie => ({
        name: serie.name,
        data: serie.data.map(point => ({
          x: point.x,
          y: point.y,
          ...point.metadata
        }))
      }));
      
      this.chartOptions = {
        chart: {
          type: this.chartType,
          toolbar: {
            show: true,
            tools: {
              download: true,
              selection: true,
              zoom: true,
              zoomin: true,
              zoomout: true,
              pan: true,
              reset: true
            }
          }
        },
        title: {
          text: config.title,
          align: 'left'
        },
        subtitle: {
          text: config.subtitle,
          align: 'left'
        },
        xaxis: {
          title: {
            text: config.x_axis_label
          },
          type: config.x_axis_type || 'category'
        },
        yaxis: {
          title: {
            text: config.y_axis_label
          }
        },
        legend: {
          show: config.show_legend !== false
        },
        dataLabels: {
          enabled: config.show_data_labels === true
        },
        colors: series.map(s => s.color).filter(Boolean),
        responsive: [{
          breakpoint: 768,
          options: {
            chart: {
              height: 300
            },
            legend: {
              position: 'bottom'
            }
          }
        }]
      };
    }
  }
};
</script>
```

### Angular with ng2-charts
```typescript
// chart.component.ts
import { Component, Input, OnInit } from '@angular/core';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';
import { ChartService } from './chart.service';

@Component({
  selector: 'app-crm-chart',
  template: `
    <div class="chart-container">
      <canvas 
        baseChart
        [data]="chartData"
        [options]="chartOptions"
        [type]="chartType"
        *ngIf="chartData">
      </canvas>
      <div *ngIf="loading" class="loading-spinner">
        Loading chart data...
      </div>
    </div>
  `
})
export class CRMChartComponent implements OnInit {
  @Input() endpoint!: string;
  @Input() chartType: ChartType = 'bar';
  @Input() height: number = 400;

  chartData: ChartData | null = null;
  chartOptions: ChartConfiguration['options'] = {};
  loading = true;

  constructor(private chartService: ChartService) {}

  async ngOnInit() {
    await this.loadChartData();
  }

  async loadChartData() {
    try {
      const response = await this.chartService.getChartData(this.endpoint);
      this.transformData(response);
      this.loading = false;
    } catch (error) {
      console.error('Failed to load chart data:', error);
      this.loading = false;
    }
  }

  private transformData(apiData: any) {
    const { series, config } = apiData;

    this.chartData = {
      labels: series[0].data.map((point: any) => point.x),
      datasets: series.map((serie: any, index: number) => ({
        label: serie.name,
        data: serie.data.map((point: any) => point.y),
        backgroundColor: serie.color || this.getDefaultColor(index),
        borderColor: serie.color || this.getDefaultColor(index),
        borderWidth: 2
      }))
    };

    this.chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: config.title
        },
        legend: {
          display: config.show_legend !== false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: config.y_axis_label
          }
        },
        x: {
          title: {
            display: true,
            text: config.x_axis_label
          }
        }
      }
    };
  }

  private getDefaultColor(index: number): string {
    const colors = ['#3366CC', '#DC3912', '#FF9900', '#109618', '#990099'];
    return colors[index % colors.length];
  }
}

// chart.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ChartService {
  private baseUrl = '/api/charts';

  constructor(private http: HttpClient) {}

  async getChartData(endpoint: string): Promise<any> {
    return firstValueFrom(
      this.http.get(`${this.baseUrl}/${endpoint}`)
    );
  }

  async createCustomChart(config: any): Promise<any> {
    return firstValueFrom(
      this.http.post(`${this.baseUrl}/custom`, config)
    );
  }

  async exportChart(chartId: string, format: string): Promise<any> {
    return firstValueFrom(
      this.http.get(`${this.baseUrl}/export/${chartId}?format=${format}`)
    );
  }
}
```

## 📊 Chart Templates

The system provides pre-built chart templates for quick implementation:

```javascript
// Get available templates
GET /api/charts/templates

// Response
{
  "categories": [
    "customer_analytics",
    "revenue_analytics", 
    "campaign_analytics",
    "conversion_analytics",
    "geographic_analytics",
    "kpi_dashboards"
  ],
  "templates": {
    "customer_analytics": [
      {
        "id": "customer_demographics",
        "name": "Customer Demographics",
        "description": "Age and gender distribution of customers",
        "chart_type": "pie",
        "preview_url": "/api/charts/customer/demographics"
      }
    ]
    // ... more templates
  }
}
```

## 🎯 Real-time Updates

For real-time dashboard updates, implement WebSocket connections or polling:

```javascript
// WebSocket approach
const ws = new WebSocket('ws://your-domain.com/ws/charts');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  if (update.type === 'chart_update') {
    refreshChart(update.chart_id);
  }
};

// Polling approach
setInterval(async () => {
  const latestData = await fetchChartData('dashboard/kpi');
  updateChartDisplay(latestData);
}, 30000); // Update every 30 seconds
```

## 📤 Export Capabilities

Charts can be exported in multiple formats:

```javascript
// Export chart data
const exportChart = async (chartId, format) => {
  const response = await fetch(`/api/charts/export/${chartId}?format=${format}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (format === 'csv' || format === 'json') {
    return await response.text();
  } else {
    // For PNG/PDF, handle as blob
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chart_${chartId}.${format}`;
    a.click();
  }
};
```

## 🎨 Styling and Themes

The chart engine supports theming and custom styling:

```javascript
// Custom color palettes
const customChart = {
  chart_type: "bar",
  title: "Custom Styled Chart",
  color_palette: [
    "#FF6B6B", "#4ECDC4", "#45B7D1", 
    "#96CEB4", "#FFEAA7", "#DDA0DD"
  ],
  // ... other config
};

// Dark theme support
const darkThemeOptions = {
  theme: "dark",
  background_color: "#1a1a1a",
  text_color: "#ffffff",
  grid_color: "#333333"
};
```

## 🔧 Error Handling

Implement proper error handling for chart loading:

```javascript
const ChartWithErrorBoundary = ({ endpoint, fallback }) => {
  const [error, setError] = useState(null);
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    fetchChartData(endpoint)
      .catch(err => {
        setError(err);
        console.error('Chart loading failed:', err);
      });
  }, [endpoint]);

  if (error) {
    return fallback || (
      <div className="chart-error">
        <p>Unable to load chart data</p>
        <button onClick={() => window.location.reload()}>
          Retry
        </button>
      </div>
    );
  }

  return <Chart data={chartData} />;
};
```

## 📱 Responsive Design

Ensure charts work well on all devices:

```css
.chart-container {
  width: 100%;
  height: 400px;
  position: relative;
}

@media (max-width: 768px) {
  .chart-container {
    height: 300px;
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .chart-container {
    height: 250px;
  }
}
```

## 🚀 Performance Tips

1. **Lazy Loading**: Load charts only when visible
2. **Data Pagination**: Use limit parameters for large datasets
3. **Caching**: Implement client-side caching for chart data
4. **Debouncing**: Debounce filter changes to avoid excessive API calls
5. **Progressive Loading**: Show skeleton loaders while data loads

This comprehensive system provides everything needed for a modern CRM dashboard with rich data visualizations! 📊✨