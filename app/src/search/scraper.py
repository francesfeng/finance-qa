import requests
from bs4 import BeautifulSoup
import fitz

from loguru import logger
level_search = logger.level("SCRAPE", no=38, color="<yellow>", icon="♣")


def extract_text_from_url(url: str, session: requests.Session):
    content = ""

    try:
        if url.endswith(".pdf"):
            content = scrape_pdf(url, session)
        elif "arxiv.org" in url:
            doc_num = url.split("/")[-1]
            content = scrape_arxiv(doc_num)
        
        else:
            content = scrape_html(url, session)

        if content is None or len(content) < 100:
            return {'url': url, 'raw_content': None}
        
        return {'url': url, 'raw_content': content}
    
    except Exception as e:
        return {'url': url, 'raw_content': None}
    



def scrape_pdf(url: str, session: requests.Session):
    """
    Scrape the pdf and return the text
    """
    text = ""
    try:
        response = session.get(url, timeout=4)
        pdf_stream = response.content
        doc = fitz.open(stream = pdf_stream, filetype='pdf') 
        
        for page in doc:
            text += page.get_text() + '\n'

        # Store in DB
        logger.opt(lazy=True).log("SCRAPE", f"Type: PDF | URL: {url} | Content: {len(text.split())}")
        return text
    except Exception as e:
        logger.error(f"Error in scraping PDF: {e} | URL: {url}")
        return



def scrape_arxiv(url: str):
    """
    Scrape the arxiv page and return the text
    """
    return


def scrape_html(url: str, session: requests.Session):
    """
    Scrape the html page and return the text
    """

    try:
        response = session.get(url, timeout=4)
        soup = BeautifulSoup(response.content, 'lxml', from_encoding=response.encoding)

        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()


        raw_content = get_raw_content(soup)
        lines = (line.strip() for line in raw_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = "\n".join(chunk for chunk in chunks if chunk)

        # Store in DB
        logger.opt(lazy=True).log("SCRAPE", f"Type: HTML | URL: {url} | Content length: {len(content.split())}")
        return content
    
    except Exception as e:
        logger.error(f"Error in scrapting HTML: {e} | URL: {url}")
        return




def get_raw_content(soup: BeautifulSoup):
    """
    Get the raw content from the soup
    """
    text = ""
    tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5']
    for element in soup.find_all(tags):
        text += element.text + "\n"
    return text
