import os
import requests
import hashlib
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print(f"Warning: .env file not found at {dotenv_path}")

# Cache directory
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".cache")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# PDF directory
PDF_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pdfs")
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)


def check_grobid_status() -> bool:
    """Check if Grobid service is running"""
    try:
        # Get GROBID API URL from environment variable, default to http://localhost:8070/api
        grobid_api_url = os.getenv("GROBID_API_URL", "http://localhost:8070/api")
        response = requests.get(f"{grobid_api_url}/isalive", timeout=10)
        return response.status_code == 200 and response.text == "true"
    except Exception:
        return False


def generate_bibtex_citation_key(paper_info: Dict) -> str:
    """Generate a bibtex citation key from paper information
    
    Args:
        paper_info: Dictionary containing paper information
        
    Returns:
        Bibtex citation key in the format "lastnameYearTitle"
    """
    # Get first author's last name
    authors = paper_info.get('authors', [])
    if authors:
        first_author = authors[0]
        # Split into first and last name
        name_parts = first_author.split()
        last_name = name_parts[-1].lower() if name_parts else "unknown"
    else:
        last_name = "unknown"
    
    # Get year
    year = paper_info.get('year', '')
    # Convert to string if it's an integer
    if isinstance(year, int):
        year = str(year)
    # Take first 4 characters in case of full date
    year = year[:4]
    if not year:
        year = ""
    
    # Get title and extract first few words
    title = paper_info.get('title', '')
    if title:
        # Remove special characters and split into words
        import re
        title_words = re.findall(r'\b\w+\b', title.lower())
        # Take first 2 words
        title_part = "".join(title_words[:2]) if title_words else ""
    else:
        title_part = ""
    
    # Combine parts
    citation_key = f"{last_name}{year}{title_part}"
    
    # Remove any non-alphanumeric characters
    citation_key = re.sub(r'[^a-zA-Z0-9]', '', citation_key)
    
    return citation_key

def download_pdf(url: str, filename: str = None, save_dir: str = None, paper_info: Dict = None) -> Optional[str]:
    """Download PDF from URL to local file
    
    Args:
        url: URL of the PDF file
        filename: Optional filename to save the PDF as
        save_dir: Optional directory to save the PDF in
        paper_info: Optional paper information for generating citation key
        
    Returns:
        Path to the downloaded PDF file, or None if download failed
    """
    try:
        # Determine save directory
        if save_dir:
            # Use specified directory
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            target_dir = save_dir
        else:
            # Use default PDF directory
            target_dir = PDF_DIR
        
        # Generate filename if not provided
        if not filename:
            if paper_info:
                # Generate bibtex citation key
                citation_key = generate_bibtex_citation_key(paper_info)
                filename = f"{citation_key}.pdf"
            else:
                # Extract filename from URL
                filename = os.path.basename(url)
                if not filename.endswith('.pdf'):
                    filename = f"{filename}.pdf"
        
        # Full path to save the PDF
        pdf_path = os.path.join(target_dir, filename)
        
        # Download PDF
        print(f"Downloading PDF from {url} to {pdf_path}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Save PDF to file
        with open(pdf_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"PDF downloaded successfully: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return None


def get_pdf_hash(pdf_path: str) -> str:
    """Generate a hash for the PDF file"""
    hasher = hashlib.md5()
    with open(pdf_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def get_xml_cache_file(pdf_path: str, endpoint: str) -> str:
    """Get the XML cache file path for the PDF"""
    pdf_hash = get_pdf_hash(pdf_path)
    return os.path.join(CACHE_DIR, f"{pdf_hash}_{endpoint.replace('/', '_')}.xml")


def save_xml_response(pdf_path: str, endpoint: str, xml_response: str):
    """Save XML response to cache"""
    xml_cache_file = get_xml_cache_file(pdf_path, endpoint)
    try:
        with open(xml_cache_file, 'w', encoding='utf-8') as f:
            f.write(xml_response)
        print(f"Saved XML response: {xml_cache_file}")
    except Exception as e:
        print(f"Error saving XML response: {e}")


def load_xml_response(pdf_path: str, endpoint: str) -> Optional[str]:
    """Load XML response from cache"""
    xml_cache_file = get_xml_cache_file(pdf_path, endpoint)
    if os.path.exists(xml_cache_file):
        try:
            with open(xml_cache_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading XML response: {e}")
    return None


def process_pdf(pdf_input: str, endpoint: str = "processFulltextDocument") -> str:
    """Process PDF with Grobid and return XML response
    
    Args:
        pdf_input: Path to local PDF file or URL to PDF
        endpoint: Grobid API endpoint to use
        
    Returns:
        XML response from Grobid
    """
    # Check if Grobid is running
    if not check_grobid_status():
        error_message = "Grobid service is not running. Please start Grobid first."
        print(error_message)
        return error_message
    
    # Check if input is a URL
    if pdf_input.startswith('http://') or pdf_input.startswith('https://'):
        # Download PDF from URL
        pdf_path = download_pdf(pdf_input)
        if not pdf_path:
            return ""
    else:
        # Use local PDF path
        pdf_path = pdf_input
    
    # Check if XML response is already cached
    xml_response = load_xml_response(pdf_path, endpoint)
    if xml_response:
        print(f"Loaded XML response from cache: {get_xml_cache_file(pdf_path, endpoint)}")
        return xml_response
    
    # Get GROBID API URL from environment variable, default to http://localhost:8070/api
    grobid_api_url = os.getenv("GROBID_API_URL", "http://localhost:8070/api")
    grobid_url = f"{grobid_api_url}/{endpoint}"
    
    print(f"Processing PDF: {pdf_path}")
    print(f"Grobid URL: {grobid_url}")
    
    try:
        # Check if PDF file exists
        if not os.path.exists(pdf_path):
            print(f"PDF file not found: {pdf_path}")
            return ""
        
        # Check if PDF file is readable
        if not os.access(pdf_path, os.R_OK):
            print(f"PDF file not readable: {pdf_path}")
            return ""
        
        # Send PDF to Grobid for processing with consolidate parameters
        print("Sending PDF to Grobid...")
        with open(pdf_path, 'rb') as f:
            files = {'input': f}
            data = {
                'consolidateHeader': '1',
                'consolidateCitations': '1'
            }
            # Set timeout to 5 minutes
            response = requests.post(grobid_url, files=files, data=data, timeout=300)
        
        print(f"Grobid response status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Grobid API call successful")
            # Get XML response
            xml_response = response.text
            
            # Save XML response
            save_xml_response(pdf_path, endpoint, xml_response)
            
            # Print first 500 characters of XML response for debugging
            print(f"XML response (first 500 chars): {xml_response[:500]}...")
            
            return xml_response
        else:
            print(f"Grobid API error: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.Timeout:
        print("Grobid API request timed out")
    except requests.exceptions.ConnectionError:
        print("Grobid API connection error - is Grobid running?")
    except Exception as e:
        print(f"Error processing PDF with Grobid: {e}")
        import traceback
        print(traceback.format_exc())
    
    return ""


def analyze_pdf_header(pdf_input: str) -> str:
    """Analyze PDF header and return XML response
    
    Args:
        pdf_input: Path to local PDF file or URL to PDF
        
    Returns:
        XML response from Grobid
    """
    return process_pdf(pdf_input, endpoint="processHeaderDocument")


def analyze_pdf_fulltext(pdf_input: str) -> str:
    """Analyze PDF fulltext and return XML response
    
    Args:
        pdf_input: Path to local PDF file or URL to PDF
        
    Returns:
        XML response from Grobid
    """
    return process_pdf(pdf_input, endpoint="processFulltextDocument")