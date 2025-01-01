

#Standard import section
import os
import time
from datetime import datetime
#Third party import section
from langchain_community.document_loaders import(
    PyPDFLoader, 
    Docx2txtLoader, 
    TextLoader, 
    UnstructuredHTMLLoader, 
    UnstructuredExcelLoader
) 
from langchain_community.document_loaders.powerpoint import UnstructuredPowerPointLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_milvus.vectorstores import Milvus



#Local import section
from logs import logger  # Import the logger from the logger.py file
import utils
import config


class Synapse:
    def __init__(self):
        pass
        
    def __str__(self):
        return f"Synapse(weight={self.weight}, neuron={self.neuron})"

    '''
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.neuron == other.neuron and self.weight == other.weight

    def __hash__(self):
        return hash((self.neuron, self.weight))
    '''

    def ingest_data_to_vector_db(self, 
                                 source: str, 
                                 title: str, 
                                 description: str, 
                                 collection_name: str, 
                                 metadata:str, 
                                 user_id: int):

        log = f"ingest_data_to_vector_db: {source}, {title}, {description}, {collection_name}, {user_id}"
        logger.debug(log)
        #check if the source is file or url
        if os.path.isfile(source):
            self._ingest_file(source, title, description, collection_name, metadata, user_id)
            return
        else:
            self._ingest_url(source, title, description, collection_name, metadata, user_id)
            return
        
        logger.error(f"ingest_data_to_vector_db: Source is {source} invalid")    
        return

    def _ingest_file(self, 
                    source: str, 
                    title: str, 
                    description: str, 
                    collection_name: str, 
                    metadata:str, 
                    user_id: int):
        
        fi_stime = datetime.now()

        file_ext = utils.get_file_extension(source)

        if file_ext == 'pdf':
            loader = PyPDFLoader(source)
        elif file_ext == 'docx':
            loader = Docx2txtLoader(source)
        elif file_ext == 'txt' or file_ext == 'md':
            loader = TextLoader(source)
        elif file_ext == 'html':
            loader = UnstructuredHTMLLoader(source)
        elif file_ext == 'xlsx':
            loader = UnstructuredExcelLoader(source)
        elif file_ext == 'pptx' or file_ext == 'ppt':
            loader = UnstructuredPowerPointLoader(source)
        else:
            logger.error(f"File type not supported: {file_ext} for file: {source}")
            return


        #load and split file
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size = config.SPLITTER_CHUNK_SIZE, 
            chunk_overlap = config.SPLITTER_CHUNK_OVERLAP_SIZE
            )
        chunks = splitter.split_documents(documents)
        
        for c in chunks:
            c.metadata['title'] = title
            c.metadata['tag'] = metadata
            c.metadata['source'] = source
        fi_etime = datetime.now()
        logger.info(f"File load and split time: {fi_etime - fi_stime}")

        #create embeddings
        si_stime = datetime.now()

        hf_embeddings = HuggingFaceBgeEmbeddings(
            model_name = config.EMBEDDING_MODEL,
            model_kwargs = {"device": config.EMBEDDING_DEVICE},
            encode_kwargs = {"normalize_embeddings" : True}
        )

        Milvus.from_documents(
                    documents = chunks,
                    embedding = hf_embeddings,
                    collection_name = collection_name,
                    connection_args = {'uri' : config.MILVUS_URI},
                    drop_old = False,
                    enable_dynamic_field = True,    
                )
        si_etime = datetime.now()
        logger.info(f"Embedding creation time: {si_etime - si_stime}")
        return
    
    def _ingest_url(self, 
                    source: str, 
                    title: str, 
                    description: str, 
                    collection_name: str, 
                    metadata:str, 
                    user_id: int):
        pass