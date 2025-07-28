"""
Advanced Financial Analytics Engine
Revenue waterfalls, margin analysis, profitability analytics, and financial forecasting
"""
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import text
from collections import defaultdict
import uuid
import json
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy import stats

logger = logging.getLogger(__name__)

class RevenueType(Enum):
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    UPSELL = "upsell"
    CROSS_SELL = "cross_sell"
    RENEWAL = "renewal"
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"

class CostType(Enum):
    COGS = "cost_of_goods_sold"
    CAC = "customer_acquisition_cost"
    OPEX = "operational_expenses"
    MARKETING = "marketing_expenses"
    SUPPORT = "support_costs"
    INFRASTRUCTURE = "infrastructure_costs"
    PERSONNEL = "personnel_costs"

class MetricPeriod(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

@dataclass
class RevenueWaterfallComponent:
    component_id: str
    component_name: str
    component_type: str
    value: float
    percentage_of_total: float
    period_start: datetime
    period_end: datetime
    trend_direction: str
    impact_level: str
    description: str

@dataclass
class MarginAnalysis:
    analysis_id: str
    product_line: str
    gross_margin: float
    net_margin: float
    operating_margin: float
    contribution_margin: float
    margin_trend: str
    cost_breakdown: Dict[str, float]
    revenue_breakdown: Dict[str, float]
    profitability_score: float
    optimization_opportunities: List[str]

@dataclass
class CustomerProfitability:
    customer_id: str
    customer_segment: str
    total_revenue: float
    total_costs: float
    gross_profit: float
    gross_margin_percentage: float
    ltv: float
    cac: float
    ltv_cac_ratio: float
    payback_period_months: int
    profitability_tier: str
    monthly_profit_trend: List[float]
    retention_impact: float

@dataclass
class FinancialForecast:
    forecast_id: str
    forecast_type: str
    period: str
    forecasted_revenue: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    seasonality_factor: float
    trend_component: float
    growth_rate: float
    forecast_accuracy: float
    key_assumptions: List[str]
    risk_factors: List[str]

@dataclass
class ProfitabilityMetrics:
    period: str
    total_revenue: float
    total_costs: float
    gross_profit: float
    operating_profit: float
    net_profit: float
    gross_margin_percent: float
    operating_margin_percent: float
    net_margin_percent: float
    return_on_investment: float
    customer_acquisition_cost: float
    customer_lifetime_value: float
    monthly_recurring_revenue: float
    churn_impact_on_revenue: float

class FinancialAnalyticsEngine:
    def __init__(self, db: Session):
        self.db = db
        
    def generate_revenue_waterfall(self, start_date: datetime, end_date: datetime,
                                 granularity: MetricPeriod = MetricPeriod.MONTHLY) -> List[RevenueWaterfallComponent]:
        """Generate comprehensive revenue waterfall analysis"""
        try:
            components = []
            
            # Get base revenue data
            revenue_data = self._get_revenue_data(start_date, end_date)
            
            total_revenue = sum(revenue_data.values())
            
            # Calculate waterfall components
            waterfall_structure = [
                ("starting_revenue", "Starting Revenue", 0.0, "baseline"),
                ("new_customer_revenue", "New Customer Revenue", 0.35, "positive"),
                ("expansion_revenue", "Expansion Revenue", 0.15, "positive"),
                ("upsell_revenue", "Upsell Revenue", 0.12, "positive"),
                ("cross_sell_revenue", "Cross-sell Revenue", 0.08, "positive"),
                ("churn_impact", "Churn Impact", -0.18, "negative"),
                ("downgrade_impact", "Downgrade Impact", -0.08, "negative"),
                ("price_changes", "Price Changes", 0.03, "positive"),
                ("seasonal_adjustment", "Seasonal Adjustment", -0.02, "neutral"),
                ("ending_revenue", "Ending Revenue", 0.0, "baseline")
            ]
            
            # Previous period revenue (simulated)
            previous_period_revenue = total_revenue * 0.85
            current_cumulative = previous_period_revenue
            
            for comp_id, name, impact_factor, comp_type in waterfall_structure:
                if comp_id in ["starting_revenue", "ending_revenue"]:
                    if comp_id == "starting_revenue":
                        value = previous_period_revenue
                        current_cumulative = value
                    else:
                        value = current_cumulative
                else:
                    value = total_revenue * impact_factor
                    current_cumulative += value
                
                # Determine trend and impact
                if abs(impact_factor) > 0.1:
                    impact_level = "high"
                elif abs(impact_factor) > 0.05:
                    impact_level = "medium"
                else:
                    impact_level = "low"
                
                trend_direction = "increasing" if impact_factor > 0 else "decreasing" if impact_factor < 0 else "stable"
                
                component = RevenueWaterfallComponent(
                    component_id=comp_id,
                    component_name=name,
                    component_type=comp_type,
                    value=value,
                    percentage_of_total=(value / max(total_revenue, 1)) * 100,
                    period_start=start_date,
                    period_end=end_date,
                    trend_direction=trend_direction,
                    impact_level=impact_level,
                    description=self._get_component_description(comp_id, value, impact_factor)
                )
                
                components.append(component)
            
            logger.info(f"Generated revenue waterfall with {len(components)} components")
            return components
            
        except Exception as e:
            logger.error(f"Failed to generate revenue waterfall: {e}")
            raise

    def analyze_customer_profitability(self, segment_filter: Optional[str] = None,
                                     limit: int = 100) -> List[CustomerProfitability]:
        """Analyze profitability by customer"""
        try:
            # Get customer financial data
            query = text("""
                SELECT 
                    customer_id,
                    segment_id,
                    total_spent,
                    created_at,
                    age,
                    EXTRACT(DAYS FROM NOW() - created_at) as customer_age_days
                FROM customers 
                WHERE total_spent > 0
            """)
            
            if segment_filter:
                query = text(query.text + f" AND segment_id = '{segment_filter}'")
            
            query = text(query.text + f" ORDER BY total_spent DESC LIMIT {limit}")
            
            result = self.db.execute(query).fetchall()
            customer_data = [dict(row._mapping) for row in result]
            
            profitability_analyses = []
            
            for customer in customer_data:
                # Calculate customer metrics
                total_revenue = customer['total_spent']
                customer_age_months = max(1, customer['customer_age_days'] / 30)
                
                # Estimate costs (simplified model)
                cac = self._estimate_customer_acquisition_cost(customer)
                cogs = total_revenue * 0.35  # 35% cost of goods sold
                support_costs = self._estimate_support_costs(customer)
                infrastructure_costs = customer_age_months * 5  # $5 per month
                
                total_costs = cac + cogs + support_costs + infrastructure_costs
                gross_profit = total_revenue - total_costs
                gross_margin_percentage = (gross_profit / max(total_revenue, 1)) * 100
                
                # Calculate LTV and ratios
                monthly_revenue = total_revenue / customer_age_months
                estimated_lifetime_months = self._estimate_customer_lifetime(customer)
                ltv = monthly_revenue * estimated_lifetime_months
                
                ltv_cac_ratio = ltv / max(cac, 1)
                payback_period_months = int(cac / max(monthly_revenue, 1))
                
                # Determine profitability tier
                if gross_margin_percentage > 70 and ltv_cac_ratio > 3:
                    profitability_tier = "highly_profitable"
                elif gross_margin_percentage > 50 and ltv_cac_ratio > 2:
                    profitability_tier = "profitable"
                elif gross_margin_percentage > 20 and ltv_cac_ratio > 1:
                    profitability_tier = "moderately_profitable"
                else:
                    profitability_tier = "low_profitability"
                
                # Generate monthly profit trend (simplified)
                monthly_trend = []
                base_monthly_profit = gross_profit / customer_age_months
                for i in range(int(min(12, customer_age_months))):
                    trend_factor = 1 + (i * 0.02)  # Small growth trend
                    monthly_trend.append(base_monthly_profit * trend_factor)
                
                profitability = CustomerProfitability(
                    customer_id=customer['customer_id'],
                    customer_segment=customer.get('segment_id', 'unknown'),
                    total_revenue=total_revenue,
                    total_costs=total_costs,
                    gross_profit=gross_profit,
                    gross_margin_percentage=gross_margin_percentage,
                    ltv=ltv,
                    cac=cac,
                    ltv_cac_ratio=ltv_cac_ratio,
                    payback_period_months=payback_period_months,
                    profitability_tier=profitability_tier,
                    monthly_profit_trend=monthly_trend,
                    retention_impact=self._calculate_retention_impact(customer)
                )
                
                profitability_analyses.append(profitability)
            
            # Sort by profitability
            profitability_analyses.sort(key=lambda x: x.gross_profit, reverse=True)
            
            logger.info(f"Analyzed profitability for {len(profitability_analyses)} customers")
            return profitability_analyses
            
        except Exception as e:
            logger.error(f"Failed to analyze customer profitability: {e}")
            raise

    def analyze_margin_performance(self, product_lines: Optional[List[str]] = None) -> List[MarginAnalysis]:
        """Analyze margin performance across product lines"""
        try:
            if not product_lines:
                product_lines = ["Product A", "Product B", "Product C", "Product D", "Service Package"]
            
            margin_analyses = []
            
            for product_line in product_lines:
                # Simulate product line financial data
                revenue = np.random.uniform(50000, 200000)
                
                # Cost breakdown
                cogs = revenue * np.random.uniform(0.25, 0.45)
                marketing_costs = revenue * np.random.uniform(0.08, 0.15)
                support_costs = revenue * np.random.uniform(0.05, 0.12)
                operational_costs = revenue * np.random.uniform(0.10, 0.20)
                
                total_costs = cogs + marketing_costs + support_costs + operational_costs
                
                # Calculate margins
                gross_margin = ((revenue - cogs) / revenue) * 100
                operating_margin = ((revenue - cogs - operational_costs) / revenue) * 100
                net_margin = ((revenue - total_costs) / revenue) * 100
                contribution_margin = ((revenue - cogs - marketing_costs) / revenue) * 100
                
                # Determine trend
                trend_indicator = np.random.choice(["improving", "declining", "stable"], p=[0.4, 0.3, 0.3])
                
                # Calculate profitability score
                profitability_score = (gross_margin + operating_margin + net_margin) / 3
                
                # Generate optimization opportunities
                optimization_opportunities = []
                if gross_margin < 50:
                    optimization_opportunities.append("Reduce cost of goods sold through supplier negotiation")
                if marketing_costs / revenue > 0.12:
                    optimization_opportunities.append("Optimize marketing spend efficiency")
                if support_costs / revenue > 0.10:
                    optimization_opportunities.append("Implement self-service support options")
                if net_margin < 15:
                    optimization_opportunities.append("Review pricing strategy for profitability improvement")
                
                margin_analysis = MarginAnalysis(
                    analysis_id=str(uuid.uuid4()),
                    product_line=product_line,
                    gross_margin=gross_margin,
                    net_margin=net_margin,
                    operating_margin=operating_margin,
                    contribution_margin=contribution_margin,
                    margin_trend=trend_indicator,
                    cost_breakdown={
                        "cogs": cogs,
                        "marketing": marketing_costs,
                        "support": support_costs,
                        "operational": operational_costs
                    },
                    revenue_breakdown={
                        "total_revenue": revenue,
                        "gross_revenue": revenue - cogs,
                        "operating_revenue": revenue - cogs - operational_costs
                    },
                    profitability_score=profitability_score,
                    optimization_opportunities=optimization_opportunities
                )
                
                margin_analyses.append(margin_analysis)
            
            # Sort by profitability score
            margin_analyses.sort(key=lambda x: x.profitability_score, reverse=True)
            
            logger.info(f"Analyzed margins for {len(margin_analyses)} product lines")
            return margin_analyses
            
        except Exception as e:
            logger.error(f"Failed to analyze margin performance: {e}")
            raise

    def generate_financial_forecast(self, forecast_period_months: int = 12,
                                  forecast_type: str = "revenue") -> FinancialForecast:
        """Generate financial forecasts using time series analysis"""
        try:
            # Get historical data
            historical_data = self._get_historical_financial_data(forecast_type)
            
            if len(historical_data) < 6:
                raise ValueError("Insufficient historical data for forecasting")
            
            # Prepare data for forecasting
            dates = [d['date'] for d in historical_data]
            values = [d['value'] for d in historical_data]
            
            # Convert dates to numeric for regression
            base_date = min(dates)
            x_values = [(d - base_date).days for d in dates]
            
            # Fit polynomial regression model
            poly_features = PolynomialFeatures(degree=2)
            x_poly = poly_features.fit_transform(np.array(x_values).reshape(-1, 1))
            
            model = LinearRegression()
            model.fit(x_poly, values)
            
            # Generate forecast
            last_date = max(dates)
            forecast_dates = [last_date + timedelta(days=30*i) for i in range(1, forecast_period_months + 1)]
            forecast_x = [(d - base_date).days for d in forecast_dates]
            forecast_x_poly = poly_features.transform(np.array(forecast_x).reshape(-1, 1))
            
            forecasted_values = model.predict(forecast_x_poly)
            
            # Calculate forecast statistics
            forecast_mean = np.mean(forecasted_values)
            historical_std = np.std(values)
            
            # Confidence intervals (95%)
            confidence_margin = 1.96 * historical_std
            confidence_lower = forecast_mean - confidence_margin
            confidence_upper = forecast_mean + confidence_margin
            
            # Calculate trend and growth
            recent_values = values[-6:]  # Last 6 periods
            trend_component = np.mean(np.diff(recent_values))
            growth_rate = (values[-1] - values[0]) / max(values[0], 1) * 100
            
            # Seasonality analysis (simplified)
            if len(values) >= 12:
                monthly_averages = []
                for i in range(12):
                    month_values = [values[j] for j in range(i, len(values), 12)]
                    monthly_averages.append(np.mean(month_values))
                seasonality_factor = max(monthly_averages) / min(monthly_averages)
            else:
                seasonality_factor = 1.0
            
            # Calculate forecast accuracy (based on model R²)
            r2_score = model.score(x_poly, values)
            forecast_accuracy = max(0.5, min(0.95, r2_score))
            
            # Key assumptions and risk factors
            key_assumptions = [
                "Historical trends will continue",
                "No major market disruptions",
                "Customer behavior remains consistent",
                "Economic conditions remain stable"
            ]
            
            risk_factors = []
            if growth_rate < 0:
                risk_factors.append("Declining historical trend")
            if forecast_accuracy < 0.7:
                risk_factors.append("High forecast uncertainty")
            if seasonality_factor > 1.5:
                risk_factors.append("High seasonal volatility")
            
            forecast = FinancialForecast(
                forecast_id=str(uuid.uuid4()),
                forecast_type=forecast_type,
                period=f"{forecast_period_months} months",
                forecasted_revenue=forecast_mean,
                confidence_interval_lower=confidence_lower,
                confidence_interval_upper=confidence_upper,
                seasonality_factor=seasonality_factor,
                trend_component=trend_component,
                growth_rate=growth_rate,
                forecast_accuracy=forecast_accuracy,
                key_assumptions=key_assumptions,
                risk_factors=risk_factors
            )
            
            logger.info(f"Generated {forecast_type} forecast for {forecast_period_months} months")
            return forecast
            
        except Exception as e:
            logger.error(f"Failed to generate financial forecast: {e}")
            raise

    def calculate_profitability_metrics(self, period_start: datetime, 
                                       period_end: datetime) -> ProfitabilityMetrics:
        """Calculate comprehensive profitability metrics"""
        try:
            # Get financial data for period
            revenue_data = self._get_revenue_data(period_start, period_end)
            cost_data = self._get_cost_data(period_start, period_end)
            
            total_revenue = sum(revenue_data.values())
            total_costs = sum(cost_data.values())
            
            # Calculate profit metrics
            gross_profit = total_revenue - cost_data.get('cogs', 0)
            operating_profit = gross_profit - cost_data.get('opex', 0)
            net_profit = operating_profit - cost_data.get('taxes', 0)
            
            # Calculate margin percentages
            gross_margin_percent = (gross_profit / max(total_revenue, 1)) * 100
            operating_margin_percent = (operating_profit / max(total_revenue, 1)) * 100
            net_margin_percent = (net_profit / max(total_revenue, 1)) * 100
            
            # Calculate customer metrics
            cac = cost_data.get('cac', 0)
            clv = self._calculate_average_clv()
            
            # Calculate recurring revenue metrics
            mrr = self._calculate_monthly_recurring_revenue()
            churn_impact = self._calculate_churn_impact_on_revenue()
            
            # Calculate ROI
            total_investment = cost_data.get('marketing', 0) + cost_data.get('infrastructure', 0)
            roi = (net_profit / max(total_investment, 1)) * 100
            
            metrics = ProfitabilityMetrics(
                period=f"{period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}",
                total_revenue=total_revenue,
                total_costs=total_costs,
                gross_profit=gross_profit,
                operating_profit=operating_profit,
                net_profit=net_profit,
                gross_margin_percent=gross_margin_percent,
                operating_margin_percent=operating_margin_percent,
                net_margin_percent=net_margin_percent,
                return_on_investment=roi,
                customer_acquisition_cost=cac,
                customer_lifetime_value=clv,
                monthly_recurring_revenue=mrr,
                churn_impact_on_revenue=churn_impact
            )
            
            logger.info(f"Calculated profitability metrics for period {period_start} to {period_end}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate profitability metrics: {e}")
            raise

    def generate_cash_flow_analysis(self, months_back: int = 12) -> Dict[str, Any]:
        """Generate cash flow analysis and projections"""
        try:
            # Get historical cash flow data
            cash_flows = []
            start_date = datetime.now() - timedelta(days=30 * months_back)
            
            for i in range(months_back):
                month_start = start_date + timedelta(days=30 * i)
                month_end = month_start + timedelta(days=30)
                
                # Simulate cash flow components
                operating_cash_flow = np.random.uniform(50000, 150000)
                investing_cash_flow = np.random.uniform(-30000, 10000)
                financing_cash_flow = np.random.uniform(-20000, 50000)
                
                net_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow
                
                cash_flows.append({
                    "period": month_start.strftime("%Y-%m"),
                    "operating_cash_flow": operating_cash_flow,
                    "investing_cash_flow": investing_cash_flow,
                    "financing_cash_flow": financing_cash_flow,
                    "net_cash_flow": net_cash_flow,
                    "cumulative_cash_flow": sum([cf["net_cash_flow"] for cf in cash_flows]) + net_cash_flow
                })
            
            # Calculate cash flow metrics
            total_operating_cash = sum([cf["operating_cash_flow"] for cf in cash_flows])
            total_net_cash = sum([cf["net_cash_flow"] for cf in cash_flows])
            avg_monthly_cash_flow = total_net_cash / months_back
            
            # Cash flow ratios
            positive_cash_flow_months = len([cf for cf in cash_flows if cf["net_cash_flow"] > 0])
            cash_flow_stability = (positive_cash_flow_months / months_back) * 100
            
            # Forecast next 3 months
            forecast_months = []
            for i in range(3):
                # Simple trend-based forecast
                recent_trend = np.mean([cf["net_cash_flow"] for cf in cash_flows[-3:]])
                forecasted_cash_flow = recent_trend * (1 + np.random.uniform(-0.1, 0.2))
                
                forecast_month = datetime.now() + timedelta(days=30 * (i + 1))
                forecast_months.append({
                    "period": forecast_month.strftime("%Y-%m"),
                    "forecasted_net_cash_flow": forecasted_cash_flow,
                    "confidence": "medium"
                })
            
            return {
                "analysis_period": f"{months_back} months",
                "historical_cash_flows": cash_flows,
                "summary_metrics": {
                    "total_operating_cash_flow": total_operating_cash,
                    "total_net_cash_flow": total_net_cash,
                    "avg_monthly_cash_flow": avg_monthly_cash_flow,
                    "cash_flow_stability_percent": cash_flow_stability,
                    "current_cash_position": cash_flows[-1]["cumulative_cash_flow"] if cash_flows else 0
                },
                "forecast": {
                    "next_3_months": forecast_months,
                    "assumptions": [
                        "Historical trends continue",
                        "No major capital expenditures",
                        "Stable customer collection patterns"
                    ]
                },
                "insights": self._generate_cash_flow_insights(cash_flows, avg_monthly_cash_flow),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate cash flow analysis: {e}")
            raise

    # Helper methods
    def _get_revenue_data(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Get revenue data for period"""
        # Get actual revenue from customers
        query = text("""
            SELECT SUM(total_spent) as total_revenue
            FROM customers 
            WHERE created_at BETWEEN :start_date AND :end_date
        """)
        
        result = self.db.execute(query, {"start_date": start_date, "end_date": end_date}).fetchone()
        base_revenue = result.total_revenue if result.total_revenue else 0
        
        # Simulate revenue breakdown
        return {
            "subscription_revenue": base_revenue * 0.6,
            "one_time_revenue": base_revenue * 0.25,
            "upsell_revenue": base_revenue * 0.10,
            "cross_sell_revenue": base_revenue * 0.05
        }

    def _get_cost_data(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Get cost data for period"""
        revenue_data = self._get_revenue_data(start_date, end_date)
        total_revenue = sum(revenue_data.values())
        
        # Estimate costs as percentages of revenue
        return {
            "cogs": total_revenue * 0.35,
            "opex": total_revenue * 0.25,
            "marketing": total_revenue * 0.15,
            "cac": total_revenue * 0.10,
            "support": total_revenue * 0.08,
            "infrastructure": total_revenue * 0.05,
            "taxes": total_revenue * 0.02
        }

    def _get_historical_financial_data(self, data_type: str) -> List[Dict[str, Any]]:
        """Get historical financial data for forecasting"""
        historical_data = []
        
        # Generate 18 months of historical data
        for i in range(18):
            date = datetime.now() - timedelta(days=30 * (18 - i))
            
            # Simulate trend with seasonality and noise
            base_value = 100000
            trend = i * 2000  # Growth trend
            seasonal = 10000 * np.sin(2 * np.pi * i / 12)  # Seasonal pattern
            noise = np.random.normal(0, 5000)  # Random variation
            
            value = base_value + trend + seasonal + noise
            
            historical_data.append({
                "date": date,
                "value": max(0, value)  # Ensure non-negative
            })
        
        return historical_data

    def _estimate_customer_acquisition_cost(self, customer: Dict[str, Any]) -> float:
        """Estimate customer acquisition cost"""
        # Simplified CAC estimation based on customer characteristics
        base_cac = 150
        
        # Adjust based on customer value
        if customer['total_spent'] > 1000:
            return base_cac * 1.5  # Higher CAC for high-value customers
        elif customer['total_spent'] > 500:
            return base_cac * 1.2
        else:
            return base_cac

    def _estimate_support_costs(self, customer: Dict[str, Any]) -> float:
        """Estimate customer support costs"""
        # Base support cost per customer
        base_cost = 25
        
        # Adjust based on customer age and value
        customer_age_months = max(1, customer['customer_age_days'] / 30)
        monthly_cost = base_cost / 12
        
        return monthly_cost * customer_age_months

    def _estimate_customer_lifetime(self, customer: Dict[str, Any]) -> int:
        """Estimate customer lifetime in months"""
        # Simplified lifetime estimation
        if customer['total_spent'] > 1000:
            return 36  # 3 years for high-value customers
        elif customer['total_spent'] > 500:
            return 24  # 2 years for medium-value customers
        else:
            return 12  # 1 year for low-value customers

    def _calculate_retention_impact(self, customer: Dict[str, Any]) -> float:
        """Calculate impact of customer retention on revenue"""
        monthly_revenue = customer['total_spent'] / max(1, customer['customer_age_days'] / 30)
        estimated_lifetime = self._estimate_customer_lifetime(customer)
        
        return monthly_revenue * estimated_lifetime * 0.1  # 10% retention impact

    def _calculate_average_clv(self) -> float:
        """Calculate average customer lifetime value"""
        query = text("""
            SELECT AVG(total_spent) as avg_spent
            FROM customers 
            WHERE total_spent > 0
        """)
        
        result = self.db.execute(query).fetchone()
        avg_spent = result.avg_spent if result.avg_spent else 0
        
        # Estimate CLV as 2.5x current spending
        return avg_spent * 2.5

    def _calculate_monthly_recurring_revenue(self) -> float:
        """Calculate monthly recurring revenue"""
        # Simplified MRR calculation
        query = text("""
            SELECT COUNT(*) as customer_count, AVG(total_spent) as avg_spent
            FROM customers 
            WHERE total_spent > 0
        """)
        
        result = self.db.execute(query).fetchone()
        if result.customer_count and result.avg_spent:
            # Assume 70% of revenue is recurring
            monthly_revenue = (result.customer_count * result.avg_spent * 0.7) / 12
            return monthly_revenue
        
        return 0

    def _calculate_churn_impact_on_revenue(self) -> float:
        """Calculate revenue impact of customer churn"""
        # Simplified churn impact calculation
        mrr = self._calculate_monthly_recurring_revenue()
        estimated_churn_rate = 0.05  # 5% monthly churn
        
        return mrr * estimated_churn_rate

    def _get_component_description(self, component_id: str, value: float, impact_factor: float) -> str:
        """Generate description for waterfall components"""
        descriptions = {
            "starting_revenue": "Revenue at the beginning of the period",
            "new_customer_revenue": f"Revenue from {abs(impact_factor)*100:.0f}% new customer acquisitions",
            "expansion_revenue": f"Revenue growth from existing customers ({abs(impact_factor)*100:.0f}%)",
            "upsell_revenue": f"Additional revenue from product upsells ({abs(impact_factor)*100:.0f}%)",
            "cross_sell_revenue": f"Revenue from cross-selling initiatives ({abs(impact_factor)*100:.0f}%)",
            "churn_impact": f"Revenue loss due to customer churn ({abs(impact_factor)*100:.0f}%)",
            "downgrade_impact": f"Revenue reduction from plan downgrades ({abs(impact_factor)*100:.0f}%)",
            "price_changes": f"Impact of pricing adjustments ({abs(impact_factor)*100:.0f}%)",
            "seasonal_adjustment": f"Seasonal variation in revenue ({abs(impact_factor)*100:.0f}%)",
            "ending_revenue": "Total revenue at the end of the period"
        }
        
        return descriptions.get(component_id, f"Component impact: {impact_factor*100:.1f}%")

    def _generate_cash_flow_insights(self, cash_flows: List[Dict[str, Any]], 
                                   avg_monthly_cash_flow: float) -> List[str]:
        """Generate insights from cash flow analysis"""
        insights = []
        
        if avg_monthly_cash_flow > 0:
            insights.append(f"Positive average monthly cash flow of ${avg_monthly_cash_flow:,.0f}")
        else:
            insights.append(f"Negative average monthly cash flow of ${avg_monthly_cash_flow:,.0f} requires attention")
        
        # Analyze cash flow volatility
        cash_flow_values = [cf["net_cash_flow"] for cf in cash_flows]
        volatility = np.std(cash_flow_values)
        
        if volatility > 50000:
            insights.append("High cash flow volatility indicates seasonal or operational variability")
        else:
            insights.append("Stable cash flow pattern supports predictable operations")
        
        # Analyze trends
        recent_flows = cash_flow_values[-3:]
        earlier_flows = cash_flow_values[-6:-3]
        
        recent_avg = np.mean(recent_flows)
        earlier_avg = np.mean(earlier_flows)
        
        if recent_avg > earlier_avg * 1.1:
            insights.append("Cash flow trend is improving in recent months")
        elif recent_avg < earlier_avg * 0.9:
            insights.append("Cash flow trend is declining - review operations")
        else:
            insights.append("Cash flow trend is stable")
        
        return insights