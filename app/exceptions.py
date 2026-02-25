from fastapi import Request, status
from fastapi.responses import JSONResponse


class DuplicateEntryError(Exception):
    def __init__(self, *args, name):
        self.name = name
        super().__init__(*args)


class NotFoundError(Exception):
    def __init__(self, *args, name):
        self.name = name
        super().__init__(*args)


class ResourceDisableError(Exception):
    def __init__(self, *args, name):
        self.name = name
        super().__init__(*args)


def duplicate_entry_handler(request: Request, exc: DuplicateEntryError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={
        "detail": f"Duplicate entry: {exc.name}",
        "path": request.url.path
    })

def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
        "detail": f"Not found: {exc.name}",
        "path": request.url.path
    })

def resource_disable_handler(request: Request, exc: ResourceDisableError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
        "detail": f"Disable: {exc.name}",
        "path": request.url.path
    })

