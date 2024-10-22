import time
import re
import bs4
import requests
from random_user_agent.user_agent import UserAgent  # Библиотека для генерации агентов
from random_user_agent.params import SoftwareName, OperatingSystem
import random_user_agent

class FlatPageParser:
    def __init__(self, session, url):
        self.session = session
        self.url = url
        software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
        self.user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

    def __get_random_user_agent(self):
        return self.user_agent_rotator.get_random_user_agent()

    def __load_page__(self):
        # print(self.__get_random_user_agent())
        headers = {
            'User-Agent': self.__get_random_user_agent(),  # Теперь вызывается правильный метод
            'Referer': 'https://google.com',
        }

        retries = 3
        for _ in range(retries):
            res = self.session.get(self.url, headers=headers)
            if res.status_code == 429:
                time.sleep(10)
            else:
                break
        res.raise_for_status()
        self.offer_page_html = res.text
        self.offer_page_soup = bs4.BeautifulSoup(self.offer_page_html, 'html.parser')

    def __parse_flat_offer_page_json__(self):
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

        phone_match = re.search(r"\+7\s?\d{3}\s?\d{3}-?\d{2}-?\d{2}", self.offer_page_html)
        if phone_match:
            page_data["phone"] = phone_match.group().replace(" ", "").replace("-", "")

        station_list = self.offer_page_soup.find('ul', class_='a10a3f92e9--undergrounds--sGE99')
        stations = station_list.find_all('li', class_='a10a3f92e9--underground--pjGNr')

        result = []

        # with open("parsed_page2.html", "w", encoding="utf-8") as file:
        #     file.write(self.offer_page_soup.prettify())
        for station in stations:
            station_name = station.find('a', class_='a10a3f92e9--underground_link--VnUVj').text.strip()

            time_to_station = station.find('span', class_='a10a3f92e9--underground_time--YvrcI').text.strip()

            icon_svg = self.offer_page_soup.find('svg', class_='a10a3f92e9--container--xt4AF a10a3f92e9--display_inline-block--wFJ1O a10a3f92e9--color_gray_icons_100--iUfv9')
            # print(icon_svg)
            if icon_svg:
                path_data = icon_svg.find('path')['d']

                if "m14 7" in path_data:  # путь иконки машины
                    travel_mode = 'на машине'
                elif "M8.67 4.471" in path_data:  # путь иконки пешехода
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

        page_data['metro_times'] = result
        return page_data

    def parse_page(self):
        self.__load_page__()
        return self.__parse_flat_offer_page_json__()
