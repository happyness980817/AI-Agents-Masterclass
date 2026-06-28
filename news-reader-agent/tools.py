import time
from crewai.tools import tool
from crewai_tools import SerperDevTool
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

search_tool = SerperDevTool()

@tool
def scrape_tool(url: str):
    """
    Use this when you need read the content of a web page.
    Returns the content of a web page.
    In case the website is not available, return 'No content found'.
    Input should be a URL string.
    """

    print(f"Scraping URL: {url}")

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.goto(url)

        time.sleep(5)

        html = page.content()

        browser.close()

        soup = BeautifulSoup(html, "html.parser")

        unwanted_tags = [
            "header",
            "footer",
            "nav",
            "aside",
            "script",
            "style",
            "noscript",
            "iframe",
            "form",
            "button",
            "input",
            "select",
            "textarea",
            "img",
            "svg",
            "canvas",
            "audio",
            "video",
            "embed",
            "object",
        ]

        for tag in soup.find_all(unwanted_tags):
            tag.decompose()

        content = soup.get_text(separator="\n")

        return content if content != "" else "No content found"
