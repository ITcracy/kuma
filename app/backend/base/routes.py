from typing import Callable, Dict, List, Optional, Type

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from .models import BaseOps


class CRUDRouter(APIRouter):
    def init_crud(
        self,
        ops: Type[BaseOps],
        schema_in: Dict[str, Type[BaseModel]],
        schema_out: Dict[str, Type[BaseModel]],
        dependencies: Optional[Dict[str, List[Callable]]] = None,
    ):
        self.ops = ops
        self.schema_in = schema_in
        self.schema_out = schema_out
        if not dependencies:
            dependencies = {}
        self.add_api_route(
            "",
            self.read(),
            methods=["GET"],
            response_model=List[schema_out.get("read")],
            dependencies=dependencies.get("read"),
            status_code=status.HTTP_200_OK,
        )
        self.add_api_route(
            "",
            self.create(),
            methods=["POST"],
            dependencies=dependencies.get("create"),
            status_code=status.HTTP_201_CREATED,
        )
        self.add_api_route(
            "",
            self.remove(),
            methods=["DELETE"],
            dependencies=dependencies.get("remove"),
            status_code=status.HTTP_204_NO_CONTENT,
        )

    def create(self):
        schema_in = self.schema_in.get("create")
        ops = self.ops

        async def _create(body: schema_in, ops: ops = Depends()):
            await ops.insert(body.dict())

        return _create

    def read(self):
        schema_out = self.schema_out.get("read")
        ops = self.ops

        async def _read(ops: ops = Depends()) -> List[schema_out]:
            result = await ops.select()
            return [schema_out.from_orm(res) for res in result]

        return _read

    def remove(self):
        ops = self.ops

        async def _remove(item_id: int, ops: ops = Depends()):
            await ops.delete(id=item_id)

        return _remove
