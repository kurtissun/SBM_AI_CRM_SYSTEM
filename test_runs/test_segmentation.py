#!/usr/bin/env python3
"""
Test customer segmentation directly
"""
import sys
import pandas as pd
sys.path.append('.')

def test_segmentation():
    try:
        # Import the clustering engine
        from backend.ai_engine.adaptive_clustering import AdaptiveClustering
        from backend.ai_engine.insight_generator import IntelligentInsightGenerator
        
        print("✅ Successfully imported clustering modules")
        
        # Load sample data
        df = pd.read_csv('sample_customers.csv')
        print(f"✅ Loaded {len(df)} customer records")
        print(f"📊 Columns: {list(df.columns)}")
        
        # Initialize clustering engine
        clustering_engine = AdaptiveClustering()
        print("✅ Initialized clustering engine")
        
        # Run segmentation
        print("🔄 Running customer segmentation...")
        result = clustering_engine.fit_transform(df)
        
        print("🎉 SEGMENTATION RESULTS:")
        print("=" * 50)
        print(f"📊 Number of segments: {result['n_clusters']}")
        print(f"📈 Silhouette score: {result['silhouette_score']:.3f}")
        print(f"🔧 Algorithm used: {result['algorithm_used']}")
        
        print("\n📋 SEGMENT PROFILES:")
        for segment_id, profile in result['cluster_profiles'].items():
            print(f"\n🎯 Segment {segment_id}:")
            print(f"   Size: {profile['size']} customers ({profile['percentage']:.1f}%)")
            if 'demographics' in profile:
                demo = profile['demographics']
                if 'avg_age' in demo:
                    print(f"   Average age: {demo['avg_age']:.1f}")
                if 'avg_rating' in demo:
                    print(f"   Average rating: {demo['avg_rating']:.1f}")
                if 'gender_dist' in demo:
                    print(f"   Gender distribution: {demo['gender_dist']}")
        
        print("\n🧠 BUSINESS INSIGHTS:")
        for segment_id, insight in result['insights'].items():
            print(f"\n💡 Segment {segment_id}: {insight['description']}")
            print(f"   Value tier: {insight['predicted_value']}")
            print(f"   Recommended actions: {', '.join(insight['recommended_actions'])}")
        
        # Generate comprehensive insights
        print("\n🔍 GENERATING COMPREHENSIVE INSIGHTS...")
        insight_generator = IntelligentInsightGenerator()
        comprehensive_insights = insight_generator.generate_comprehensive_insights(result)
        
        print("\n📈 EXECUTIVE SUMMARY:")
        if 'executive_summary' in comprehensive_insights:
            summary = comprehensive_insights['executive_summary']
            print(f"   Total customers analyzed: {summary.get('total_customers', 'N/A')}")
            print(f"   Segmentation quality: {summary.get('segmentation_quality', 'N/A')}")
            print(f"   Key findings: {summary.get('key_findings', ['N/A'])}")
        
        print("\n🎯 BUSINESS OPPORTUNITIES:")
        if 'business_opportunities' in comprehensive_insights:
            opportunities = comprehensive_insights['business_opportunities']
            for category, ops in opportunities.items():
                if ops:  # Only show categories with opportunities
                    print(f"   {category.replace('_', ' ').title()}:")
                    for op in ops[:2]:  # Show first 2 opportunities
                        print(f"     - {op.get('opportunity', 'N/A')}")
        
        print("\n✅ SEGMENTATION TEST COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Segmentation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_segmentation()
    sys.exit(0 if success else 1)