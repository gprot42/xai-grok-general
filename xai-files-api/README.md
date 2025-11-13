# X.AI Files API Demo

This demo shows how to use the **X.AI Files API** to upload, manage, and use files with Grok models.

📚 **Official Documentation**: https://docs.x.ai/docs/guides/files

## Overview

The X.AI Files API allows you to:
- **Upload files** for use with assistants or fine-tuning
- **List uploaded files** to view your file library
- **Retrieve file information** including metadata
- **Delete files** when no longer needed
- **Download file content** to retrieve uploaded files
- **Use files in chat completions** to provide context

## Setup

### Prerequisites

1. Python 3.7 or higher
2. [uv](https://docs.astral.sh/uv/) - Fast Python package installer

### Installation

**Option 1: Using requirements.txt (Recommended)**
```bash
# With uv (fast)
uv pip install -r requirements.txt

# Or with pip
pip install -r requirements.txt
```

**Note:** The requirements include PyPDF2 for PDF support. If you only need text files, you can skip PyPDF2.

**Option 2: Manual installation**
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install requests python-dotenv
```

### API Key Configuration

You have three options to configure your API key:

**Option 1: Environment Variable (Temporary)**
```bash
export XAI_API_KEY="your-api-key-here"
```

**Option 2: .env File (Recommended)**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
# XAI_API_KEY=your-actual-api-key-here
```

**Option 3: Quick .env creation**
```bash
echo "XAI_API_KEY=your-api-key-here" > .env
```

**Important:** The `.env` file is automatically ignored by git and will not be committed to version control.

## Running the Demo

```bash
cd xai-files-api

# Run with auto-generated sample file
python files_api_query_demo.py

# Upload a single file (default question)
python files_api_query_demo.py path/to/your/file.txt

# Upload file with custom prompt
python files_api_query_demo.py report.pdf "Summarize the key findings"
python files_api_query_demo.py data.csv "What are the trends?"

# Upload folder with custom prompt
python files_api_query_demo.py ~/Documents/ "Find security concerns"
python files_api_query_demo.py ./reports/ "List all action items"

# More examples
python files_api_query_demo.py contract.pdf "What are the main obligations?"
python files_api_query_demo.py code.py "Review for bugs and improvements"
python files_api_query_demo.py ~/research/ "Summarize the main conclusions"
```

## API Endpoints

### Base URL
```
https://api.x.ai/v1
```

### 1. Upload File

**Endpoint:** `POST /files`

**Parameters:**
- `file` (required): The file to upload
- `purpose` (required): Purpose of the file (e.g., "assistants", "fine-tune")

**Example:**
```python
import requests

url = "https://api.x.ai/v1/files"
headers = {"Authorization": f"Bearer {api_key}"}

with open("document.txt", "rb") as f:
    files = {"file": ("document.txt", f)}
    data = {"purpose": "assistants"}
    response = requests.post(url, headers=headers, files=files, data=data)

print(response.json())
```

**Response:**
```json
{
  "id": "file-abc123",
  "object": "file",
  "bytes": 1024,
  "created_at": 1699061776,
  "filename": "document.txt",
  "purpose": "assistants"
}
```

### 2. List Files

**Endpoint:** `GET /files`

**Example:**
```python
url = "https://api.x.ai/v1/files"
headers = {"Authorization": f"Bearer {api_key}"}

response = requests.get(url, headers=headers)
print(response.json())
```

**Response:**
```json
{
  "data": [
    {
      "id": "file-abc123",
      "object": "file",
      "bytes": 1024,
      "created_at": 1699061776,
      "filename": "document.txt",
      "purpose": "assistants"
    }
  ],
  "object": "list"
}
```

### 3. Retrieve File

**Endpoint:** `GET /files/{file_id}`

**Example:**
```python
file_id = "file-abc123"
url = f"https://api.x.ai/v1/files/{file_id}"
headers = {"Authorization": f"Bearer {api_key}"}

response = requests.get(url, headers=headers)
print(response.json())
```

### 4. Delete File

**Endpoint:** `DELETE /files/{file_id}`

**Example:**
```python
file_id = "file-abc123"
url = f"https://api.x.ai/v1/files/{file_id}"
headers = {"Authorization": f"Bearer {api_key}"}

response = requests.delete(url, headers=headers)
print(response.json())
```

**Response:**
```json
{
  "id": "file-abc123",
  "object": "file",
  "deleted": true
}
```

### 5. Download File Content

**Endpoint:** `GET /files/{file_id}/content`

**Example:**
```python
file_id = "file-abc123"
url = f"https://api.x.ai/v1/files/{file_id}/content"
headers = {"Authorization": f"Bearer {api_key}"}

response = requests.get(url, headers=headers)
content = response.content
```

### 6. Using File Content in Chat Completions

**Note:** The `file_ids` parameter may not be supported yet. As an alternative, download the file content and include it in your chat messages.

**Endpoint:** `POST /chat/completions` (with file content in message)

**Example:**
```python
# First, download the file content
file_content = api.download_file_content("file-abc123")
file_text = file_content.decode('utf-8')

# Then include it in the chat
url = "https://api.x.ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "grok-4",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant. Answer questions about the provided file content."
        },
        {
            "role": "user",
            "content": f"Here is the file content:\n\n{file_text}\n\nQuestion: Summarize the key points"
        }
    ]
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

## File Purposes

The `purpose` parameter determines how the file will be used:

- **`assistants`**: Files used to provide context to chat assistants
- **`fine-tune`**: Files used for fine-tuning models (training data)

## Supported File Types

### Fully Supported (Built-in):
- **Text files** (`.txt`) - Direct text analysis
- **Markdown files** (`.md`) - Documentation and notes
- **Code files** (`.py`, `.js`, `.java`, etc.) - Source code analysis
- **Data files** (`.json`, `.csv`) - Structured data

### PDF Support (with PyPDF2):
- **PDF files** (`.pdf`) - Automatically extracts text for analysis
  - Requires PyPDF2: `pip install PyPDF2`
  - Text extraction happens automatically
  - Works with multi-page PDFs

### Example with PDF:
```bash
# Upload and analyze a PDF
python files_api_query_demo.py ~/Documents/report.pdf

# The demo will:
# 1. Upload the PDF to X.AI
# 2. Download and extract text from all pages
# 3. Send extracted text to Grok-4 for analysis
# 4. Show AI response about PDF content
```

### Multi-File Analysis:
When uploading a folder, **ALL files are processed and queried together**:

```bash
# Upload and analyze multiple files
python files_api_query_demo.py samples/ "summarize these files"

# The demo will:
# 1. Upload ALL files in the folder to X.AI
# 2. Download and extract text from each file
# 3. Combine all file contents with clear separators
# 4. Send combined content to Grok-4
# 5. Grok analyzes ALL files and provides comprehensive response
```

**Note:** Each file's content is labeled clearly (e.g., `FILE: report1.pdf`) so Grok can reference specific files in its response.

## Best Practices

1. **File Size Limits**: Be aware of file size limitations for uploads
2. **Clean Up**: Delete files when they're no longer needed to manage storage
3. **Organization**: Use descriptive filenames for easier management
4. **Security**: Never commit API keys to version control
5. **Error Handling**: Always implement proper error handling for API calls

## Use Cases

### 1. Knowledge Base Assistant
Upload documentation and reference materials to create an informed assistant:
```python
# Upload company documentation
doc_response = api.upload_file("company_handbook.pdf", "assistants")

# Use in chat
response = api.chat_with_file(
    [doc_response['id']], 
    "What is our vacation policy?"
)
```

### 2. Code Analysis
Upload code files for review and analysis:
```python
# Upload source code
code_response = api.upload_file("app.py", "assistants")

# Request analysis
response = api.chat_with_file(
    [code_response['id']], 
    "Review this code for potential security issues"
)
```

### 3. Data Processing
Upload datasets for analysis:
```python
# Upload CSV data
data_response = api.upload_file("sales_data.csv", "assistants")

# Request insights
response = api.chat_with_file(
    [data_response['id']], 
    "What are the top 3 trends in this sales data?"
)
```

## Troubleshooting

### Common Issues

**Authentication Error:**
```
Error: 401 Unauthorized
```
**Solution:** Verify your API key is set correctly

**File Not Found:**
```
Error: 404 Not Found
```
**Solution:** Check that the file_id exists using the list_files endpoint

**Invalid File Type:**
```
Error: 400 Bad Request
```
**Solution:** Ensure the file type is supported

## Additional Resources

- **[X.AI Files API Documentation](https://docs.x.ai/docs/guides/files)** - Official Files API guide
- [X.AI API Reference](https://docs.x.ai/api) - Complete API reference
- [X.AI Console](https://console.x.ai/) - Manage your API keys and usage
- [uv Documentation](https://docs.astral.sh/uv/) - Fast Python package installer

## License

This demo is provided as-is for educational purposes.
