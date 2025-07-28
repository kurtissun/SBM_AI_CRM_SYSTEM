"""
Network Analysis & Social Intelligence Engine
Customer referral networks, influence mapping, and social connection analysis
"""
import networkx as nx
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import text
from collections import defaultdict, Counter
import uuid
import json
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import community.community_louvain as community

logger = logging.getLogger(__name__)

class NodeType(Enum):
    CUSTOMER = "customer"
    INFLUENCER = "influencer"
    BRAND_ADVOCATE = "brand_advocate"
    CHURNED_CUSTOMER = "churned_customer"
    HIGH_VALUE_CUSTOMER = "high_value_customer"
    NEW_CUSTOMER = "new_customer"

class EdgeType(Enum):
    REFERRAL = "referral"
    SOCIAL_CONNECTION = "social_connection"
    TRANSACTION = "transaction"
    INTERACTION = "interaction"
    INFLUENCE = "influence"
    COLLABORATION = "collaboration"

class CentralityType(Enum):
    DEGREE = "degree"
    BETWEENNESS = "betweenness"
    CLOSENESS = "closeness"
    EIGENVECTOR = "eigenvector"
    PAGERANK = "pagerank"

@dataclass
class NetworkNode:
    node_id: str
    node_type: NodeType
    customer_id: str
    attributes: Dict[str, Any]
    centrality_scores: Dict[str, float]
    community_id: Optional[str]
    influence_score: float
    connection_count: int
    referral_count: int
    revenue_generated: float
    engagement_level: str

@dataclass
class NetworkEdge:
    edge_id: str
    source_node: str
    target_node: str
    edge_type: EdgeType
    weight: float
    created_at: datetime
    attributes: Dict[str, Any]
    interaction_frequency: int
    relationship_strength: float

@dataclass
class NetworkCommunity:
    community_id: str
    name: str
    member_count: int
    total_value: float
    avg_influence_score: float
    community_type: str
    key_influencers: List[str]
    growth_rate: float
    engagement_metrics: Dict[str, float]
    characteristics: Dict[str, Any]

@dataclass
class InfluenceAnalysis:
    influencer_id: str
    influence_score: float
    reach: int
    engagement_rate: float
    conversion_impact: float
    revenue_impact: float
    network_position: str
    influence_topics: List[str]
    recommended_actions: List[str]
    trend_direction: str

@dataclass
class ReferralAnalysis:
    analysis_id: str
    total_referrals: int
    successful_conversions: int
    conversion_rate: float
    total_referral_value: float
    avg_referral_value: float
    top_referrers: List[Dict[str, Any]]
    referral_channels: Dict[str, int]
    viral_coefficient: float
    network_growth_rate: float

