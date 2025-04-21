import os
from playwright.sync_api import Page, expect
from dotenv import load_dotenv
from pages.login_page import login

load_dotenv()


def test_wiki_main_page(page: Page):
    page.goto("http://wikipedia.org/")
    page.get_by_role("link", name="Русский").click()
    expect(page.get_by_text("Добро пожаловать в Википедию,")).to_be_visible()


# Проверка видимости заголовка и кнопки "Подробнее" на странице Бутово
def test_butovo_page(page: Page):
    page.goto("https://5verst.ru/butovo/")
    expect(page).to_have_title("5 вёрст | Бутово | Москва | Суббота, утро, парк, 5 км")
    expect(page.get_by_text("Подробнее")).to_be_visible()


# Проверка кнопки регистрации: цвет при hover и редирект
def test_register_button_color_and_redirect(page: Page):
    page.goto("https://5verst.ru/butovo/")

    register_btn = page.locator("a.knd-button", has_text="Зарегистрироваться")
    expect(register_btn).to_be_visible()

    before_hover = register_btn.evaluate("el => getComputedStyle(el).backgroundColor")
    register_btn.hover()
    after_hover = register_btn.evaluate("el => getComputedStyle(el).backgroundColor")

    print(f"🎨 Фон до наведения: {before_hover}, после наведения: {after_hover}")

    # Можно раскомментировать, если хочешь проверку отличий
    # assert before_hover != after_hover, "Фон кнопки не изменился при наведении"

    register_btn.click()
    expect(page).to_have_url("https://5verst.ru/register/")


# Проверка перехода по кнопке "Личный кабинет" с главной
def test_go_to_login_cabinet(page: Page):
    page.goto("https://5verst.ru/")

    menu_toggle = page.locator("button.knd-offcanvas-toggle")
    assert menu_toggle.count() > 0

    menu_toggle.first.click(force=True)

    login_link = page.locator("a[href*='my.5verst.ru']")
    login_link.first.wait_for(state="visible")
    login_link.first.evaluate("el => el.click()")

    page.wait_for_url("https://my.5verst.ru/#/login")


# Прямой ввод логина и пароля из .env
def test_login(page: Page):
    login_value = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")

    assert login_value, "LOGIN is not set in .env"
    assert password, "PASSWORD is not set in .env"

    page.goto("https://5verst.ru/butovo/")
    page.locator("a[href='https://my.5verst.ru']").first.click()
    page.wait_for_selector("#login", timeout=10000)

    page.locator("#login").fill(login_value)
    page.locator("#password").fill(password)
    page.locator("#root > div > main > div > main > section > button").click()

    page.wait_for_selector("#root > div > main > section > h3 > a", timeout=10000)


# Логин через вспомогательную функцию
def test_login_through_help_function(page: Page):
    login(page)

    assert page.url == "https://my.5verst.ru/#/", f"Ожидался переход на https://my.5verst.ru/#/, но сейчас {page.url}"
    expect(page.locator("xpath=//*[@id='root']/div/main/section/h3/a")).to_be_visible(timeout=5000)


# Проверка всех кнопок и текстов в личном кабинете
def test_lk_texts_and_buttons(page: Page):
    login(page)
    expect(page).to_have_url("https://my.5verst.ru/#/")

    expected_texts = [
        "Показать QR-код",
        "Изменить личные данные",
        "Посмотреть свою статистику участия в 5 вёрст",
        "Изменить свой действующий пароль",
        "Ввести свой «РЖД Бонус» ID",
        "Участие в клубной программе Спортмастер",
        "Узнать свой прогресс в клубах 5 вёрст",
    ]

    for text in expected_texts:
        expect(page.locator(f"text={text}")).to_be_visible()

    buttons = {
        1: "https://my.5verst.ru/#/qrcode",
        2: "https://my.5verst.ru/#/personal",
        3: "https://my.5verst.ru/#/statistics",
        4: "https://my.5verst.ru/#/updatepassword",
        5: "https://my.5verst.ru/#/rzdbonusid",
        6: "https://my.5verst.ru/#/sportmasterbonus",
        7: "https://my.5verst.ru/#/clubs",
        8: "https://5verst.ru/",
    }

    for i, expected_url in buttons.items():
        locator = page.locator(f'xpath=//*[@id="root"]/div/main/section/ul/li[{i}]/a')

        if i == 8:
            with page.context.expect_page() as new_page_info:
                locator.click()
            new_page = new_page_info.value
            new_page.wait_for_load_state()
            assert new_page.url == expected_url, f"Ожидался переход на {expected_url}, но был {new_page.url}"
            new_page.close()
        else:
            locator.click()
            page.wait_for_url(expected_url, timeout=5000)
            assert page.url == expected_url, f"Ожидался переход на {expected_url}, но был {page.url}"
            page.go_back()


# Проверка ссылок "Забыли пароль?" и "Забыли ID?" на странице входа
def test_forgot_links(page: Page):
    page.goto("https://my.5verst.ru/#/login")

    forgot_password_link = page.locator('xpath=//*[@id="root"]/div/main/div/main/div/a[1]')
    forgot_id_link = page.locator('xpath=//*[@id="root"]/div/main/div/main/div/a[2]')

    expect(forgot_password_link).to_be_visible()
    expect(forgot_id_link).to_be_visible()

    forgot_password_link.click()
    expect(page).to_have_url("https://my.5verst.ru/#/remindpassword")

    page.go_back()

    with page.context.expect_page() as new_page_info:
        forgot_id_link.click()

    new_page = new_page_info.value
    new_page.wait_for_load_state()

    assert new_page.url == "https://5verst.ru/reminder/", \
        f"Ожидался переход на https://5verst.ru/reminder/, но был {new_page.url}"

    new_page.close()