# import time
# import re
# import bs4
# import requests
# import datetime
# import random
#
# from random_user_agent.user_agent import UserAgent
# from random_user_agent.params import SoftwareName, OperatingSystem
# from transliterate import translit
#
#
# class FlatPageParser:
#     def __init__(self, session, url, deal_type):
#         self.session = session
#         self.url = url
#         self.deal_type = deal_type
#         software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value]
#         operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
#         self.user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems,
#                                             limit=100)
#
#     def __get_random_user_agent(self):
#         return self.user_agent_rotator.get_random_user_agent()
#
#     def __load_page(self):
#         headers = {
#             'User-Agent': self.__get_random_user_agent(),
#             'Referer': 'https://google.com',
#             'Accept-Language': 'en-US,en;q=0.9',
#             'Connection': 'keep-alive',
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
#             'Accept-Encoding': 'gzip, deflate, br'
#         }
#
#         retries = 5
#         delay = 2
#
#         for attempt in range(retries):
#             try:
#                 headers['User-Agent'] = self.__get_random_user_agent()
#                 print(headers['User-Agent'])
#
#                 res = self.session.get(self.url, headers=headers)
#
#                 if res.status_code == 429:
#                     wait_time = delay * (2 ** attempt) + random.uniform(1, 5)
#                     print('Current User-Agent: ', headers['User-Agent'])
#                     print(f"429 Too Many Requests. Waiting {wait_time} seconds before retrying...")
#                     time.sleep(wait_time)
#                 else:
#                     res.raise_for_status()
#                     self.offer_page_html = res.text
#                     self.offer_page_soup = bs4.BeautifulSoup(self.offer_page_html, 'html.parser')
#                     return
#             except requests.exceptions.RequestException as e:
#                 print(f"Request failed (Attempt {attempt + 1}/{retries}): {e}")
#                 time.sleep(delay + random.uniform(1, 3))
#
#         raise Exception("Failed to load page after multiple attempts")
#
#     def __parse_metro_times(self):
#         """Парсит станции метро, время до них и способ передвижения."""
#         station_list = self.offer_page_soup.find('ul', class_='a10a3f92e9--undergrounds--sGE99')
#         stations = station_list.find_all('li', class_='a10a3f92e9--underground--pjGNr')
#
#         result = []
#
#         # with open("parsed_page2.html", "w", encoding="utf-8") as file:
#         #     file.write(self.offer_page_soup.prettify())
#         for station in stations:
#             station_name = station.find('a', class_='a10a3f92e9--underground_link--VnUVj').text.strip()
#
#             time_to_station = station.find('span', class_='a10a3f92e9--underground_time--YvrcI').text.strip()
#
#             icon_svg = station.find('svg', class_='a10a3f92e9--container--izJBY a10a3f92e9--display_inline-block--xc1D8 a10a3f92e9--color_icon-secondary-default--Pnd5e')
#             # print(icon_svg)
#             if icon_svg:
#                 path_data = icon_svg.find('path')['d']
#
#                 if "m14 7" in path_data:  # путь иконки машины
#                     travel_mode = 'на машине'
#                 elif "M8.67 4.471" in path_data:  # путь иконки пешехода
#                     travel_mode = 'пешком'
#                 else:
#                     travel_mode = 'неизвестный способ'
#             else:
#                 travel_mode = 'неизвестный способ'
#
#             result.append({
#                 'Станция': station_name,
#                 'Время': time_to_station,
#                 'Способ передвижения': travel_mode
#             })
#
#         return result
#
#     def __parse_flat_offer_page_json(self):
#         page_data = {
#             "year_of_construction": -1,
#             "object_type": -1,
#             "house_material_type": -1,
#             "heating_type": -1,
#             "finish_type": -1,
#             "living_meters": -1,
#             "kitchen_meters": -1,
#             "floor": -1,
#             "floors_count": -1,
#             "phone": "",
#             "total_views": -1,
#             "today_views": -1,
#             "metro_times": []
#         }
#
#         spans = self.offer_page_soup.select("span")
#         for index, span in enumerate(spans):
#             if "Тип жилья" == span.text:
#                 page_data["object_type"] = spans[index + 1].text
#
#             if "Тип дома" == span.text:
#                 page_data["house_material_type"] = spans[index + 1].text
#
#             if "Отопление" == span.text:
#                 page_data["heating_type"] = spans[index + 1].text
#
#             if "Отделка" == span.text:
#                 page_data["finish_type"] = spans[index + 1].text
#
#             if "Площадь кухни" == span.text:
#                 page_data["kitchen_meters"] = spans[index + 1].text
#
#             if "Жилая площадь" == span.text:
#                 page_data["living_meters"] = spans[index + 1].text
#
#             if "Год постройки" in span.text:
#                 page_data["year_of_construction"] = spans[index + 1].text
#
#             if "Год сдачи" in span.text:
#                 page_data["year_of_construction"] = spans[index + 1].text
#
#             if "Этаж" == span.text:
#                 ints = re.findall(r'\d+', spans[index + 1].text)
#                 if len(ints) == 2:
#                     page_data["floor"] = int(ints[0])
#                     page_data["floors_count"] = int(ints[1])
#
#         if "+7" in self.offer_page_html:
#             page_data["phone"] = \
#             self.offer_page_html[self.offer_page_html.find("+7"): self.offer_page_html.find("+7") + 16].split('"')[0]. \
#                 replace(" ", ""). \
#                 replace("-", "")
#
#         current_date = datetime.datetime.now()
#         formatted_time = current_date.strftime('%Y-%m-%d %H:%M:%S')
#         page_data["current_date"] = formatted_time
#
#         with open("views_logs.html", "w", encoding="utf-8") as file:
#             file.write(self.offer_page_soup.prettify())
#
#         views_button = self.offer_page_soup.find('button', {'data-name': 'OfferStats'})
#         if views_button:
#             # Извлечение текста из элемента кнопки
#             views_text = views_button.get_text(strip=True)
#
#             # Регулярное выражение для поиска количества просмотров
#             match = re.search(r'(\d[\d\s,]*)\s*(просмотров?|просмотр)', views_text)
#             if match:
#                 # Общее количество просмотров
#                 page_data["total_views"] = int(match.group(1).strip().replace(",", "").replace(" ", ""))
#
#                 # Поиск просмотров за сегодня
#                 today_match = re.search(r'(\d[\d\s,]*)\s*за сегодня', views_text)
#                 if today_match:
#                     page_data["today_views"] = int(today_match.group(1).strip().replace(",", ""))
#             else:
#                 print("Не удалось найти количество просмотров.")
#         else:
#             print("Не удалось найти кнопку с просмотрами.")
#
#         page_data['metro_times'] = self.__parse_metro_times()
#         page_info = self.__parse_flat_home_info()
#         # print(page_info)
#         page_data.update(page_info)
#
#         return page_data
#
#     def __parse_flat_home_info(self):
#         flat_info_label = self.offer_page_soup.find("div", class_="a10a3f92e9--header--RGZa5")
#         flat_info_label = flat_info_label.find_next("div")
#
#         info_dict = {}
#
#         info_blocks = flat_info_label.find_all("div", recursive=False)
#         for block in info_blocks:
#             label = block.find("p")
#
#             if label:
#                 label_text = label.get_text().strip()
#                 value = label.find_next("p")
#                 if value:
#                     value_text = value.get_text().strip()
#                     label_text = translit(label_text, 'ru', reversed=True)
#                     info_dict[label_text] = value_text
#
#         home_info_label = flat_info_label.find_next("div", class_="a10a3f92e9--header--RGZa5").find_next("div")
#         home_info_block = home_info_label.find_all("div")
#         for block in home_info_block:
#             label = block.find("p")
#
#             if label:
#                 label_text = label.get_text().strip()
#                 label_text = translit(label_text, 'ru', reversed=True)
#                 value = label.find_next("p")
#                 if value:
#                     value_text = value.get_text().strip()
#                     info_dict[label_text] = value_text
#
#         return info_dict
#
#
#     def parse_page(self):
#         self.__load_page()
#         return self.__parse_flat_offer_page_json()

