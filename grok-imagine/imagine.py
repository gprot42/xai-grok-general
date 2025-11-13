#!/usr/bin/env python3
"""
X.AI Image Generation (Grok Imagine) Demo

This script demonstrates how to use the x.ai Image Generation API to:
- Generate images from text prompts
- Download and save images as JPEG files
- Support multiple image generation

Requirements:
    pip install requests python-dotenv pillow
    # or using uv:
    uv pip install requests python-dotenv pillow

Usage:
    # Generate a single image with default prompt
    python imagine.py
    
    # Generate image with custom prompt
    python imagine.py "A serene landscape with mountains at sunset"
    
    # Generate multiple images (default is 1)
    python imagine.py "A futuristic city" --count 2
    
    # Specify output directory
    python imagine.py "Abstract art" --output ./images
    
    # All options together
    python imagine.py "A cat in space" --count 3 --output ./my_images
"""

import os
import sys
import argparse
import requests
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load from .env in current directory or parent directories
    load_dotenv()
    # Also try loading from the script's directory
    load_dotenv(Path(__file__).parent / '.env')
    # Try parent directory too
    load_dotenv(Path(__file__).parent.parent / '.env')
except ImportError:
    # python-dotenv not installed, will fall back to environment variables only
    pass

# Try to import PIL for image processing (optional)
try:
    from PIL import Image
    from io import BytesIO
    PIL_SUPPORT = True
except ImportError:
    PIL_SUPPORT = False


