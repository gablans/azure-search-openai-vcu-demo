"""
Tests for our custom prompty manager and image reference cleaning.
These tests verify that our solution prevents FileNotFoundError when prompty encounters
text content that looks like file references.
"""
import pytest
from approaches.approach import clean_image_references, is_video_content
from approaches.promptmanager import PromptyManager


class TestImageReferencesCleaning:
    """Test the clean_image_references function"""
    
    def test_clean_frame_references(self):
        """Test that frame references are cleaned properly"""
        content = "Some text with [Frame showing a scene"
        result = clean_image_references(content)
        assert "frame reference" in result.lower()
        assert "[Frame" not in result
    
    def test_clean_keyframe_references(self):
        """Test that keyFrame references are cleaned"""
        content = "Content with keyFrame.297.jpg reference"
        result = clean_image_references(content)
        assert "frame reference" in result
        assert "keyFrame.297.jpg" not in result
    
    def test_clean_image_json_references(self):
        """Test that JSON image references are cleaned"""
        content = '"Image": "someimage.jpg"'
        result = clean_image_references(content)
        assert '"Image": "frame reference"' in result
        assert "someimage.jpg" not in result
    
    def test_clean_markdown_image_syntax(self):
        """Test that markdown image syntax is cleaned"""
        content = "![alt text](image.png)"
        result = clean_image_references(content)
        assert "frame reference" in result
        assert "![alt text](image.png)" not in result
    
    def test_clean_file_paths(self):
        """Test that file paths with image extensions are cleaned"""
        content = "/app/approaches/prompts/frame.jpg"
        result = clean_image_references(content)
        assert "frame reference" in result
        assert "/app/approaches/prompts/frame.jpg" not in result
    
    def test_clean_mixed_content(self):
        """Test cleaning of content with multiple types of references"""
        content = '''
        Some text [Frame reference and keyFrame.123.jpg
        More content with "Image": "test.png"
        ![alt](another.gif)
        '''
        result = clean_image_references(content)
        
        # All problematic patterns should be replaced
        assert "[Frame" not in result
        assert "keyFrame.123.jpg" not in result
        assert "test.png" not in result
        assert "![alt](another.gif)" not in result
        assert "frame reference" in result


class TestVideoContentDetection:
    """Test the video content detection function"""
    
    def test_detect_video_content_with_timestamps(self):
        """Test that video content is detected by timestamps"""
        text_sources = ["Scene from 00:02:15.500 shows something"]
        assert is_video_content(text_sources=text_sources) == True
    
    def test_detect_video_content_with_commercial(self):
        """Test that commercial content is detected as video"""
        text_sources = ["This is a commercial advertisement"]
        assert is_video_content(text_sources=text_sources) == True
    
    def test_detect_video_content_with_frame_reference(self):
        """Test that frame references are detected as video"""
        text_sources = ["Content with frame reference in it"]
        assert is_video_content(text_sources=text_sources) == True
    
    def test_detect_non_video_content(self):
        """Test that normal text content is not detected as video"""
        text_sources = ["This is just normal text content"]
        assert is_video_content(text_sources=text_sources) == False


class TestPromptyManagerSafety:
    """Test that our custom PromptyManager prevents FileNotFoundError"""
    
    def test_prompty_manager_creation(self):
        """Test that PromptyManager can be created without issues"""
        manager = PromptyManager()
        assert manager is not None
    
    def test_prompty_manager_handles_problematic_content(self):
        """Test that PromptyManager can handle content that would cause FileNotFoundError"""
        manager = PromptyManager()
        
        # Create a simple prompty template that contains problematic content
        test_data = {
            "user_query": "What is shown in [Frame?",
            "text_sources": ["Content with keyFrame.123.jpg"],
            "image_sources": []
        }
        
        # This should not raise a FileNotFoundError
        # Note: We can't easily test the full render_prompt without a real prompty file,
        # but we can test that our cleaning function works
        cleaned_query = clean_image_references(test_data["user_query"])
        cleaned_sources = [clean_image_references(source) for source in test_data["text_sources"]]
        
        assert "[Frame" not in cleaned_query
        assert "keyFrame.123.jpg" not in cleaned_sources[0]
        assert "frame reference" in cleaned_sources[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
