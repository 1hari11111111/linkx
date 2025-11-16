
from playwright.async_api import async_playwright

async def vplinks_bypass(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(3500)
            btns=["#go",".btn","a#link","a[href*='go']"]
            for b in btns:
                try:
                    await page.click(b)
                    await page.wait_for_timeout(2000)
                except:
                    pass
            final = page.url
            await browser.close()
            return final
    except:
        return None
