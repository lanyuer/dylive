from playwright.sync_api import Playwright, sync_playwright
from playwright.sync_api import Page, expect
from playwright.async_api import async_playwright


async def get_websocket_url(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Note the change below: the user agent is set while creating the page
        context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        page = await context.new_page()

        # 访问页面
        await page.goto(url)  # Fixed: using 'page' instead of 'context'

        # 等待页面加载完成

        # 获取websocket URL
        ws_url = await page.evaluate('''() => {
            console.log(window.byted_acrawler.frontierSign('85b7d91a636fc42f73ca523b51402fbb'));

            return window.byted_acrawler.frontierSign('85b7d91a636fc42f73ca523b51402fbb');
        }''')

        print(f"urls is :{ws_url}")

        await browser.close()

        return ws_url

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    signature = loop.run_until_complete(get_websocket_url(
        'https://live.douyin.com/326500301367'))
    print(signature)
