import os
from neo4j import AsyncGraphDatabase

class Neo4jConnection:
    def __init__(self, uri: str | None = None, user: str | None = None, password: str | None = None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "decentrlai123")
        self._driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))

    async def close(self) -> None:
        await self._driver.close()

    def get_driver(self):
        return self._driver
