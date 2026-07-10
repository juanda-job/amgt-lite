from playwright.sync_api import sync_playwright, Page
registroFacturas = ""

def new_context(p,headless=False):
    browser = p.chromium.launch(headless=headless)
    context = browser.new_context()
    page = context.new_page()
    return browser, context, page

def login(page: Page, link: str, username: str, password: str):
    try:
        page.goto(link, wait_until="domcontentloaded", timeout=10000)
        page.locator("#idUsuario").fill(username)
        page.locator("#password").fill(password)
        page.locator("#bIngresar").click()

        grupo = page.locator('[data-grupo="contabilidad"]')
        # 1. Clic en el grupo contabilidad para desplegar menú
        grupo.click()

        # 3. Clic en "Oper. Contabilidad"
        grupo.locator('a:has-text("Oper. Contabilidad")').click()

        # Devuelves el locator junto con la página
        return page
    except TimeoutError as e:
        print(f"Error de tiempo de espera: {e}")
        return None, None

def go_to_conecta(login_result, context, token: str):
    page = login_result

    with context.expect_page() as new_page_info:
        # 3. Clic en "Oper. Contabilidad"
        page.locator('a:has-text("Registro Movimiento")').click()
    page2 = new_page_info.value
    page2.wait_for_load_state()

    # Navegar al token en ambas páginas
    page.goto(token)
    page2.goto(token)

    return page2, page