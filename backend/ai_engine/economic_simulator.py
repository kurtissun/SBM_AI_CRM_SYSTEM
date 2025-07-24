import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass
from enum import Enum
import math

from .campaign_intelligence import CampaignIntelligenceEngine
from .adaptive_clustering import AdaptiveClusteringEngine
from ..core.config import settings

logger = logging.getLogger(__name__)

class MarketCondition(Enum):
    RECESSION = "recession"
    NORMAL = "normal"
    GROWTH = "growth"
    BOOM = "boom"

class CompetitorResponse(Enum):
    PASSIVE = "passive"
    DEFENSIVE = "defensive"
    AGGRESSIVE = "aggressive"

@dataclass
class EconomicFactors:
    gdp_growth_rate: float = 0.03
    inflation_rate: float = 0.02
    unemployment_rate: float = 0.05
    consumer_confidence: float = 0.75
    disposable_income_change: float = 0.02
    market_saturation: float = 0.6

@dataclass
class SimulationScenario:
    scenario_name: str
    probability: float
    roi_multiplier: float
    revenue_impact: float
    market_share_change: float
    customer_acquisition_cost: float
    description: str

class EconomicImpactSimulator:
    def __init__(self):
        self.campaign_engine = CampaignIntelligenceEngine()
        self.clustering_engine = AdaptiveClusteringEngine()
        
        # Economic modeling parameters
        self.market_elasticity = -0.8  # Price elasticity
        self.competition_factor = 0.3
        self.seasonality_weights = self._initialize_seasonality()
        self.economic_history = []
        
        # Market intelligence data
        self.market_data = self._load_market_intelligence()
        
    def _initialize_seasonality(self) -> Dict[int, float]:
        return {
            1: 1.1,   # January - New Year promotions
            2: 1.3,   # February - Chinese New Year
            3: 0.9,   # March - Post-holiday dip
            4: 1.0,   # April - Spring shopping
            5: 1.1,   # May - Labor Day holiday
            6: 1.2,   # June - Summer start, 618 shopping
            7: 0.95,  # July - Summer lull
            8: 0.9,   # August - Back to school prep
            9: 1.0,   # September - Back to school
            10: 1.1,  # October - National Day holiday
            11: 1.4,  # November - Singles Day
            12: 1.3   # December - Year-end shopping
        }
    
    def _load_market_intelligence(self) -> Dict:
        return {
            "mall_category": "premium_lifestyle",
            "market_size_rmb": 50_000_000,  # 50M RMB annual market
            "competitors": 3,
            "market_growth_rate": 0.08,
            "customer_base": 50000,
            "average_transaction": 350,
            "visit_frequency_monthly": 2.1
        }
    
    def simulate_campaign_impact(self, campaign_params: Dict, 
                                economic_scenario: str = "normal",
                                time_horizon_days: int = 30) -> Dict[str, Any]:
        
        logger.info(f"Simulating campaign impact for {time_horizon_days} days")
        
        # Get baseline prediction from campaign intelligence
        baseline_prediction = self.campaign_engine.predict_campaign_roi(campaign_params)
        
        # Apply economic factors
        economic_factors = self._get_economic_factors(economic_scenario)
        
        # Generate multiple scenarios
        scenarios = self._generate_impact_scenarios(
            campaign_params, baseline_prediction, economic_factors, time_horizon_days
        )
        
        # Calculate market dynamics
        market_impact = self._calculate_market_impact(campaign_params, economic_factors)
        
        # Competitor response simulation
        competitor_scenarios = self._simulate_competitor_responses(campaign_params)
        
        # Risk analysis
        risk_assessment = self._assess_campaign_risks(campaign_params, economic_factors)
        
        simulation_result = {
            "simulation_id": f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "campaign_params": campaign_params,
            "baseline_prediction": baseline_prediction,
            "economic_scenario": economic_scenario,
            "time_horizon_days": time_horizon_days,
            "scenarios": scenarios,
            "market_impact": market_impact,
            "competitor_scenarios": competitor_scenarios,
            "risk_assessment": risk_assessment,
            "recommendations": self._generate_recommendations(scenarios, risk_assessment),
            "confidence_interval": self._calculate_confidence_interval(scenarios),
            "simulation_date": datetime.now().isoformat()
        }
        
        # Store simulation for future reference
        self.economic_history.append(simulation_result)
        
        return simulation_result
    
    def _get_economic_factors(self, scenario: str) -> EconomicFactors:
        scenarios_map = {
            "recession": EconomicFactors(
                gdp_growth_rate=-0.02,
                inflation_rate=0.01,
                unemployment_rate=0.08,
                consumer_confidence=0.45,
                disposable_income_change=-0.05,
                market_saturation=0.8
            ),
            "normal": EconomicFactors(),
            "growth": EconomicFactors(
                gdp_growth_rate=0.06,
                inflation_rate=0.025,
                unemployment_rate=0.03,
                consumer_confidence=0.85,
                disposable_income_change=0.04,
                market_saturation=0.5
            ),
            "boom": EconomicFactors(
                gdp_growth_rate=0.10,
                inflation_rate=0.03,
                unemployment_rate=0.02,
                consumer_confidence=0.95,
                disposable_income_change=0.08,
                market_saturation=0.4
            )
        }
        
        return scenarios_map.get(scenario, EconomicFactors())
    
    def _generate_impact_scenarios(self, campaign_params: Dict, 
                                  baseline_prediction: Dict,
                                  economic_factors: EconomicFactors,
                                  time_horizon: int) -> List[SimulationScenario]:
        
        base_roi = baseline_prediction.get("predicted_roi", 1.5)
        budget = campaign_params.get("budget", 10000)
        
        scenarios = []
        
        # Best case scenario (20% probability)
        best_case_multiplier = (
            1.0 + economic_factors.consumer_confidence * 0.3 +
            (1 - economic_factors.market_saturation) * 0.2 +
            self._get_seasonal_boost(campaign_params) * 0.15
        )
        
        scenarios.append(SimulationScenario(
            scenario_name="best_case",
            probability=0.20,
            roi_multiplier=best_case_multiplier,
            revenue_impact=budget * base_roi * best_case_multiplier,
            market_share_change=0.02,
            customer_acquisition_cost=budget * 0.15 / max(1, budget * 0.001),
            description="Optimal market conditions, high customer response"
        ))
        
        # Most likely scenario (50% probability)
        likely_multiplier = (
            1.0 + economic_factors.consumer_confidence * 0.1 -
            economic_factors.market_saturation * 0.1 +
            self._get_seasonal_boost(campaign_params) * 0.05
        )
        
        scenarios.append(SimulationScenario(
            scenario_name="most_likely",
            probability=0.50,
            roi_multiplier=likely_multiplier,
            revenue_impact=budget * base_roi * likely_multiplier,
            market_share_change=0.005,
            customer_acquisition_cost=budget * 0.25 / max(1, budget * 0.0008),
            description="Expected market response under current conditions"
        ))
        
        # Conservative scenario (25% probability)
        conservative_multiplier = (
            1.0 - (1 - economic_factors.consumer_confidence) * 0.2 -
            economic_factors.market_saturation * 0.15 +
            self._get_seasonal_boost(campaign_params) * 0.03
        )
        
        scenarios.append(SimulationScenario(
            scenario_name="conservative",
            probability=0.25,
            roi_multiplier=max(0.3, conservative_multiplier),
            revenue_impact=budget * base_roi * max(0.3, conservative_multiplier),
            market_share_change=-0.001,
            customer_acquisition_cost=budget * 0.35 / max(1, budget * 0.0005),
            description="Below-average response due to market challenges"
        ))
        
        # Worst case scenario (5% probability)
        worst_case_multiplier = max(0.1, (
            1.0 - (1 - economic_factors.consumer_confidence) * 0.4 -
            economic_factors.market_saturation * 0.3 -
            economic_factors.unemployment_rate * 0.5
        ))
        
        scenarios.append(SimulationScenario(
            scenario_name="worst_case",
            probability=0.05,
            roi_multiplier=worst_case_multiplier,
            revenue_impact=budget * base_roi * worst_case_multiplier,
            market_share_change=-0.01,
            customer_acquisition_cost=budget * 0.50 / max(1, budget * 0.0003),
            description="Poor market response, economic headwinds"
        ))
        
        return scenarios
    
    def _get_seasonal_boost(self, campaign_params: Dict) -> float:
        start_date = campaign_params.get("start_date")
        if isinstance(start_date, str):
            try:
                start_month = datetime.fromisoformat(start_date).month
            except:
                start_month = datetime.now().month
        else:
            start_month = datetime.now().month
        
        return (self.seasonality_weights.get(start_month, 1.0) - 1.0)
    
    def _calculate_market_impact(self, campaign_params: Dict, 
                               economic_factors: EconomicFactors) -> Dict[str, Any]:
        
        budget = campaign_params.get("budget", 10000)
        duration = campaign_params.get("duration_days", 14)
        
        # Market penetration calculation
        total_market_size = self.market_data["market_size_rmb"]
        budget_as_market_share = budget / total_market_size
        
        # Customer acquisition potential
        avg_transaction = self.market_data["average_transaction"]
        potential_new_customers = (budget * 0.3) / avg_transaction
        
        # Market share impact
        current_market_share = 0.12  # Assume 12% current market share
        market_share_lift = budget_as_market_share * economic_factors.consumer_confidence
        
        return {
            "potential_new_customers": int(potential_new_customers),
            "market_penetration_increase": budget_as_market_share * 100,
            "estimated_market_share_lift": market_share_lift * 100,
            "customer_lifetime_impact": potential_new_customers * avg_transaction * 12,  # Annual CLV
            "brand_awareness_lift": min(5.0, budget / 10000),  # 1% per 10k budget
            "competitive_pressure_increase": budget / 100000  # Pressure on competitors
        }
    
    def _simulate_competitor_responses(self, campaign_params: Dict) -> Dict[str, Any]:
        
        budget = campaign_params.get("budget", 10000)
        
        responses = {}
        
        # Passive response (60% probability)
        responses["passive"] = {
            "probability": 0.60,
            "description": "Competitors maintain current strategy",
            "roi_impact": 0.0,
            "market_share_impact": 0.0,
            "customer_acquisition_difficulty": 1.0
        }
        
        # Defensive response (30% probability)
        defensive_impact = min(0.15, budget / 100000)
        responses["defensive"] = {
            "probability": 0.30,
            "description": "Competitors increase their marketing spend by 10-20%",
            "roi_impact": -defensive_impact,
            "market_share_impact": -defensive_impact * 0.5,
            "customer_acquisition_difficulty": 1.2
        }
        
        # Aggressive response (10% probability)
        aggressive_impact = min(0.25, budget / 50000)
        responses["aggressive"] = {
            "probability": 0.10,
            "description": "Competitors launch counter-campaigns and price wars",
            "roi_impact": -aggressive_impact,
            "market_share_impact": -aggressive_impact * 0.8,
            "customer_acquisition_difficulty": 1.5
        }
        
        # Calculate expected impact
        expected_roi_impact = sum(
            response["probability"] * response["roi_impact"]
            for response in responses.values()
        )
        
        return {
            "response_scenarios": responses,
            "expected_roi_impact": expected_roi_impact,
            "recommendation": self._get_competitive_recommendation(expected_roi_impact)
        }
    
    def _assess_campaign_risks(self, campaign_params: Dict, 
                             economic_factors: EconomicFactors) -> Dict[str, Any]:
        
        risks = []
        risk_score = 0.0
        
        # Budget risk
        budget = campaign_params.get("budget", 10000)
        if budget > 50000:
            risks.append({
                "type": "budget_risk",
                "severity": "medium",
                "description": "High budget exposure increases financial risk",
                "mitigation": "Consider phased rollout or A/B testing"
            })
            risk_score += 0.2
        
        # Economic environment risk
        if economic_factors.consumer_confidence < 0.6:
            risks.append({
                "type": "economic_risk",
                "severity": "high",
                "description": "Low consumer confidence may reduce campaign effectiveness",
                "mitigation": "Focus on value propositions and essential products"
            })
            risk_score += 0.3
        
        # Market saturation risk
        if economic_factors.market_saturation > 0.7:
            risks.append({
                "type": "saturation_risk",
                "severity": "medium",
                "description": "High market saturation limits growth potential",
                "mitigation": "Target underserved segments or new product categories"
            })
            risk_score += 0.25
        
        # Seasonal risk
        seasonal_factor = self._get_seasonal_boost(campaign_params)
        if seasonal_factor < -0.1:
            risks.append({
                "type": "seasonal_risk",
                "severity": "low",
                "description": "Campaign timing during low-demand period",
                "mitigation": "Adjust messaging to create urgency or delay campaign"
            })
            risk_score += 0.1
        
        return {
            "overall_risk_score": min(1.0, risk_score),
            "risk_level": self._categorize_risk_level(risk_score),
            "identified_risks": risks,
            "risk_mitigation_plan": self._generate_risk_mitigation_plan(risks)
        }
    
    def _categorize_risk_level(self, risk_score: float) -> str:
        if risk_score < 0.3:
            return "low"
        elif risk_score < 0.6:
            return "medium"
        else:
            return "high"
    
    def _generate_risk_mitigation_plan(self, risks: List[Dict]) -> List[str]:
        mitigation_plan = []
        
        for risk in risks:
            mitigation_plan.append(f"{risk['type']}: {risk['mitigation']}")
        
        # Add general mitigation strategies
        mitigation_plan.extend([
            "Implement real-time campaign monitoring",
            "Establish clear KPIs and exit criteria",
            "Prepare contingency budget for optimization"
        ])
        
        return mitigation_plan
    
    def _generate_recommendations(self, scenarios: List[SimulationScenario],
                                risk_assessment: Dict) -> List[str]:
        
        recommendations = []
        
        # Calculate expected ROI
        expected_roi = sum(
            scenario.probability * scenario.roi_multiplier
            for scenario in scenarios
        )
        
        # ROI-based recommendations
        if expected_roi > 2.0:
            recommendations.append("🚀 High ROI potential - recommend full budget allocation")
        elif expected_roi > 1.5:
            recommendations.append("✅ Positive ROI expected - proceed with campaign")
        elif expected_roi > 1.0:
            recommendations.append("⚠️ Marginal ROI - consider optimization or reduced budget")
        else:
            recommendations.append("❌ Negative ROI risk - recommend campaign redesign")
        
        # Risk-based recommendations
        risk_level = risk_assessment["risk_level"]
        if risk_level == "high":
            recommendations.append("🔴 High risk detected - implement gradual rollout strategy")
        elif risk_level == "medium":
            recommendations.append("🟡 Moderate risk - establish monitoring checkpoints")
        
        # Scenario-specific recommendations
        best_case = next(s for s in scenarios if s.scenario_name == "best_case")
        worst_case = next(s for s in scenarios if s.scenario_name == "worst_case")
        
        roi_variance = best_case.roi_multiplier - worst_case.roi_multiplier
        if roi_variance > 1.0:
            recommendations.append("📊 High variance - consider A/B testing different approaches")
        
        # Timing recommendations
        current_month = datetime.now().month
        seasonal_factor = self.seasonality_weights.get(current_month, 1.0)
        
        if seasonal_factor > 1.2:
            recommendations.append("🎯 Optimal timing - strong seasonal demand expected")
        elif seasonal_factor < 0.95:
            recommendations.append("📅 Consider delaying campaign to more favorable period")
        
        return recommendations
    
    def _calculate_confidence_interval(self, scenarios: List[SimulationScenario]) -> Dict[str, float]:
        
        # Calculate weighted statistics
        weighted_roi = sum(s.probability * s.roi_multiplier for s in scenarios)
        weighted_variance = sum(
            s.probability * (s.roi_multiplier - weighted_roi) ** 2 
            for s in scenarios
        )
        std_dev = math.sqrt(weighted_variance)
        
        # 90% confidence interval
        confidence_level = 0.90
        z_score = 1.645  # 90% confidence
        
        margin_of_error = z_score * std_dev
        
        return {
            "confidence_level": confidence_level,
            "expected_roi": weighted_roi,
            "standard_deviation": std_dev,
            "lower_bound": weighted_roi - margin_of_error,
            "upper_bound": weighted_roi + margin_of_error,
            "margin_of_error": margin_of_error
        }
    
    def _get_competitive_recommendation(self, expected_roi_impact: float) -> str:
        if expected_roi_impact > -0.05:
            return "Low competitive threat - proceed as planned"
        elif expected_roi_impact > -0.15:
            return "Moderate competitive risk - monitor competitors closely"
        else:
            return "High competitive threat - consider defensive strategies"
    
    def simulate_budget_optimization(self, base_campaign: Dict, 
                                   budget_range: Tuple[float, float],
                                   budget_steps: int = 10) -> Dict[str, Any]:
        
        min_budget, max_budget = budget_range
        budget_increment = (max_budget - min_budget) / budget_steps
        
        optimization_results = []
        
        for i in range(budget_steps + 1):
            test_budget = min_budget + (i * budget_increment)
            test_campaign = base_campaign.copy()
            test_campaign["budget"] = test_budget
            
            simulation = self.simulate_campaign_impact(test_campaign)
            
            # Calculate key metrics
            expected_roi = sum(
                s.probability * s.roi_multiplier 
                for s in simulation["scenarios"]
            )
            
            expected_revenue = sum(
                s.probability * s.revenue_impact 
                for s in simulation["scenarios"]
            )
            
            optimization_results.append({
                "budget": test_budget,
                "expected_roi": expected_roi,
                "expected_revenue": expected_revenue,
                "expected_profit": expected_revenue - test_budget,
                "risk_score": simulation["risk_assessment"]["overall_risk_score"]
            })
        
        # Find optimal budget
        optimal_budget_result = max(optimization_results, key=lambda x: x["expected_profit"])
        
        return {
            "optimization_results": optimization_results,
            "optimal_budget": optimal_budget_result["budget"],
            "optimal_roi": optimal_budget_result["expected_roi"],
            "optimal_profit": optimal_budget_result["expected_profit"],
            "budget_efficiency_curve": self._calculate_efficiency_curve(optimization_results)
        }
    
    def _calculate_efficiency_curve(self, results: List[Dict]) -> List[Dict]:
        efficiency_curve = []
        
        for result in results:
            budget = result["budget"]
            profit = result["expected_profit"]
            
            efficiency = profit / budget if budget > 0 else 0
            
            efficiency_curve.append({
                "budget": budget,
                "efficiency": efficiency,
                "marginal_efficiency": efficiency  # Simplified - could calculate true marginal
            })
        
        return efficiency_curve
    
    def compare_campaign_scenarios(self, campaign_variants: List[Dict]) -> Dict[str, Any]:
        
        comparison_results = []
        
        for i, variant in enumerate(campaign_variants):
            simulation = self.simulate_campaign_impact(variant)
            
            expected_roi = sum(
                s.probability * s.roi_multiplier 
                for s in simulation["scenarios"]
            )
            
            comparison_results.append({
                "variant_id": i,
                "variant_name": variant.get("name", f"Variant {i+1}"),
                "expected_roi": expected_roi,
                "risk_score": simulation["risk_assessment"]["overall_risk_score"],
                "simulation": simulation
            })
        
        # Rank variants
        ranked_variants = sorted(comparison_results, key=lambda x: x["expected_roi"], reverse=True)
        
        return {
            "comparison_results": comparison_results,
            "recommended_variant": ranked_variants[0],
            "ranking": [v["variant_name"] for v in ranked_variants],
            "performance_spread": {
                "best_roi": ranked_variants[0]["expected_roi"],
                "worst_roi": ranked_variants[-1]["expected_roi"],
                "roi_range": ranked_variants[0]["expected_roi"] - ranked_variants[-1]["expected_roi"]
            }
        }
    
    def get_market_intelligence_summary(self) -> Dict[str, Any]:
        
        return {
            "market_overview": self.market_data,
            "current_economic_indicators": {
                "consumer_confidence": "normal",
                "market_growth": "steady",
                "competitive_intensity": "moderate"
            },
            "seasonal_outlook": {
                "current_month_factor": self.seasonality_weights.get(datetime.now().month, 1.0),
                "next_month_factor": self.seasonality_weights.get(
                    (datetime.now().month % 12) + 1, 1.0
                ),
                "peak_seasons": [month for month, factor in self.seasonality_weights.items() if factor > 1.2]
            },
            "simulation_history_summary": {
                "total_simulations": len(self.economic_history),
                "average_predicted_roi": np.mean([
                    sum(s.probability * s.roi_multiplier for s in sim["scenarios"])
                    for sim in self.economic_history
                ]) if self.economic_history else 0
            }
        }

economic_simulator = EconomicImpactSimulator()
