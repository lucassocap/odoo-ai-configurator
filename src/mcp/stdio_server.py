"""
Standard MCP Server for Odoo Configurator
Dependency-free implementation (Python 3.9 compatible)
"""
import sys
import json
import logging
import os
from typing import Any, Dict, List, Optional

# Configure logging to stderr so it doesn't interfere with stdout JSON-RPC
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("mcp-server")

# Import Orchestrator
try:
    from ..orchestrator import Orchestrator
except ImportError:
    # Allow running as script from src/..
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from orchestrator import Orchestrator

# Global state
ORCHESTRATOR = None

def get_orchestrator() -> Orchestrator:
    """Get or create the orchestrator instance"""
    global ORCHESTRATOR
    if ORCHESTRATOR:
        return ORCHESTRATOR
    
    # Determine project config from env
    rag_path = os.environ.get("ODOO_RAG_PATH", "projects/odoo-bearings-config/knowledge/rag_db")
    memory_config = {"rag_path": rag_path}
    
    ORCHESTRATOR = Orchestrator(
        url="http://localhost:8069",
        memory_config=memory_config
    )
    return ORCHESTRATOR

class MCPServerRequest:
    def __init__(self, request: Dict):
        self.jsonrpc = request.get("jsonrpc")
        self.method = request.get("method")
        self.params = request.get("params", {})
        self.id = request.get("id")

def handle_tool_call(name: str, args: Dict) -> Dict:
    """Handle tool execution"""
    if name == "search_project_memory":
        query = args.get("query", "")
        orch = get_orchestrator()
        results = []
        if orch.agents:
            # Use first agent to search shared memory
            hits = orch.agents[0].search_context(query, n_results=5)
            for hit in hits:
                doc = hit.get('document', '')
                meta = hit.get('metadata', {})
                results.append(f"Source: {meta.get('agent_name', 'System')}\nContent: {doc}\n---\n")
        
        content = "\n".join(results) if results else "No relevant memories found."
        return {"content": [{"type": "text", "text": content}]}
    
    elif name == "configure_odoo":
        instruction = args.get("instruction", "")
        orch = get_orchestrator()
        result = orch.configure(instruction)
        return {"content": [{"type": "text", "text": str(result)}]}
        
    elif name == "get_project_status":
        return {"content": [{"type": "text", "text": "Project 'Bearings Inc' active. Running on Odoo 17."}]}
    
    raise ValueError(f"Unknown tool: {name}")

def main():
    """Main JSON-RPC loop"""
    logger.info("Starting Odoo MCP Server...")
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            method = request.get("method")
            req_id = request.get("id")
            
            response = None
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {"name": "odoo-configurator", "version": "1.0.0"}
                    }
                }
            
            elif method == "notifications/initialized":
                # client acknowledging init
                pass
                
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": [
                            {
                                "name": "search_project_memory",
                                "description": "Search the project's RAG memory/context",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {"query": {"type": "string"}},
                                    "required": ["query"]
                                }
                            },
                            {
                                "name": "configure_odoo",
                                "description": "Configure Odoo via natural language",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {"instruction": {"type": "string"}},
                                    "required": ["instruction"]
                                }
                            },
                            {
                                "name": "get_project_status",
                                "description": "Get current project status",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {},
                                }
                            }
                        ]
                    }
                }
                
            elif method == "tools/call":
                params = request.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                
                try:
                    result = handle_tool_call(name, args)
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": result
                    }
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32603, "message": str(e)}
                    }

            if response:
                print(json.dumps(response), flush=True)
                
        except json.JSONDecodeError:
            continue
        except Exception as e:
            logger.error(f"Server error: {e}")

if __name__ == "__main__":
    main()
