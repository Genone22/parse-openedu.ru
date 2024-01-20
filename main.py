import json
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from loguru import logger


logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")

chrome_options = Options()
chrome_options.add_argument("--headless")

logger.debug("Старт")
driver = webdriver.Chrome(options=chrome_options)

course_url = "https://apps.openedu.ru/learning/course/course-v1:spbstu+ACCOUNT+fall_2023/block-v1:spbstu+ACCOUNT+fall_2023+type@sequential+block@3e875f2ec0544631bedefc76a0082041/block-v1:spbstu+ACCOUNT+fall_2023+type@vertical+block@1f41ce8b3f124587bb33fb43b82cdc7d"
logger.debug("Переход по ссылке")
driver.get(course_url)

wait = WebDriverWait(driver, 10)
logger.debug("Ожидание элемента")
social_form_item = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.social-form__item:nth-child(5) > a:nth-child(1) > span:nth-child(2)")))
social_form_item.click()

logger.debug("Ожидание поля ввода")
username_field = wait.until(EC.visibility_of_element_located((By.ID, "user")))
username_field.send_keys("gusejnov.dn")
driver.find_element(By.ID, "password").send_keys("takXo4co")

login_button = wait.until(EC.element_to_be_clickable((By.ID, "doLogin")))
logger.debug("Логин")
login_button.click()

logger.debug("Повторный переход по url")
driver.get(course_url)

logger.debug("Прокрутка до конца страницы")
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def generate_file_name(base_name, extension):
    current_time = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
    return f"{base_name}_{current_time}.{extension}"


try:
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "unit-iframe")))

    problems = driver.find_elements(By.CLASS_NAME, 'problems-wrapper')
    extracted_data = {}

    for problem in problems:
        question = problem.find_element(By.TAG_NAME, 'h3').text.strip()
        options = [opt.text.strip() for opt in problem.find_elements(By.CLASS_NAME, 'response-label')]
        correct_answer = [opt.text.strip() for opt in problem.find_elements(By.CLASS_NAME, 'choicegroup_correct')]
        extracted_data[question] = [options, correct_answer]

    file_name = generate_file_name("extracted_data", "json")
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=4)

    logger.success(f"Cохранил в {file_name}")

except Exception as e:
    logger.error(f"Ошибка: {e}")

finally:
    driver.quit()
