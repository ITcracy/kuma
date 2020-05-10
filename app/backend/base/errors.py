from typing import Union

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.constants import REF_PREFIX
from fastapi.openapi.utils import validation_error_response_definition
from fastapi.responses import JSONResponse
from pydantic import ValidationError


async def http_error_handler(_: Request, exc: HTTPException):
    return JSONResponse({"errors": [exc.detail]}, status_code=exc.status_code)


async def http422_error_handler(
    _: Request, exc: Union[RequestValidationError, ValidationError],
) -> JSONResponse:
    return JSONResponse({"errors": exc.errors()}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,)


validation_error_response_definition["properties"] = {
    "errors": {
        "title": "Errors",
        "type": "array",
        "items": {"$ref": "{0}ValidationError".format(REF_PREFIX)},
    },
}


class EntityDoesNotExist(Exception):
    pass
