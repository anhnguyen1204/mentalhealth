from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import SummaryExtractor
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
import openai
import streamlit as st
from src.global_settings import STORAGE_PATH, FILES_PATH, CACHE_FILE
from src.prompts import CUSTORM_SUMMARY_EXTRACT_TEMPLATE


# Set OpenAI API key and model settings
openai.api_key = #your api key
Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.2)

def ingest_documents():
    # Load documents from file path instead of directory (for portability across devices)
    documents = SimpleDirectoryReader(
        input_files=FILES_PATH,
        filename_as_id=True
    ).load_data()

    # Print document IDs for debugging
    for doc in documents:
        print(doc.id_)

    # Try to load the ingestion cache
    try:
        cached_hashes = IngestionCache.from_persist_path(CACHE_FILE)
        print("Cache file found. Running using cache...")
    except Exception:
        cached_hashes = ""
        print("No cache file found. Running without cache...")

    # Set up the ingestion pipeline
    pipeline = IngestionPipeline(
        transformations=[
            TokenTextSplitter(
                chunk_size=512,
                chunk_overlap=20
            ),
            SummaryExtractor(
                summaries=["self"],
                prompt_template=CUSTORM_SUMMARY_EXTRACT_TEMPLATE
            ),
            OpenAIEmbedding()
        ],
        cache=cached_hashes
    )

    # Run the pipeline and persist cache
    nodes = pipeline.run(documents=documents)
    pipeline.cache.persist(CACHE_FILE)

    return nodes
