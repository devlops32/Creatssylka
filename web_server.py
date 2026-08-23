from aiohttp import web
import os
import time
from datetime import datetime, timedelta
import asyncio

links = {}  # {link_id: (filepath, expire_time)}

async def handle_photo(request):
    link_id = request.match_info.get('id')
    if link_id not in links:
        return web.Response(text="Ссылка истекла или не существует", status=404)
    
    filepath, expire = links[link_id]
    if datetime.now() > expire:
        del links[link_id]
        return web.Response(text="Ссылка истекла", status=404)
    
    return web.FileResponse(filepath)

async def cleanup_loop():
    while True:
        await asyncio.sleep(60)
        now = datetime.now()
        to_delete = [k for k, (_, exp) in links.items() if now > exp]
        for k in to_delete:
            try:
                os.remove(links[k][0])
            except:
                pass
            del links[k]

def start_web():
    app = web.Application()
    app.router.add_get('/photo/{id}', handle_photo)
    runner = web.AppRunner(app)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, WEB_HOST, WEB_PORT)
    loop.run_until_complete(site.start())
    loop.create_task(cleanup_loop())
    loop.run_forever()