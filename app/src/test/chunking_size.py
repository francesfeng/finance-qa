import asyncio

from typing import List, Optional
from app.models.models import DocumentSearch, DocumentChunkMetadata

from app.src.utils.chunking import chunking
from app.src.search.google import GoogleSearch
from app.src.context.context import Context


async def search(queries: List[str], period: str="m3"):
    # get search links
    search = GoogleSearch(queries)
    tasks = [search.search(q) for q in queries]
    docs = await asyncio.gather(*tasks)
    docs = [item for items in docs for item in items]

    # scrape the urls
    urls = [d.metadata.url for d in docs]
    text = search.scrape_urls(urls)

    # update the text and return valid docs
    for i, t in enumerate(text):
        if t['raw_content']:
            docs[i].text = t['raw_content']

    return [d for d in docs if d.text]


def get_chunking(docs: List[DocumentSearch], chunking_sizes: List[int]=[350, 1000, 4000]):
    """
        Chunking the document by different chunking sizes
    """
    results = []
    for chunking_size in chunking_sizes:
        context = Context()
        context.chunking_size = chunking_size
        
        chunks = context.get_chunks(docs)
        chunks_simi = context.semantic_search(chunks)
        results.append(chunks_simi)
        print(f"Completed chunking size: {chunking_size}")
    return results
