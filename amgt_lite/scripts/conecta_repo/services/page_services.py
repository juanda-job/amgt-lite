from playwright.sync_api import sync_playwright, Page

def new_context(p,headless=False):
    browser = p.chromium.launch(headless=headless)
    context = browser.new_context()
    page = context.new_page()
    return browser, context, page

def login(page: Page, link: str, username: str, password: str):
    try:
        # Navegar a la URL principal
        page.goto(link, wait_until="domcontentloaded", timeout=10000)

        # Ingresar credenciales
        page.locator("#idUsuario").fill(username)
        page.locator("#password").fill(password)
        page.locator("#bIngresar").click()

        # Esperar menú lateral y navegar a Registro Facturas
        page.wait_for_selector('#ul_0 >> #li_23', timeout=8000)
        page.locator('#ul_0 >> #li_23').click()

        page.wait_for_selector('#ul_0 >> #li_23 >> #ul_23 >> a:has-text("Registro Facturas")', timeout=8000)
        return page

    except TimeoutError as e:
        print(f"Error de tiempo de espera: {e}")
        return None
    
def go_to_conecta(page:Page, context, token:str):
    # Esperar a que se abra una nueva página al hacer clic en el botón
            with context.expect_page() as new_page_info:
                # botón que abre otra pestaña/ventana
                page.locator('#ul_0 >> #li_23 >> #ul_23 >> a:has-text("Registro Facturas")').click()
            page2 = new_page_info.value
            # Ahora puedes usar la nueva página
            page.wait_for_load_state()
            page.goto(token)
            page2.goto(token)
            page.goto(token)
            return page, page2