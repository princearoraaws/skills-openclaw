import requests
import os
from dotenv import load_dotenv
from typing import Dict, Optional

# Try to import pyzotero
try:
    from pyzotero import Zotero
except ImportError:
    print("pyzotero not installed. Using direct API calls instead.")
    Zotero = None

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print(f"Warning: .env file not found at {dotenv_path}")


def detect_item_type(paper_info: Dict) -> str:
    """Detect item type based on paper information
    
    Args:
        paper_info: Dictionary containing paper information
        
    Returns:
        Item type string
    """
    if paper_info.get("is_survey"):
        return "journalArticle"
    return "conferencePaper"


def is_duplicate(paper_info: Dict, api_key: str, library_id: str, library_type: str = "user") -> bool:
    """Check if paper already exists in Zotero library
    
    Args:
        paper_info: Dictionary containing paper information
        api_key: Zotero API key
        library_id: Zotero library ID
        library_type: Zotero library type ("user" or "group")
        
    Returns:
        True if duplicate exists, False otherwise
    """
    # Check by DOI first if available
    doi = paper_info.get("doi")
    if doi:
        url = f"https://api.zotero.org/{library_type}s/{library_id}/items"
        params = {"q": doi}
        headers = {
            "Zotero-API-Key": api_key
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            items = response.json()
            if len(items) > 0:
                print(f"Duplicate found by DOI: {doi}")
                return True
        except Exception as e:
            print(f"Error checking for duplicate by DOI: {e}")
    
    # Check by title and authors if DOI is not available or check failed
    title = paper_info.get("title")
    authors = paper_info.get("authors", [])
    
    if title:
        # Search by title
        url = f"https://api.zotero.org/{library_type}s/{library_id}/items"
        params = {"q": title}
        headers = {
            "Zotero-API-Key": api_key
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            items = response.json()
            print(f"Searching for duplicate by title: {title}")
            print(f"Found {len(items)} items")
            
            # Check if any item with the same title has matching authors
            for item in items:
                item_data = item.get("data", {})
                item_title = item_data.get("title")
                print(f"Found item: {item_title}")
                if item_title and item_title.lower() == title.lower():
                    # Check if authors match
                    item_creators = item_data.get("creators", [])
                    item_authors = [f"{c.get('firstName', '')} {c.get('lastName', '')}".strip() for c in item_creators if c.get('creatorType') == 'author']
                    print(f"Item authors: {item_authors}")
                    print(f"Paper authors: {authors}")
                    
                    # If at least one author matches, consider it a duplicate
                    if any(author in item_authors for author in authors):
                        print("Duplicate found by title and authors")
                        return True
        except Exception as e:
            print(f"Error checking for duplicate by title and authors: {e}")
    
    print("No duplicate found")
    return False


def create_item(paper_info: Dict, api_key: str, library_id: str, library_type: str = "user") -> Dict:
    """Create item in Zotero library
    
    Args:
        paper_info: Dictionary containing paper information
        api_key: Zotero API key
        library_id: Zotero library ID
        library_type: Zotero library type ("user" or "group")
        
    Returns:
        Response from Zotero API
    """
    url = f"https://api.zotero.org/{library_type}s/{library_id}/items"
    
    headers = {
        "Zotero-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    item_type = detect_item_type(paper_info)
    
    item = {
        "itemType": item_type,
        "title": paper_info.get("title", ""),
        "abstractNote": paper_info.get("abstract", ""),
        "url": paper_info.get("url", ""),
        "DOI": paper_info.get("doi", ""),
        "date": paper_info.get("year", ""),
        "creators": []
    }
    
    # Add authors
    authors = paper_info.get("authors", [])
    for author in authors:
        # Split author name into first and last name
        name_parts = author.split()
        if len(name_parts) >= 2:
            last_name = name_parts[-1]
            first_name = " ".join(name_parts[:-1])
        else:
            last_name = author
            first_name = ""
        
        item["creators"].append({
            "creatorType": "author",
            "firstName": first_name,
            "lastName": last_name
        })
    
    # Add venue information
    venue = paper_info.get("venue", "")
    if venue:
        item["publicationTitle"] = venue
    
    # Add keywords
    keywords = paper_info.get("keywords", [])
    if keywords:
        item["tags"] = [{'tag': keyword} for keyword in keywords]
    
    # Add BibTeX info if available
    if "bibtex" in paper_info:
        item["extra"] = paper_info["bibtex"]
    
    try:
        response = requests.post(url, json=[item], headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error creating item: {e}")
        return {"error": str(e)}


def get_collection_id(zot: 'Zotero', collection_name: str) -> Optional[str]:
    """Get collection ID by name
    
    Args:
        zot: Zotero client instance
        collection_name: Name of the collection
        
    Returns:
        Collection ID if found, None otherwise
    """
    try:
        collections = zot.collections()
        # Check if collections is a list
        if not isinstance(collections, list):
            print(f"Unexpected collections format: {type(collections)}")
            return None
        
        for collection in collections:
            # Check if collection is a dictionary
            if not isinstance(collection, dict):
                print(f"Unexpected collection format: {type(collection)}")
                continue
            
            # Get key directly from collection
            if collection.get('name') == collection_name:
                return collection.get('key')
            # Fallback to checking data field
            elif collection.get('data', {}).get('name') == collection_name:
                return collection.get('key')
        return None
    except Exception as e:
        print(f"Error getting collection ID: {e}")
        return None

def create_collection(zot: 'Zotero', collection_name: str) -> Optional[str]:
    """Create a new collection
    
    Args:
        zot: Zotero client instance
        collection_name: Name of the collection
        
    Returns:
        Collection ID if created successfully, None otherwise
    """
    try:
        collection = zot.create_collections([{'name': collection_name}])
        if isinstance(collection, dict) and 'successful' in collection:
            successful_collections = collection['successful']
            if successful_collections and isinstance(successful_collections, dict):
                first_key = next(iter(successful_collections))
                return first_key
        return None
    except Exception as e:
        print(f"Error creating collection: {e}")
        return None

def add_to_collection(zot: 'Zotero', item_key: str, collection_id: str) -> bool:
    """Add item to collection
    
    Args:
        zot: Zotero client instance
        item_key: Item key
        collection_id: Collection ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Print debug information
        print(f"Adding item {item_key} to collection {collection_id}")
        
        # Try a different approach using the collections API directly
        # Instead of using zot.addto_collection, use the items API to update the item's collections
        item = zot.item(item_key)
        if isinstance(item, dict):
            # Get existing collections
            collections = item.get('data', {}).get('collections', [])
            if not isinstance(collections, list):
                collections = []
            
            # Add the collection ID if it's not already there
            if collection_id not in collections:
                collections.append(collection_id)
                # Update the item with the new collections
                item['data']['collections'] = collections
                update_result = zot.update_item(item)
                print(f"Update result: {update_result}")
                return True
            else:
                print("Item already in collection")
                return True
        else:
            print(f"Unexpected item format: {type(item)}")
            return False
    except Exception as e:
        print(f"Error adding item to collection: {e}")
        import traceback
        traceback.print_exc()
        return False

def archive_paper(paper_info: Dict, zotero_api_key: Optional[str] = None, zotero_library_id: Optional[str] = None, zotero_library_type: str = "user", use_pyzotero: bool = False, collection: str = "openclaw") -> Dict:
    """Archive paper to Zotero
    
    Args:
        paper_info: Dictionary containing paper information
        zotero_api_key: Zotero API key (optional, will use environment variable if not provided)
        zotero_library_id: Zotero library ID (optional, will use environment variable if not provided)
        zotero_library_type: Zotero library type ("user" or "group")
        use_pyzotero: Whether to use pyzotero library for archiving
        collection: Name of the collection to add the paper to (default: "openclaw")
        
    Returns:
        Dictionary with archiving result
    """
    # Get API key and library ID from environment variables if not provided
    if not zotero_api_key:
        zotero_api_key = os.getenv("ZOTERO_API_KEY")
    
    if not zotero_library_id:
        zotero_library_id = os.getenv("ZOTERO_LIBRARY_ID")
    
    if not zotero_api_key or not zotero_library_id:
        error_msg = "Zotero API key or library ID not provided"
        return {"error": error_msg}
    
    # Use pyzotero if requested and available
    if use_pyzotero and Zotero:
        try:
            # Initialize pyzotero client
            zot = Zotero(zotero_library_id, zotero_library_type, zotero_api_key)
            
            # Check for duplicate
            # First check by DOI if available
            doi = paper_info.get("doi")
            if doi:
                try:
                    # Search by DOI
                    items = zot.items(q=doi)
                    if items:
                        print(f"Duplicate found by DOI: {doi}")
                        return {"error": "Paper already exists in Zotero library"}
                except Exception as e:
                    print(f"Error checking duplicate by DOI: {e}")
            
            # Check by title and authors if DOI is not available
            title = paper_info.get("title")
            authors = paper_info.get("authors", [])
            if title:
                try:
                    # Search by title
                    items = zot.items(q=title)
                    print(f"Searching for duplicate by title: {title}")
                    print(f"Found {len(items)} items")
                    for item in items:
                        item_data = item.get("data", {})
                        item_title = item_data.get("title")
                        print(f"Found item: {item_title}")
                        if item_title and item_title.lower() == title.lower():
                            # Check if authors match
                            item_creators = item_data.get("creators", [])
                            item_authors = [f"{c.get('firstName', '')} {c.get('lastName', '')}".strip() for c in item_creators if c.get('creatorType') == 'author']
                            print(f"Item authors: {item_authors}")
                            print(f"Paper authors: {authors}")
                            # If at least one author matches, consider it a duplicate
                            if any(author in item_authors for author in authors):
                                print("Duplicate found by title and authors")
                                return {"error": "Paper already exists in Zotero library"}
                except Exception as e:
                    print(f"Error checking duplicate by title and authors: {e}")
            
            # Prepare item data
            creators = []
            for author in paper_info.get("authors", []):
                name_parts = author.split()
                if len(name_parts) >= 2:
                    first_name = " ".join(name_parts[:-1])
                    last_name = name_parts[-1]
                else:
                    first_name = ""
                    last_name = author
                creators.append({"creatorType": "author", "firstName": first_name, "lastName": last_name})
            
            item_data = {
                "itemType": detect_item_type(paper_info),
                "title": paper_info.get("title", ""),
                "creators": creators,
                "abstractNote": paper_info.get("abstract", ""),
                "date": paper_info.get("year", ""),
                "url": paper_info.get("url", ""),
                "DOI": paper_info.get("doi", "")
            }
            
            # Add BibTeX info if available
            if "bibtex" in paper_info:
                item_data["extra"] = paper_info["bibtex"]
            
            # Create item
            item = zot.create_items([item_data])
            
            # Check if result is a dictionary with 'successful' field
            item_key = None
            if isinstance(item, dict) and 'successful' in item:
                successful_items = item['successful']
                if successful_items and isinstance(successful_items, dict):
                    # Get the first successful item
                    first_key = next(iter(successful_items))
                    first_item = successful_items[first_key]
                    if isinstance(first_item, dict) and 'key' in first_item:
                        item_key = first_item['key']
            elif isinstance(item, list) and len(item) > 0:
                # Handle case where result is a list
                if isinstance(item[0], dict) and 'key' in item[0]:
                    item_key = item[0]['key']
            
            if not item_key:
                return {"error": f"Failed to create item using pyzotero, result: {item}"}
            
            # Add PDF URL as attachment if available
            pdf_url = paper_info.get('pdf_url')
            if pdf_url:
                try:
                    # Create attachment item
                    attachment_data = {
                        "itemType": "attachment",
                        "title": "PDF",
                        "url": pdf_url,
                        "linkMode": "imported_url"
                    }
                    # Create attachment and link it to the parent item
                    attachment = zot.create_items([attachment_data], parentid=item_key)
                    print(f"Added PDF attachment: {pdf_url}")
                except Exception as e:
                    print(f"Error adding PDF attachment: {e}")
            
            # Add to specified collection
            collection_id = get_collection_id(zot, collection)
            
            if not collection_id:
                # Create collection if it doesn't exist
                collection_id = create_collection(zot, collection)
            
            added_to_collection = False
            if collection_id:
                added_to_collection = add_to_collection(zot, item_key, collection_id)
            
            return {
                "success": True,
                "item_id": item_key,
                "added_to_collection": added_to_collection
            }
        except Exception as e:
            return {"error": f"Error using pyzotero: {str(e)}"}
    
    # Continue with existing direct API calls if pyzotero is not used or not available
    
    # Check for duplicate
    if is_duplicate(paper_info, zotero_api_key, zotero_library_id, zotero_library_type):
        return {"error": "Paper already exists in Zotero library"}
    
    # Create item in Zotero
    item_result = create_item(paper_info, zotero_api_key, zotero_library_id, zotero_library_type)
    
    # Handle different response formats
    if isinstance(item_result, dict):
        # Check if response has "successful" field (newer Zotero API format)
        if "successful" in item_result:
            successful_items = item_result["successful"]
            if successful_items:
                # Get the first successful item
                first_item_key = list(successful_items.keys())[0]
                item_key = successful_items[first_item_key].get("key")
                if item_key:
                    return {
                        "success": True,
                        "item_id": item_key,
                        "added_to_collection": False
                    }
        # Check if response has "error" field
        elif "error" in item_result:
            return {"error": f"Failed to create item: {item_result['error']}"}
    elif isinstance(item_result, list) and len(item_result) > 0:
        # Older Zotero API format
        item_key = item_result[0].get("key")
        if item_key:
            return {
                "success": True,
                "item_id": item_key,
                "added_to_collection": False
            }
    
    return {"error": "Failed to create item: unknown error"}