class XAIImageAPI:
    """Wrapper for X.AI Image Generation API operations"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "XAI_API_KEY not found. Please either:\n"
                "  1. Set environment variable: export XAI_API_KEY='your-key'\n"
                "  2. Create a .env file with: XAI_API_KEY=your-key\n"
                "  3. Copy .env.example to .env and add your key"
            )
        
        self.base_url = "https://api.x.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_image(self, prompt, n=1, size=None, response_format="url"):
        """
        Generate an image using X.AI's Grok Imagine API (Aurora model)
        
        Args:
            prompt (str): Text description of the image to generate
            n (int): Number of images to generate (1-10)
            size (str): Size parameter (not currently supported by X.AI API, defaults to 1024x768)
            response_format (str): Format of the response ("url" or "base64")
        
        Returns:
            dict: Response containing image URLs or base64 encoded images
        """
        url = f"{self.base_url}/images/generations"
        
        payload = {
            "model": "grok-2-image",  # Aurora image generation model
            "prompt": prompt,
            "n": n,
            "response_format": response_format
        }
        
        # Note: X.AI API does not currently support size, quality, style, or aspect_ratio parameters
        # Images are generated at the default size: 1024x768
        # Pricing: $0.07 per image
        
        response = requests.post(
            url,
            headers=self.headers,
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def download_image(self, image_url, output_path):
        """
        Download an image from a URL and save it to disk
        
        Args:
            image_url (str): URL of the image to download
            output_path (str): Path where to save the image
        
        Returns:
            str: Path to the saved image
        """
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the image
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return str(output_path)
    
    def convert_to_jpeg(self, image_path):
        """
        Convert an image to JPEG format if it's not already
        
        Args:
            image_path (str): Path to the image file
        
        Returns:
            str: Path to the JPEG image
        """
        if not PIL_SUPPORT:
            print("⚠ Pillow not installed. Cannot convert to JPEG.")
            return image_path
        
        image_path = Path(image_path)
        
        # If already JPEG, return as is
        if image_path.suffix.lower() in ['.jpg', '.jpeg']:
            return str(image_path)
        
        # Open and convert to JPEG
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = rgb_img
            
            # Save as JPEG
            jpeg_path = image_path.with_suffix('.jpg')
            img.save(jpeg_path, 'JPEG', quality=95)
        
        # Remove original if different
        if jpeg_path != image_path:
            image_path.unlink()
        
        return str(jpeg_path)


def sanitize_filename(text, max_length=50):
    """
    Create a safe filename from text
    
    Args:
        text (str): Text to convert to filename
        max_length (int): Maximum length of the filename
    
    Returns:
        str: Sanitized filename
    """
    # Remove or replace unsafe characters
    safe_chars = []
    for char in text[:max_length]:
        if char.isalnum() or char in (' ', '-', '_'):
            safe_chars.append(char)
        elif char in ('/\\', ':', '*', '?', '"', '<', '>', '|'):
            safe_chars.append('_')
    
    return ''.join(safe_chars).strip().replace(' ', '_')


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    """Main function to generate images from prompts"""
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Generate images using X.AI Grok Imagine API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "A beautiful sunset over the ocean"
  %(prog)s "Abstract geometric patterns" --count 3
  %(prog)s "Futuristic robot" --output ./my_images
        """
    )
    
    parser.add_argument(
        '--count', '-n',
        type=int,
        default=1,
        help='Number of images to generate (1-10, default: 1)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='./generated_images',
        help='Output directory for generated images (default: ./generated_images)'
    )
    
    parser.add_argument(
        '--size', '-s',
        type=str,
        default='1024x1024',
        help='Image size in WIDTHxHEIGHT format (e.g., 1024x1024, 2048x2048, 1792x1024). Common: 256x256, 512x512, 1024x1024, 2048x2048, 1792x1024. Default: 1024x1024'
    )
    
    parser.add_argument(
        'prompt',
        nargs='?',
        default="A majestic dragon flying over a medieval castle at sunset",
        help='Text prompt describing the image to generate (default: sample prompt)'
    )
    
    args = parser.parse_args()
    
    # Validate count
    if args.count < 1 or args.count > 10:
        print("❌ Error: Count must be between 1 and 10", file=sys.stderr)
        sys.exit(1)
    
    print_section("X.AI Grok Imagine - Image Generation")
    
    try:
        # Show API key source for debugging
        api_key_from_env = os.getenv("XAI_API_KEY")
        if api_key_from_env:
            key_preview = api_key_from_env[:8] + "..." if len(api_key_from_env) > 8 else "***"
            print(f"✓ Found XAI_API_KEY in environment: {key_preview}")
        
        # Initialize the API client
        api = XAIImageAPI()
        print("✓ API client initialized successfully")
        
        # Display generation parameters
        print(f"\n📝 Generation Parameters:")
        print(f"  Prompt: \"{args.prompt}\"")
        print(f"  Count: {args.count}")
        print(f"  Size: {args.size} (note: size parameter not currently supported by X.AI API)")
        print(f"  Output: {args.output}")
        
        # Generate images
        print_section("Generating Images")
        print(f"⏳ Generating {args.count} image(s)...")
        print("   This may take a moment...\n")
        
        response = api.generate_image(
            prompt=args.prompt,
            n=args.count,
            size=args.size,
            response_format="url"
        )
        
        print(f"✓ Successfully generated {len(response.get('data', []))} image(s)!")
        
        # Download and save images
        print_section("Downloading Images")
        
        # Create timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_slug = sanitize_filename(args.prompt, max_length=30)
        
        saved_files = []
        
        for idx, image_data in enumerate(response.get('data', []), 1):
            image_url = image_data.get('url')
            
            if not image_url:
                print(f"⚠ No URL found for image {idx}")
                continue
            
            # Create filename
            if args.count == 1:
                filename = f"{prompt_slug}_{timestamp}.jpg"
            else:
                filename = f"{prompt_slug}_{timestamp}_{idx}.jpg"
            
            output_path = Path(args.output) / filename
            
            try:
                print(f"⏳ Downloading image {idx}/{args.count}...")
                
                # Download the image
                temp_path = api.download_image(image_url, output_path.with_suffix('.tmp'))
                
                # Convert to JPEG
                final_path = api.convert_to_jpeg(temp_path)
                
                # Rename to final name
                final_path = Path(final_path)
                if final_path.name != filename:
                    final_output = output_path
                    final_path.rename(final_output)
                    final_path = final_output
                
                saved_files.append(str(final_path))
                
                # Get file size
                file_size = final_path.stat().st_size
                size_kb = file_size / 1024
                
                print(f"✓ Saved: {final_path.name} ({size_kb:.1f} KB)")
                
            except Exception as e:
                print(f"✗ Failed to download image {idx}: {str(e)}")
        
        # Summary
        print_section("Summary")
        print(f"✓ Successfully saved {len(saved_files)} image(s)")
        print(f"\n📁 Output directory: {Path(args.output).absolute()}")
        print(f"\n📋 Generated files:")
        for filepath in saved_files:
            print(f"  • {filepath}")
        
        if not PIL_SUPPORT:
            print("\n💡 Tip: Install Pillow for better image format support:")
            print("   pip install pillow")
        
        print_section("Complete")
        print("✓ Image generation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
