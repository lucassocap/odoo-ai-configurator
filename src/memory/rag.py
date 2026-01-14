"""
RAG Memory System
Vector database for context persistence using ChromaDB
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: ChromaDB not installed. RAG memory will be disabled.")
    print("Install with: pip install chromadb sentence-transformers")


class RAGMemory:
    """Vector database for storing and retrieving context"""
    
    def __init__(self, persist_directory: str = None):
        if not CHROMADB_AVAILABLE:
            self.enabled = False
            return
        
        if persist_directory is None:
            persist_directory = Path(__file__).parent.parent.parent / "memory" / "rag"
            persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.persist_directory = str(persist_directory)
        self.enabled = True
        
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Use sentence transformers for embeddings
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            
            self.collection = self.client.get_or_create_collection(
                name="odoo_context",
                embedding_function=self.embedding_function,
                metadata={"description": "Odoo AI Configurator context memory"}
            )
        except Exception as e:
            print(f"Warning: Failed to initialize RAG memory: {e}")
            self.enabled = False
    
    def store(self, action: str, params: Dict, result: str, 
             context: str, agent_name: str, metadata: Dict = None):
        """Store an action in memory"""
        if not self.enabled:
            return
        
        try:
            timestamp = datetime.now().isoformat()
            doc_id = f"{agent_name}_{action}_{timestamp}"
            
            # Create document text
            document = f"""
            Agent: {agent_name}
            Action: {action}
            Context: {context}
            Parameters: {json.dumps(params)}
            Result: {result}
            """
            
            # Metadata
            meta = {
                "agent_name": agent_name,
                "action": action,
                "result": result,
                "timestamp": timestamp
            }
            
            if metadata:
                meta.update(metadata)
            
            self.collection.add(
                documents=[document],
                metadatas=[meta],
                ids=[doc_id]
            )
        except Exception as e:
            print(f"Warning: Failed to store in RAG: {e}")
    
    def search(self, query: str, n_results: int = 5, 
              agent_name: str = None) -> List[Dict]:
        """Search for relevant context"""
        if not self.enabled:
            return []
        
        try:
            where_filter = None
            if agent_name:
                where_filter = {"agent_name": agent_name}
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
            
            # Format results
            formatted_results = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'document': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else None
                    })
            
            return formatted_results
        except Exception as e:
            print(f"Warning: Failed to search RAG: {e}")
            return []
    
    def get_recent(self, agent_name: str = None, limit: int = 10) -> List[Dict]:
        """Get recent actions"""
        if not self.enabled:
            return []
        
        try:
            where_filter = None
            if agent_name:
                where_filter = {"agent_name": agent_name}
            
            results = self.collection.get(
                where=where_filter,
                limit=limit
            )
            
            formatted_results = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents']):
                    formatted_results.append({
                        'document': doc,
                        'metadata': results['metadatas'][i] if results['metadatas'] else {}
                    })
            
            return formatted_results
        except Exception as e:
            print(f"Warning: Failed to get recent from RAG: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get statistics about stored context"""
        if not self.enabled:
            return {'enabled': False}
        
        try:
            count = self.collection.count()
            return {
                'enabled': True,
                'total_documents': count,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            return {'enabled': False, 'error': str(e)}
