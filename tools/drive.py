import asyncio, json, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 390, 'height': 900}, device_scale_factor=2)
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
        await pg.goto('http://127.0.0.1:8765/'); await pg.wait_for_timeout(600)
        await pg.screenshot(path='/tmp/webt/s1.png', full_page=True)
        await pg.click('#scan'); await pg.wait_for_selector('#list li'); await pg.wait_for_timeout(200)
        await pg.click('#list li:nth-child(1)'); await pg.fill('#pw', 'a+b c%20&=中文')
        await pg.screenshot(path='/tmp/webt/s2.png', full_page=True)
        pg.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
        await pg.click('#apply'); await pg.wait_for_timeout(800)
        open('/tmp/webt/big.gcode', 'wb').write(b';QQS test\n' + b'G1 X1 Y1\n' * 40000)
        await pg.set_input_files('#file', '/tmp/webt/big.gcode'); await pg.wait_for_timeout(3000)
        await pg.screenshot(path='/tmp/webt/s3.png', full_page=True)
        # hotspot mode with a short password
        await pg.click('#mAp'); await pg.fill('#pw', '1234'); await pg.click('#apply'); await pg.wait_for_timeout(300)
        print('wmsg', await pg.inner_text('#wmsg'))
        print('umsg', await pg.inner_text('#umsg'))
        print('errors', errs)
        await b.close()
asyncio.run(main())
