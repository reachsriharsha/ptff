


import time
from logs import logger  # Import the logger from the logger.py file

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
        time.sleep(10)
        return
