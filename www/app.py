import asyncio, os, json, time
from datetime import datetime
import logging; logging.basicConfig(level=logging.INFO)

from aiohttp import web

async def index(request):
    return web.Response(text='<h1>awesome blog</h1>',content_type='text/html')

async def second(request):
    return web.Response(text='<h2>second</h2>',content_type='text/html')

app = web.Application()
app.add_routes([
    web.get('/', index),
    web.get('/se', second),
])

web.run_app(app=app,
            host='127.0.0.1',
            port=8000)
