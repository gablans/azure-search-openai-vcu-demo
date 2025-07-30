import json
import pathlib
import re

import prompty
from openai.types.chat import ChatCompletionMessageParam


class PromptManager:

    def load_prompt(self, path: str):
        raise NotImplementedError

    def load_tools(self, path: str):
        raise NotImplementedError

    def render_prompt(self, prompt, data) -> list[ChatCompletionMessageParam]:
        raise NotImplementedError


class PromptyManager(PromptManager):

    PROMPTS_DIRECTORY = pathlib.Path(__file__).parent / "prompts"

    def load_prompt(self, path: str):
        return prompty.load(self.PROMPTS_DIRECTORY / path)

    def load_tools(self, path: str):
        return json.loads(open(self.PROMPTS_DIRECTORY / path).read())

    def render_prompt(self, prompt, data) -> list[ChatCompletionMessageParam]:
        """
        Render prompt using prompty but with custom parsing to avoid file loading errors.
        This prevents prompty from trying to load text content as image files.
        """
        # Create a custom parser that doesn't process inline images
        from prompty.parsers import PromptyChatParser
        
        class SafePromptyChatParser(PromptyChatParser):
            def parse_content(self, content: str):
                """Override parse_content to disable automatic image file loading"""
                # Instead of processing markdown images, just return the content as text
                # This prevents FileNotFoundError when content contains words like "frame"
                return content
        
        # Temporarily replace the default parser
        original_parser = prompty.InvokerFactory._parsers.get("prompty.chat")
        prompty.InvokerFactory.add_parser("prompty.chat", SafePromptyChatParser)
        
        try:
            # Use prompty to render the template with custom parser
            result = prompty.prepare(prompt, data)
            
            # Post-process the result to handle image_sources for GPT-4V
            if 'image_sources' in data and data['image_sources']:
                # Find the user message and add image content to it
                for message in result:
                    if message.get('role') == 'user':
                        content = message.get('content', '')
                        
                        # Create a content array with text and images
                        content_array = [{"type": "text", "text": content}]
                        
                        # Add each image as a separate content item
                        for image_source in data['image_sources']:
                            content_array.append({
                                "type": "image_url",
                                "image_url": {"url": image_source}
                            })
                        
                        # Replace the simple string content with the array
                        message['content'] = content_array
                        break
            
            return result
        finally:
            # Restore the original parser
            if original_parser:
                prompty.InvokerFactory.add_parser("prompty.chat", original_parser)
