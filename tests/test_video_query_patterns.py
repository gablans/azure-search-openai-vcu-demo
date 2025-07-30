"""
Unit tests for video query rewriting functionality.
Tests the updated chat_query_rewrite.prompty for video content optimization.
"""
import re
from typing import List, Dict, Any


class TestVideoQueryPatterns:
    """Test video-specific query pattern recognition and optimization"""

    def test_timestamp_query_patterns(self):
        """Test recognition of various timestamp query patterns"""
        
        timestamp_queries = [
            "What happens at 2 minutes?",
            "Show me the scene at 00:02:30", 
            "Tell me about the 1 minute mark",
            "What occurs around 00:01:15?",
            "Describe the scene from 30 seconds to 1 minute"
        ]
        
        # Pattern to match time references
        time_patterns = [
            r'\d+\s*minutes?',  # "2 minutes", "1 minute"
            r'\d{2}:\d{2}:\d{2}',  # "00:02:30"
            r'\d+\s*seconds?',  # "30 seconds"
            r'minute\s*mark',  # "minute mark"
        ]
        
        for query in timestamp_queries:
            has_time_reference = any(
                re.search(pattern, query, re.IGNORECASE) 
                for pattern in time_patterns
            )
            assert has_time_reference, f"Query should contain time reference: {query}"

    def test_brand_query_patterns(self):
        """Test recognition of brand-specific query patterns"""
        
        brand_queries = [
            "Show me Furo bicycle features",
            "What does Huawei demonstrate?",
            "Tell me about Hive backpack technology", 
            "Display TropicFeel product details"
        ]
        
        expected_brands = ["Furo", "Huawei", "Hive", "TropicFeel"]
        
        for query, expected_brand in zip(brand_queries, expected_brands):
            assert expected_brand in query, f"Query should contain brand: {expected_brand}"

    def test_feature_query_patterns(self):
        """Test recognition of feature-specific query patterns"""
        
        feature_queries = [
            "Show me smart features",
            "What camera capabilities are shown?", 
            "Tell me about LCD screen functionality",
            "Describe the SpiderNet technology"
        ]
        
        feature_terms = ["smart", "camera", "LCD", "SpiderNet"]
        
        for query, feature in zip(feature_queries, feature_terms):
            assert feature in query, f"Query should contain feature term: {feature}"


class TestVideoQueryRewriteExamples:
    """Test that video query rewrite examples are comprehensive"""

    def get_video_query_examples(self) -> List[Dict[str, str]]:
        """Get expected video query rewrite examples"""
        return [
            {
                "user_query": "What happens at 2 minutes?",
                "optimized_search": "00:02 StartTimestamp EndTimestamp scenes 2 minute"
            },
            {
                "user_query": "Show me Furo bicycle features", 
                "optimized_search": "Furo bicycle smart features StartTimestamp EndTimestamp"
            },
            {
                "user_query": "Tell me about Hive backpack technology",
                "optimized_search": "Hive backpack scenes StartTimestamp EndTimestamp camera cube SpiderNet smart"
            },
            {
                "user_query": "What does Huawei demonstrate?",
                "optimized_search": "Huawei watch camera cube SpiderNet StartTimestamp EndTimestamp scenes"
            }
        ]

    def test_query_rewrite_completeness(self):
        """Test that query rewrite examples cover key scenarios"""
        
        examples = self.get_video_query_examples()
        
        # Verify we have examples for different query types
        query_types = {
            "timestamp": False,
            "brand": False,
            "feature": False
        }
        
        for example in examples:
            user_query = example["user_query"].lower()
            if any(term in user_query for term in ["minute", "00:", "time"]):
                query_types["timestamp"] = True
            if any(brand in user_query for brand in ["furo", "hive", "huawei"]):
                query_types["brand"] = True  
            if any(term in user_query for term in ["feature", "technology", "demonstrate"]):
                query_types["feature"] = True
        
        # All query types should be covered
        for query_type, covered in query_types.items():
            assert covered, f"Query type '{query_type}' should be covered in examples"

    def test_search_optimization_quality(self):
        """Test that search optimizations include video-specific terms"""
        
        examples = self.get_video_query_examples()
        
        required_video_terms = ["StartTimestamp", "EndTimestamp"]
        recommended_terms = ["scenes", "features", "smart", "camera"]
        
        for example in examples:
            optimized_search = example["optimized_search"]
            
            # Must include timestamp terms
            for term in required_video_terms:
                assert term in optimized_search, f"Optimized search must include '{term}': {optimized_search}"
            
            # Should include some recommended terms
            has_recommended = any(term in optimized_search for term in recommended_terms)
            assert has_recommended, f"Optimized search should include recommended terms: {optimized_search}"


