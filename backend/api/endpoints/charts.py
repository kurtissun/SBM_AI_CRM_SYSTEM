"""
Chart Generation API Endpoints
Frontend-ready chart data for CRM dashboards and analytics
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import get_current_user, require_permission
from ...reporting.chart_engine import (
    ChartEngine,
    ChartType,
    TimeGranularity,
    AggregationType
)

router = APIRouter()

class CustomChartRequest(BaseModel):
    chart_type: str
    title: str
    subtitle: Optional[str] = ""
    data_source: str  # customers, campaigns, revenue, etc.
    x_field: str
    y_field: str
    group_by: Optional[str] = None
    aggregation: str = "count"
    filters: Dict[str, Any] = {}
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    show_legend: bool = True
    show_data_labels: bool = False
    color_palette: List[str] = []

class ChartResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

@router.get("/dashboard/kpi")
async def get_kpi_dashboard(
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get KPI dashboard with key CRM metrics"""
    try:
        chart_engine = ChartEngine(db)
        chart_output = chart_engine.generate_kpi_dashboard()
        
        return {
            "chart_id": chart_output.chart_id,
            "config": chart_output.config.__dict__,
            "series": [series.__dict__ for series in chart_output.series],
            "metadata": chart_output.metadata,
            "generated_at": chart_output.generated_at.isoformat(),
            "export_formats": chart_output.export_formats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate KPI dashboard: {str(e)}")

@router.get("/customer/demographics")
async def get_customer_demographics_chart(
    chart_type: str = Query("pie", regex="^(pie|bar|column)$"),
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get customer demographics visualization"""
    try:
        chart_engine = ChartEngine(db)
        chart_output = chart_engine.generate_customer_demographics_chart(
            ChartType(chart_type)
        )
        
        return {
            "chart_id": chart_output.chart_id,
            "config": chart_output.config.__dict__,
            "series": [
                {
                    "name": series.name,
                    "data": [
                        {
                            "x": point.x,
                            "y": point.y,
                            "label": point.label,
                            "color": point.color,
                            "metadata": point.metadata
                        }
                        for point in series.data
                    ],
                    "color": series.color,
                    "type": series.type,
                    "metadata": series.metadata
                }
                for series in chart_output.series
            ],
            "metadata": chart_output.metadata,
            "generated_at": chart_output.generated_at.isoformat(),
            "data_source": chart_output.data_source,
            "export_formats": chart_output.export_formats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate demographics chart: {str(e)}")

@router.get("/revenue/trend")
async def get_revenue_trend_chart(
    days: int = Query(30, ge=1, le=365),
    granularity: str = Query("day", regex="^(hour|day|week|month|quarter|year)$"),
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get revenue trend visualization"""
    try:
        chart_engine = ChartEngine(db)
        chart_output = chart_engine.generate_revenue_trend_chart(
            days=days,
            granularity=TimeGranularity(granularity)
        )
        
        return {
            "chart_id": chart_output.chart_id,
            "config": chart_output.config.__dict__,
            "series": [
                {
                    "name": series.name,
                    "data": [
                        {
                            "x": point.x,
                            "y": point.y,
                            "label": point.label,
                            "metadata": point.metadata
                        }
                        for point in series.data
                    ],
                    "color": series.color,
                    "type": series.type
                }
                for series in chart_output.series
            ],
            "metadata": chart_output.metadata,
            "generated_at": chart_output.generated_at.isoformat(),
            "export_formats": chart_output.export_formats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate revenue trend chart: {str(e)}")

@router.get("/campaign/performance")
async def get_campaign_performance_chart(
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get campaign performance comparison chart"""
    try:
        chart_engine = ChartEngine(db)
        chart_output = chart_engine.generate_campaign_performance_chart()
        
        return {
            "chart_id": chart_output.chart_id,
            "config": chart_output.config.__dict__,
            "series": [
                {
                    "name": series.name,
                    "data": [
                        {
                            "x": point.x,
                            "y": point.y,
                            "metadata": point.metadata
                        }
                        for point in series.data
                    ],
                    "color": series.color
                }
                for series in chart_output.series
            ],
            "metadata": chart_output.metadata,
            "generated_at": chart_output.generated_at.isoformat(),
            "export_formats": chart_output.export_formats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate campaign performance chart: {str(e)}")

@router.get("/customer/segmentation")
async def get_customer_segmentation_chart(
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get customer segmentation visualization"""
    try:
        chart_engine = ChartEngine(db)
        chart_output = chart_engine.generate_customer_segmentation_chart()
        
        return {
            "chart_id": chart_output.chart_id,
            "config": chart_output.config.__dict__,
            "series": [
                {
                    "name": series.name,
                    "data": [
                        {
                            "x": point.x,
                            "y": point.y,
                            "label": point.label,
                            "metadata": point.metadata
                        }
                        for point in series.data
                    ]
                }
                for series in chart_output.series
            ],
            "metadata": chart_output.metadata,
            "generated_at": chart_output.generated_at.isoformat(),
            "export_formats": chart_output.export_formats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate segmentation chart: {str(e)}")

@router.get("/conversion/funnel")
async def get_conversion_funnel_chart(
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get conversion funnel analysis chart"""
    try:
        chart_engine = ChartEngine(db)
        chart_output = chart_engine.generate_funnel_analysis_chart()
        
        return {
            "chart_id": chart_output.chart_id,
            "config": chart_output.config.__dict__,
            "series": [
                {
                    "name": series.name,
                    "data": [
                        {
                            "x": point.x,
                            "y": point.y,
                            "label": point.label,
                            "metadata": point.metadata
                        }
                        for point in series.data
                    ],
                    "color": series.color
                }
                for series in chart_output.series
            ],
            "metadata": chart_output.metadata,
            "generated_at": chart_output.generated_at.isoformat(),
            "export_formats": chart_output.export_formats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate funnel chart: {str(e)}")

@router.get("/geographic/distribution")
async def get_geographic_distribution_chart(
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get geographic customer distribution chart"""
    try:
        chart_engine = ChartEngine(db)
        chart_output = chart_engine.generate_geographic_distribution_chart()
        
        return {
            "chart_id": chart_output.chart_id,
            "config": chart_output.config.__dict__,
            "series": [
                {
                    "name": series.name,
                    "data": [
                        {
                            "x": point.x,
                            "y": point.y,
                            "label": point.label,
                            "metadata": point.metadata
                        }
                        for point in series.data
                    ]
                }
                for series in chart_output.series
            ],
            "metadata": chart_output.metadata,
            "generated_at": chart_output.generated_at.isoformat(),
            "export_formats": chart_output.export_formats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate geographic chart: {str(e)}")

@router.post("/custom", response_model=ChartResponse)
async def create_custom_chart(
    request: CustomChartRequest,
    current_user: dict = Depends(require_permission("create_charts")),
    db: Session = Depends(get_db)
):
    """Create custom chart based on user configuration"""
    try:
        chart_engine = ChartEngine(db)
        
        chart_config = {
            "chart_type": request.chart_type,
            "title": request.title,
            "subtitle": request.subtitle,
            "data_source": request.data_source,
            "x_field": request.x_field,
            "y_field": request.y_field,
            "group_by": request.group_by,
            "aggregation": request.aggregation,
            "filters": request.filters,
            "x_axis_label": request.x_axis_label,
            "y_axis_label": request.y_axis_label,
            "show_legend": request.show_legend,
            "show_data_labels": request.show_data_labels,
            "color_palette": request.color_palette
        }
        
        chart_output = chart_engine.generate_custom_chart(chart_config)
        
        return ChartResponse(
            success=True,
            message="Custom chart created successfully",
            data={
                "chart_id": chart_output.chart_id,
                "config": chart_output.config.__dict__,
                "series": [
                    {
                        "name": series.name,
                        "data": [
                            {
                                "x": point.x,
                                "y": point.y,
                                "label": point.label,
                                "metadata": point.metadata
                            }
                            for point in series.data
                        ]
                    }
                    for series in chart_output.series
                ],
                "metadata": chart_output.metadata,
                "generated_at": chart_output.generated_at.isoformat(),
                "export_formats": chart_output.export_formats
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create custom chart: {str(e)}")

@router.get("/export/{chart_id}")
async def export_chart_data(
    chart_id: str,
    format: str = Query("json", regex="^(json|csv|png|pdf)$"),
    current_user: dict = Depends(require_permission("export_data")),
    db: Session = Depends(get_db)
):
    """Export chart data in specified format"""
    try:
        # Note: In a real implementation, you'd retrieve the chart from storage
        # For now, we'll return a placeholder response
        
        if format in ["png", "pdf"]:
            return {
                "message": f"Chart export to {format.upper()} format would be generated here",
                "chart_id": chart_id,
                "format": format,
                "download_url": f"/api/charts/download/{chart_id}.{format}",
                "expires_at": (datetime.now().timestamp() + 3600)  # 1 hour
            }
        else:
            return {
                "message": f"Chart data export in {format.upper()} format",
                "chart_id": chart_id,
                "format": format,
                "data": {
                    "note": "Chart data would be exported here based on chart_id",
                    "supported_formats": ["json", "csv", "png", "pdf"]
                }
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export chart: {str(e)}")

@router.get("/templates")
async def get_chart_templates(
    category: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get available chart templates for quick creation"""
    templates = {
        "customer_analytics": [
            {
                "id": "customer_demographics",
                "name": "Customer Demographics",
                "description": "Age and gender distribution of customers",
                "chart_type": "pie",
                "preview_url": "/api/charts/customer/demographics"
            },
            {
                "id": "customer_segmentation",
                "name": "Customer Segmentation",
                "description": "Customer segments analysis with spending patterns",
                "chart_type": "scatter",
                "preview_url": "/api/charts/customer/segmentation"
            }
        ],
        "revenue_analytics": [
            {
                "id": "revenue_trend",
                "name": "Revenue Trend",
                "description": "Revenue over time with trends and patterns",
                "chart_type": "line",
                "preview_url": "/api/charts/revenue/trend"
            },
            {
                "id": "revenue_by_segment",
                "name": "Revenue by Segment",
                "description": "Revenue breakdown by customer segments",
                "chart_type": "bar",
                "preview_url": "/api/charts/revenue/segments"
            }
        ],
        "campaign_analytics": [
            {
                "id": "campaign_performance",
                "name": "Campaign Performance",
                "description": "Campaign metrics comparison and analysis",
                "chart_type": "bar",
                "preview_url": "/api/charts/campaign/performance"
            },
            {
                "id": "campaign_roi",
                "name": "Campaign ROI",
                "description": "Return on investment for marketing campaigns",
                "chart_type": "column",
                "preview_url": "/api/charts/campaign/roi"
            }
        ],
        "conversion_analytics": [
            {
                "id": "conversion_funnel",
                "name": "Conversion Funnel",
                "description": "Customer journey and conversion analysis",
                "chart_type": "funnel",
                "preview_url": "/api/charts/conversion/funnel"
            },
            {
                "id": "conversion_rates",
                "name": "Conversion Rates",
                "description": "Conversion rates across different channels",
                "chart_type": "line",
                "preview_url": "/api/charts/conversion/rates"
            }
        ],
        "geographic_analytics": [
            {
                "id": "geographic_distribution",
                "name": "Geographic Distribution",
                "description": "Customer distribution across regions",
                "chart_type": "geographic",
                "preview_url": "/api/charts/geographic/distribution"
            }
        ],
        "kpi_dashboards": [
            {
                "id": "executive_dashboard",
                "name": "Executive Dashboard",
                "description": "Key performance indicators for executives",
                "chart_type": "kpi",
                "preview_url": "/api/charts/dashboard/kpi"
            }
        ]
    }
    
    if category:
        return {
            "category": category,
            "templates": templates.get(category, [])
        }
    
    return {
        "categories": list(templates.keys()),
        "templates": templates
    }

@router.get("/chart-types")
async def get_available_chart_types(
    current_user: dict = Depends(get_current_user)
):
    """Get available chart types and their configurations"""
    chart_types = [
        {
            "id": "line",
            "name": "Line Chart",
            "description": "Show trends and changes over time",
            "best_for": ["time_series", "trends", "continuous_data"],
            "supports_multiple_series": True,
            "supports_stacking": False
        },
        {
            "id": "bar",
            "name": "Bar Chart", 
            "description": "Compare values across categories",
            "best_for": ["categorical_data", "comparisons", "rankings"],
            "supports_multiple_series": True,
            "supports_stacking": True
        },
        {
            "id": "column",
            "name": "Column Chart",
            "description": "Vertical bars for comparing categories",
            "best_for": ["categorical_data", "time_periods", "comparisons"],
            "supports_multiple_series": True,
            "supports_stacking": True
        },
        {
            "id": "pie",
            "name": "Pie Chart",
            "description": "Show parts of a whole",
            "best_for": ["percentages", "composition", "simple_distributions"],
            "supports_multiple_series": False,
            "supports_stacking": False
        },
        {
            "id": "doughnut",
            "name": "Doughnut Chart",
            "description": "Pie chart with center hole for additional info",
            "best_for": ["percentages", "composition", "kpis"],
            "supports_multiple_series": False,
            "supports_stacking": False
        },
        {
            "id": "area",
            "name": "Area Chart",
            "description": "Show volume and trends over time",
            "best_for": ["cumulative_data", "volume_trends", "multiple_categories"],
            "supports_multiple_series": True,
            "supports_stacking": True
        },
        {
            "id": "scatter",
            "name": "Scatter Plot",
            "description": "Show relationships between two variables",
            "best_for": ["correlations", "distributions", "outliers"],
            "supports_multiple_series": True,
            "supports_stacking": False
        },
        {
            "id": "funnel",
            "name": "Funnel Chart",
            "description": "Show conversion processes and drop-offs",
            "best_for": ["conversion_analysis", "process_flow", "sales_pipeline"],
            "supports_multiple_series": False,
            "supports_stacking": False
        },
        {
            "id": "gauge",
            "name": "Gauge Chart",
            "description": "Show single values against targets",
            "best_for": ["kpis", "performance_metrics", "targets"],
            "supports_multiple_series": False,
            "supports_stacking": False
        },
        {
            "id": "heatmap",
            "name": "Heatmap",
            "description": "Show data density and patterns",
            "best_for": ["correlation_matrices", "time_patterns", "geographic_data"],
            "supports_multiple_series": False,
            "supports_stacking": False
        },
        {
            "id": "geographic",
            "name": "Geographic Map",
            "description": "Show data on maps with geographic context",
            "best_for": ["location_data", "regional_analysis", "global_metrics"],
            "supports_multiple_series": True,
            "supports_stacking": False
        },
        {
            "id": "kpi",
            "name": "KPI Cards",
            "description": "Display key metrics in card format",
            "best_for": ["dashboards", "key_metrics", "performance_overview"],
            "supports_multiple_series": False,
            "supports_stacking": False
        }
    ]
    
    return {
        "chart_types": chart_types,
        "aggregation_types": [
            {"id": "sum", "name": "Sum", "description": "Total of all values"},
            {"id": "count", "name": "Count", "description": "Number of records"},
            {"id": "average", "name": "Average", "description": "Mean value"},
            {"id": "min", "name": "Minimum", "description": "Smallest value"},
            {"id": "max", "name": "Maximum", "description": "Largest value"},
            {"id": "median", "name": "Median", "description": "Middle value"},
            {"id": "distinct", "name": "Distinct Count", "description": "Number of unique values"},
            {"id": "percentage", "name": "Percentage", "description": "Percentage of total"}
        ],
        "time_granularities": [
            {"id": "hour", "name": "Hourly", "description": "Group by hour"},
            {"id": "day", "name": "Daily", "description": "Group by day"},
            {"id": "week", "name": "Weekly", "description": "Group by week"},
            {"id": "month", "name": "Monthly", "description": "Group by month"},
            {"id": "quarter", "name": "Quarterly", "description": "Group by quarter"},
            {"id": "year", "name": "Yearly", "description": "Group by year"}
        ]
    }