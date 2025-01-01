import os




SPLITTER_CHUNK_SIZE = int(os.getenv("SPLITTER_CHUNK_SIZE", "250"))
SPLITTER_CHUNK_OVERLAP_SIZE = int(os.getenv("SPLITTER_CHUNK_OVERLAP_SIZE", "25"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en")
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")

MILVUS_URI = os.getenv("MILVUS_URI", "http://milvus_standalone:19530")