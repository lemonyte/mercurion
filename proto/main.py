import os

from deta import Deta
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import Message

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['POST'],
)
templates = Jinja2Templates(directory='templates')
deta = Deta()
messages_db = deta.Base('messages')
hostname = os.getenv('DETA_SPACE_APP_HOSTNAME')


@app.get('/', response_class=RedirectResponse)
async def index():
    return RedirectResponse('/inbox')


@app.get('/inbox', response_class=HTMLResponse)
async def inbox(request: Request):
    messages = messages_db.fetch({'destination': hostname}).items
    messages = sorted(messages, key=lambda m: m['timestamp'], reverse=True)
    return templates.TemplateResponse(
        'messages.html',
        {
            'request': request,
            'messages': messages,
        },
    )


@app.get('/sent', response_class=HTMLResponse)
async def sent(request: Request):
    messages = messages_db.fetch({'origin': hostname}).items
    messages = sorted(messages, key=lambda m: m['timestamp'], reverse=True)
    return templates.TemplateResponse(
        'messages.html',
        {
            'request': request,
            'messages': messages,
        },
    )


@app.get('/compose', response_class=HTMLResponse)
async def compose(request: Request):
    return templates.TemplateResponse(
        'compose.html',
        {
            'request': request,
        },
    )


@app.post('/api/receive', status_code=201)
# async def api_receive(request: Request, message: Message):
async def api_receive(message: Message):
    if hostname not in (message.destination, message.origin):
        raise HTTPException(
            status_code=400,
            detail=(
                "Destination does not match location reached.\n"
                f"Destination: {message.destination}\nLocation: {hostname}"
            ),
        )
    # NOTE: Disabled because headers are not proxied through Space's proxy, so request origin is unknown.
    # Without this check, message origin can be spoofed.
    # if message.origin != request.client.host:  # type: ignore
    #     raise HTTPException(
    #         status_code=400,
    #         detail=(
    #             "Origin does not match client host.\n"
    #             f"Origin: {message.origin}\nClient host: {request.client.host}"  # type: ignore
    #         ),
    #     )
    messages_db.put(message.dict())
    return


@app.get('/api/message/{id}', response_model=Message)
async def api_message(id: str):
    messages_db.update({'read': True}, key=id)
    return messages_db.get(id)


@app.exception_handler(404)
async def not_found_handler(request: Request, exception):  # pylint: disable=unused-argument
    return templates.TemplateResponse('404.html', {'request': request})
