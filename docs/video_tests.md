# Video Content Understanding Tests

This document describes the test suite for the video content understanding functionality added to the Azure Search OpenAI demo.

## Test Files Added

### 1. `test_video_integration.py`
**Purpose**: Integration tests that validate the complete video functionality pipeline

**Test Coverage**:
- **VideoPromptOptimization**: Tests the updated `chat_query_rewrite.prompty` file
  - Verifies video-specific patterns (StartTimestamp, EndTimestamp, brands)
  - Confirms healthcare patterns were replaced with video patterns
  - Validates YAML front matter syntax
- **VideoSearchPatterns**: Tests search optimization for video content
  - Timestamp-based query optimization
  - Brand-specific search patterns
- **VideoResponseFormatting**: Tests expected response formats
  - Scene timestamp format validation
  - Multi-scene response structure

### 2. `test_video_query_patterns.py`
**Purpose**: Unit tests for video query pattern recognition and optimization

**Test Coverage**:
- **VideoQueryPatterns**: Tests recognition of different query types
  - Timestamp queries ("What happens at 2 minutes?")
  - Brand queries ("Show me Furo bicycle features")
  - Feature queries ("Tell me about smart features")
- **VideoQueryRewriteExamples**: Tests query rewrite optimization quality
  - Completeness of example coverage
  - Quality of search term optimization
- **VideoDataCompatibility**: Tests compatibility with actual video data
  - Timestamp format validation (HH:MM:SS.mmm)
  - Brand extraction alignment
  - Object/feature compatibility
- **VideoResponseExpectations**: Tests expected response formats
  - Scene description format
  - Multi-scene response structure
  - Feature integration in responses

## Test Statistics

- **Total Tests**: 19 video-specific tests
- **Test Status**: All tests passing ✅
- **Coverage Areas**:
  - Query rewriting optimization (5 tests)
  - Data structure validation (4 tests)
  - Search pattern optimization (3 tests)
  - Response formatting (4 tests)
  - Integration validation (3 tests)

## Key Test Validations

### 1. Prompt Optimization Validation
```python
# Validates that chat_query_rewrite.prompty contains video patterns
video_patterns = ["StartTimestamp", "EndTimestamp", "Hive", "Furo", "Huawei"]
healthcare_patterns = ["health plans", "Northwind Health Plus"]  # Should be removed
```

### 2. Video Data Structure Validation
```python
# Validates video JSON files have expected timestamp structure
timestamp_pattern = r'^\d{2}:\d{2}:\d{2}\.\d{3}$'
# Example: "00:00:00.778"
```

### 3. Query Pattern Recognition
```python
# Tests various user query patterns
timestamp_queries = [
    "What happens at 2 minutes?",
    "Show me the scene at 00:02:30",
    "Tell me about the 1 minute mark"
]
```

### 4. Response Format Validation
```python
# Expected scene format in responses
scene_pattern = r'Scene from \d{2}:\d{2}:\d{2}\.\d{3} - \d{2}:\d{2}:\d{2}\.\d{3}: .+'
# Example: "Scene from 00:00:00.778 - 00:00:01.556: Description"
```

## Running the Tests

```bash
# Run all video tests
python -m pytest tests/test_video_*.py -v

# Run specific test categories
python -m pytest tests/test_video_integration.py -v
python -m pytest tests/test_video_query_patterns.py -v
```

## Test Benefits

1. **Regression Protection**: Ensures video functionality continues to work as expected
2. **Documentation**: Tests serve as living documentation of expected behavior
3. **Validation**: Confirms our prompt optimizations are working correctly
4. **Quality Assurance**: Validates data structure compatibility and response formats
5. **Future Development**: Provides foundation for testing additional video features

## Integration with Existing Tests

- Video tests are designed to complement existing test suite
- No conflicts with existing functionality tests
- Can be run independently or as part of full test suite
- Follow same pytest patterns as existing tests

The test suite provides comprehensive coverage of the video content understanding functionality, ensuring that our implementation of scene timestamp inclusion and video-optimized query rewriting works correctly.
