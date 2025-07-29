"""
Network Analytics API Endpoints
Social network and influence analysis
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import networkx as nx
import numpy as np

from ...core.database import get_db, Customer, Purchase
from ...core.security import get_current_user
from ...analytics.network_engine import NetworkAnalyticsEngine

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/social-network-analysis")
async def get_social_network_analysis(
    analysis_type: str = Query("comprehensive", regex="^(basic|comprehensive|advanced)$"),
    time_range: str = Query("90d", regex="^(30d|90d|180d|1y)$"),
    min_connection_strength: float = Query(0.3, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    🌐 **Social Network Analysis**
    
    Analyze customer social networks and influence patterns.
    """
    try:
        # Calculate time range
        time_mapping = {
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
            "180d": timedelta(days=180),
            "1y": timedelta(days=365)
        }
        
        start_date = datetime.now() - time_mapping[time_range]
        
        # Get customer and purchase data
        customers = db.query(Customer).filter(Customer.created_at >= start_date).all()
        purchases = db.query(Purchase).join(Customer).filter(Customer.created_at >= start_date).all()
        
        if not customers:
            return {"message": "No customer data available for network analysis"}
        
        # Initialize network analytics engine
        network_engine = NetworkAnalyticsEngine(db)
        
        # Build customer network based on purchase patterns and demographics
        network_graph = network_engine.build_customer_network(
            customers, purchases, min_connection_strength
        )
        
        network_analysis = {
            "network_metadata": {
                "analysis_type": analysis_type,
                "time_range": time_range,
                "total_nodes": len(customers),
                "network_connections": network_graph.number_of_edges(),
                "connection_threshold": min_connection_strength,
                "generated_at": datetime.now().isoformat()
            },
            "network_metrics": network_engine.calculate_network_metrics(network_graph),
            "influence_analysis": network_engine.analyze_customer_influence(network_graph, customers),
            "community_detection": network_engine.detect_communities(network_graph),
            "centrality_analysis": network_engine.calculate_centrality_measures(network_graph)
        }
        
        if analysis_type in ["comprehensive", "advanced"]:
            network_analysis["connection_patterns"] = network_engine.analyze_connection_patterns(
                network_graph, customers, purchases
            )
            network_analysis["influence_propagation"] = network_engine.model_influence_propagation(
                network_graph, customers
            )
            network_analysis["network_segmentation"] = network_engine.perform_network_segmentation(
                network_graph, customers
            )
        
        if analysis_type == "advanced":
            network_analysis["temporal_network_analysis"] = network_engine.analyze_temporal_networks(
                customers, purchases, time_range
            )
            network_analysis["influence_prediction"] = network_engine.predict_influence_spread(
                network_graph, customers
            )
            network_analysis["network_optimization"] = network_engine.suggest_network_optimizations(
                network_graph, customers
            )
        
        return network_analysis
        
    except Exception as e:
        logger.error(f"Social network analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Network analysis failed: {str(e)}")