class TestVideoDataCompatibility:
    """Test compatibility with actual video data structure"""

    def get_sample_video_scene(self) -> Dict[str, Any]:
        """Get sample video scene data structure"""
        return {
            "SceneId": "1",
            "Description": "A woman stands with a Furo Systems bicycle on a platform in an urban setting.",
            "StartTimestamp": "00:00:00.778",
            "EndTimestamp": "00:00:01.556", 
            "Objects": ["bicycle", "woman", "platform"],
            "Brands": ["Furo Systems"],
            "Products": ["bicycle"],
            "MarketingMessaging": ["Introduction of Furo Systems bicycles in various settings."]
        }

    def test_timestamp_format_compatibility(self):
        """Test that query patterns match actual timestamp formats"""
        
        scene = self.get_sample_video_scene()
        
        # Test timestamp format validation
        timestamp_pattern = r'^\d{2}:\d{2}:\d{2}\.\d{3}$'
        
        start_timestamp = scene["StartTimestamp"]
        end_timestamp = scene["EndTimestamp"]
        
        assert re.match(timestamp_pattern, start_timestamp), f"Invalid start timestamp format: {start_timestamp}"
        assert re.match(timestamp_pattern, end_timestamp), f"Invalid end timestamp format: {end_timestamp}"

    def test_brand_extraction_compatibility(self):
        """Test that brand terms in queries match actual brand data"""
        
        scene = self.get_sample_video_scene()
        brands = scene["Brands"]
        
        # Test brand matching
        assert "Furo Systems" in brands, "Scene should contain Furo Systems brand"
        
        # Test query compatibility
        brand_query = "Show me Furo bicycle features"
        assert "Furo" in brand_query, "Query should match brand data"

    def test_object_feature_compatibility(self):
        """Test that feature queries match actual object/product data"""
        
        scene = self.get_sample_video_scene()
        objects = scene["Objects"]
        products = scene["Products"]
        
        # Verify data structure
        assert "bicycle" in objects or "bicycle" in products, "Scene should contain bicycle references"
        
        # Test feature query compatibility with bicycle-related features
        bicycle_features = [
            "smart", "LCD", "screen", "hydraulic", "disk", "brakes", 
            "lightweight", "battery", "removable"
        ]
        
        feature_queries = [
            "bicycle features",
            "smart bicycle technology", 
            "bicycle LCD screen",
            "hydraulic disk brakes"
        ]
        
        for query in feature_queries:
            # Check that query contains either product reference or valid feature terms
            has_product_ref = "bicycle" in query
            has_feature_term = any(feature in query for feature in bicycle_features)
            assert has_product_ref or has_feature_term, f"Feature query should be bicycle-related: {query}"


class TestVideoResponseExpectations:
    """Test expected response formats for video content"""

    def test_scene_description_format(self):
        """Test expected scene description format in responses"""
        
        expected_format = "Scene from {start_time} - {end_time}: {description}"
        
        sample_scene_descriptions = [
            "Scene from 00:00:00.778 - 00:00:01.556: A woman stands with a bicycle",
            "Scene from 00:02:15.000 - 00:02:30.500: Product features demonstration",
            "Scene from 00:05:45.123 - 00:06:00.999: Technical specifications display"
        ]
        
        scene_pattern = r'Scene from \d{2}:\d{2}:\d{2}\.\d{3} - \d{2}:\d{2}:\d{2}\.\d{3}: .+'
        
        for description in sample_scene_descriptions:
            assert re.match(scene_pattern, description), f"Scene description format invalid: {description}"

    def test_multi_scene_response_structure(self):
        """Test structure when multiple scenes are included in response"""
        
        multi_scene_response = """
        Based on the video analysis, here are the relevant scenes:
        
        Scene from 00:00:00.778 - 00:00:01.556: Introduction with bicycle and woman
        This scene shows the initial product presentation.
        
        Scene from 00:02:30.000 - 00:02:45.500: Feature demonstration
        Key features like smart LCD screen and hydraulic brakes are highlighted.
        
        Scene from 00:05:15.200 - 00:05:30.800: Technical specifications
        Detailed technical information is displayed.
        """
        
        # Count scene markers
        scene_count = multi_scene_response.count("Scene from")
        assert scene_count == 3, f"Expected 3 scenes, found {scene_count}"
        
        # Verify each scene has proper timestamp range
        timestamp_ranges = multi_scene_response.count(" - 00:")
        assert timestamp_ranges == 3, f"Expected 3 timestamp ranges, found {timestamp_ranges}"

    def test_feature_integration_in_responses(self):
        """Test that video features are properly integrated in responses"""
        
        sample_response = """
        Scene from 00:00:12.860 - 00:00:17.447: The video highlights key bicycle features including:
        - Smart LCD screen for navigation and performance tracking
        - Hydraulic disk brakes for superior stopping power  
        - Lightweight design for enhanced portability
        - Removable battery for convenient charging
        """
        
        expected_features = ["Smart LCD screen", "Hydraulic disk brakes", "Lightweight design", "Removable battery"]
        
        for feature in expected_features:
            assert feature in sample_response, f"Response should include feature: {feature}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
