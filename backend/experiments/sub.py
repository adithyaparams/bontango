
from fastapi.routing import APIRouter
from starlette.responses import RedirectResponse
from main import app

subapi = APIRouter(prefix="/subapi")


@subapi.get("/sub")
async def read_sub():
    return {"message": "Hello World from sub API"}


@subapi.get("/redirect")
async def redirect():
    url = app.url_path_for("redirected")
    response = RedirectResponse(url=url)
    return response


@subapi.get("/redirected")
async def redirected():
    return {"message": "you've been redirected"}


app.include_router(subapi)