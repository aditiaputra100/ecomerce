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


class FileMaximumError(Exception):
    ...


def duplicate_entry_handler(request: Request, exc: DuplicateEntryError) -> JSONResponse:
    return JSONResponse(
        content={"success": False, "message": f"Duplicate entry: {exc.name}", "data": None},
        status_code=status.HTTP_409_CONFLICT
    )


def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        content={"success": False, "message": f"Not found: {exc.name}", "data": None},
        status_code=status.HTTP_404_NOT_FOUND
    )


def resource_disable_handler(request: Request, exc: ResourceDisableError) -> JSONResponse:
    return JSONResponse(
        content={"success": False, "message": f"Disable: {exc.name}", "data": None},
        status_code=status.HTTP_400_BAD_REQUEST
    )
