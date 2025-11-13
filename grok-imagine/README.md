# Grok Imagine - Image Generation Script

**Powered by X.AI Aurora Model** (`grok-2-image` / `grok-2-image-1212`)

Generate beautiful images using X.AI's Grok Imagine API, powered by the Aurora image generation model.

## 🎯 API Overview

**Endpoint:** `https://api.x.ai/v1/images/generations`

**Model:** `grok-2-image` or `grok-2-image-1212`

**Features:**
- ✅ Text-to-image generation from prompts
- ✅ Batch generation (multiple images per request)
- ✅ Output formats: `url` (hosted URL) or `base64` (raw image bytes)
- ✅ Default size: 1024x768 pixels
- ⚠️ No support yet for: quality, size, style, or aspect ratio parameters

**Pricing:** $0.07 per image generated

**Requirements:**
- X.AI API key from https://x.ai/api
- SuperGrok or Premium+ subscription for API access

**Documentation:** https://docs.x.ai/docs/guides/image-generations

**Compatible with OpenAI SDK** - Use `base_url="https://api.x.ai/v1"` and `model="grok-2-image"`

## Features

- 🎨 Generate images from text prompts
- 📥 Automatic download and save as JPEG
- 🔢 Support for generating multiple images at once
- 📁 Customizable output directory
- 🖼️ Multiple image size options
- ✨ Clean, formatted output with progress tracking

## Prerequisites

1. **X.AI API Key**: Get your API key from https://console.x.ai/
2. **Python 3.7+**: Make sure Python is installed on your system

## Setup

### 1. Install Dependencies

Using pip:
```bash
pip install -r requirements.txt
```

Or using uv (faster):
```bash
uv pip install -r requirements.txt
```

### 2. Configure API Key

The script automatically loads `XAI_API_KEY` from multiple sources in this priority order:
1. Shell environment variable (highest priority)
2. `.env` file in the script's directory (`grok-imagine/.env`)
3. `.env` file in the parent directory (`grok-general/.env`)

**Test your configuration:**
```bash
./test_api_key.sh
```

Choose one of these setup methods:

**Option A: Environment Variable (Temporary)**
```bash
export XAI_API_KEY='your-api-key-here'
```

**Option B: .env File (Recommended - Persistent)**

Create a `.env` file in the parent directory:
```bash
# Copy the example file
cp ../.env.example ../.env

# Edit .env and add your API key
# XAI_API_KEY=your-actual-api-key-here
```

Or create a local `.env` file in the grok-imagine directory:
```bash
echo "XAI_API_KEY=your-actual-api-key-here" > .env
```

**Get your API key:** https://console.x.ai/

## Usage

### Quick Start (Recommended)

The easiest way to run the script is using the provided `run.sh` wrapper:

```bash
# Make sure you're in the grok-imagine directory
cd grok-imagine

# Run with default prompt
./run.sh

# Run with custom prompt
./run.sh "A serene landscape with mountains at sunset"

# Run with options (prompt at the end)
./run.sh -n 3 -o ./my_images "A beautiful sunset"
```

The `run.sh` script automatically:
- Checks if `uv` is installed
- Creates virtual environment if needed
- Installs dependencies if needed
- Checks for API key
- Runs the image generation script

### Basic Examples

**Generate a single image with default prompt:**
```bash
python imagine.py
# or
./run.sh
```

**Generate image with custom prompt:**
```bash
python imagine.py "A serene landscape with mountains at sunset"
# or
./run.sh "A serene landscape with mountains at sunset"
```

**Generate multiple images:**
```bash
python imagine.py "A futuristic city" --count 3
```

**Specify output directory:**
```bash
python imagine.py "Abstract art" --output ./my_images
```

**Change image size:**
```bash
python imagine.py "A cat in space" --size 512x512
```

### All Options

```bash
python imagine.py "Your prompt here" \
  --count 2 \
  --size 1024x1024 \
  --output ./generated_images
```

### Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `prompt` | - | Text description of the image | Sample prompt |
| `--count` | `-n` | Number of images (1-10) | 1 |
| `--output` | `-o` | Output directory | `./generated_images` |
| `--size` | `-s` | Image size | `1024x1024` |

**Available Sizes:**
- `256x256` - Small, fast generation
- `512x512` - Medium size
- `1024x1024` - High resolution (standard)
- `2048x2048` - Very high resolution
- `1792x1024` - Landscape format (16:9-ish)
- `1024x1792` - Portrait format (9:16-ish)
- Custom sizes in `WIDTHxHEIGHT` format

Note: The API will determine which sizes are supported. Larger sizes may take longer to generate and consume more API credits.

## Examples

### Creative Prompts

```bash
# Fantasy art
python imagine.py "A majestic dragon perched on a crystal mountain under aurora lights"

# Science fiction
python imagine.py "A cyberpunk street market with neon signs and flying cars"

# Nature
python imagine.py "A bioluminescent forest with glowing mushrooms and fireflies"

# Abstract
python imagine.py "Geometric patterns in blue and gold, Art Deco style"

# Portrait
python imagine.py "Portrait of a wise wizard with a long beard, oil painting style"
```

### Batch Generation

Generate multiple variations:
```bash
# Create 5 variations of the same concept
python imagine.py "Sunset over the ocean" --count 5

# Different sizes for different uses
python imagine.py "Company logo concept" --size 512x512 --count 3

# High-resolution wallpaper
python imagine.py "Epic space battle" --size 2048x2048

# Landscape format for wide displays
python imagine.py "Panoramic mountain vista" --size 1792x1024

# Portrait format for mobile wallpapers
python imagine.py "Elegant fashion portrait" --size 1024x1792
```

## Output

Images are saved with descriptive filenames:
```
generated_images/
├── A_serene_landscape_with_moun_20231113_142530.jpg
├── Abstract_art_20231113_142645_1.jpg
├── Abstract_art_20231113_142645_2.jpg
└── Abstract_art_20231113_142645_3.jpg
```

Filename format: `{prompt_snippet}_{timestamp}_{index}.jpg`

## Troubleshooting

### "XAI_API_KEY not found"
Make sure you've set up your API key using one of the methods in the Setup section.

### "Pillow not installed" warning
While images will still download, installing Pillow enables better format conversion:
```bash
pip install pillow
```

### Rate limits
If you encounter rate limit errors, try:
- Reducing the number of images generated at once
- Adding delays between requests
- Checking your API tier limits at https://console.x.ai/

### Network errors
- Check your internet connection
- Verify your API key is valid
- Ensure you have sufficient API credits

## Advanced Usage

### Using as a Module

```python
from imagine import XAIImageAPI

# Initialize
api = XAIImageAPI(api_key="your-key")

# Generate
response = api.generate_image(
    prompt="A beautiful sunset",
    n=2,
    size="1024x1024"
)

# Download
for idx, img in enumerate(response['data']):
    api.download_image(img['url'], f"image_{idx}.jpg")
```

## API Documentation

For more information about the X.AI Image Generation API:
- Documentation: https://docs.x.ai/
- Console: https://console.x.ai/
- API Reference: https://docs.x.ai/api

## License

This script is provided as-is for use with the X.AI API.

## Support

For issues related to:
- **This script**: Open an issue in the repository
- **X.AI API**: Visit https://docs.x.ai/ or contact X.AI support
- **API Keys**: Manage at https://console.x.ai/