@router.get("/influence-analysis")
async def get_influence_analysis(
    customer_id: Optional[str] = None,
    segment_id: Optional[int] = None,
    influence_metric: str = Query("comprehensive", regex="^(centrality|reach|engagement|comprehensive)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    📊 **Customer Influence Analysis**
    
    Analyze individual customer or segment influence within the network.
    """
    try:
        network_engine = NetworkAnalyticsEngine(db)
        
        # Get relevant customers
        if customer_id:
            customers = db.query(Customer).filter(Customer.customer_id == customer_id).all()
            if not customers:
                raise HTTPException(status_code=404, detail="Customer not found")
            analysis_scope = "individual"
            target_id = customer_id
            
        elif segment_id is not None:
            customers = db.query(Customer).filter(Customer.segment_id == segment_id).all()
            if not customers:
                raise HTTPException(status_code=404, detail="No customers found in segment")
            analysis_scope = "segment"
            target_id = segment_id
            
        else:
            customers = db.query(Customer).all()
            analysis_scope = "all_customers"
            target_id = "all"
        
        # Get purchase data for network building
        purchases = db.query(Purchase).filter(
            Purchase.customer_id.in_([c.customer_id for c in customers])
        ).all()
        
        # Build network and analyze influence
        network_graph = network_engine.build_customer_network(customers, purchases, 0.3)
        
        influence_analysis = {
            "analysis_metadata": {
                "analysis_scope": analysis_scope,
                "target_id": target_id,
                "influence_metric": influence_metric,
                "customers_analyzed": len(customers),
                "generated_at": datetime.now().isoformat()
            }
        }
        
        if customer_id:
            # Individual customer influence analysis
            influence_analysis["individual_influence"] = network_engine.analyze_individual_influence(
                network_graph, customer_id, customers, influence_metric
            )
            influence_analysis["influence_network"] = network_engine.get_customer_influence_network(
                network_graph, customer_id
            )
            influence_analysis["influence_potential"] = network_engine.calculate_influence_potential(
                network_graph, customer_id, customers
            )
            
        elif segment_id is not None:
            # Segment influence analysis
            influence_analysis["segment_influence"] = network_engine.analyze_segment_influence(
                network_graph, segment_id, customers, influence_metric
            )
            influence_analysis["top_influencers"] = network_engine.identify_segment_influencers(
                network_graph, segment_id, customers
            )
            influence_analysis["influence_distribution"] = network_engine.analyze_influence_distribution(
                network_graph, customers
            )
            
        else:
            # Overall influence analysis
            influence_analysis["overall_influence_metrics"] = network_engine.calculate_overall_influence_metrics(
                network_graph, customers
            )
            influence_analysis["top_influencers"] = network_engine.identify_top_influencers(
                network_graph, customers, limit=20
            )
            influence_analysis["influence_hierarchy"] = network_engine.build_influence_hierarchy(
                network_graph, customers
            )
        
        # Common analysis for all scopes
        influence_analysis["influence_insights"] = network_engine.generate_influence_insights(
            network_graph, customers, analysis_scope
        )
        influence_analysis["actionable_recommendations"] = network_engine.generate_influence_recommendations(
            network_graph, customers, analysis_scope, target_id
        )
        
        return influence_analysis
        
    except Exception as e:
        logger.error(f"Influence analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Influence analysis failed: {str(e)}")

@router.get("/community-analysis")
async def get_community_analysis(
    algorithm: str = Query("louvain", regex="^(louvain|leiden|girvan_newman|label_propagation)$"),
    min_community_size: int = Query(5, ge=2),
    resolution: float = Query(1.0, ge=0.1, le=2.0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    👥 **Community Detection Analysis**
    
    Detect and analyze customer communities within the network.
    """
    try:
        network_engine = NetworkAnalyticsEngine(db)
        
        # Get all customers and their purchase data
        customers = db.query(Customer).all()
        purchases = db.query(Purchase).all()
        
        if not customers:
            return {"message": "No customer data available for community analysis"}
        
        # Build network
        network_graph = network_engine.build_customer_network(customers, purchases, 0.3)
        
        # Detect communities using specified algorithm
        communities = network_engine.detect_communities_advanced(
            network_graph, algorithm, min_community_size, resolution
        )
        
        community_analysis = {
            "analysis_metadata": {
                "algorithm": algorithm,
                "min_community_size": min_community_size,
                "resolution": resolution,
                "total_customers": len(customers),
                "communities_detected": len(communities),
                "generated_at": datetime.now().isoformat()
            },
            "community_overview": network_engine.analyze_community_overview(
                communities, customers
            ),
            "community_details": network_engine.analyze_community_details(
                communities, customers, purchases
            ),
            "community_characteristics": network_engine.analyze_community_characteristics(
                communities, customers, network_graph
            ),
            "inter_community_analysis": network_engine.analyze_inter_community_connections(
                communities, network_graph
            ),
            "community_evolution": network_engine.predict_community_evolution(
                communities, customers, purchases
            ),
            "business_insights": network_engine.generate_community_business_insights(
                communities, customers, purchases
            )
        }
        
        return community_analysis
        
    except Exception as e:
        logger.error(f"Community analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Community analysis failed: {str(e)}")

@router.get("/network-visualization")
async def get_network_visualization(
    layout: str = Query("spring", regex="^(spring|circular|kamada_kawai|fruchterman_reingold)$"),
    node_size_metric: str = Query("influence", regex="^(influence|purchases|connections|rating)$"),
    edge_weight_metric: str = Query("similarity", regex="^(similarity|transaction_frequency|shared_interests)$"),
    max_nodes: int = Query(100, ge=10, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    🎨 **Network Visualization Data**
    
    Generate data for network visualization with customizable layouts and metrics.
    """
    try:
        network_engine = NetworkAnalyticsEngine(db)
        
        # Get customer data (limited for visualization performance)
        customers = db.query(Customer).limit(max_nodes).all()
        purchases = db.query(Purchase).filter(
            Purchase.customer_id.in_([c.customer_id for c in customers])
        ).all()
        
        if not customers:
            return {"message": "No customer data available for visualization"}
        
        # Build network
        network_graph = network_engine.build_customer_network(customers, purchases, 0.3)
        
        # Generate visualization data
        visualization_data = {
            "visualization_metadata": {
                "layout": layout,
                "node_size_metric": node_size_metric,
                "edge_weight_metric": edge_weight_metric,
                "total_nodes": len(customers),
                "total_edges": network_graph.number_of_edges(),
                "generated_at": datetime.now().isoformat()
            },
            "nodes": network_engine.generate_node_data(
                network_graph, customers, node_size_metric
            ),
            "edges": network_engine.generate_edge_data(
                network_graph, edge_weight_metric
            ),
            "layout_positions": network_engine.calculate_layout_positions(
                network_graph, layout
            ),
            "visualization_config": network_engine.get_visualization_config(
                network_graph, customers, layout
            ),
            "color_coding": network_engine.generate_color_coding(
                network_graph, customers
            ),
            "interactive_features": network_engine.get_interactive_features(
                network_graph, customers
            )
        }
        
        return visualization_data
        
    except Exception as e:
        logger.error(f"Network visualization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Network visualization failed: {str(e)}")

@router.post("/influence-simulation")
async def run_influence_simulation(
    simulation_config: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    🎯 **Influence Propagation Simulation**
    
    Simulate how influence spreads through the customer network.
    """
    try:
        network_engine = NetworkAnalyticsEngine(db)
        
        # Validate simulation configuration
        required_fields = ["seed_customers", "influence_model", "simulation_steps"]
        for field in required_fields:
            if field not in simulation_config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Get network data
        customers = db.query(Customer).all()
        purchases = db.query(Purchase).all()
        
        if not customers:
            return {"message": "No customer data available for simulation"}
        
        # Build network
        network_graph = network_engine.build_customer_network(customers, purchases, 0.3)
        
        # Run influence simulation
        simulation_results = network_engine.run_influence_simulation(
            network_graph, customers, simulation_config
        )
        
        return {
            "simulation_metadata": {
                "simulation_id": f"sim_{datetime.now().timestamp()}",
                "seed_customers": simulation_config["seed_customers"],
                "influence_model": simulation_config["influence_model"],
                "simulation_steps": simulation_config["simulation_steps"],
                "network_size": len(customers),
                "generated_at": datetime.now().isoformat()
            },
            "simulation_results": simulation_results,
            "influence_metrics": network_engine.calculate_simulation_metrics(
                simulation_results, network_graph
            ),
            "visualization_data": network_engine.generate_simulation_visualization(
                simulation_results, network_graph, customers
            ),
            "business_implications": network_engine.interpret_simulation_results(
                simulation_results, customers, simulation_config
            )
        }
        
    except Exception as e:
        logger.error(f"Influence simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Influence simulation failed: {str(e)}")

@router.get("/connection-recommendations")
async def get_connection_recommendations(
    customer_id: str,
    recommendation_type: str = Query("similar_customers", regex="^(similar_customers|potential_influencers|community_bridges|high_value_connections)$"),
    max_recommendations: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    🤝 **Connection Recommendations**
    
    Recommend potential connections for customers based on network analysis.
    """
    try:
        # Verify customer exists
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        network_engine = NetworkAnalyticsEngine(db)
        
        # Get network data
        customers = db.query(Customer).all()
        purchases = db.query(Purchase).all()
        
        # Build network
        network_graph = network_engine.build_customer_network(customers, purchases, 0.3)
        
        # Generate recommendations based on type
        recommendations = network_engine.generate_connection_recommendations(
            network_graph, customer_id, customers, recommendation_type, max_recommendations
        )
        
        return {
            "recommendation_metadata": {
                "target_customer": customer_id,
                "recommendation_type": recommendation_type,
                "max_recommendations": max_recommendations,
                "recommendations_found": len(recommendations),
                "generated_at": datetime.now().isoformat()
            },
            "recommendations": recommendations,
            "recommendation_rationale": network_engine.explain_recommendation_rationale(
                network_graph, customer_id, recommendations, recommendation_type
            ),
            "expected_outcomes": network_engine.predict_connection_outcomes(
                network_graph, customer_id, recommendations
            ),
            "implementation_suggestions": network_engine.suggest_connection_strategies(
                customer_id, recommendations, recommendation_type
            )
        }
        
    except Exception as e:
        logger.error(f"Connection recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=f"Connection recommendations failed: {str(e)}")

@router.get("/network-health")
async def get_network_health(
    health_metrics: str = Query("comprehensive", regex="^(basic|comprehensive|detailed)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    ❤️ **Network Health Analysis**
    
    Analyze the overall health and resilience of the customer network.
    """
    try:
        network_engine = NetworkAnalyticsEngine(db)
        
        # Get network data
        customers = db.query(Customer).all()
        purchases = db.query(Purchase).all()
        
        if not customers:
            return {"message": "No customer data available for network health analysis"}
        
        # Build network
        network_graph = network_engine.build_customer_network(customers, purchases, 0.3)
        
        # Analyze network health
        health_analysis = {
            "health_metadata": {
                "health_metrics": health_metrics,
                "network_size": len(customers),
                "network_density": network_engine.calculate_network_density(network_graph),
                "analysis_date": datetime.now().isoformat()
            },
            "connectivity_health": network_engine.analyze_connectivity_health(network_graph),
            "robustness_analysis": network_engine.analyze_network_robustness(network_graph),
            "influence_distribution": network_engine.analyze_influence_distribution_health(
                network_graph, customers
            )
        }
        
        if health_metrics in ["comprehensive", "detailed"]:
            health_analysis["structural_health"] = network_engine.analyze_structural_health(
                network_graph
            )
            health_analysis["community_health"] = network_engine.analyze_community_health(
                network_graph, customers
            )
            health_analysis["growth_potential"] = network_engine.assess_network_growth_potential(
                network_graph, customers, purchases
            )
        
        if health_metrics == "detailed":
            health_analysis["vulnerability_analysis"] = network_engine.analyze_network_vulnerabilities(
                network_graph, customers
            )
            health_analysis["optimization_opportunities"] = network_engine.identify_optimization_opportunities(
                network_graph, customers
            )
            health_analysis["health_trends"] = network_engine.analyze_health_trends(
                network_graph, customers, purchases
            )
        
        # Overall health score and recommendations
        health_analysis["overall_health_score"] = network_engine.calculate_overall_health_score(
            health_analysis
        )
        health_analysis["health_recommendations"] = network_engine.generate_health_recommendations(
            health_analysis, network_graph, customers
        )
        
        return health_analysis
        
    except Exception as e:
        logger.error(f"Network health analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Network health analysis failed: {str(e)}")

@router.get("/temporal-network-analysis")
async def get_temporal_network_analysis(
    time_window: str = Query("monthly", regex="^(weekly|monthly|quarterly)$"),
    analysis_period: str = Query("1y", regex="^(6m|1y|2y)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    ⏰ **Temporal Network Analysis**
    
    Analyze how the customer network evolves over time.
    """
    try:
        network_engine = NetworkAnalyticsEngine(db)
        
        # Calculate analysis period
        period_mapping = {"6m": 180, "1y": 365, "2y": 730}
        start_date = datetime.now() - timedelta(days=period_mapping[analysis_period])
        
        # Get temporal data
        customers = db.query(Customer).filter(Customer.created_at >= start_date).all()
        purchases = db.query(Purchase).join(Customer).filter(
            Customer.created_at >= start_date
        ).all()
        
        if not customers:
            return {"message": "Insufficient temporal data for analysis"}
        
        # Perform temporal analysis
        temporal_analysis = network_engine.analyze_temporal_networks(
            customers, purchases, time_window, analysis_period
        )
        
        return {
            "temporal_metadata": {
                "time_window": time_window,
                "analysis_period": analysis_period,
                "start_date": start_date.isoformat(),
                "end_date": datetime.now().isoformat(),
                "data_points": len(customers),
                "generated_at": datetime.now().isoformat()
            },
            "temporal_analysis": temporal_analysis,
            "network_evolution": network_engine.track_network_evolution(
                customers, purchases, time_window
            ),
            "influence_evolution": network_engine.track_influence_evolution(
                customers, purchases, time_window
            ),
            "community_evolution": network_engine.track_community_evolution(
                customers, purchases, time_window
            ),
            "predictive_insights": network_engine.predict_network_future(
                temporal_analysis, customers
            )
        }
        
    except Exception as e:
        logger.error(f"Temporal network analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Temporal network analysis failed: {str(e)}")