from playwright.sync_api import sync_playwright, Page, expect

def login(page: Page, link: str, username: str, password: str):
    # Navegar a la URL
    page.goto(link)
    page.locator("#idUsuario").fill(username)
    page.locator("#password").fill(password)
    page.locator("#bIngresar").click()

