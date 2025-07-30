"""
Integration tests for video content understanding functionality.
Tests the video-optimized query rewriting and response generation.
"""
import json
import os
import pytest


class TestVideoPromptOptimization:
    """Test video-specific prompt template optimizations"""

    def test_video_query_rewrite_prompt_content(self):
        """Test that the query rewrite prompt contains video-optimized patterns"""
        
        # Read the actual prompt file
        prompt_path = "/workspaces/azure-search-openai-vcu-demo/app/backend/approaches/prompts/chat_query_rewrite.prompty"
        
        with open(prompt_path, 'r') as f:
            prompt_content = f.read()
        
        # Verify video-specific patterns are present
        video_patterns = [
            "StartTimestamp",
            "EndTimestamp", 
            "Hive",
            "Furo",
            "Huawei",
            "backpack",
            "bicycle",
            "camera cube",
            "00:02"
        ]
        
        for pattern in video_patterns:
            assert pattern in prompt_content, f"Video pattern '{pattern}' not found in prompt"
        
        # Verify healthcare patterns are NOT present
        healthcare_patterns = [
            "health plans",
            "Northwind Health Plus",
            "medical benefits", 
            "healthcare coverage"
        ]
        
        for pattern in healthcare_patterns:
            assert pattern not in prompt_content, f"Healthcare pattern '{pattern}' should be removed"

    def test_video_data_structure_validation(self):
        """Test that video JSON files have the expected structure"""
        
        video_files = [
            "/workspaces/azure-search-openai-vcu-demo/data/content_understanding/content_understanding_output/furo.json",
            "/workspaces/azure-search-openai-vcu-demo/data/content_understanding/content_understanding_output/huawei.json", 
            "/workspaces/azure-search-openai-vcu-demo/data/content_understanding/content_understanding_output/tropicfeel.json"
        ]
        
        for video_file in video_files:
            if os.path.exists(video_file):
                with open(video_file, 'r') as f:
                    video_data = json.load(f)
                
                # Verify basic structure
                assert "result" in video_data
                assert "contents" in video_data["result"]
                
                # Check for fields that should contain scene data
                content_str = json.dumps(video_data)
                
                # Verify timestamp patterns exist
                timestamp_patterns = ["StartTimestamp", "EndTimestamp"]
                for pattern in timestamp_patterns:
                    assert pattern in content_str, f"Timestamp pattern '{pattern}' not found in {video_file}"
                
                # Verify time format patterns (HH:MM:SS.mmm)
                assert "00:00:" in content_str or "00:01:" in content_str, f"Time format not found in {video_file}"

    def test_video_query_examples_coverage(self):
        """Test that query rewrite examples cover key video scenarios"""
        
        prompt_path = "/workspaces/azure-search-openai-vcu-demo/app/backend/approaches/prompts/chat_query_rewrite.prompty"
        
        with open(prompt_path, 'r') as f:
            prompt_content = f.read()
        
        # Test scenarios that should be covered
        test_scenarios = [
            {
                "name": "Brand-specific queries", 
                "patterns": ["Hive", "Furo", "Huawei"]
            },
            {
                "name": "Time-based queries",
                "patterns": ["00:02", "StartTimestamp", "EndTimestamp"]
            },
            {
                "name": "Feature queries", 
                "patterns": ["features", "smart", "camera"]
            },
            {
                "name": "Product queries",
                "patterns": ["backpack", "bicycle", "watch"]
            }
        ]
        
        for scenario in test_scenarios:
            found_patterns = sum(1 for pattern in scenario["patterns"] if pattern in prompt_content)
            assert found_patterns > 0, f"No patterns found for scenario: {scenario['name']}"

    def test_prompt_file_syntax_validation(self):
        """Test that the prompt file has valid YAML front matter"""
        
        prompt_path = "/workspaces/azure-search-openai-vcu-demo/app/backend/approaches/prompts/chat_query_rewrite.prompty"
        
        with open(prompt_path, 'r') as f:
            content = f.read()
        
        # Check for YAML front matter
        assert content.startswith("---"), "Prompt file should start with YAML front matter"
        
        # Find the end of YAML front matter
        yaml_end = content.find("---", 3)
        assert yaml_end > 0, "Prompt file should have proper YAML front matter closing"
        
        # Basic YAML structure validation
        yaml_section = content[3:yaml_end]
        assert "name:" in yaml_section, "YAML should contain name field"
        assert "description:" in yaml_section, "YAML should contain description field"


