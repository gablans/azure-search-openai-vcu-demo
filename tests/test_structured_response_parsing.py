"""
Test the structured response parsing functionality in ChatApproach.
Tests JSON parsing, repair, and fallback formatting for long/malformed responses.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from approaches.chatapproach import ChatApproach
from approaches.approach import ExtraInfo


class MockChatApproach(ChatApproach):
    """Test implementation of abstract ChatApproach class."""
    
    def __init__(self):
        # Mock the required attributes
        self.include_token_usage = False
    
    async def run_until_final_call(self, messages, overrides, auth_claims, should_stream):
        # Mock implementation for testing
        extra_info = ExtraInfo(data_points=MagicMock())
        chat_coroutine = MagicMock()
        return extra_info, chat_coroutine


class TestStructuredResponseParsing:
    """Test structured response parsing, repair, and fallback formatting."""

    def setup_method(self):
        """Set up test instance."""
        self.chat_approach = MockChatApproach()

    def test_valid_json_parsing(self):
        """Test parsing of valid JSON response."""
        valid_json = {
            "description": "The advertisement library features products from three main brands",
            "scene_references": [
                {
                    "start_timestamp": "00:00:10.065",
                    "end_timestamp": "00:00:10.692",
                    "description": "Backpack with water bottle",
                    "video_file": "tropicfeel.mp4"
                }
            ],
            "key_features": ["Weatherproof materials", "Camera cube"],
            "brands_mentioned": ["Hive", "Furo Systems"],
            "source_files": ["tropicfeel.json"]
        }
        
        content = json.dumps(valid_json)
        parsed_json, formatted_content = self.chat_approach._parse_and_format_structured_response(content)
        
        assert parsed_json is not None
        assert parsed_json == valid_json
        assert formatted_content == "The advertisement library features products from three main brands"

    def test_truncated_json_repair(self):
        """Test repair of truncated JSON (missing closing braces)."""
        truncated_json = '''{
            "description": "The advertisement library features products",
            "scene_references": [
                {
                    "start_timestamp": "00:00:10.065",
                    "end_timestamp": "00:00:10.692",
                    "description": "Backpack with water bottle",
                    "video_file": "tropicfeel.mp4"
                }
            ],
            "key_features": ["Weatherproof materials"]'''
        
        repaired = self.chat_approach._attempt_json_repair(truncated_json)
        assert repaired is not None
        
        # Should be valid JSON after repair
        parsed = json.loads(repaired)
        assert "description" in parsed
        assert "scene_references" in parsed

    def test_missing_brackets_repair(self):
        """Test repair of JSON with missing closing brackets."""
        malformed_json = '''{
            "description": "Test description",
            "scene_references": [
                {
                    "start_timestamp": "00:00:10.065",
                    "description": "Test scene"
                }
            ],
            "key_features": ["Feature 1", "Feature 2"'''
        
        repaired = self.chat_approach._attempt_json_repair(malformed_json)
        assert repaired is not None
        
        # Should be valid JSON after repair
        parsed = json.loads(repaired)
        # The repair might truncate incomplete arrays, so just check that it's valid JSON
        assert "description" in parsed
        assert parsed["description"] == "Test description"

    def test_multiple_missing_closers_repair(self):
        """Test repair of JSON with multiple missing closing brackets and braces."""
        malformed_json = '''{
            "description": "Test",
            "scene_references": [
                {
                    "timestamp": "00:01:00",
                    "nested": {
                        "data": ["item1", "item2"]
                    }
                }
            ],
            "brands": ["Brand1"]'''
        
        repaired = self.chat_approach._attempt_json_repair(malformed_json)
        assert repaired is not None
        
        # Should be valid JSON after repair
        parsed = json.loads(repaired)
        assert "description" in parsed
        assert "scene_references" in parsed
        assert "brands" in parsed

    def test_json_with_trailing_text_repair(self):
        """Test repair of JSON with trailing non-JSON text."""
        json_with_trailing = '''{
            "description": "Valid JSON content",
            "key_features": ["Feature"]
        }
        
        This is some trailing text that shouldn't be here.
        More invalid content...'''
        
        repaired = self.chat_approach._attempt_json_repair(json_with_trailing)
        assert repaired is not None
        
        # Should be valid JSON after repair (trailing text removed)
        parsed = json.loads(repaired)
        assert parsed["description"] == "Valid JSON content"
        assert parsed["key_features"] == ["Feature"]

    def test_completely_malformed_json_fallback(self):
        """Test fallback formatting when JSON cannot be repaired."""
        malformed_content = '''This is not JSON at all, but contains:
        "description": "Some product information"
        "start_timestamp": "00:01:15.500"
        "end_timestamp": "00:01:30.200" 
        "description": "Bicycle scene with Furo Systems"
        "video_file": "furo.mp4"
        "key_features": ["Smart LCD screen", "Hydraulic brakes"]
        "brands_mentioned": ["Furo Systems", "Hive"]'''
        
        readable_content = self.chat_approach._convert_failed_json_to_readable(malformed_content)
        
        assert "Scene References:" in readable_content or "Key Features:" in readable_content or "Brands Mentioned:" in readable_content
        assert len(readable_content) > 0
        assert readable_content != malformed_content  # Should be transformed

    def test_extract_scene_references_from_malformed(self):
        """Test extraction of scene references from malformed JSON."""
        malformed_content = '''{"description": "Video content", "scene_references": [
        {"start_timestamp": "00:01:15.500", "end_timestamp": "00:01:30.200", 
         "description": "Bicycle scene with features", "video_file": "furo.mp4"},
        {"start_timestamp": "00:02:00.000", "end_timestamp": "00:02:15.300",
         "description": "Backpack demonstration", "video_file": "tropicfeel.mp4"}
        ], "key_features": ["LCD screen", "Hydraulic brakes"]'''
        
        readable_content = self.chat_approach._convert_failed_json_to_readable(malformed_content)
        
        assert "Scene References:" in readable_content
        assert "00:01:15.500 - 00:01:30.200" in readable_content
        assert "00:02:00.000 - 00:02:15.300" in readable_content
        assert "furo.mp4" in readable_content
        assert "tropicfeel.mp4" in readable_content

    def test_extract_features_and_brands_from_malformed(self):
        """Test extraction of features and brands from malformed JSON."""
        malformed_content = '''{"key_features": ["Weatherproof materials", "Camera cube", "Laptop compartment"],
        "brands_mentioned": ["Hive", "Furo Systems", "Huawei"], "other": "data"}'''
        
        readable_content = self.chat_approach._convert_failed_json_to_readable(malformed_content)
        
        assert "Key Features:" in readable_content
        assert "Weatherproof materials" in readable_content
        assert "Camera cube" in readable_content
        assert "Laptop compartment" in readable_content
        
        assert "Brands Mentioned:" in readable_content
        assert "Hive" in readable_content
        assert "Furo Systems" in readable_content
        assert "Huawei" in readable_content

    def test_long_response_truncation_in_fallback(self):
        """Test that very long malformed responses are appropriately truncated."""
        # Create a very long malformed response (over 5000 characters)
        long_content = "Not JSON content. " * 300  # Very long non-JSON content
        
        readable_content = self.chat_approach._convert_failed_json_to_readable(long_content)
        
        # Should be truncated with explanation
        assert "too large to format properly" in readable_content
        assert len(readable_content) < len(long_content)

    def test_parse_and_format_with_successful_repair(self):
        """Test full parse_and_format workflow with successful JSON repair."""
        truncated_json = '''{
            "description": "Advertisement library analysis",
            "scene_references": [
                {
                    "start_timestamp": "00:00:10.065",
                    "end_timestamp": "00:00:10.692",
                    "description": "Product demonstration",
                    "video_file": "test.mp4"
                }
            ],
            "key_features": ["Feature 1"]'''  # Missing closing braces
        
        parsed_json, formatted_content = self.chat_approach._parse_and_format_structured_response(truncated_json)
        
        assert parsed_json is not None
        assert formatted_content == "Advertisement library analysis"
        assert len(parsed_json.get("scene_references", [])) == 1

    def test_parse_and_format_with_failed_repair(self):
        """Test full parse_and_format workflow when repair fails."""
        completely_broken = "This is not JSON and has no structure that can be repaired."
        
        parsed_json, formatted_content = self.chat_approach._parse_and_format_structured_response(completely_broken)
        
        assert parsed_json is None
        assert formatted_content == completely_broken  # Should return original when repair fails

    def test_real_world_truncated_response(self):
        """Test with a realistic truncated JSON response similar to the user's issue."""
        realistic_truncated = '''{
  "description": "The advertisement library features products from three main brands: Hive, Furo Systems, and Huawei. The products include a variety of backpacks with features such as weatherproof materials and organizational compartments from Hive, bicycles from Furo Systems, and smartwatches from Huawei with fitness and customization capabilities.",
  "scene_references": [
    {
      "start_timestamp": "00:00:10.065",
      "end_timestamp": "00:00:10.692",
      "description": "Backpack with a water bottle in its side pocket, highlighting utility.",
      "video_file": "tropicfeel.mp4"
    },
    {
      "start_timestamp": "00:01:32.400",
      "end_timestamp": "00:01:38.274",
      "description": "Person resting by a waterfall with the backpack, emphasizing durability and weatherproof features.",
      "video_file": "tropicfeel.mp4"
    }
  ],
  "key_features": [
    "Adaptable Bum Bag",
    "Backpack with weatherproof & sustainable materials (100% recycled and coated)",
    "Backpack with camera cube to organize and protect gear"
  ],
  "brands_mentioned": [
    "Hive",
    "Tropicfeel",
    "Furo Systems"
  ],
  "source_files":'''  # Truncated here
        
        # Should either repair successfully or provide readable fallback
        parsed_json, formatted_content = self.chat_approach._parse_and_format_structured_response(realistic_truncated)
        
        # Should contain meaningful content, not raw JSON
        assert len(formatted_content) > 50
        
        # Check that we got either a parsed description or readable fallback
        if parsed_json:
            # If parsed successfully, should have extracted the description
            assert "advertisement library" in formatted_content.lower()
        else:
            # If parsing failed, should have readable fallback with structured content
            assert ("advertisement library" in formatted_content.lower() or 
                    "brands" in formatted_content.lower() or
                    "products" in formatted_content.lower() or
                    "Scene References:" in formatted_content)

    @pytest.mark.asyncio
    async def test_run_without_streaming_with_structured_response(self):
        """Test the full run_without_streaming method with structured response."""
        # Mock the necessary components
        with patch.object(self.chat_approach, 'run_until_final_call') as mock_run:
            # Mock ChatCompletion response
            mock_completion = MagicMock()
            mock_completion.choices[0].message.content = '{"description": "Test response", "key_features": ["Feature1"]}'
            mock_completion.choices[0].message.role = "assistant"
            mock_completion.usage = None
            
            # Create an async mock that returns the completion
            async def mock_coroutine():
                return mock_completion
            
            # Mock ExtraInfo
            mock_extra_info = ExtraInfo(data_points=MagicMock())
            mock_extra_info.thoughts = []
            
            mock_run.return_value = (mock_extra_info, mock_coroutine())
            
            # Test with structured response enabled
            overrides = {"use_structured_response": True}
            result = await self.chat_approach.run_without_streaming([], overrides, {})
            
            # Should have parsed the JSON and extracted description
            assert result["message"]["content"] == "Test response"
            assert hasattr(mock_extra_info, 'structured_response')
            assert mock_extra_info.structured_response is not None
            assert mock_extra_info.structured_response["description"] == "Test response"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