import time
import re
import bs4
import requests
import datetime
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from transliterate import translit


class FlatPageParser:
    def __init__(self, session, url, deal_type):
        self.session = session
        self.url = url
        self.deal_type = deal_type
        self.offer_page_html = None  # Store page HTML after loading
        software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
        self.user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

    def __get_random_user_agent(self):
        return self.user_agent_rotator.get_random_user_agent()

    def __load_page(self):
        # self.__load_page_with_selenium()
        headers = {
            'User-Agent': self.__get_random_user_agent(),
            'Referer': 'https://google.com',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br'
        }

        retries = 1  # Number of retries before switching to Selenium
        delay = 2

        # Attempt to load the page using requests
        for attempt in range(retries):
            try:
                headers['User-Agent'] = self.__get_random_user_agent()
                print(f"Attempting with User-Agent: {headers['User-Agent']}")

                res = self.session.get(self.url, headers=headers)

                if res.status_code == 429:
                    wait_time = delay * (2 ** attempt) + random.uniform(1, 5)
                    print(f"429 Too Many Requests. Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                else:
                    res.raise_for_status()
                    self.offer_page_html = res.text
                    self.offer_page_soup = bs4.BeautifulSoup(self.offer_page_html, 'html.parser')
                    return  # Exit if successful
            except requests.exceptions.RequestException as e:
                print(f"Request failed (Attempt {attempt + 1}/{retries}): {e}")
                time.sleep(delay + random.uniform(1, 3))

        # If all attempts fail, fall back to Selenium
        print("switch to selenium...\n")
        self.__load_page_with_selenium()

    def __load_page_with_selenium(self):
        print("Switching to Selenium to load the page...")
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.page_load_strategy = 'eager'
        options.add_argument(f"user-agent={self.__get_random_user_agent()}")
        driver = webdriver.Chrome(options=options)

        try:
            driver.get(self.url)

            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            self.offer_page_html = driver.page_source
            self.offer_page_soup = bs4.BeautifulSoup(self.offer_page_html, 'html.parser')
            print("Page loaded successfully with Selenium.")
        except Exception as e:
            print(f"Failed to load page with Selenium: {e}")
        finally:
            driver.quit()

    def __parse_metro_times(self):
        """Парсит станции метро, время до них и способ передвижения."""
        station_list = self.offer_page_soup.find('ul', class_='a10a3f92e9--undergrounds--sGE99')
        print('тип странички ', type(self.offer_page_soup), 'тип листа со станциями метро ', type(station_list))
        stations = station_list.find_all('li', class_='a10a3f92e9--underground--pjGNr')
        print('станции тип ', type(stations))
        result = []
        for station in stations:
            station_name = station.find('a', class_='a10a3f92e9--underground_link--VnUVj').text.strip()
            time_to_station = station.find('span', class_='a10a3f92e9--underground_time--YvrcI').text.strip()

            icon_svg = station.find('svg', class_='a10a3f92e9--container--izJBY a10a3f92e9--display_inline-block--xc1D8 a10a3f92e9--color_icon-secondary-default--Pnd5e')
            if icon_svg:
                path_data = icon_svg.find('path')['d']
                if "m14 7" in path_data:
                    travel_mode = 'на машине'
                elif "M8.67 4.471" in path_data:
                    travel_mode = 'пешком'
                else:
                    travel_mode = 'неизвестный способ'
            else:
                travel_mode = 'неизвестный способ'

            result.append({
                'Станция': station_name,
                'Время': time_to_station,
                'Способ передвижения': travel_mode
            })
        return result

    def __parse_flat_offer_page_json(self):
        page_data = {
            "year_of_construction": -1,
            "object_type": -1,
            "house_material_type": -1,
            "heating_type": -1,
            "finish_type": -1,
            "living_meters": -1,
            "kitchen_meters": -1,
            "floor": -1,
            "floors_count": -1,
            "phone": "",
            "total_views": -1,
            "today_views": -1,
            "metro_times": []
        }

        spans = self.offer_page_soup.select("span")
        for index, span in enumerate(spans):
            if "Тип жилья" == span.text:
                page_data["object_type"] = spans[index + 1].text

            if "Тип дома" == span.text:
                page_data["house_material_type"] = spans[index + 1].text

            if "Отопление" == span.text:
                page_data["heating_type"] = spans[index + 1].text

            if "Отделка" == span.text:
                page_data["finish_type"] = spans[index + 1].text

            if "Площадь кухни" == span.text:
                page_data["kitchen_meters"] = spans[index + 1].text

            if "Жилая площадь" == span.text:
                page_data["living_meters"] = spans[index + 1].text

            if "Год постройки" in span.text:
                page_data["year_of_construction"] = spans[index + 1].text

            if "Год сдачи" in span.text:
                page_data["year_of_construction"] = spans[index + 1].text

            if "Этаж" == span.text:
                ints = re.findall(r'\d+', spans[index + 1].text)
                if len(ints) == 2:
                    page_data["floor"] = int(ints[0])
                    page_data["floors_count"] = int(ints[1])

        if "+7" in self.offer_page_html:
            page_data["phone"] = \
            self.offer_page_html[self.offer_page_html.find("+7"): self.offer_page_html.find("+7") + 16].split('"')[0]. \
                replace(" ", ""). \
                replace("-", "")

        current_date = datetime.datetime.now()
        formatted_time = current_date.strftime('%Y-%m-%d %H:%M:%S')
        page_data["current_date"] = formatted_time

        with open("views_logs.html", "w", encoding="utf-8") as file:
            file.write(self.offer_page_soup.prettify())

        views_button = self.offer_page_soup.find('button', {'data-name': 'OfferStats'})
        if views_button:
            # Извлечение текста из элемента кнопки
            views_text = views_button.get_text(strip=True)

            # Регулярное выражение для поиска количества просмотров
            match = re.search(r'(\d[\d\s,]*)\s*(просмотров?|просмотр)', views_text)
            if match:
                # Общее количество просмотров
                page_data["total_views"] = int(match.group(1).strip().replace(",", "").replace(" ", ""))

                # Поиск просмотров за сегодня
                today_match = re.search(r'(\d[\d\s,]*)\s*за сегодня', views_text)
                if today_match:
                    page_data["today_views"] = int(today_match.group(1).strip().replace(",", ""))
            else:
                print("Не удалось найти количество просмотров.")
        else:
            print("Не удалось найти кнопку с просмотрами.")

        page_data['metro_times'] = self.__parse_metro_times()
        page_info = self.__parse_flat_home_info()
        # print(page_info)
        page_data.update(page_info)

        return page_data

    def __parse_flat_home_info(self):
        flat_info_label = self.offer_page_soup.find("div", class_="a10a3f92e9--header--RGZa5")
        flat_info_label = flat_info_label.find_next("div")

        info_dict = {}
        print('flat_info тип ', type(flat_info_label))
        info_blocks = flat_info_label.find_all("div", recursive=False)
        print('info_blocks тип ', type(info_blocks))
        for block in info_blocks:
            label = block.find("p")

            if label:
                label_text = label.get_text().strip()
                value = label.find_next("p")
                if value:
                    value_text = value.get_text().strip()
                    label_text = translit(label_text, 'ru', reversed=True)
                    info_dict[label_text] = value_text

        home_info_label = flat_info_label.find_next("div", class_="a10a3f92e9--header--RGZa5").find_next("div")
        print('home_info тип ', type(home_info_label))
        home_info_block = home_info_label.find_all("div")
        print('home_info_blocks тип ', type(home_info_block))
        for block in home_info_block:
            label = block.find("p")

            if label:
                label_text = label.get_text().strip()
                label_text = translit(label_text, 'ru', reversed=True)
                value = label.find_next("p")
                if value:
                    value_text = value.get_text().strip()
                    info_dict[label_text] = value_text

        return info_dict

    def parse_page(self):
        self.__load_page()  # Will try `requests`, then fallback to Selenium if needed
        return self.__parse_flat_offer_page_json()