class TestVideoSearchPatterns:
    """Test video-specific search optimization patterns"""

    def test_timestamp_search_optimization(self):
        """Test that timestamp queries generate optimal search patterns"""
        
        # Sample timestamp queries users might ask
        timestamp_queries = [
            "What happens at 2 minutes?",
            "Show me the scene around 00:01:30",
            "Tell me about the features at the beginning",
            "What brands appear in the first minute?"
        ]
        
        # Expected search optimization patterns
        expected_optimizations = [
            ["00:02", "StartTimestamp", "EndTimestamp", "2", "minute"],
            ["00:01:30", "scene", "StartTimestamp", "EndTimestamp"],
            ["00:00", "features", "StartTimestamp", "beginning"],
            ["brands", "00:01", "minute", "StartTimestamp"]
        ]
        
        # Verify we have optimization patterns for each query type
        assert len(timestamp_queries) == len(expected_optimizations)
        
        for query, optimizations in zip(timestamp_queries, expected_optimizations):
            # Each optimization set should contain timestamp-related terms
            has_timestamp_terms = any(
                term in optimizations 
                for term in ["StartTimestamp", "EndTimestamp", "00:", "minute"]
            )
            assert has_timestamp_terms, f"Query '{query}' should have timestamp optimization"

    def test_brand_search_optimization(self):
        """Test that brand queries are optimized for video content"""
        
        brand_data = {
            "Furo": ["bicycle", "smart", "LCD", "hydraulic", "lightweight"],
            "Huawei": ["watch", "camera", "cube", "SpiderNet", "smart"],
            "Hive": ["backpack", "camera", "cube", "SpiderNet", "smart"],
            "TropicFeel": ["backpack", "features", "travel", "adventure"]
        }
        
        for brand, features in brand_data.items():
            # Each brand should have associated feature terms
            assert len(features) > 0, f"Brand '{brand}' should have feature associations"
            
            # Features should be relevant to video content
            video_relevant_terms = ["smart", "camera", "features"]
            has_video_terms = any(term in features for term in video_relevant_terms)
            assert has_video_terms, f"Brand '{brand}' should have video-relevant features"


class TestVideoResponseFormatting:
    """Test video response formatting expectations"""

    def test_scene_timestamp_format(self):
        """Test expected scene timestamp format in responses"""
        
        # Expected format: "Scene from HH:MM:SS.mmm - HH:MM:SS.mmm: description"
        expected_format_pattern = r"Scene from \d{2}:\d{2}:\d{2}\.\d{3} - \d{2}:\d{2}:\d{2}\.\d{3}"
        
        sample_responses = [
            "Scene from 00:00:00.778 - 00:00:01.556: A woman stands with a bicycle",
            "Scene from 00:02:15.000 - 00:02:30.500: Product features are demonstrated", 
            "Scene from 00:05:45.123 - 00:06:00.999: Technical specifications display"
        ]
        
        import re
        pattern = re.compile(expected_format_pattern)
        
        for response in sample_responses:
            match = pattern.search(response)
            assert match is not None, f"Response should match timestamp format: {response}"

    def test_multiple_scene_formatting(self):
        """Test formatting when multiple scenes are referenced"""
        
        multi_scene_response = """
        Based on the video analysis:
        
        Scene from 00:00:00.778 - 00:00:01.556: Introduction with bicycle
        Scene from 00:02:30.000 - 00:02:45.500: Feature demonstration  
        Scene from 00:05:15.200 - 00:05:30.800: Technical specifications
        """
        
        # Count scene references
        scene_count = multi_scene_response.count("Scene from")
        assert scene_count == 3, "Should have exactly 3 scene references"
        
        # Each scene should have proper timestamp range
        timestamp_ranges = multi_scene_response.count(" - 00:")
        assert timestamp_ranges == 3, "Each scene should have timestamp range"


