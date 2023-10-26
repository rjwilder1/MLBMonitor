import json
import os
import time
import random
from undetected_playwright import stealth_async
from urllib.request import Request, urlopen

import asyncio
from playwright.async_api import async_playwright

GameCodes = []

proxy_strings = []

with open('proxies.txt', 'r') as file:
    proxy_strings = file.readlines()

proxies = []

for proxy_str in proxy_strings:
    parts = proxy_str.split(':')
    ip_port = f"{parts[0]}:{parts[1]}"
    username = parts[2]
    password = parts[3]
    proxy_config = {
        "server": ip_port,
        "username": username,
        "password": password.strip("\n")
    }
    proxies.append(proxy_config)

async def GetGameUrl(game):
    #url = f"https://mlb.tickets.com/?agency=MLB_MPV&orgid=18&pid={game}#/event/{game}"
    url = f"https://mlb.tickets.com/?agency=MLB_MPV&orgid=18&pid={game}#/event/{game}/ticketlist/?view=sections&minPrice=0&maxPrice=500&quantity=2&sort=price_desc&ada=false&seatSelection=false&onlyCoupon=true&onlyVoucher=false"
    return url

def SendBot(embed):
    payload = json.dumps({'content': embed, 'username': 'Dusty Baker', 'avatar_url': 'https://akamai-tickets.akamaized.net/images/primarysales/mtm/90x90_hou_logo.png'})
    headers2 = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
        }
    req = Request('https://discord.com/api/webhooks/1141893615493333133/iPYs56-1P6xmBwERAYmG4GmDfFZjOX_8SdvzVfX2VoOBad09Uv48lBw9SR4sj7_cMkej', data=payload.encode(), headers=headers2)
    urlopen(req)

async def CheckProxy(page):
    if await page.is_visible("//*[contains(text(),'An unexpected error has occurred.')]"): return True
    if await page.is_visible("//*[contains(text(),'Access Denied')]"): return True
    return False

async def FoundTickets(page):
    if await page.is_visible("//button[contains(text(),'Add To Cart')]"): return True
    return False

async def settitle(title):
    loop = asyncio.get_event_loop()
    command = f'\033]0;{title}\007'
    await loop.run_in_executor(None, os.system, f"echo '{command}'")

async def Monitor(browser):
    pages = []
    Working = True
    context = await browser.new_context()
    await stealth_async(context)
    try:
        await settitle('Loading games 0/4')
        page = await context.new_page()
        await page.goto(await GetGameUrl("9278235"), wait_until="domcontentloaded", timeout=15000)
        await settitle('Loading games 1/4')
        page1 = await context.new_page()
        await page1.goto(await GetGameUrl("9278236"), wait_until="domcontentloaded", timeout=15000)
        await settitle('Loading games 2/4')
        page2 = await context.new_page()
        await page2.goto(await GetGameUrl("9278237"), wait_until="domcontentloaded", timeout=15000)
        await settitle('Loading games 3/4')
        page3 = await context.new_page()
        await page3.goto(await GetGameUrl("9278238"), wait_until="domcontentloaded", timeout=15000)
        await settitle('Loading games 4/4')
        pages.append(page)
        pages.append(page1)
        pages.append(page2)
        pages.append(page3)
    except:
        Working = False
        await context.close()
        return
    await settitle('All games loaded')
    while Working:
        for i in pages:
            if not Working: return
            try:
                await settitle(f'Reloading - {await i.title()}')
                await i.reload(wait_until="load", timeout=15000)
            except:
                await i.evaluate("window.dispatchEvent(new Event('load'));")
            #await page.wait_for_selector("text=Set Your Search Options", timeout=60000) 
            selector = "text=Set Your Search Options"
            await page.wait_for_selector(selector)
            while not await page.is_visible(selector): time.sleep(0.5)
            await settitle(f'Loaded and Checking - {await i.title()}')
            #await i.screenshot(path= await i.title() + ".png")
            #print(f"SS {await i.title()}")
            #print(f"Checking {await i.title()}") 
            if await CheckProxy(i):
                Working=False
                break
            
            if await FoundTickets(i):
                #input('Good!')
                SendBot(f"{await i.title()} - {i.url}")
                print(f"{await i.title()} - {i.url}")
                await settitle(f'Tickets found! - {await i.title()}')
            await settitle(f'No tickets found... - {await i.title()}')
    try:
        await context.close()
    except:
        print("Browser already closed...")

async def Main():
    async with async_playwright() as p:
        while True:
            for proxy_config in proxies:
                print("Starting new proxy: " + str(proxy_config))
                browser = await p.firefox.launch(headless=True, proxy=proxy_config)
                await Monitor(browser)
                time.sleep(1)

asyncio.run(Main())