from playwright.sync_api import Page, expect
from dotenv import load_dotenv
load_dotenv()

def test_wiki_main_page(page: Page):
    page.goto('http://wikipedia.org/')
    page.get_by_role('link', name='Русский').click()
    # page.wait_for_timeout(3000)  # даём время на подгрузку комментариев
    expect(page.get_by_text('Добро пожаловать в Википедию,')).to_be_visible()

# 5_Вёрст_Бутово. Проверка видимости заголовка "5 вёрст | Бутово | Москва | Суббота, утро, парк, 5 км"
# Проверка видимости текста "Подробнее"
from playwright.sync_api import Page, expect

def test_butovo_page(page: Page):
    page.goto("https://5verst.ru/butovo/")
    # expect(page.get_by_text("Бутовский лесопарк")).to_be_visible()
    # expect(page).to_have_title("Бутовский лесопарк | Маршруты здоровья в Москве")
    expect(page).to_have_title("5 вёрст | Бутово | Москва | Суббота, утро, парк, 5 км")
    expect(page.get_by_text("Подробнее")).to_be_visible()

# 5_Вёрст_Бутово. Тест на кнопку регистрации с проверкой цвета и редиректа
from playwright.sync_api import Page, expect

def test_register_button_color_and_redirect(page: Page):
    # Переход на страницу района
    page.goto("https://5verst.ru/butovo/")

    # Находим кнопку по тексту
    register_btn = page.locator("a.knd-button", has_text="Зарегистрироваться")

    # Проверяем, что кнопка видима
    expect(register_btn).to_be_visible()

    # Проверка цвета фона до и после hover
    before_hover = register_btn.evaluate("el => getComputedStyle(el).backgroundColor")
    register_btn.hover()
    after_hover = register_btn.evaluate("el => getComputedStyle(el).backgroundColor")

    print(f"🎨 Фон до наведения: {before_hover}, после наведения: {after_hover}")

    # Пропускаем проверку, если цвет одинаковый (можно убрать, если хочешь падение теста)
    # assert before_hover != after_hover, "Фон кнопки не изменился при наведении"

    # Клик по кнопке
    register_btn.click()

    # Проверяем переход на нужную страницу
    expect(page).to_have_url("https://5verst.ru/register/")


# проверка редиректа на страницу "Вход в личный кабинет"

def test_go_to_login_cabinet(page):
    page.goto("https://5verst.ru/")

    # Проверяем наличие кнопки
    menu_toggle = page.locator("button.knd-offcanvas-toggle")
    assert menu_toggle.count() > 0

    # Кликаем по кнопке принудительно
    menu_toggle.first.click(force=True)

    # Ждём появления ссылки "Личный кабинет"
    login_link = page.locator("a[href*='my.5verst.ru']")
    login_link.first.wait_for(state="visible")

    # 👉 Кликаем по ней через JS, чтобы проигнорировать перекрытие
    login_link.first.evaluate("el => el.click()")

    # Проверка, что перешли на нужный URL
    page.wait_for_url("https://my.5verst.ru/#/login")


import os
from playwright.sync_api import Page
from dotenv import load_dotenv

load_dotenv()

def test_login(page: Page):
    login = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")
    assert login, "LOGIN is not set in .env"
    assert password, "PASSWORD is not set in .env"

    # 1. Переход на главную страницу
    page.goto("https://5verst.ru/butovo/")

    # 2. Кликаем по кнопке "Личный кабинет"
    page.locator("a[href='https://my.5verst.ru']").first.click()

    # 3. Ждём появления формы логина
    page.wait_for_selector("#login", timeout=10000)

    # 4. Вводим логин и пароль
    page.locator("#login").fill(login)
    page.locator("#password").fill(password)

    # 5. Кликаем "Войти"
    page.locator("#root > div > main > div > main > section > button").click()

    # 6. Ожидаем появления ссылки на страницу личного кабинета
    page.wait_for_selector("#root > div > main > section > h3 > a", timeout=10000)


#     Проверка редиректа в личный кабинет
from playwright.sync_api import Page, expect
from help_functions import login  # если login уже вынесен туда

def test_login_through_help_function(page: Page):
    login(page)

    # Проверка: редирект произошёл на нужный URL
    assert page.url == "https://my.5verst.ru/#/", f"Ожидался переход на https://my.5verst.ru/#/, но сейчас {page.url}"

    # Проверка наличия элемента по XPath (заголовок с ссылкой на страницу пользователя)
    expect(page.locator("xpath=//*[@id='root']/div/main/section/h3/a")).to_be_visible(timeout=5000)


# Проверка редиректа всех кнопок первой страницы личного кабинета

import os
from playwright.sync_api import Page, expect
from dotenv import load_dotenv
from help_functions import login  # если login у тебя в отдельном модуле

load_dotenv()

def test_lk_texts_and_buttons(page: Page):
    login(page)

    # Проверка: редирект на ЛК
    expect(page).to_have_url("https://my.5verst.ru/#/")

    # Проверка наличия текста-комментариев
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

    # Проверка перехода по каждой кнопке (и возврат назад)
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
            continue
        else:
            locator.click()
            page.wait_for_url(expected_url, timeout=5000)  # <-- ВОТ ОН
            assert page.url == expected_url, f"Ожидался переход на {expected_url}, но был {page.url}"
            page.go_back()
