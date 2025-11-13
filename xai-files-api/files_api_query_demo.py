#!/usr/bin/env python3
"""
X.AI Files API Demo

This script demonstrates how to use the x.ai Files API for:
- Uploading files
- Listing files
- Retrieving file information
- Deleting files
- Using files in chat completions

Requirements:
    pip install requests python-dotenv
    # or using uv:
    uv pip install requests python-dotenv

Usage:
    # Run with auto-generated sample file
    python files_api_query_demo.py
    
    # Upload a single file with default question
    python files_api_query_demo.py path/to/your/file.txt
    
    # Upload a file with custom prompt
    python files_api_query_demo.py myfile.pdf "Summarize the key findings"
    
    # Upload folder with custom prompt
    python files_api_query_demo.py path/to/folder/ "What are the main topics discussed?"
    
    # More examples
    python files_api_query_demo.py report.pdf "List all action items"
    python files_api_query_demo.py ~/Documents/ "Find security concerns"
"""

import os
import sys
import requests
import json
from pathlib import Path
from io import BytesIO

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load from .env in current directory or parent directories
    load_dotenv()
    # Also try loading from the script's directory
    load_dotenv(Path(__file__).parent / '.env')
except ImportError:
    # python-dotenv not installed, will fall back to environment variables only
    pass

# Try to import PDF library (optional)
try:
    from PyPDF2 import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


class XAIFilesAPI:
    """Wrapper for X.AI Files API operations"""
    
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
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def upload_file(self, file_path, purpose="assistants"):
        """
        Upload a file to x.ai
        
        Args:
            file_path: Path to the file to upload
            purpose: Purpose of the file (e.g., "assistants", "fine-tune")
        
        Returns:
            dict: Response containing file information
        """
        url = f"{self.base_url}/files"
        
        with open(file_path, 'rb') as f:
            files = {
                'file': (Path(file_path).name, f)
            }
            data = {
                'purpose': purpose
            }
            
            response = requests.post(
                url,
                headers=self.headers,
                files=files,
                data=data
            )
            
        response.raise_for_status()
        return response.json()
    
    def list_files(self):
        """
        List all uploaded files
        
        Returns:
            dict: Response containing list of files
        """
        url = f"{self.base_url}/files"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_file(self, file_id):
        """
        Retrieve information about a specific file
        
        Args:
            file_id: ID of the file
        
        Returns:
            dict: File information
        """
        url = f"{self.base_url}/files/{file_id}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def delete_file(self, file_id):
        """
        Delete a file
        
        Args:
            file_id: ID of the file to delete
        
        Returns:
            dict: Deletion confirmation
        """
        url = f"{self.base_url}/files/{file_id}"
        
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def download_file_content(self, file_id):
        """
        Download file content
        
        Args:
            file_id: ID of the file
        
        Returns:
            bytes: File content
        """
        url = f"{self.base_url}/files/{file_id}/content"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.content
    
    def chat_with_file(self, file_ids, message, model="grok-4"):
        """
        Create a chat completion using uploaded files
        
        Args:
            file_ids: List of file IDs to use in the conversation
            message: User message
            model: Model to use for chat
        
        Returns:
            dict: Chat completion response
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "file_ids": file_ids
        }
        
        response = requests.post(
            url,
            headers={**self.headers, "Content-Type": "application/json"},
            json=payload
        )
        response.raise_for_status()
        return response.json()


def extract_text_from_pdf(pdf_bytes):
    """
    Extract text from PDF bytes
    
    Args:
        pdf_bytes: PDF file content as bytes
    
    Returns:
        str: Extracted text from PDF
    """
    if not PDF_SUPPORT:
        raise ImportError("PyPDF2 is required for PDF support. Install with: pip install PyPDF2")
    
    reader = PdfReader(BytesIO(pdf_bytes))
    text = ""
    for page_num, page in enumerate(reader.pages, 1):
        page_text = page.extract_text()
        text += f"\n--- Page {page_num} ---\n{page_text}\n"
    
    return text


def get_files_from_path(path):
    """
    Get list of files from a path (file or directory)
    
    Args:
        path: File path or directory path
    
    Returns:
        list: List of file paths
    """
    path_obj = Path(path)
    
    if path_obj.is_file():
        return [path]
    elif path_obj.is_dir():
        # Get all files in directory (non-recursive)
        files = []
        for item in path_obj.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                files.append(str(item))
        return sorted(files)
    else:
        return []


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo():
    """Run the Files API demo"""
    
    print_section("X.AI Files API Demo")
    
    try:
        # Initialize the API client
        api = XAIFilesAPI()
        print("✓ API client initialized successfully")
        
        # Check if a path was provided as command-line argument
        custom_prompt = None
        if len(sys.argv) > 1:
            input_path = sys.argv[1]
            if not os.path.exists(input_path):
                print(f"❌ Error: Path not found: {input_path}", file=sys.stderr)
                sys.exit(1)
            
            # Check if custom prompt was provided
            if len(sys.argv) > 2:
                custom_prompt = sys.argv[2]
                print(f"✓ Custom prompt: \"{custom_prompt}\"")
            
            # Get files from path (file or directory)
            files_to_upload = get_files_from_path(input_path)
            
            if not files_to_upload:
                print(f"❌ Error: No files found in: {input_path}", file=sys.stderr)
                sys.exit(1)
            
            if len(files_to_upload) == 1:
                print(f"✓ Using provided file: {files_to_upload[0]}")
            else:
                print(f"✓ Found {len(files_to_upload)} files in directory: {input_path}")
                for f in files_to_upload:
                    print(f"  - {Path(f).name}")
            
            cleanup_files = False  # Don't delete user's files
        else:
            # Create a sample file to upload
            sample_file = "sample_data.txt"
            with open(sample_file, 'w') as f:
                f.write("""Sample Data for X.AI Files API Demo
            
