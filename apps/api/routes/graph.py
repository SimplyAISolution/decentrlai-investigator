from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

from packages.graph.neo4j.connection import Neo4jConnection

router = APIRouter(tags=["Graph"])

class GraphResponse(BaseModel):
    elements: list[dict[str, Any]]

@router.get("/investigations/{investigation_id}/graph", response_model=GraphResponse)
async def get_investigation_graph(investigation_id: str):
    conn = Neo4jConnection()
    driver = conn.get_driver()
    
    # Query Neo4j for all connections linked to this investigation ID
    query = """
    MATCH (s:Entity {investigation_id: $inv_id})-[r]->(t:Entity)
    RETURN s.name AS source, type(r) AS rel_type, t.name AS target
    """
    
    nodes = {}
    edges = []
    
    try:
        async with driver.session() as session:
            result = await session.run(query, inv_id=investigation_id)
            records = await result.data()
            
            for record in records:
                s_name = record["source"]
                t_name = record["target"]
                rel = record["rel_type"]
                
                # Deduplicate nodes using a dictionary
                nodes[s_name] = {"data": {"id": s_name, "label": s_name}}
                nodes[t_name] = {"data": {"id": t_name, "label": t_name}}
                
                edges.append({
                    "data": {
                        "source": s_name, 
                        "target": t_name, 
                        "label": rel
                    }
                })
                
        return {"elements": list(nodes.values()) + edges}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()