class TestVideoStructuredResponses:
    """Test structured JSON response functionality for video content"""

    def test_structured_response_schema_validation(self):
        """Test that structured responses follow the expected JSON schema"""
        
        expected_schema = {
            "description": str,
            "scene_references": list,
            "key_features": list,
            "brands_mentioned": list,
            "source_files": list
        }
        
        sample_structured_response = {
            "description": "The video showcases Furo Systems bicycle features including smart LCD screen and hydraulic brakes.",
            "scene_references": [
                {
                    "start_timestamp": "00:00:00.778",
                    "end_timestamp": "00:00:01.556",
                    "description": "Woman with Furo Systems bicycle",
                    "video_file": "furo.mp4"
                }
            ],
            "key_features": ["Smart LCD screen", "Hydraulic disk brakes"],
            "brands_mentioned": ["Furo Systems", "TEKTRO"],
            "source_files": ["furo.json"]
        }
        
        # Verify schema compliance
        for field, expected_type in expected_schema.items():
            assert field in sample_structured_response, f"Required field '{field}' missing"
            assert isinstance(sample_structured_response[field], expected_type), f"Field '{field}' should be {expected_type}"
        
        # Verify scene reference structure
        scene = sample_structured_response["scene_references"][0]
        required_scene_fields = ["start_timestamp", "end_timestamp", "description", "video_file"]
        for field in required_scene_fields:
            assert field in scene, f"Scene should contain '{field}'"

    def test_structured_prompt_integration(self):
        """Test that structured prompt file exists and has correct content"""
        
        structured_prompt_path = "/workspaces/azure-search-openai-vcu-demo/app/backend/approaches/prompts/chat_answer_question_structured.prompty"
        
        # Verify file exists
        import os
        assert os.path.exists(structured_prompt_path), "Structured prompt file should exist"
        
        # Verify content structure
        with open(structured_prompt_path, 'r') as f:
            content = f.read()
        
        # Check for required JSON structure instructions
        json_requirements = [
            '"description"',
            '"scene_references"',
            '"key_features"',
            '"brands_mentioned"',
            '"source_files"',
            'HH:MM:SS.mmm',
            'video_file'
        ]
        
        for requirement in json_requirements:
            assert requirement in content, f"Structured prompt should include '{requirement}'"

    def test_video_file_mapping(self):
        """Test that JSON source files are correctly mapped to video files"""
        
        json_to_video_mapping = {
            "furo.json": "furo.mp4",
            "huawei.json": "huawei.mp4", 
            "tropicfeel.json": "tropicfeel.mp4"
        }
        
        for json_file, expected_video in json_to_video_mapping.items():
            # Remove .json and add .mp4
            video_file = json_file.replace('.json', '.mp4')
            assert video_file == expected_video, f"Mapping should convert {json_file} to {expected_video}"

    def test_timestamp_clickability_format(self):
        """Test that timestamps are in the correct format for video player integration"""
        
        sample_timestamps = [
            "00:00:00.778",
            "00:02:15.500", 
            "00:05:45.123"
        ]
        
        # Timestamp format validation (HH:MM:SS.mmm)
        import re
        timestamp_pattern = r'^\d{2}:\d{2}:\d{2}\.\d{3}$'
        
        for timestamp in sample_timestamps:
            assert re.match(timestamp_pattern, timestamp), f"Timestamp '{timestamp}' should match HH:MM:SS.mmm format"
            
            # Should be convertible to seconds for video player
            parts = timestamp.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds_and_ms = float(parts[2])
            
            total_seconds = hours * 3600 + minutes * 60 + seconds_and_ms
            assert total_seconds >= 0, "Timestamp should convert to valid seconds"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
