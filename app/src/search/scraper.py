import requests
from bs4 import BeautifulSoup
import fitz

from loguru import logger
level_search = logger.level("SCRAPE", no=38, color="<yellow>", icon="♣")


def extract_text_from_url(url: str, session: requests.Session):
    content = ""
    scrape_type = ''
    try:
        response = session.get(url, timeout=10)

        if url.endswith(".pdf") or response.headers.get('content-type') == 'application/pdf':
            content = scrape_pdf(response)
            scrape_type = 'PDF'

        elif "arxiv.org" in url:
            doc_num = url.split("/")[-1]
            content = scrape_arxiv(doc_num)
            scrape_type = 'Arxiv'

        else:
            content = scrape_html(response)
            scrape_type = 'HTML'

        logger.opt(lazy=True).log("SCRAPE", f"Type: {scrape_type} | URL: {url}| Content length: {len(content.split())}")

        # set to None if content is too short
        if content is None or len(content) < 100:
            return {'url': url, 'raw_content': None}
        else:
            content = content.replace('\n', ' ')
        
        return {'url': url, 'raw_content': content}
    
    except Exception as e:
        return {'url': url, 'raw_content': None}
    



def scrape_pdf(response):
    """
    Scrape the pdf and return the text
    """
    text = ""
    try:
        pdf_stream = response.content
        doc = fitz.open(stream = pdf_stream, filetype='pdf') 
        
        for page in doc:
            text += page.get_text() + ' '

        return text
    except Exception as e:
        logger.error(f"Error in scraping PDF: {e}")
        return



def scrape_arxiv(url: str):
    """
    Scrape the arxiv page and return the text
    """
    return


def scrape_html(response):
    """
    Scrape the html page and return the text
    """

    try:
        soup = BeautifulSoup(response.content, 'lxml', from_encoding=response.encoding)

        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()


        raw_content = get_raw_content(soup)
        lines = (line.strip() for line in raw_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = " ".join(chunk for chunk in chunks if chunk)

        # Store in DB
        
        return content
    
    except Exception as e:
        logger.error(f"Error in scrapting HTML: {e} | URL:")
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
