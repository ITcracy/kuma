from typing import Any, Dict, List, Mapping, Optional, Union

from loguru import logger
from sqlalchemy import Table, and_

from ..core.db import database
from .errors import EntityDoesNotExist


def _log_query(query: str, query_params: Union[Dict, List] = None) -> None:
    logger.debug("query: {0}, values: {1}", query, query_params)


class BaseOps:
    table: Table

    def __init__(self):
        self._db = database

    async def _log_and_fetch(self, query: str) -> List[Mapping]:
        _log_query(query)
        return await self._db.fetch_all(query)

    async def _log_and_fetch_row(self, query: str) -> Mapping:
        _log_query(query)
        return await self._db.fetch_one(query)

    async def _log_and_execute(self, query: str, values: Optional[Dict] = None) -> None:
        _log_query(query, values)
        await self._db.execute(query, values)

    async def _log_and_execute_many(self, query: str, values: Optional[List[Dict]] = None) -> None:
        _log_query(query, values)
        await self._db.execute_many(query, values)

    async def select_one(self, id: int) -> Mapping:
        query = self.table.select().where(self.table.c.id == id)
        item = await self._log_and_fetch_row(query)
        if item:
            return item
        raise EntityDoesNotExist(f"user with id:{id} does not exist")

    async def select(self, query_params: Optional[dict] = None) -> List[Mapping]:
        query = self.table.select()
        if query_params:
            where_clause = {self.table.c[k]: self.table.c[v] for k, v in query_params.items()}
            query = query.where(and_(**where_clause))
        return await self._log_and_fetch(query)

    async def insert(self, obj: Dict):
        query = self.table.insert().values(**obj)
        await self._log_and_execute(query)

    async def update(self, obj: Dict, condition: Dict):
        where_clause = {self.table.c[k]: self.table.c[v] for k, v in condition.items()}
        query = self.table.update().where(and_(**where_clause)).values(**obj)
        await self._log_and_execute(query)

    async def delete(self, id: int):
        query = self.table.delete().where(self.table.c.id == id)
        await self._log_and_execute(query)