This is a sample text file containing information that can be used
by the AI model during conversations.

Key Facts:
- The X.AI Files API allows uploading documents for context
- Supported purposes include 'assistants' and 'fine-tune'
- Files can be listed, retrieved, and deleted via the API
- Files can be referenced in chat completions

Example Use Cases:
1. Providing context documents for specialized knowledge
2. Uploading training data for fine-tuning
3. Storing reference materials for long-term conversations
""")
            print(f"✓ Created sample file: {sample_file}")
            files_to_upload = [sample_file]
            cleanup_files = True  # Clean up our created file
        
        # 1. Upload file(s)
        print_section(f"1. Upload File{'s' if len(files_to_upload) > 1 else ''}")
        uploaded_files = []
        
        for file_path in files_to_upload:
            try:
                upload_response = api.upload_file(file_path, purpose="assistants")
                uploaded_files.append(upload_response)
                print(f"✓ Uploaded: {Path(file_path).name}")
                print(f"  File ID: {upload_response.get('id')}")
                print(f"  Bytes: {upload_response.get('bytes')}")
            except Exception as e:
                print(f"✗ Failed to upload {Path(file_path).name}: {str(e)}")
        
        if not uploaded_files:
            print("❌ No files were uploaded successfully")
            sys.exit(1)
        
        # Use the first uploaded file for demo purposes
        file_id = uploaded_files[0].get('id')
        print(f"\n✓ Total files uploaded: {len(uploaded_files)}")
        
        # 2. List all files
        print_section("2. List All Files")
        list_response = api.list_files()
        print(f"✓ Retrieved {len(list_response.get('data', []))} file(s)")
        for idx, file in enumerate(list_response.get('data', []), 1):
            print(f"  {idx}. {file.get('filename')} (ID: {file.get('id')})")
        
        # 3. Get specific file information
        print_section("3. Get File Information")
        file_info = api.get_file(file_id)
        print(f"✓ Retrieved file information:")
        print(json.dumps(file_info, indent=2))
        
        # 4. Use file content in chat completion
        print_section("4. Chat with File Content")
        print("Note: The file_ids parameter may not be supported yet.")
        print("Alternative: Download file content and include it in the chat.\n")
        
        try:
            # Download and process content from ALL uploaded files
            all_files_text = ""
            
            for idx, uploaded_file in enumerate(uploaded_files, 1):
                file_id_current = uploaded_file.get('id')
                filename = uploaded_file.get('filename', '')
                
                print(f"Downloading file {idx}/{len(uploaded_files)}: {filename}...")
                file_content = api.download_file_content(file_id_current)
                
                # Check if it's a PDF file
                if filename.lower().endswith('.pdf'):
                    if not PDF_SUPPORT:
                        print(f"⚠ PDF file detected but PyPDF2 not installed: {filename}")
                        print("  Install with: pip install PyPDF2")
                        continue
                    
                    print(f"📄 PDF detected - extracting text from {filename}...")
                    file_text = extract_text_from_pdf(file_content)
                    print(f"✓ Extracted {len(file_text)} characters from {filename}")
                else:
                    # Try to decode as UTF-8 text
                    try:
                        file_text = file_content.decode('utf-8')
                        print(f"✓ Loaded {len(file_text)} characters from {filename}")
                    except UnicodeDecodeError:
                        print(f"⚠ Unable to decode {filename} as text. Skipping.")
                        continue
                
                # Add file content with header
                all_files_text += f"\n{'='*60}\n"
                all_files_text += f"FILE: {filename}\n"
                all_files_text += f"{'='*60}\n"
                all_files_text += file_text
                all_files_text += f"\n\n"
            
            if not all_files_text:
                print("⚠ No readable content extracted from files.")
                raise Exception("No files could be processed for chat")
            
            file_text = all_files_text
            print(f"\n✓ Total content: {len(file_text)} characters from {len(uploaded_files)} file(s)")
            
            # Create a chat completion with the file content in the message
            if len(uploaded_files) == 1:
                question = custom_prompt if custom_prompt else "What are the key facts mentioned in this file?"
                context_intro = "Here is the content of a file:"
            else:
                question = custom_prompt if custom_prompt else f"What are the key facts mentioned in these {len(uploaded_files)} files?"
                context_intro = f"Here is the content of {len(uploaded_files)} files:"
            
            url = f"{api.base_url}/chat/completions"
            payload = {
                "model": "grok-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Answer questions about the provided file content."
                    },
                    {
                        "role": "user",
                        "content": f"{context_intro}\n\n{file_text}\n\nQuestion: {question}"
                    }
                ]
            }
            
            response = requests.post(
                url,
                headers={**api.headers, "Content-Type": "application/json"},
                json=payload
            )
            response.raise_for_status()
            chat_response = response.json()
            
            # Extract the assistant's response
            if chat_response.get('choices') and len(chat_response['choices']) > 0:
                assistant_message = chat_response['choices'][0]['message']['content']
                print("✓ Grok's Response:")
                print("-" * 60)
                print(assistant_message)
                print("-" * 60)
                print(f"\nModel: {chat_response.get('model')}")
                print(f"Usage: {chat_response.get('usage', {}).get('total_tokens', 'N/A')} tokens")
            else:
                print("⚠ No response content received")
                print(f"Full response: {json.dumps(chat_response, indent=2)}")
                
        except Exception as e:
            print(f"⚠ Chat with file content failed: {str(e)}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
        
        # 5. Delete the file (optional - uncomment to test)
        print_section("5. Delete File (Optional)")
        delete_choice = input("Do you want to delete the uploaded file? (y/n): ").strip().lower()
        if delete_choice == 'y':
            delete_response = api.delete_file(file_id)
            print(f"✓ File deleted successfully!")
            print(json.dumps(delete_response, indent=2))
        else:
            print(f"✓ File retained. ID: {file_id}")
        
        # Clean up local sample files (only if we created them)
        if cleanup_files:
            for file_path in files_to_upload:
                if os.path.exists(file_path):
                    os.remove(file_path)
            print(f"\n✓ Cleaned up local sample file(s)")
        
        print_section("Demo Complete")
        print("✓ All operations completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    demo()
