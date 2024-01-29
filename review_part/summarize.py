import google.generativeai as palm
import asyncio
from pyppeteer import launch
from . import config

palm.configure(api_key=config.API_KEY)
models = [
    m for m in palm.list_models() if "generateText" in m.supported_generation_methods
]
model = models[0].name


async def scrape_reviews(url):
    reviews = []

    browser = await launch(
        handleSIGINT=False,
        handleSIGTERM=False,
        handleSIGHUP=False,
        headless=True,
        args=["--window-size=800,3200"]
    )
    
    page = await browser.newPage()
    await page.setViewport({"width": 800, "height": 3200})
    await page.goto(url)
    try:
        # Implement scrolling or additional waiting strategies if needed
        button_selector = 'div.m6QErb.Hk4XGb.QoaCgb.KoSBEe.tLjsW button.M77dve'
        await page.waitForSelector(button_selector)  # Wait for the button to be visible
        button = await page.querySelector(button_selector)
        if button:
            await page.click(button_selector)

        await page.waitForSelector(".jftiEf", timeout=60000)
        elements = await page.querySelectorAll(".jftiEf")

        for element in elements:
            try:
                await page.waitForSelector(".w8nwRe")
                more_btn = await element.querySelector(".w8nwRe")
                await page.evaluate("button => button.click()", more_btn)
                await page.waitFor(5000)
            except Exception as e:
                print(f"Error while processing element: {e}")
            try:
                await page.waitForSelector(".MyEned")
                snippet = await element.querySelector(".MyEned")
                text = await page.evaluate("selected => selected.textContent", snippet)
                reviews.append(text)
            except Exception as e:
                print(f"Error while processing element: {e}")

    except Exception as e:
        print(f"Error while waiting for selector: {e}")

    finally:
        await browser.close()

    return reviews


def summarize(reviews, model):
    prompt = "I collected some reviews of a restaurant. \
    Can you summarize the reviews for me and also give a score out of 5 of the following critera: Food, Service and Atmosphere? \
    Can you list out what people like and dislike. The reviews are below:\n"

    for review in reviews:
      prompt += "\n" + review

    completion = palm.generate_text(
      model=model,
      prompt=prompt,
      temperature=0,
      # The maximum length of the response
      max_output_tokens=350,
    )

    return completion.result



# reviews = asyncio.run(scrape_reviews("https://www.google.com/maps/place/Taro's+Fish/@43.7701904,-79.3746926,17z/data=!4m8!3m7!1s0x89d4d2b678d9c8fd:0xcbe80b54585d5baf!8m2!3d43.7701904!4d-79.3746926!9m1!1b1!16s%2Fg%2F1hc2w4q6x?entry=ttu"))

# print(reviews)