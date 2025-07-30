import json
import logging
import re
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Awaitable
from typing import Any, Optional, Union, cast

from openai import AsyncStream
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessageParam,
)

from approaches.approach import (
    Approach,
    ExtraInfo,
)


class ChatApproach(Approach, ABC):
    """
    Base class for chat-based approaches that use the ChatCompletion API.
    """

    def _parse_and_format_structured_response(self, content: str) -> tuple[Optional[dict], str]:
        """
        Parse JSON response with fallback handling for truncated or malformed JSON.
        Returns (parsed_json, formatted_content)
        """
        try:
            # Try parsing the full content
            structured_data = json.loads(content)
            return structured_data, structured_data.get("description", content)
        except json.JSONDecodeError as e:
            logging.warning(f"Initial JSON parse failed: {e}")
            
            # Try to fix common JSON issues
            fixed_content = self._attempt_json_repair(content)
            if fixed_content:
                try:
                    structured_data = json.loads(fixed_content)
                    return structured_data, structured_data.get("description", content)
                except json.JSONDecodeError:
                    logging.warning("JSON repair attempt failed")
            
            return None, content

    def _attempt_json_repair(self, content: str) -> Optional[str]:
        """
        Attempt to repair common JSON issues like missing closing braces or truncation.
        """
        try:
            content = content.strip()
            
            # First, try to remove any trailing non-JSON content
            # Look for the end of the main JSON object
            json_end_patterns = [
                r'}\s*$',  # Ends with closing brace
                r']\s*$',  # Ends with closing bracket
                r'}\s*\n\s*[^{}\[\]"]+.*$',  # Closing brace followed by non-JSON text
                r']\s*\n\s*[^{}\[\]"]+.*$',  # Closing bracket followed by non-JSON text
            ]
            
            for pattern in json_end_patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match and content.find(match.group(0)) > content.find('{'):
                    # Found trailing content after JSON structure, truncate it
                    json_part = content[:match.start() + 1]  # Include the closing brace/bracket
                    content = json_part
                    break
            
            # Now try to balance the braces and brackets
            # Count unmatched opening braces and brackets
            brace_count = 0
            bracket_count = 0
            in_string = False
            escape_next = False
            
            for char in content:
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                    
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                    elif char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
            
            # Add missing closing brackets and braces
            if bracket_count > 0:
                content += ']' * bracket_count
                logging.info(f"Added {bracket_count} closing brackets")
                
            if brace_count > 0:
                content += '}' * brace_count
                logging.info(f"Added {brace_count} closing braces")
                
            # Clean up any trailing commas before closing brackets/braces
            content = re.sub(r',(\s*[}\]])', r'\1', content)
            
            return content
            
        except Exception as e:
            logging.warning(f"JSON repair failed: {e}")
            return None

    def _convert_failed_json_to_readable(self, content: str) -> str:
        """
        Convert failed JSON parsing to a readable format by extracting key information.
        """
        try:
            # Check if content is extremely long and truncate if needed
            if len(content) > 5000:  # If longer than 5000 characters, it's likely too long
                return f"I found detailed information about products and brands in your advertisement library, but the response was too large to format properly. Here's a summary:\n\n{content[:1000]}..."
            
            # Try to extract description if it exists
            desc_match = re.search(r'"description":\s*"([^"]*)"', content)
            if desc_match:
                description = desc_match.group(1)
                result = description + "\n\n"
            else:
                result = "I found comprehensive information about products and brands in the advertisement library:\n\n"
            
            # Extract scene references
            scene_matches = re.findall(r'"start_timestamp":\s*"([^"]*)".*?"end_timestamp":\s*"([^"]*)".*?"description":\s*"([^"]*)".*?"video_file":\s*"([^"]*)"', content, re.DOTALL)
            if scene_matches:
                result += "**Scene References:**\n"
                for start, end, desc, video in scene_matches[:10]:  # Limit to first 10 to avoid overwhelming
                    result += f"• **{start} - {end}** ({video}): {desc}\n"
                if len(scene_matches) > 10:
                    result += f"• ... and {len(scene_matches) - 10} more scenes\n"
                result += "\n"
            
            # Extract key features
            features_match = re.search(r'"key_features":\s*\[(.*?)\]', content, re.DOTALL)
            if features_match:
                features_content = features_match.group(1)
                features = re.findall(r'"([^"]*)"', features_content)
                if features:
                    result += "**Key Features:**\n"
                    for feature in features:
                        result += f"• {feature}\n"
                    result += "\n"
            
            # Extract brands
            brands_match = re.search(r'"brands_mentioned":\s*\[(.*?)\]', content, re.DOTALL)
            if brands_match:
                brands_content = brands_match.group(1)
                brands = re.findall(r'"([^"]*)"', brands_content)
                if brands:
                    result += "**Brands Mentioned:**\n"
                    for brand in brands:
                        result += f"• {brand}\n"
                    result += "\n"
            
            return result
            
        except Exception as e:
            logging.error(f"Failed to convert JSON to readable format: {e}")
            # Last resort: return first 1000 characters with a note
            return f"I found detailed information about products and brands in your advertisement library, but the response was too large to format properly. Here's a summary:\n\n{content[:1000]}..."

    NO_RESPONSE = "0"

    @abstractmethod
    async def run_until_final_call(
        self, messages, overrides, auth_claims, should_stream
    ) -> tuple[ExtraInfo, Union[Awaitable[ChatCompletion], Awaitable[AsyncStream[ChatCompletionChunk]]]]:
        pass

    def get_search_query(self, chat_completion: ChatCompletion, user_query: str):
        response_message = chat_completion.choices[0].message

        if response_message.tool_calls:
            for tool in response_message.tool_calls:
                if tool.type != "function":
                    continue
                function = tool.function
                if function.name == "search_sources":
                    arg = json.loads(function.arguments)
                    search_query = arg.get("search_query", self.NO_RESPONSE)
                    if search_query != self.NO_RESPONSE:
                        return search_query
        elif query_text := response_message.content:
            if query_text.strip() != self.NO_RESPONSE:
                return query_text
        return user_query

    def extract_followup_questions(self, content: Optional[str]):
        if content is None:
            return content, []
        return content.split("<<")[0], re.findall(r"<<([^>>]+)>>", content)

    async def run_without_streaming(
        self,
        messages: list[ChatCompletionMessageParam],
        overrides: dict[str, Any],
        auth_claims: dict[str, Any],
        session_state: Any = None,
    ) -> dict[str, Any]:
        extra_info, chat_coroutine = await self.run_until_final_call(
            messages, overrides, auth_claims, should_stream=False
        )
        chat_completion_response: ChatCompletion = await cast(Awaitable[ChatCompletion], chat_coroutine)
        content = chat_completion_response.choices[0].message.content
        role = chat_completion_response.choices[0].message.role
        
        # Handle structured response parsing
        use_structured_response = overrides.get("use_structured_response", False)
        if use_structured_response:
            parsed_json, formatted_content = self._parse_and_format_structured_response(content)
            if parsed_json:
                extra_info.structured_response = parsed_json
                content = formatted_content
                logging.info(f"Successfully parsed structured response with {len(parsed_json.get('scene_references', []))} scenes")
            else:
                # If JSON parsing fails completely, convert to readable format
                content = self._convert_failed_json_to_readable(content)
                extra_info.structured_response = None
                logging.warning("Failed to parse JSON, converted to readable format")
        
        if overrides.get("suggest_followup_questions"):
            content, followup_questions = self.extract_followup_questions(content)
            extra_info.followup_questions = followup_questions
        # Assume last thought is for generating answer
        if self.include_token_usage and extra_info.thoughts and chat_completion_response.usage:
            extra_info.thoughts[-1].update_token_usage(chat_completion_response.usage)
        chat_app_response = {
            "message": {"content": content, "role": role},
            "context": extra_info,
            "session_state": session_state,
        }
        return chat_app_response

    async def run_with_streaming(
        self,
        messages: list[ChatCompletionMessageParam],
        overrides: dict[str, Any],
        auth_claims: dict[str, Any],
        session_state: Any = None,
    ) -> AsyncGenerator[dict, None]:
        extra_info, chat_coroutine = await self.run_until_final_call(
            messages, overrides, auth_claims, should_stream=True
        )
        chat_coroutine = cast(Awaitable[AsyncStream[ChatCompletionChunk]], chat_coroutine)
        yield {"delta": {"role": "assistant"}, "context": extra_info, "session_state": session_state}

        followup_questions_started = False
        followup_content = ""
        async for event_chunk in await chat_coroutine:
            # "2023-07-01-preview" API version has a bug where first response has empty choices
            event = event_chunk.model_dump()  # Convert pydantic model to dict
            if event["choices"]:
                # No usage during streaming
                completion = {
                    "delta": {
                        "content": event["choices"][0]["delta"].get("content"),
                        "role": event["choices"][0]["delta"]["role"],
                    }
                }
                # if event contains << and not >>, it is start of follow-up question, truncate
                content = completion["delta"].get("content")
                content = content or ""  # content may either not exist in delta, or explicitly be None
                if overrides.get("suggest_followup_questions") and "<<" in content:
                    followup_questions_started = True
                    earlier_content = content[: content.index("<<")]
                    if earlier_content:
                        completion["delta"]["content"] = earlier_content
                        yield completion
                    followup_content += content[content.index("<<") :]
                elif followup_questions_started:
                    followup_content += content
                else:
                    yield completion
            else:
                # Final chunk at end of streaming should contain usage
                # https://cookbook.openai.com/examples/how_to_stream_completions#4-how-to-get-token-usage-data-for-streamed-chat-completion-response
                if event_chunk.usage and extra_info.thoughts and self.include_token_usage:
                    extra_info.thoughts[-1].update_token_usage(event_chunk.usage)
                    yield {"delta": {"role": "assistant"}, "context": extra_info, "session_state": session_state}

        if followup_content:
            _, followup_questions = self.extract_followup_questions(followup_content)
            yield {
                "delta": {"role": "assistant"},
                "context": {"context": extra_info, "followup_questions": followup_questions},
            }

    async def run(
        self,
        messages: list[ChatCompletionMessageParam],
        session_state: Any = None,
        context: dict[str, Any] = {},
    ) -> dict[str, Any]:
        overrides = context.get("overrides", {})
        auth_claims = context.get("auth_claims", {})
        return await self.run_without_streaming(messages, overrides, auth_claims, session_state)

    async def run_stream(
        self,
        messages: list[ChatCompletionMessageParam],
        session_state: Any = None,
        context: dict[str, Any] = {},
    ) -> AsyncGenerator[dict[str, Any], None]:
        overrides = context.get("overrides", {})
        auth_claims = context.get("auth_claims", {})
        return self.run_with_streaming(messages, overrides, auth_claims, session_state)
