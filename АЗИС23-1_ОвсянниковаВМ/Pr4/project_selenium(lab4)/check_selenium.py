
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By


def main():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    print("Запускаем Microsoft Edge...")
    driver = webdriver.Edge(options=options)

    try:
        driver.get("https://www.example.com")
        print(f"Заголовок страницы: {driver.title}")

        element = driver.find_element(By.TAG_NAME, "h1")
        print(f"Текст h1: {element.text}")
    finally:
        driver.quit()
        print("Браузер закрыт.")


if __name__ == "__main__":
    main()