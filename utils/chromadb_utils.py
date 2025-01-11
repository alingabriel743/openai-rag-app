import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import sqlite3

import chromadb
from chromadb.config import Settings
import tempfile
from chromadb.api.client import SharedSystemClient
import re

SharedSystemClient.clear_system_cache()
chroma_client = chromadb.Client()

def sanitize_collection_name(name):
    sanitized_name = re.sub(r"[^a-zA-Z0-9_-]", "_", name) 
    return sanitized_name[:63]  

def create_or_get_collection(collection_name):
    print("here i am")
    print(chroma_client.list_collections())
    existing_collections = [col.name for col in chroma_client.list_collections()]
    
    if collection_name in existing_collections:
        return chroma_client.get_collection(name=collection_name)
    return chroma_client.create_collection(name=collection_name)

def add_documents_to_collection(collection, chunks, embeddings):
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        collection.add(
            ids=[f"chunk_{idx}"],
            documents=[chunk],
            metadatas=[{"chunk_index": idx}],
            embeddings=[embedding],
        )

def query_collection(collection, query_embedding, n_results=3):
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    if "documents" in results and results["documents"]:
        return results["documents"][0]  
    return [] 