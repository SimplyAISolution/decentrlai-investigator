import logging

from packages.collectors.base.registry import CollectorRegistry
from packages.collectors.http.collector import HTTPCollector
from packages.collectors.web_search.collector import WebSearchCollector
from packages.collectors.web_search.duckduckgo_provider import DuckDuckGoSearchProvider
from packages.evidence.storage.local import LocalEvidenceStorage
from packages.shared.db.session import get_engine, get_sessionmaker
from packages.graph.neo4j.connection import Neo4jConnection

from apps.worker.tasks.investigate import run_autonomous_investigation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def startup(ctx):
    logger.info("Initializing worker resources...")
    
    engine = get_engine()
    ctx["postgres_engine"] = engine
    ctx["postgres_session"] = get_sessionmaker(engine)
    
    neo4j_conn = Neo4jConnection()
    ctx["neo4j_conn"] = neo4j_conn
    ctx["neo4j_driver"] = neo4j_conn.get_driver()

    registry = CollectorRegistry()
    # Live internet search injected here
    registry.register(WebSearchCollector(provider=DuckDuckGoSearchProvider()))
    registry.register(HTTPCollector())
    
    ctx["registry"] = registry
    ctx["storage"] = LocalEvidenceStorage()
    
    logger.info("Worker resources loaded.")

async def shutdown(ctx):
    logger.info("Tearing down worker resources...")
    await ctx["postgres_engine"].dispose()
    await ctx["neo4j_conn"].close()

class WorkerSettings:
    functions = [run_autonomous_investigation]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = None
