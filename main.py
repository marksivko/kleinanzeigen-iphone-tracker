from playwright.async_api import async_playwright
import asyncio
import Bot
import json
import re

import llm

thresholds = {
    '11 ': 110,
    '11 pro ': 130,
    '11 pro max ': 150,
    ' 12  ': 140,
    ' 12 pro ': 210,
    ' 12 pro max ': 230,
    '13 ': 250,
    '13 pro ': 330,
    '13 pro max ': 460,
    '14 ': 320,
    '14 pro ': 390
}

banned_words = [
    "64", "hülle", "case", "suche", "gehäuse", "display", "iphone 4", "iphone 3", "iphone 5", "kaputt", "ankauf", "reparatur"
]

search_page = "https://www.kleinanzeigen.de/s-iphone/k0"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state="state.json")
        page = await context.new_page()
        await page.goto(search_page)
        recent_item_links = []
        while True:
            if not await is_active():
                continue
            items = await get_items(page)
            for item in items:
                if item["link"] not in recent_item_links:
                    recent_item_links.insert(0, item["link"])
                    # TODO: Check description and seller's rating, send item only if its good
                    if (await is_description_and_rating_good(item["link"], page)):
                        await Bot.send_item(item)
                        await context.storage_state(path="state.json")
                    else:
                        print("Bad deal...")
                    while len(recent_item_links) >= 30:
                        recent_item_links.pop()

            print("Refreshing the page...")
            await page.reload()
            await page.wait_for_timeout(5000)


async def is_active():
    with open("shared.json", "r") as f:
        data = json.load(f)
    return data.setdefault('running', False)

async def get_items(page):
    item_els = await page.locator("li.ad-listitem.fully-clickable-card").all()
    items = []
    for item_el in item_els:

        a_el = item_el.locator("a.ellipsis")
        # link can be either in an <a class=ellipsis> or in <span class = ellipsis>
        if await a_el.count() > 0:
            name = await a_el.inner_text()

            link = await a_el.get_attribute("href")

        else:
            span_el = item_el.locator("span.ellipsis")

            if await span_el.count() == 0:
                continue

            name = await span_el.inner_text() + " "
            link = await span_el.get_attribute("data-url")

        delivery = item_el.locator("span.simpletag.tag-with-icon")
        if await delivery.count() > 0:
            delivery = await delivery.inner_text()
        else:
            delivery = "Versand unbekannt"

        item = {
            "name": name,
            "link": "https://www.kleinanzeigen.de/" + link,
            "model": "",
            "price": re.sub("[^0-9]",
                            "",
                            await item_el.locator("p.aditem-main--middle--price-shipping--price").inner_text()),
            "location": await item_el.locator("div.aditem-main--top--left").inner_text(),
            "delivery": delivery
        }

        for threshold in thresholds:
            if threshold in item["name"].lower():
                item["model"] = threshold
        # Filters:
        if (item["model"] != "" and
            item["price"] != "" and (50 <= float(item["price"]) <= thresholds[item["model"]]) and
            not any(word in item["name"].lower() for word in banned_words)):
            items.append(item)

    return items

async def is_description_and_rating_good(link, page):
    rating = ""
    description = ""

    await page.goto(link)
    await page.wait_for_timeout(3000)
    rating_el = page.locator("a.userbadge-tag")
    if await rating_el.count() > 0:
        rating = await rating_el.first.inner_text()
    print("RATING: " + rating)
    description_el = page.locator("p.text-force-linebreak")
    if await description_el.count() > 0:
        description = await description_el.inner_text()

    print("DESCRIPTION: " + description)
    await page.goto(search_page)

    if "na ja" in rating.lower():
        print("Scammer...")
        return False

    llm_description_data = llm.get_description_rating(description)
    if llm_description_data["parts_broken"]:
        print("A part is broken...")
        return False

    if llm_description_data["battery_health"] < 80:
        print("Battery health is low...")
        return False

    return True


if __name__ == "__main__":
    asyncio.run(main())