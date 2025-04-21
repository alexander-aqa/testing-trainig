import os
from playwright.sync_api import Page
from dotenv import load_dotenv

load_dotenv()

# авторизация

def login(page: Page):
    login = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")
    assert login, "LOGIN is not set in .env"
    assert password, "PASSWORD is not set in .env"

    page.goto("https://5verst.ru/butovo/")
    page.locator("a[href='https://my.5verst.ru']").first.click()
    page.wait_for_selector("#login", timeout=10000)
    page.locator("#login").fill(login)
    page.locator("#password").fill(password)
    page.locator("#root > div > main > div > main > section > button").click()
    page.wait_for_url("https://my.5verst.ru/#/")

 # Открытие страницы авторизации

def open_login_page(page: Page):
    page.goto("https://my.5verst.ru/#/login")
    page.wait_for_selector("#login", timeout=10000)