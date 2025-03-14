## This tool essentially gets the content of the page in text format from the web page content.
import httpx
from bs4 import BeautifulSoup
async def get_page_content(url: str) -> str:
    """
    Retrieve the content of a web page and extract the main text content.
    
    Args:
        url: The URL of the web page to retrieve
        
    Returns:
        Extracted text content from the web page
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.extract()
            
            # Look for common lyric containers
            lyric_containers = soup.select('.lyrics, .Lyrics, #lyrics, .lyricbox, .song-lyrics, .songtext')
            
            if lyric_containers:
                # Use the first lyrics container found
                main_content = lyric_containers[0].get_text()
            else:
                # Fall back to extracting the main content
                main_content = soup.get_text()
            
            # Clean up the text
            lines = (line.strip() for line in main_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = '\n'.join(chunk for chunk in chunks if chunk)
            print(f"lines: {lines} \n chunks: {chunks} \n content: {content}")
            return content
    except Exception as e:
        print(f"Error getting page content: {e}")
        return f"Error retrieving content: {str(e)}"