class NetworkAnalyticsEngine:
    def __init__(self, db: Session):
        self.db = db
        self.network = nx.Graph()
        self.directed_network = nx.DiGraph()
        self.communities = {}
        self.centrality_cache = {}
        
    def build_customer_network(self, include_inactive: bool = False) -> Dict[str, Any]:
        """Build customer network graph from CRM data"""
        try:
            # Clear existing network
            self.network.clear()
            self.directed_network.clear()
            
            # Get customer data
            customers = self._get_customer_data(include_inactive)
            referrals = self._get_referral_data()
            interactions = self._get_interaction_data()
            
            # Add nodes
            for customer in customers:
                node_type = self._determine_node_type(customer)
                attributes = self._extract_customer_attributes(customer)
                
                self.network.add_node(
                    customer['customer_id'],
                    node_type=node_type.value,
                    **attributes
                )
                
                self.directed_network.add_node(
                    customer['customer_id'],
                    node_type=node_type.value,
                    **attributes
                )
            
            # Add referral edges
            for referral in referrals:
                if referral['referrer_id'] and referral['referred_id']:
                    weight = self._calculate_referral_weight(referral)
                    
                    self.network.add_edge(
                        referral['referrer_id'],
                        referral['referred_id'],
                        edge_type=EdgeType.REFERRAL.value,
                        weight=weight,
                        created_at=referral['created_at'],
                        value=referral.get('referral_value', 0)
                    )
                    
                    self.directed_network.add_edge(
                        referral['referrer_id'],
                        referral['referred_id'],
                        edge_type=EdgeType.REFERRAL.value,
                        weight=weight,
                        created_at=referral['created_at'],
                        value=referral.get('referral_value', 0)
                    )
            
            # Add interaction edges
            for interaction in interactions:
                if interaction['customer_a'] and interaction['customer_b']:
                    weight = self._calculate_interaction_weight(interaction)
                    
                    self.network.add_edge(
                        interaction['customer_a'],
                        interaction['customer_b'],
                        edge_type=EdgeType.INTERACTION.value,
                        weight=weight,
                        frequency=interaction.get('frequency', 1)
                    )
            
            # Calculate network metrics
            network_metrics = self._calculate_network_metrics()
            
            logger.info(f"Network built: {self.network.number_of_nodes()} nodes, {self.network.number_of_edges()} edges")
            
            return {
                "nodes": self.network.number_of_nodes(),
                "edges": self.network.number_of_edges(),
                "metrics": network_metrics,
                "build_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to build customer network: {e}")
            raise

    def analyze_customer_influence(self, customer_id: str) -> InfluenceAnalysis:
        """Analyze a customer's influence within the network"""
        try:
            if customer_id not in self.network:
                raise ValueError(f"Customer {customer_id} not found in network")
            
            # Calculate centrality scores
            centrality_scores = self._calculate_node_centrality(customer_id)
            
            # Calculate influence metrics
            direct_connections = len(list(self.network.neighbors(customer_id)))
            
            # Calculate reach (2-hop neighborhood)
            reach = len(set().union(*[list(self.network.neighbors(neighbor)) 
                                    for neighbor in self.network.neighbors(customer_id)]))
            
            # Referral analysis
            referrals_made = len([edge for edge in self.directed_network.out_edges(customer_id, data=True)
                                if edge[2].get('edge_type') == EdgeType.REFERRAL.value])
            
            referral_value = sum([edge[2].get('value', 0) 
                                for edge in self.directed_network.out_edges(customer_id, data=True)
                                if edge[2].get('edge_type') == EdgeType.REFERRAL.value])
            
            # Calculate influence score
            pagerank_score = nx.pagerank(self.network).get(customer_id, 0)
            influence_score = (
                centrality_scores.get('pagerank', 0) * 0.4 +
                centrality_scores.get('betweenness', 0) * 0.3 +
                (direct_connections / max(self.network.number_of_nodes(), 1)) * 0.2 +
                (referrals_made / max(10, 1)) * 0.1
            ) * 100
            
            # Determine network position
            if centrality_scores.get('betweenness', 0) > 0.1:
                network_position = "bridge"
            elif centrality_scores.get('degree', 0) > 0.1:
                network_position = "hub"
            elif influence_score > 70:
                network_position = "influencer"
            else:
                network_position = "regular"
            
            # Generate recommendations
            recommendations = self._generate_influence_recommendations(
                influence_score, network_position, referrals_made
            )
            
            return InfluenceAnalysis(
                influencer_id=customer_id,
                influence_score=influence_score,
                reach=reach,
                engagement_rate=np.random.uniform(0.1, 0.8),  # Simplified
                conversion_impact=referrals_made * 0.15,
                revenue_impact=referral_value,
                network_position=network_position,
                influence_topics=["product_advocacy", "customer_experience"],
                recommended_actions=recommendations,
                trend_direction="increasing" if influence_score > 50 else "stable"
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze customer influence: {e}")
            raise

    def detect_communities(self, algorithm: str = "louvain") -> List[NetworkCommunity]:
        """Detect communities in the customer network"""
        try:
            if algorithm == "louvain":
                communities = community.best_partition(self.network)
            else:
                # Fallback to connected components
                communities = {}
                for i, component in enumerate(nx.connected_components(self.network)):
                    for node in component:
                        communities[node] = i
            
            # Analyze each community
            community_analysis = []
            community_stats = defaultdict(list)
            
            # Group nodes by community
            for node, comm_id in communities.items():
                community_stats[comm_id].append(node)
            
            for comm_id, members in community_stats.items():
                if len(members) < 3:  # Skip very small communities
                    continue
                
                # Calculate community metrics
                subgraph = self.network.subgraph(members)
                
                # Get member attributes
                member_values = []
                member_influences = []
                
                for member in members:
                    node_data = self.network.nodes[member]
                    member_values.append(node_data.get('total_spent', 0))
                    
                    # Calculate simple influence for this member
                    degree = self.network.degree(member)
                    member_influences.append(degree)
                
                total_value = sum(member_values)
                avg_influence = np.mean(member_influences) if member_influences else 0
                
                # Identify key influencers
                influencer_threshold = np.percentile(member_influences, 80) if member_influences else 0
                key_influencers = [members[i] for i, inf in enumerate(member_influences) 
                                 if inf >= influencer_threshold][:5]
                
                # Determine community type
                if avg_influence > 10:
                    community_type = "high_influence"
                elif total_value > 5000:
                    community_type = "high_value"
                elif len(members) > 20:
                    community_type = "large_network"
                else:
                    community_type = "standard"
                
                community_obj = NetworkCommunity(
                    community_id=f"community_{comm_id}",
                    name=f"Community {comm_id} ({community_type})",
                    member_count=len(members),
                    total_value=total_value,
                    avg_influence_score=avg_influence,
                    community_type=community_type,
                    key_influencers=key_influencers,
                    growth_rate=np.random.uniform(-0.1, 0.3),  # Simplified
                    engagement_metrics={
                        "internal_connections": subgraph.number_of_edges(),
                        "density": nx.density(subgraph),
                        "clustering_coefficient": nx.average_clustering(subgraph)
                    },
                    characteristics={
                        "avg_customer_value": np.mean(member_values) if member_values else 0,
                        "geographic_spread": "mixed",  # Simplified
                        "age_distribution": "varied"   # Simplified
                    }
                )
                
                community_analysis.append(community_obj)
            
            # Store communities
            self.communities = {comm.community_id: comm for comm in community_analysis}
            
            logger.info(f"Detected {len(community_analysis)} communities")
            return community_analysis
            
        except Exception as e:
            logger.error(f"Failed to detect communities: {e}")
            raise

    def analyze_referral_network(self, time_period_days: int = 90) -> ReferralAnalysis:
        """Analyze referral patterns and viral growth"""
        try:
            cutoff_date = datetime.now() - timedelta(days=time_period_days)
            
            # Get referral edges within time period
            referral_edges = [(u, v, data) for u, v, data in self.directed_network.edges(data=True)
                            if data.get('edge_type') == EdgeType.REFERRAL.value
                            and data.get('created_at', datetime.now()) >= cutoff_date]
            
            total_referrals = len(referral_edges)
            
            # Calculate successful conversions (simplified)
            successful_conversions = int(total_referrals * np.random.uniform(0.15, 0.35))
            conversion_rate = (successful_conversions / max(total_referrals, 1)) * 100
            
            # Calculate referral values
            referral_values = [edge[2].get('value', 0) for edge in referral_edges]
            total_referral_value = sum(referral_values)
            avg_referral_value = np.mean(referral_values) if referral_values else 0
            
            # Identify top referrers
            referrer_counts = defaultdict(int)
            referrer_values = defaultdict(float)
            
            for u, v, data in referral_edges:
                referrer_counts[u] += 1
                referrer_values[u] += data.get('value', 0)
            
            top_referrers = []
            for referrer in sorted(referrer_counts.keys(), 
                                 key=lambda x: referrer_counts[x], reverse=True)[:10]:
                top_referrers.append({
                    "customer_id": referrer,
                    "referral_count": referrer_counts[referrer],
                    "total_value": referrer_values[referrer],
                    "avg_value": referrer_values[referrer] / max(referrer_counts[referrer], 1)
                })
            
            # Analyze referral channels (simplified)
            referral_channels = {
                "email": int(total_referrals * 0.4),
                "social_media": int(total_referrals * 0.3),
                "word_of_mouth": int(total_referrals * 0.2),
                "other": int(total_referrals * 0.1)
            }
            
            # Calculate viral coefficient
            active_customers = self.network.number_of_nodes()
            viral_coefficient = total_referrals / max(active_customers, 1)
            
            # Calculate network growth rate
            network_growth_rate = (total_referrals / time_period_days) * 30  # Monthly rate
            
            return ReferralAnalysis(
                analysis_id=str(uuid.uuid4()),
                total_referrals=total_referrals,
                successful_conversions=successful_conversions,
                conversion_rate=conversion_rate,
                total_referral_value=total_referral_value,
                avg_referral_value=avg_referral_value,
                top_referrers=top_referrers,
                referral_channels=referral_channels,
                viral_coefficient=viral_coefficient,
                network_growth_rate=network_growth_rate
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze referral network: {e}")
            raise

    def generate_network_visualization_data(self, layout: str = "spring") -> Dict[str, Any]:
        """Generate network visualization data for frontend"""
        try:
            # Calculate layout positions
            if layout == "spring":
                pos = nx.spring_layout(self.network, k=1, iterations=50)
            elif layout == "circular":
                pos = nx.circular_layout(self.network)
            elif layout == "random":
                pos = nx.random_layout(self.network)
            else:
                pos = nx.spring_layout(self.network)
            
            # Prepare nodes data
            nodes_data = []
            for node in self.network.nodes():
                node_data = self.network.nodes[node]
                
                # Calculate node size based on connections
                degree = self.network.degree(node)
                node_size = max(10, min(50, degree * 5))
                
                # Determine node color based on type
                node_type = node_data.get('node_type', 'customer')
                color_map = {
                    'customer': '#3498db',
                    'influencer': '#e74c3c',
                    'brand_advocate': '#2ecc71',
                    'high_value_customer': '#f39c12',
                    'new_customer': '#9b59b6',
                    'churned_customer': '#95a5a6'
                }
                node_color = color_map.get(node_type, '#3498db')
                
                nodes_data.append({
                    "id": node,
                    "label": f"Customer {node[:8]}",
                    "x": float(pos[node][0]) * 1000,  # Scale for visualization
                    "y": float(pos[node][1]) * 1000,
                    "size": node_size,
                    "color": node_color,
                    "type": node_type,
                    "degree": degree,
                    "total_spent": node_data.get('total_spent', 0),
                    "referrals_made": len(list(self.directed_network.successors(node)))
                })
            
            # Prepare edges data
            edges_data = []
            for edge in self.network.edges(data=True):
                source, target, data = edge
                
                edge_type = data.get('edge_type', 'interaction')
                edge_weight = data.get('weight', 1)
                
                # Determine edge color and width
                if edge_type == 'referral':
                    edge_color = '#e74c3c'
                    edge_width = max(1, min(5, edge_weight * 2))
                else:
                    edge_color = '#bdc3c7'
                    edge_width = 1
                
                edges_data.append({
                    "id": f"{source}_{target}",
                    "source": source,
                    "target": target,
                    "color": edge_color,
                    "width": edge_width,
                    "type": edge_type,
                    "weight": edge_weight,
                    "value": data.get('value', 0)
                })
            
            # Network statistics
            network_stats = {
                "total_nodes": len(nodes_data),
                "total_edges": len(edges_data),
                "density": nx.density(self.network),
                "average_clustering": nx.average_clustering(self.network),
                "number_of_components": nx.number_connected_components(self.network),
                "diameter": self._safe_diameter(),
                "assortativity": self._safe_assortativity()
            }
            
            return {
                "nodes": nodes_data,
                "edges": edges_data,
                "layout": layout,
                "statistics": network_stats,
                "legend": {
                    "node_types": [
                        {"type": "customer", "color": "#3498db", "description": "Regular Customer"},
                        {"type": "influencer", "color": "#e74c3c", "description": "Influencer"},
                        {"type": "brand_advocate", "color": "#2ecc71", "description": "Brand Advocate"},
                        {"type": "high_value_customer", "color": "#f39c12", "description": "High-Value Customer"},
                        {"type": "new_customer", "color": "#9b59b6", "description": "New Customer"},
                        {"type": "churned_customer", "color": "#95a5a6", "description": "Churned Customer"}
                    ],
                    "edge_types": [
                        {"type": "referral", "color": "#e74c3c", "description": "Referral Connection"},
                        {"type": "interaction", "color": "#bdc3c7", "description": "Social Interaction"}
                    ]
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate network visualization data: {e}")
            raise

    def identify_key_influencers(self, limit: int = 20) -> List[InfluenceAnalysis]:
        """Identify key influencers in the network"""
        try:
            # Calculate centrality measures for all nodes
            pagerank_scores = nx.pagerank(self.network)
            betweenness_scores = nx.betweenness_centrality(self.network)
            degree_scores = dict(self.network.degree())
            
            # Combine scores to identify influencers
            influencer_scores = {}
            
            for node in self.network.nodes():
                # Referral activity
                outgoing_referrals = len(list(self.directed_network.successors(node)))
                
                # Combined influence score
                influence_score = (
                    pagerank_scores.get(node, 0) * 0.3 +
                    betweenness_scores.get(node, 0) * 0.3 +
                    (degree_scores.get(node, 0) / max(self.network.number_of_nodes(), 1)) * 0.2 +
                    (outgoing_referrals / max(10, 1)) * 0.2
                ) * 100
                
                influencer_scores[node] = influence_score
            
            # Get top influencers
            top_influencers = sorted(influencer_scores.items(), 
                                   key=lambda x: x[1], reverse=True)[:limit]
            
            # Generate detailed analysis for each influencer
            influencer_analyses = []
            for customer_id, score in top_influencers:
                if score > 10:  # Only include significant influencers
                    analysis = self.analyze_customer_influence(customer_id)
                    influencer_analyses.append(analysis)
            
            return influencer_analyses
            
        except Exception as e:
            logger.error(f"Failed to identify key influencers: {e}")
            raise

    # Helper methods
    def _get_customer_data(self, include_inactive: bool) -> List[Dict[str, Any]]:
        """Get customer data for network building"""
        query = text("""
            SELECT 
                customer_id,
                age,
                gender,
                total_spent,
                created_at,
                segment_id
            FROM customers
        """)
        
        if not include_inactive:
            query = text(query.text + " WHERE total_spent > 0")
        
        result = self.db.execute(query).fetchall()
        return [dict(row._mapping) for row in result]

    def _get_referral_data(self) -> List[Dict[str, Any]]:
        """Get referral relationship data (simulated)"""
        # In a real implementation, this would come from a referrals table
        referrals = []
        
        # Simulate some referral relationships
        customer_query = text("SELECT customer_id FROM customers ORDER BY RANDOM() LIMIT 100")
        customers = [row.customer_id for row in self.db.execute(customer_query).fetchall()]
        
        for i in range(min(50, len(customers) // 2)):
            if len(customers) > i + 1:
                referrals.append({
                    'referrer_id': customers[i],
                    'referred_id': customers[i + 1],
                    'created_at': datetime.now() - timedelta(days=np.random.randint(1, 365)),
                    'referral_value': np.random.uniform(50, 300)
                })
        
        return referrals

    def _get_interaction_data(self) -> List[Dict[str, Any]]:
        """Get customer interaction data (simulated)"""
        # In a real implementation, this would come from interaction logs
        interactions = []
        
        # Simulate some customer interactions
        customer_query = text("SELECT customer_id FROM customers ORDER BY RANDOM() LIMIT 50")
        customers = [row.customer_id for row in self.db.execute(customer_query).fetchall()]
        
        for i in range(len(customers)):
            for j in range(i + 1, min(i + 4, len(customers))):  # Each customer connects to 3 others
                if np.random.random() < 0.3:  # 30% chance of connection
                    interactions.append({
                        'customer_a': customers[i],
                        'customer_b': customers[j],
                        'frequency': np.random.randint(1, 10),
                        'interaction_type': np.random.choice(['social', 'transactional', 'referral'])
                    })
        
        return interactions

    def _determine_node_type(self, customer: Dict[str, Any]) -> NodeType:
        """Determine the type of network node for a customer"""
        total_spent = customer.get('total_spent', 0)
        account_age = (datetime.now() - customer.get('created_at', datetime.now())).days
        
        if total_spent > 1000:
            return NodeType.HIGH_VALUE_CUSTOMER
        elif account_age < 30:
            return NodeType.NEW_CUSTOMER
        elif total_spent == 0 and account_age > 180:
            return NodeType.CHURNED_CUSTOMER
        else:
            return NodeType.CUSTOMER

    def _extract_customer_attributes(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant attributes for network nodes"""
        return {
            'total_spent': customer.get('total_spent', 0),
            'age': customer.get('age', 0),
            'gender': customer.get('gender', 'unknown'),
            'segment_id': customer.get('segment_id'),
            'account_age_days': (datetime.now() - customer.get('created_at', datetime.now())).days
        }

    def _calculate_referral_weight(self, referral: Dict[str, Any]) -> float:
        """Calculate weight for referral edges"""
        base_weight = 1.0
        value_weight = min(2.0, referral.get('referral_value', 0) / 100)
        recency_weight = max(0.1, 1.0 - ((datetime.now() - referral['created_at']).days / 365))
        
        return base_weight + value_weight + recency_weight

    def _calculate_interaction_weight(self, interaction: Dict[str, Any]) -> float:
        """Calculate weight for interaction edges"""
        frequency = interaction.get('frequency', 1)
        interaction_type = interaction.get('interaction_type', 'social')
        
        type_weights = {
            'referral': 3.0,
            'transactional': 2.0,
            'social': 1.0
        }
        
        return min(5.0, frequency * type_weights.get(interaction_type, 1.0))

    def _calculate_network_metrics(self) -> Dict[str, Any]:
        """Calculate overall network metrics"""
        try:
            metrics = {
                "density": nx.density(self.network),
                "average_clustering": nx.average_clustering(self.network),
                "number_of_components": nx.number_connected_components(self.network),
                "largest_component_size": len(max(nx.connected_components(self.network), key=len)) if self.network.nodes() else 0,
                "average_degree": sum(dict(self.network.degree()).values()) / max(self.network.number_of_nodes(), 1),
                "diameter": self._safe_diameter(),
                "assortativity": self._safe_assortativity(),
                "small_world_coefficient": self._calculate_small_world_coefficient()
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Failed to calculate network metrics: {e}")
            return {}

    def _calculate_node_centrality(self, node_id: str) -> Dict[str, float]:
        """Calculate centrality measures for a specific node"""
        try:
            # Use cached values if available
            if node_id in self.centrality_cache:
                return self.centrality_cache[node_id]
            
            centrality_scores = {}
            
            # Degree centrality
            degree_cent = nx.degree_centrality(self.network)
            centrality_scores['degree'] = degree_cent.get(node_id, 0)
            
            # Only calculate expensive centralities for connected graphs
            if nx.is_connected(self.network):
                betweenness_cent = nx.betweenness_centrality(self.network)
                closeness_cent = nx.closeness_centrality(self.network)
                centrality_scores['betweenness'] = betweenness_cent.get(node_id, 0)
                centrality_scores['closeness'] = closeness_cent.get(node_id, 0)
            else:
                centrality_scores['betweenness'] = 0
                centrality_scores['closeness'] = 0
            
            # PageRank and eigenvector centrality
            try:
                pagerank_cent = nx.pagerank(self.network)
                centrality_scores['pagerank'] = pagerank_cent.get(node_id, 0)
            except:
                centrality_scores['pagerank'] = 0
            
            try:
                eigenvector_cent = nx.eigenvector_centrality(self.network, max_iter=1000)
                centrality_scores['eigenvector'] = eigenvector_cent.get(node_id, 0)
            except:
                centrality_scores['eigenvector'] = 0
            
            # Cache the results
            self.centrality_cache[node_id] = centrality_scores
            
            return centrality_scores
            
        except Exception as e:
            logger.error(f"Failed to calculate centrality for node {node_id}: {e}")
            return {'degree': 0, 'betweenness': 0, 'closeness': 0, 'pagerank': 0, 'eigenvector': 0}

    def _safe_diameter(self) -> Optional[int]:
        """Safely calculate network diameter"""
        try:
            if nx.is_connected(self.network):
                return nx.diameter(self.network)
            else:
                # Return diameter of largest component
                largest_cc = max(nx.connected_components(self.network), key=len)
                subgraph = self.network.subgraph(largest_cc)
                return nx.diameter(subgraph)
        except:
            return None

    def _safe_assortativity(self) -> Optional[float]:
        """Safely calculate degree assortativity"""
        try:
            return nx.degree_assortativity_coefficient(self.network)
        except:
            return None

    def _calculate_small_world_coefficient(self) -> Optional[float]:
        """Calculate small world coefficient (Watts-Strogatz)"""
        try:
            if self.network.number_of_edges() == 0:
                return None
            
            # Calculate clustering coefficient
            C = nx.average_clustering(self.network)
            
            # Calculate average path length for largest component
            if nx.is_connected(self.network):
                L = nx.average_shortest_path_length(self.network)
            else:
                largest_cc = max(nx.connected_components(self.network), key=len)
                subgraph = self.network.subgraph(largest_cc)
                L = nx.average_shortest_path_length(subgraph)
            
            # Generate random graph with same degree sequence
            degree_sequence = [d for n, d in self.network.degree()]
            try:
                random_graph = nx.configuration_model(degree_sequence)
                random_graph = nx.Graph(random_graph)  # Remove multi-edges
                random_graph.remove_edges_from(nx.selfloop_edges(random_graph))  # Remove self-loops
                
                C_rand = nx.average_clustering(random_graph)
                L_rand = nx.average_shortest_path_length(random_graph) if nx.is_connected(random_graph) else L
                
                # Small world coefficient
                if C_rand > 0 and L_rand > 0:
                    return (C / C_rand) / (L / L_rand)
            except:
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to calculate small world coefficient: {e}")
            return None

    def _generate_influence_recommendations(self, influence_score: float, 
                                          network_position: str, referrals_made: int) -> List[str]:
        """Generate recommendations based on influence analysis"""
        recommendations = []
        
        if influence_score > 70:
            recommendations.append("Leverage as brand ambassador for marketing campaigns")
            recommendations.append("Invite to exclusive events and early product access")
        elif influence_score > 50:
            recommendations.append("Implement referral incentive program")
            recommendations.append("Request testimonials and case studies")
        else:
            recommendations.append("Engage with personalized content to increase influence")
            recommendations.append("Encourage social sharing and referrals")
        
        if network_position == "bridge":
            recommendations.append("Focus on community building initiatives")
        elif network_position == "hub":
            recommendations.append("Utilize for peer-to-peer marketing")
        
        if referrals_made < 1:
            recommendations.append("Introduce to referral program with attractive incentives")
        
        return recommendations[:5]