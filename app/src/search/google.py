import os
import json
import requests
from loguru import logger
import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Union
from functools import partial
from .scraper import extract_text_from_url
from concurrent.futures.thread import ThreadPoolExecutor
from ..database.cache_emb import EmbeddingCache
from ..database.cache_search import SearchCache


from app.src.config.config import Config
from app.src.context.context import Context
from app.models.models import DocumentMetadata, Source, Type, DocumentSearch

level_search = logger.level("GOOGLE_SEARCH", no=38, color="<yellow>", icon="♣")
level_search_parallel = logger.level("GOOGLE_SEARCH_PARALLEL", no=38, color="<yellow>", icon="♣")

class GoogleSearch:

    def __init__(self, 
                 queries: List[str], 
                 date_period: Optional[str] = None, 
                 config_path: str=None
                 ):
        # set environment variables
        self.api_key = os.environ.get('GOOGLE_API_KEY')
        self.cx_id = os.environ.get('CUSTOM_SEARCH_ENGINE_ID')

        # set search parameters
        self.queries = queries
        self.unique_urls = []

        if date_period:
            valid_date_period = self._validate_date_period(date_period)
            if valid_date_period:
                self.date_period = valid_date_period
        else:
            self.date_period = None

        

        # set config
        config = Config(config_path)
        self.max_search_results_per_query = config.max_search_results_per_query
        self.user_agent = config.user_agent
        self.model_embed = config.model_embed
        self.chunking_size = config.chunking_size
        self.embedding_dimension = config.embedding_dimension


        assert self.api_key is not None
        assert self.cx_id is not None

    
    async def run(self) -> List[DocumentSearch]:

        results = []
        
        # Search urls based on the query
        if len(self.queries) == 1:
            docs = self.search(self.queries[0])
        else:

            tasks = [self.search(q) for q in self.queries]
            docs = await asyncio.gather(*tasks)
            docs = [item for items in docs for item in items]

        # extract the urls from the search results
        queries_dict = {doc.id: doc.query for doc in docs}
        doc_ids = list(queries_dict.keys())

        # Retrieve the embeddings from the database
        db = EmbeddingCache()
        retrieved_context = await db.retrieve_embeddings(doc_ids)
        
        # Add the query to the retrieved context
        for doc in retrieved_context:
            doc.query = queries_dict[doc.metadata.document_id]


        retrieved_ids = set(doc.metadata.document_id for doc in retrieved_context)
        # Identify the missing embeddings
        missing_docs = []
        for doc in docs:
            if doc.id not in retrieved_ids:
                missing_docs.append(doc)


        # Find the optimal number of threads, max is the number of queries
        num_threads = len(self.queries)

        # While the number of docs to process is less than the number of threads, reduce the number of threads
        while(len(missing_docs)/num_threads < num_threads):
            num_threads -= 1
        # return the ceiling of total number of missing docs / the number of threads
        num_elements = len(missing_docs)/num_threads
        num_elements = int(num_elements) if len(missing_docs) % num_threads == 0 else int(num_elements) + 1

        # Split the missing docs into chunks
        missing_docs_list = [missing_docs[i:i+num_elements] for i in range(0, len(missing_docs), num_elements)]

        #Scrape, chunking and embedding missing result
        scrapped_context = []
        if len(missing_docs_list) > 0:
            with ThreadPoolExecutor() as executor:
                missing_context = executor.map(self.run_query, missing_docs_list)
            scrapped_context = [item for doc in missing_context for item in doc]
            

            # TODO: Insert the embedding to cache
            asyncio.create_task(db.insert_embeddings(scrapped_context, self.chunking_size, self.model_embed, self.embedding_dimension))


        # Combine the retrieved context and missing context
        context = retrieved_context + scrapped_context

        context_class = Context()
        similar_context = context_class.semantic_search(context)
        return similar_context


        
    

    def run_query(self, docs: List[DocumentSearch]):

        # scrape the urls and get the text
        urls = [doc.metadata.url for doc in docs]
        content = self.scrape_urls(urls)

        # Add retrieved text to the docs
        valid_docs = []
        for i in range(len(docs)):
            if content[i]['raw_content'] is not None:
                docs[i].text = content[i]['raw_content']
                valid_docs.append(docs[i])

        #Chunking 
        if len(valid_docs) > 0:
            context = Context()
            chunks = context.get_chunks(valid_docs)
            return chunks
        else:
            return []
        
            



    async def search(self, query: str, max_results: Optional[int] = None):
        """
        Search Google for the query and return the results
        #TODO Transform into functionall, with parameters
            There are a few optionalities can add to google search: see here https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list
            fileType=pdf (only include PDF search results)
            dateRestrict=m3 (to include only last 3 months data)
            gl=uk (to include only UK results, now showing big difference)
            sort=date (not shown good result)

        """

        # construct the date parameter in google API     
        if self.date_period:
            q_date = f"&dateRestrict={self.date_period}"
        else:
            q_date = ""

        # get the search results using Google API
        url = f"https://www.googleapis.com/customsearch/v1?key={self.api_key}&cx={self.cx_id}&q={query}&start=1{q_date}"
        resp = requests.get(url)
        max_results = max_results or self.max_search_results_per_query 

        if resp is None:
            return 
        try: 
            search_results = json.loads(resp.text)
        except Exception as e:
            logger.error(f"Error loading search results: {e}")
            return
        if search_results is None:
            return
        
        # Retrieve search results
        results = search_results.get('items', [])
        logger.opt(lazy=True).log("GOOGLE_SEARCH", f"Search term: {query} | Number of results: {len(results)} | Search Results: {search_results}")
      

        # filter out youtube links, and reform the results
        # TODO: Uploading to Database
        docs = []
        for result in results:
            
            # Filter out Youtube links
            if 'youtube.com' in result['link']:
                continue
            
            # Skip if the link is already in the unique_urls
            if result['link'] in self.unique_urls:
                continue

            # Create a DocumentChunk object

            metadata = DocumentMetadata(
                source=Source.google_search,
                type = Type.html,
                title=result['title'],
                url=result['link'],
                publisher=result['displayLink'],
                created_at=self._extract_date(result['snippet'])
            )

            doc = DocumentSearch(
                id=metadata.url.replace("'", ""),  # remove \' in url that used for ID
                text='',
                query=query,
                metadata=metadata
            )
            docs.append(doc)

            # Add the new link to the unique_urls
            self.unique_urls.append(result['link'])

        # Upload the search result to search_cache
        search_cache = SearchCache()
        asyncio.create_task(search_cache.insert_searches(docs))

        return docs[:max_results]
    
    
    def scrape_urls(self, urls: List[str]) -> List[str]:
        """
        Scrape the urls and return the text
        """
        texts = []
        session = requests.Session()
        session.headers.update({
            "User-Agent": self.user_agent
        })

        time_start = time.time()
        partial_extract = partial(extract_text_from_url, session=session)
        with ThreadPoolExecutor(max_workers=20) as executor:
            contents = executor.map(partial_extract, urls)
        time_end = time.time()
        logger.opt(lazy=True).log("GOOGLE_SEARCH", f"Scrapping | Number of URLs: {len(urls)} | Processing time: {time_end - time_start} seconds | URLs: {urls}")

        res = [content for content in contents]
        return res
    


    def _validate_date_period(self, date_period: str) -> Optional[str]:
        """
        Validate the date period. see https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list
        """
        date_period = date_period.lower()
        values = ['d'+str(i) for i in range(1, 32)] + ['w'+str(i) for i in range(1, 53)] + ['m'+str(i) for i in range(1, 13)] + ['y'+str(i) for i in range(1, 11)]
        if date_period in values:
            return date_period
        else:
            return
        

    def _extract_date(self, snippet: str) -> str:
        """
        Extract the date from the Google search snippet results, normally, it is in 3 formsts (1) 2 days ago (2) 6 hours ago (3) Nov 22, 2023
        Args:
            snippet: the snippet from Google search results
        Returns:
            date: the date in string format, YYYY-MM-DD
        """
        
        date_str = snippet.split('...')[0].strip()
        date = None

        if len(date_str) > 0:

            # Convert the date if in 'xx hours ago format'
            if 'hours ago' in date_str:
                num_hours = int(date_str.split(' ')[0])
                date = datetime.now() - timedelta(hours=num_hours)
                return date.strftime('%Y-%m-%d')

            
            # Convert the date if in 'xx days ago format'
            if 'days ago' in date_str:
                num_days = int(date_str.split(' ')[0])
                date = datetime.now() - timedelta(days=num_days)
                return date.strftime('%Y-%m-%d')
            
            # Convert the date if in 'MMM DD, YYYY' format
            else:
                try:
                    date = datetime.strptime(date_str, '%b %d, %Y')
                    return date.strftime('%Y-%m-%d')
                except:
                    return
            return

