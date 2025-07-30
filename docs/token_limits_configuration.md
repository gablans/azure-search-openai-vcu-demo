# Token Limits and Timeout Configuration Guide

This document explains how to configure token limits and timeouts to prevent truncated responses and raw JSON display issues.

## Environment Variables for Token Limits

You can now configure token limits using environment variables:

### 1. Standard Model Token Limits
```bash
# Default response token limit for standard models (default: 4096)
AZURE_OPENAI_MAX_TOKENS=8192

# Token limit for reasoning models like o1, o3 (default: 16384) 
AZURE_OPENAI_REASONING_MAX_TOKENS=16384
```

### 2. How to Set Environment Variables

**For local development (.env file):**
```bash
echo "AZURE_OPENAI_MAX_TOKENS=8192" >> .env
echo "AZURE_OPENAI_REASONING_MAX_TOKENS=16384" >> .env
```

**For Azure deployment (azd env set):**
```bash
azd env set AZURE_OPENAI_MAX_TOKENS 8192
azd env set AZURE_OPENAI_REASONING_MAX_TOKENS 16384
```

## Current Configuration Changes Made

### 1. Token Limits Increased
- **Standard models**: 1024 → 4096 tokens (4x increase)
- **Reasoning models**: 8192 → 16384 tokens (2x increase)  
- **Vision responses**: 1024 → 4096 tokens (4x increase)

### 2. Timeout Settings Extended
- **Gunicorn timeout**: 230 → 480 seconds (2x increase)
- Allows for longer AI processing time

### 3. Configurable via Environment Variables
- `AZURE_OPENAI_MAX_TOKENS`: Controls standard model token limits
- `AZURE_OPENAI_REASONING_MAX_TOKENS`: Controls reasoning model token limits

## Model-Specific Recommendations

### For Video Analysis (GPT-4V)
```bash
# Recommended for detailed video analysis with structured responses
AZURE_OPENAI_MAX_TOKENS=8192
```

### For Complex Document Analysis
```bash
# For handling large document analysis
AZURE_OPENAI_MAX_TOKENS=16384
AZURE_OPENAI_REASONING_MAX_TOKENS=16384
```

### For Real-time Chat
```bash
# Balanced performance and response time
AZURE_OPENAI_MAX_TOKENS=4096  # Default
AZURE_OPENAI_REASONING_MAX_TOKENS=16384  # Default
```

## Cost Considerations

Higher token limits will increase costs. Monitor usage with these guidelines:

- **4096 tokens**: ~3000 words, suitable for most responses
- **8192 tokens**: ~6000 words, good for detailed analysis
- **16384 tokens**: ~12000 words, for comprehensive reports
- **32768 tokens**: ~24000 words, for extensive analysis

## Testing the Changes

Run the existing tests to ensure no regressions:
```bash
python -m pytest tests/test_structured_response_parsing.py -v
python -m pytest tests/test_chatapproach.py -v
```

## Troubleshooting

If you still see truncated responses after increasing limits:

1. **Check model limits**: Ensure your Azure OpenAI model supports the token count
2. **Monitor costs**: Higher limits = higher costs per request
3. **Verify environment variables**: Use `azd env get-values` to confirm settings
4. **Check application logs**: Look for timeout or token limit warnings

## Fallback Strategy

The application now includes robust JSON parsing and repair logic, so even if responses are truncated, users will see readable content instead of raw JSON.
