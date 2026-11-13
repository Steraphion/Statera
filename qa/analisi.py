import asyncio, re
from playwright.async_api import async_playwright
BASE="http://localhost:4173"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for name, opts, scheme in [("mob", {**p.devices["Pixel 7"]}, "light"), ("pc", {"viewport": {"width": 1280, "height": 900}}, "dark")]:
            ctx = await b.new_context(**opts, locale="it-IT", color_scheme=scheme)
            pg = await ctx.new_page(); errs=[]
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
            await pg.goto(BASE+"/#/conti"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(500)
            await pg.get_by_role("button", name="Conto").first.click()
            await pg.get_by_label("Nome").fill("Conto"); await pg.get_by_label("Saldo iniziale (€)").fill("3000")
            await pg.locator("dialog input[type=date]").fill("2025-12-01")
            await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(300)
            print("inseriti:", await pg.evaluate(open(__import__('os').path.join(__import__('os').path.dirname(__file__), 'anno-di-esempio.js')).read()))
            await pg.goto(BASE+"/#/analisi"); await pg.reload(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(1000)
            await pg.screenshot(path=f"/home/claude/qa/an-{name}-0.png", full_page=True)
            print("errori finora:", errs)
            # budget
            await pg.get_by_role("button", name="Imposta budget").click()
            await pg.get_by_label("Budget Casa (€)").fill("600")
            await pg.get_by_label("Budget Spesa alimentare (€)").fill("250")
            await pg.get_by_label("Budget Svago (€)").fill("30")
            await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(500)
            await pg.locator(".bars .row").first.click(); await pg.wait_for_timeout(200)
            await pg.screenshot(path=f"/home/claude/qa/an-{name}.png", full_page=True)
            # hover column
            hits = pg.locator("rect.hit")
            await hits.nth(10).hover(); await pg.wait_for_timeout(200)
            print(name, "tooltip:", (await pg.locator(".tooltip").inner_text()).replace("\n"," | "))
            await pg.screenshot(path=f"/home/claude/qa/an-{name}-tip.png")
            print(name, "tiles:", (await pg.locator(".tiles").inner_text()).replace("\n"," "))
            print(name, "budget:", (await pg.locator(".meters").inner_text()).replace("\n"," | "))
            await pg.get_by_role("radio", name="Anno").click(); await pg.wait_for_timeout(300)
            print(name, "anno:", (await pg.locator(".tiles").inner_text()).replace("\n"," "))
            await pg.get_by_role("radio", name="Mese").click()
            await pg.get_by_role("button", name="Vedi i movimenti ›").click(); await pg.wait_for_timeout(500)
            print(name, "vai a cerca:", await pg.evaluate("location.hash"), (await pg.locator(".summary").inner_text()).replace("\n"," "))
            print(name, "errori:", errs)
            await ctx.close()
        await b.close()
asyncio.run(main())
