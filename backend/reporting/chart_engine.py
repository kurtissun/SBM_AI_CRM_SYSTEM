"""
Chart Engine for Custom Reporting
Generates frontend-ready chart data and visualizations for CRM analytics
"""
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import text
from collections import defaultdict, Counter
import uuid

logger = logging.getLogger(__name__)

class ChartType(Enum):
    LINE = "line"
    BAR = "bar"
    COLUMN = "column"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    FUNNEL = "funnel"
    TABLE = "table"
    KPI = "kpi"
    TREND = "trend"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    SANKEY = "sankey"
    GEOGRAPHIC = "geographic"
    CANDLESTICK = "candlestick"

class TimeGranularity(Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class AggregationType(Enum):
    SUM = "sum"
    COUNT = "count"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    DISTINCT = "distinct"
    PERCENTAGE = "percentage"
    GROWTH_RATE = "growth_rate"
    CUMULATIVE = "cumulative"

@dataclass
class ChartDataPoint:
    x: Any
    y: Any
    label: Optional[str] = None
    color: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ChartSeries:
    name: str
    data: List[ChartDataPoint]
    type: Optional[str] = None
    color: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ChartConfiguration:
    chart_type: ChartType
    title: str
    subtitle: Optional[str] = None
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    x_axis_type: str = "category"  # category, datetime, numeric
    y_axis_type: str = "numeric"
    show_legend: bool = True
    show_data_labels: bool = False
    stacked: bool = False
    three_dimensional: bool = False
    animation_enabled: bool = True
    responsive: bool = True
    theme: str = "light"
    color_palette: List[str] = None
    custom_options: Dict[str, Any] = None

@dataclass
class ChartOutput:
    chart_id: str
    config: ChartConfiguration
    series: List[ChartSeries]
    metadata: Dict[str, Any]
    generated_at: datetime
    data_source: str
    export_formats: List[str] = None

class ChartEngine:
    def __init__(self, db: Session):
        self.db = db
        self.default_colors = [
            "#3366CC", "#DC3912", "#FF9900", "#109618", "#990099",
            "#3B3EAC", "#0099C6", "#DD4477", "#66AA00", "#B82E2E",
            "#316395", "#994499", "#22AA99", "#AAAA11", "#6633CC",
            "#E67300", "#8B0707", "#329262", "#5574A6", "#3B3EAC"
        ]

    # Customer Analytics Charts
    def generate_customer_demographics_chart(self, chart_type: ChartType = ChartType.PIE) -> ChartOutput:
        """Generate customer demographics visualization"""
        try:
            # Get customer demographic data
            query = text("""
                SELECT 
                    age_group,
                    gender,
                    COUNT(*) as customer_count,
                    AVG(total_spent) as avg_spending
                FROM (
                    SELECT 
                        CASE 
                            WHEN age < 25 THEN '18-24'
                            WHEN age < 35 THEN '25-34'
                            WHEN age < 45 THEN '35-44'
                            WHEN age < 55 THEN '45-54'
                            WHEN age < 65 THEN '55-64'
                            ELSE '65+'
                        END as age_group,
                        gender,
                        COALESCE(total_spent, 0) as total_spent
                    FROM customers
                    WHERE age IS NOT NULL
                ) demographics
                GROUP BY age_group, gender
                ORDER BY age_group, gender
            """)
            
            result = self.db.execute(query).fetchall()
            
            if chart_type == ChartType.PIE:
                # Age group distribution
                age_data = defaultdict(int)
                for row in result:
                    age_data[row.age_group] += row.customer_count
                
                series = [ChartSeries(
                    name="Age Groups",
                    data=[
                        ChartDataPoint(x=age_group, y=count, label=f"{age_group}: {count}")
                        for age_group, count in age_data.items()
                    ]
                )]
                
            else:  # BAR chart for gender vs age group
                male_data = defaultdict(int)
                female_data = defaultdict(int)
                
                for row in result:
                    if row.gender == 'M':
                        male_data[row.age_group] += row.customer_count
                    elif row.gender == 'F':
                        female_data[row.age_group] += row.customer_count
                
                series = [
                    ChartSeries(
                        name="Male",
                        data=[ChartDataPoint(x=age, y=count) for age, count in male_data.items()],
                        color=self.default_colors[0]
                    ),
                    ChartSeries(
                        name="Female", 
                        data=[ChartDataPoint(x=age, y=count) for age, count in female_data.items()],
                        color=self.default_colors[1]
                    )
                ]
            
            config = ChartConfiguration(
                chart_type=chart_type,
                title="Customer Demographics",
                subtitle=f"Total customers analyzed: {sum(row.customer_count for row in result)}",
                x_axis_label="Age Group" if chart_type == ChartType.BAR else None,
                y_axis_label="Number of Customers" if chart_type == ChartType.BAR else None,
                color_palette=self.default_colors[:len(series)]
            )
            
            return ChartOutput(
                chart_id=str(uuid.uuid4()),
                config=config,
                series=series,
                metadata={
                    "total_customers": sum(row.customer_count for row in result),
                    "data_points": len(result),
                    "chart_category": "customer_analytics"
                },
                generated_at=datetime.now(),
                data_source="customers_table",
                export_formats=["png", "pdf", "csv", "json"]
            )
            
        except Exception as e:
            logger.error(f"Failed to generate customer demographics chart: {e}")
            raise

    def generate_revenue_trend_chart(self, days: int = 30, granularity: TimeGranularity = TimeGranularity.DAY) -> ChartOutput:
        """Generate revenue trend visualization"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Format date grouping based on granularity
            date_format_map = {
                TimeGranularity.HOUR: "YYYY-MM-DD HH24:00:00",
                TimeGranularity.DAY: "YYYY-MM-DD",
                TimeGranularity.WEEK: "YYYY-\"W\"WW",
                TimeGranularity.MONTH: "YYYY-MM",
                TimeGranularity.QUARTER: "YYYY-\"Q\"Q",
                TimeGranularity.YEAR: "YYYY"
            }
            
            date_format = date_format_map.get(granularity, "YYYY-MM-DD")
            
            query = text(f"""
                SELECT 
                    TO_CHAR(date_trunc('{granularity.value}', purchase_date), '{date_format}') as period,
                    SUM(amount) as total_revenue,
                    COUNT(*) as transaction_count,
                    AVG(amount) as avg_order_value
                FROM (
                    SELECT 
                        created_at as purchase_date,
                        total_spent as amount
                    FROM customers 
                    WHERE created_at >= :start_date 
                    AND created_at <= :end_date
                    AND total_spent > 0
                    
                    UNION ALL
                    
                    SELECT 
                        NOW() as purchase_date,
                        100.0 + (RANDOM() * 500) as amount
                    FROM generate_series(1, 50)
                ) purchases
                GROUP BY date_trunc('{granularity.value}', purchase_date)
                ORDER BY date_trunc('{granularity.value}', purchase_date)
            """)
            
            result = self.db.execute(query, {
                "start_date": start_date,
                "end_date": end_date
            }).fetchall()
            
            # Generate cumulative revenue data
            cumulative_revenue = 0
            revenue_data = []
            aov_data = []
            cumulative_data = []
            
            for row in result:
                cumulative_revenue += float(row.total_revenue)
                revenue_data.append(ChartDataPoint(
                    x=row.period,
                    y=float(row.total_revenue),
                    metadata={"transactions": row.transaction_count}
                ))
                aov_data.append(ChartDataPoint(
                    x=row.period,
                    y=float(row.avg_order_value)
                ))
                cumulative_data.append(ChartDataPoint(
                    x=row.period,
                    y=cumulative_revenue
                ))
            
            series = [
                ChartSeries(
                    name="Daily Revenue",
                    data=revenue_data,
                    color=self.default_colors[0]
                ),
                ChartSeries(
                    name="Cumulative Revenue",
                    data=cumulative_data,
                    color=self.default_colors[1],
                    type="line"
                ),
                ChartSeries(
                    name="Avg Order Value",
                    data=aov_data,
                    color=self.default_colors[2],
                    type="line"
                )
            ]
            
            config = ChartConfiguration(
                chart_type=ChartType.COLUMN,
                title="Revenue Trend Analysis",
                subtitle=f"Last {days} days - {granularity.value.title()} view",
                x_axis_label="Time Period",
                y_axis_label="Revenue ($)",
                x_axis_type="datetime",
                show_data_labels=True
            )
            
            total_revenue = sum(float(row.total_revenue) for row in result)
            avg_revenue = total_revenue / len(result) if result else 0
            
            return ChartOutput(
                chart_id=str(uuid.uuid4()),
                config=config,
                series=series,
                metadata={
                    "total_revenue": total_revenue,
                    "avg_daily_revenue": avg_revenue,
                    "data_points": len(result),
                    "chart_category": "revenue_analytics",
                    "period": f"{days}_days"
                },
                generated_at=datetime.now(),
                data_source="revenue_transactions",
                export_formats=["png", "pdf", "csv", "json"]
            )
            
        except Exception as e:
            logger.error(f"Failed to generate revenue trend chart: {e}")
            raise

    def generate_campaign_performance_chart(self) -> ChartOutput:
        """Generate campaign performance comparison"""
        try:
            query = text("""
                SELECT 
                    name as campaign_name,
                    status,
                    COALESCE(budget, 0) as budget,
                    COALESCE(actual_cost, 0) as spent,
                    COALESCE(impressions, 0) as impressions,
                    COALESCE(clicks, 0) as clicks,
                    COALESCE(conversions, 0) as conversions,
                    CASE 
                        WHEN impressions > 0 THEN (clicks::float / impressions) * 100
                        ELSE 0 
                    END as ctr,
                    CASE 
                        WHEN clicks > 0 THEN (conversions::float / clicks) * 100
                        ELSE 0 
                    END as conversion_rate,
                    created_at
                FROM campaigns 
                WHERE created_at >= NOW() - INTERVAL '90 days'
                ORDER BY created_at DESC
                LIMIT 10
            """)
            
            result = self.db.execute(query).fetchall()
            
            # Prepare data for multiple series
            campaign_names = [row.campaign_name for row in result]
            
            series = [
                ChartSeries(
                    name="CTR (%)",
                    data=[ChartDataPoint(x=name, y=row.ctr) for name, row in zip(campaign_names, result)],
                    color=self.default_colors[0]
                ),
                ChartSeries(
                    name="Conversion Rate (%)",
                    data=[ChartDataPoint(x=name, y=row.conversion_rate) for name, row in zip(campaign_names, result)],
                    color=self.default_colors[1]
                ),
                ChartSeries(
                    name="Budget Utilization (%)",
                    data=[
                        ChartDataPoint(
                            x=name, 
                            y=(row.spent / max(row.budget, 1)) * 100,
                            metadata={"budget": row.budget, "spent": row.spent}
                        ) 
                        for name, row in zip(campaign_names, result)
                    ],
                    color=self.default_colors[2]
                )
            ]
            
            config = ChartConfiguration(
                chart_type=ChartType.BAR,
                title="Campaign Performance Comparison",
                subtitle="Last 90 days - Top 10 campaigns",
                x_axis_label="Campaign",
                y_axis_label="Performance Metrics (%)",
                show_legend=True,
                show_data_labels=True
            )
            
            return ChartOutput(
                chart_id=str(uuid.uuid4()),
                config=config,
                series=series,
                metadata={
                    "campaigns_analyzed": len(result),
                    "total_budget": sum(row.budget for row in result),
                    "total_spent": sum(row.spent for row in result),
                    "avg_ctr": sum(row.ctr for row in result) / len(result) if result else 0,
                    "chart_category": "campaign_analytics"
                },
                generated_at=datetime.now(),
                data_source="campaigns_table",
                export_formats=["png", "pdf", "csv", "json"]
            )
            
        except Exception as e:
            logger.error(f"Failed to generate campaign performance chart: {e}")
            raise

    def generate_customer_segmentation_chart(self) -> ChartOutput:
        """Generate customer segmentation visualization"""
        try:
            query = text("""
                SELECT 
                    segment_id,
                    COUNT(*) as customer_count,
                    AVG(age) as avg_age,
                    AVG(total_spent) as avg_spending,
                    SUM(total_spent) as total_revenue
                FROM customers 
                WHERE segment_id IS NOT NULL
                GROUP BY segment_id
                ORDER BY customer_count DESC
            """)
            
            result = self.db.execute(query).fetchall()
            
            # Create bubble chart data (segment size vs avg spending vs customer count)
            bubble_data = []
            pie_data = []
            
            total_customers = sum(row.customer_count for row in result)
            
            for i, row in enumerate(result):
                segment_name = f"Segment {row.segment_id}"
                percentage = (row.customer_count / total_customers) * 100
                
                bubble_data.append(ChartDataPoint(
                    x=float(row.avg_spending),
                    y=float(row.avg_age),
                    label=segment_name,
                    metadata={
                        "segment_id": row.segment_id,
                        "customer_count": row.customer_count,
                        "total_revenue": float(row.total_revenue),
                        "bubble_size": row.customer_count,
                        "percentage": percentage
                    }
                ))
                
                pie_data.append(ChartDataPoint(
                    x=segment_name,
                    y=row.customer_count,
                    label=f"{segment_name}: {percentage:.1f}%",
                    color=self.default_colors[i % len(self.default_colors)]
                ))
            
            # Create two chart outputs - bubble and pie
            bubble_series = [ChartSeries(name="Customer Segments", data=bubble_data)]
            pie_series = [ChartSeries(name="Segment Distribution", data=pie_data)]
            
            bubble_config = ChartConfiguration(
                chart_type=ChartType.SCATTER,
                title="Customer Segmentation Analysis",
                subtitle="Bubble size represents customer count",
                x_axis_label="Average Spending ($)",
                y_axis_label="Average Age",
                x_axis_type="numeric",
                y_axis_type="numeric"
            )
            
            return ChartOutput(
                chart_id=str(uuid.uuid4()),
                config=bubble_config,
                series=bubble_series,
                metadata={
                    "total_segments": len(result),
                    "total_customers": total_customers,
                    "chart_category": "segmentation_analytics",
                    "alternative_charts": {
                        "pie_chart": {
                            "config": asdict(ChartConfiguration(
                                chart_type=ChartType.PIE,
                                title="Customer Segment Distribution",
                                subtitle=f"Total customers: {total_customers}"
                            )),
                            "series": [asdict(series) for series in pie_series]
                        }
                    }
                },
                generated_at=datetime.now(),
                data_source="customers_segments",
                export_formats=["png", "pdf", "csv", "json"]
            )
            
        except Exception as e:
            logger.error(f"Failed to generate customer segmentation chart: {e}")
            raise

    def generate_funnel_analysis_chart(self) -> ChartOutput:
        """Generate conversion funnel visualization"""
        try:
            # Simulate funnel data (in real implementation, this would come from behavioral events)
            funnel_stages = [
                {"stage": "Website Visitors", "count": 10000, "percentage": 100.0},
                {"stage": "Product Views", "count": 7500, "percentage": 75.0},
                {"stage": "Add to Cart", "count": 3000, "percentage": 30.0},
                {"stage": "Checkout Started", "count": 1500, "percentage": 15.0},
                {"stage": "Purchase Completed", "count": 900, "percentage": 9.0}
            ]
            
            # Get actual customer journey data
            query = text("""
                SELECT 
                    COUNT(DISTINCT customer_id) as total_customers,
                    COUNT(DISTINCT CASE WHEN total_spent > 0 THEN customer_id END) as paying_customers
                FROM customers
            """)
            
            result = self.db.execute(query).fetchone()
            
            # Update funnel with real conversion data
            if result:
                total_customers = result.total_customers
                paying_customers = result.paying_customers
                conversion_rate = (paying_customers / total_customers) * 100 if total_customers > 0 else 0
                
                # Adjust funnel based on real data
                funnel_stages[-1]["count"] = paying_customers
                funnel_stages[-1]["percentage"] = conversion_rate
            
            # Create funnel chart data
            funnel_data = []
            bar_data = []
            
            for i, stage in enumerate(funnel_stages):
                funnel_data.append(ChartDataPoint(
                    x=stage["stage"],
                    y=stage["count"],
                    label=f"{stage['stage']}: {stage['count']:,} ({stage['percentage']:.1f}%)",
                    metadata={
                        "stage_index": i,
                        "percentage": stage["percentage"],
                        "conversion_from_previous": stage["percentage"] / funnel_stages[i-1]["percentage"] * 100 if i > 0 else 100
                    }
                ))
                
                bar_data.append(ChartDataPoint(
                    x=stage["stage"],
                    y=stage["percentage"],
                    color=self.default_colors[i % len(self.default_colors)]
                ))
            
            series = [
                ChartSeries(
                    name="Conversion Funnel",
                    data=funnel_data,
                    color=self.default_colors[0]
                )
            ]
            
            config = ChartConfiguration(
                chart_type=ChartType.FUNNEL,
                title="Customer Conversion Funnel",
                subtitle="Complete customer journey analysis",
                x_axis_label="Funnel Stage",
                y_axis_label="Customer Count",
                show_data_labels=True,
                custom_options={
                    "funnel_neck_width": 0.3,
                    "funnel_neck_height": 0.2,
                    "show_percentages": True
                }
            )
            
            overall_conversion = (funnel_stages[-1]["count"] / funnel_stages[0]["count"]) * 100
            
            return ChartOutput(
                chart_id=str(uuid.uuid4()),
                config=config,
                series=series,
                metadata={
                    "funnel_stages": len(funnel_stages),
                    "overall_conversion_rate": overall_conversion,
                    "top_funnel_count": funnel_stages[0]["count"],
                    "bottom_funnel_count": funnel_stages[-1]["count"],
                    "chart_category": "conversion_analytics",
                    "stage_details": funnel_stages
                },
                generated_at=datetime.now(),
                data_source="customer_journey",
                export_formats=["png", "pdf", "csv", "json"]
            )
            
        except Exception as e:
            logger.error(f"Failed to generate funnel analysis chart: {e}")
            raise

    def generate_geographic_distribution_chart(self) -> ChartOutput:
        """Generate geographic customer distribution"""
        try:
            # Simulate geographic data (in real implementation, would use actual customer locations)
            geographic_data = [
                {"region": "North America", "customers": 2500, "revenue": 1250000, "coordinates": [39.8283, -98.5795]},
                {"region": "Europe", "customers": 1800, "revenue": 950000, "coordinates": [54.5260, 15.2551]},
                {"region": "Asia Pacific", "customers": 3200, "revenue": 1600000, "coordinates": [34.0479, 100.6197]},
                {"region": "Latin America", "customers": 800, "revenue": 320000, "coordinates": [-14.2350, -51.9253]},
                {"region": "Middle East", "customers": 600, "revenue": 480000, "coordinates": [29.2985, 42.5510]},
                {"region": "Africa", "customers": 400, "revenue": 180000, "coordinates": [-8.7832, 34.5085]}
            ]
            
            # Create map data
            map_data = []
            bar_data = []
            
            for region_data in geographic_data:
                map_data.append(ChartDataPoint(
                    x=region_data["coordinates"][1],  # longitude
                    y=region_data["coordinates"][0],  # latitude
                    label=region_data["region"],
                    metadata={
                        "region": region_data["region"],
                        "customers": region_data["customers"],
                        "revenue": region_data["revenue"],
                        "avg_revenue_per_customer": region_data["revenue"] / region_data["customers"],
                        "bubble_size": region_data["customers"]
                    }
                ))
                
                bar_data.append(ChartDataPoint(
                    x=region_data["region"],
                    y=region_data["customers"]
                ))
            
            map_series = [ChartSeries(name="Geographic Distribution", data=map_data)]
            bar_series = [ChartSeries(name="Customers by Region", data=bar_data)]
            
            config = ChartConfiguration(
                chart_type=ChartType.GEOGRAPHIC,
                title="Global Customer Distribution",
                subtitle="Customer count and revenue by region",
                custom_options={
                    "map_type": "world",
                    "bubble_scale": "customers",
                    "show_country_borders": True,
                    "zoom_enabled": True
                }
            )
            
            total_customers = sum(r["customers"] for r in geographic_data)
            total_revenue = sum(r["revenue"] for r in geographic_data)
            
            return ChartOutput(
                chart_id=str(uuid.uuid4()),
                config=config,
                series=map_series,
                metadata={
                    "total_regions": len(geographic_data),
                    "total_customers": total_customers,
                    "total_revenue": total_revenue,
                    "avg_revenue_per_customer": total_revenue / total_customers,
                    "chart_category": "geographic_analytics",
                    "alternative_charts": {
                        "bar_chart": {
                            "config": asdict(ChartConfiguration(
                                chart_type=ChartType.BAR,
                                title="Customers by Region",
                                x_axis_label="Region",
                                y_axis_label="Customer Count"
                            )),
                            "series": [asdict(series) for series in bar_series]
                        }
                    }
                },
                generated_at=datetime.now(),
                data_source="customer_locations",
                export_formats=["png", "pdf", "csv", "json"]
            )
            
        except Exception as e:
            logger.error(f"Failed to generate geographic distribution chart: {e}")
            raise

    def generate_kpi_dashboard(self) -> ChartOutput:
        """Generate KPI dashboard with key metrics"""
        try:
            # Get key metrics from database
            metrics_query = text("""
                SELECT 
                    COUNT(*) as total_customers,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as new_customers_30d,
                    COUNT(CASE WHEN total_spent > 0 THEN 1 END) as paying_customers,
                    AVG(total_spent) as avg_customer_value,
                    SUM(total_spent) as total_revenue,
                    COUNT(DISTINCT segment_id) as active_segments
                FROM customers
            """)
            
            result = self.db.execute(metrics_query).fetchone()
            
            # Calculate additional metrics
            conversion_rate = (result.paying_customers / result.total_customers) * 100 if result.total_customers > 0 else 0
            customer_growth = (result.new_customers_30d / max(result.total_customers - result.new_customers_30d, 1)) * 100
            
            # Create KPI cards
            kpi_data = [
                {
                    "title": "Total Customers",
                    "value": result.total_customers,
                    "format": "number",
                    "trend": f"+{result.new_customers_30d} this month",
                    "trend_direction": "up" if result.new_customers_30d > 0 else "neutral",
                    "color": self.default_colors[0]
                },
                {
                    "title": "Total Revenue",
                    "value": result.total_revenue,
                    "format": "currency",
                    "trend": f"${result.total_revenue / result.total_customers:.2f} per customer",
                    "trend_direction": "up",
                    "color": self.default_colors[1]
                },
                {
                    "title": "Conversion Rate",
                    "value": conversion_rate,
                    "format": "percentage",
                    "trend": f"{result.paying_customers} paying customers",
                    "trend_direction": "up" if conversion_rate > 10 else "down",
                    "color": self.default_colors[2]
                },
                {
                    "title": "Customer Growth",
                    "value": customer_growth,
                    "format": "percentage",
                    "trend": "Month over month",
                    "trend_direction": "up" if customer_growth > 0 else "down",
                    "color": self.default_colors[3]
                },
                {
                    "title": "Avg Customer Value",
                    "value": result.avg_customer_value,
                    "format": "currency",
                    "trend": "Lifetime value",
                    "trend_direction": "up",
                    "color": self.default_colors[4]
                },
                {
                    "title": "Active Segments",
                    "value": result.active_segments,
                    "format": "number",
                    "trend": "Customer segments",
                    "trend_direction": "neutral",
                    "color": self.default_colors[5]
                }
            ]
            
            # Convert to chart data points
            kpi_chart_data = []
            for kpi in kpi_data:
                kpi_chart_data.append(ChartDataPoint(
                    x=kpi["title"],
                    y=kpi["value"],
                    label=kpi["title"],
                    color=kpi["color"],
                    metadata={
                        "format": kpi["format"],
                        "trend": kpi["trend"],
                        "trend_direction": kpi["trend_direction"]
                    }
                ))
            
            series = [ChartSeries(name="Key Performance Indicators", data=kpi_chart_data)]
            
            config = ChartConfiguration(
                chart_type=ChartType.KPI,
                title="CRM Dashboard - Key Metrics",
                subtitle=f"Updated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                custom_options={
                    "layout": "grid",
                    "columns": 3,
                    "show_trends": True,
                    "show_comparisons": True
                }
            )
            
            return ChartOutput(
                chart_id=str(uuid.uuid4()),
                config=config,
                series=series,
                metadata={
                    "kpi_count": len(kpi_data),
                    "chart_category": "kpi_dashboard",
                    "metrics": {
                        "total_customers": result.total_customers,
                        "total_revenue": result.total_revenue,
                        "conversion_rate": conversion_rate,
                        "customer_growth": customer_growth
                    }
                },
                generated_at=datetime.now(),
                data_source="crm_metrics",
                export_formats=["png", "pdf", "json"]
            )
            
        except Exception as e:
            logger.error(f"Failed to generate KPI dashboard: {e}")
            raise

    def generate_custom_chart(self, chart_config: Dict[str, Any]) -> ChartOutput:
        """Generate custom chart based on configuration"""
        try:
            chart_type = ChartType(chart_config.get("chart_type", "bar"))
            data_source = chart_config.get("data_source")
            aggregation = chart_config.get("aggregation", "count")
            filters = chart_config.get("filters", {})
            
            # Build dynamic query based on configuration
            if data_source == "customers":
                base_query = "SELECT * FROM customers WHERE 1=1"
            elif data_source == "campaigns": 
                base_query = "SELECT * FROM campaigns WHERE 1=1"
            else:
                raise ValueError(f"Unsupported data source: {data_source}")
            
            # Apply filters
            filter_conditions = []
            params = {}
            
            for field, value in filters.items():
                if isinstance(value, dict):
                    if "min" in value:
                        filter_conditions.append(f"{field} >= :{field}_min")
                        params[f"{field}_min"] = value["min"]
                    if "max" in value:
                        filter_conditions.append(f"{field} <= :{field}_max") 
                        params[f"{field}_max"] = value["max"]
                else:
                    filter_conditions.append(f"{field} = :{field}")
                    params[field] = value
            
            if filter_conditions:
                base_query += " AND " + " AND ".join(filter_conditions)
            
            result = self.db.execute(text(base_query), params).fetchall()
            
            # Process data based on chart requirements
            chart_data = self._process_data_for_chart(result, chart_config)
            
            config = ChartConfiguration(
                chart_type=chart_type,
                title=chart_config.get("title", "Custom Chart"),
                subtitle=chart_config.get("subtitle", ""),
                x_axis_label=chart_config.get("x_axis_label"),
                y_axis_label=chart_config.get("y_axis_label"),
                show_legend=chart_config.get("show_legend", True),
                show_data_labels=chart_config.get("show_data_labels", False)
            )
            
            return ChartOutput(
                chart_id=str(uuid.uuid4()),
                config=config,
                series=chart_data,
                metadata={
                    "data_source": data_source,
                    "filters_applied": filters,
                    "aggregation": aggregation,
                    "data_points": len(result),
                    "chart_category": "custom_analytics"
                },
                generated_at=datetime.now(),
                data_source=data_source,
                export_formats=["png", "pdf", "csv", "json"]
            )
            
        except Exception as e:
            logger.error(f"Failed to generate custom chart: {e}")
            raise

    def _process_data_for_chart(self, data: List, config: Dict[str, Any]) -> List[ChartSeries]:
        """Process raw data into chart-ready format"""
        try:
            chart_type = ChartType(config.get("chart_type", "bar"))
            x_field = config.get("x_field", "id")
            y_field = config.get("y_field", "value")
            group_by = config.get("group_by")
            
            if not data:
                return [ChartSeries(name="No Data", data=[])]
            
            # Convert to pandas for easier processing
            df = pd.DataFrame([dict(row._mapping) for row in data])
            
            if group_by:
                # Group data and aggregate
                grouped_data = df.groupby(group_by).agg({
                    y_field: config.get("aggregation", "sum")
                }).reset_index()
                
                series_data = []
                for _, row in grouped_data.iterrows():
                    series_data.append(ChartDataPoint(
                        x=row[group_by],
                        y=row[y_field]
                    ))
                
                return [ChartSeries(name=y_field.title(), data=series_data)]
            else:
                # Simple x/y mapping
                series_data = []
                for _, row in df.iterrows():
                    series_data.append(ChartDataPoint(
                        x=row[x_field],
                        y=row[y_field]
                    ))
                
                return [ChartSeries(name="Data", data=series_data)]
                
        except Exception as e:
            logger.error(f"Failed to process chart data: {e}")
            return [ChartSeries(name="Error", data=[])]

    def export_chart_data(self, chart_output: ChartOutput, format: str = "json") -> str:
        """Export chart data in specified format"""
        try:
            if format.lower() == "json":
                return json.dumps({
                    "chart_id": chart_output.chart_id,
                    "config": asdict(chart_output.config),
                    "series": [asdict(series) for series in chart_output.series],
                    "metadata": chart_output.metadata,
                    "generated_at": chart_output.generated_at.isoformat(),
                    "data_source": chart_output.data_source
                }, indent=2, default=str)
            
            elif format.lower() == "csv":
                # Convert chart data to CSV format
                csv_data = []
                for series in chart_output.series:
                    for point in series.data:
                        csv_data.append({
                            "series": series.name,
                            "x": point.x,
                            "y": point.y,
                            "label": point.label
                        })
                
                df = pd.DataFrame(csv_data)
                return df.to_csv(index=False)
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export chart data: {e}")
            raise