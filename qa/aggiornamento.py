import asyncio, subprocess, sys
from playwright.async_api import async_playwright
BASE="http://localhost:4174"
def serve(d): subprocess.run(f"rm -rf /home/claude/srv/* && cp -r /home/claude/{d}/* /home/claude/srv/", shell=True, check=True)
async def version(pg):
    await pg.goto(BASE+"/#/altro"); await pg.wait_for_timeout(1200)
    return (await pg.locator("dd.num").text_content()).strip()
async def bump(pg):
    await pg.evaluate("Object.defineProperty(document,'visibilityState',{value:'hidden',configurable:true}); document.dispatchEvent(new Event('visibilitychange')); Object.defineProperty(document,'visibilityState',{value:'visible',configurable:true}); document.dispatchEvent(new Event('visibilitychange'))")
async def scenario(b, p, name, first, second, controlled):
    ctx = await b.new_context(**p.devices["Pixel 7"], locale="it-IT")
    pg = await ctx.new_page(); errs=[]
    pg.on("pageerror", lambda e: errs.append(str(e)))
    serve(first)
    await pg.goto(BASE+"/#/conti"); await pg.wait_for_timeout(1500)
    await pg.get_by_role("button", name="Conto").first.tap()
    await pg.get_by_label("Nome").fill("Conto"); await pg.get_by_label("Saldo iniziale (€)").fill("500")
    await pg.get_by_role("button", name="Salva").tap(); await pg.wait_for_timeout(300)
    if controlled:
        await pg.reload(); await pg.wait_for_timeout(1200)
    ctrl = await pg.evaluate("!!navigator.serviceWorker.controller")
    v1 = await version(pg)
    serve(second)
    await bump(pg)
    ok_banner = True
    try: await pg.get_by_role("button", name="Aggiorna").wait_for(timeout=15000)
    except Exception: ok_banner = False
    if ok_banner:
        await pg.get_by_role("button", name="Aggiorna").tap(); await pg.wait_for_timeout(4500)
    v2 = await version(pg)
    await pg.goto(BASE+"/#/conti"); await pg.wait_for_timeout(800)
    data = await pg.locator(".list .name").all_text_contents()
    print(f"{name}: pagina gestita={ctrl} | {v1} -> {v2} | avviso={ok_banner} | dati={data} | errori={errs}")
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        await scenario(b, p, "0.8.0 -> 0.9.0 (telefono già in uso)", "old-dist", "new-dist", True)
        await scenario(b, p, "0.9.0 -> successiva, primo avvio", "new-dist", "newer-dist", False)
        await scenario(b, p, "0.9.0 -> successiva, app già in uso", "new-dist", "newer-dist", True)
        await b.close()
asyncio.run(main())
