from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, status
from starlette.responses import JSONResponse

from app.controller import book_controller
from core.exception.runtime_exception import RuntimeException
from core.response import Response
from core.status_enum import StatusEnum

app = FastAPI()
app.include_router(book_controller.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 提取错误信息
    error_details = []
    for error in exc.errors():
        field_path = ".".join(map(str, error["loc"]))
        error_details.append({
            "field": field_path,
            "message": error["msg"]
        })

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=Response.error(message=str(error_details), code=StatusEnum.validate_fail).model_dump())


@app.exception_handler(RuntimeException)
async def runtime_exception_handler(request: Request, exc: RuntimeException):
    return JSONResponse(status_code=status.HTTP_200_OK, content=Response.error(message=exc.message, code=exc.code).model_dump())

@app.exception_handler(Exception)
async def runtime_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=status.HTTP_200_OK, content=Response.error(message="系统内部错误", code=StatusEnum.error).model_dump())
