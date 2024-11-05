import bs4
import time
import pathlib
import random
import requests


from datetime import datetime
from datetime import datetime
from transliterate import translit
from cianparser.constants import FILE_NAME_FLAT_FORMAT, USER_AGENTS
from cianparser.helpers import union_dicts, define_author, define_location_data, define_specification_data, define_deal_url_id, define_price_data
from cianparser.flat.page import FlatPageParser
from cianparser.base_list import BaseListPageParser


def get_random_user_agent():
    return random.choice(USER_AGENTS)


class FlatListPageParser(BaseListPageParser):
    def make_request_with_user_agent_rotation(self, url, max_attempts=5):
        attempts = 0
        while attempts < max_attempts:
            try:
                headers = {
                    'User-Agent': get_random_user_agent(),
                    'Referer': 'https://google.com',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
                    'Connection': 'keep-alive'
                }

                response = self.session.get(url, headers=headers)

                # Проверка на статус-код 429
                if response.status_code == 429:
                    wait_time = (2 ** attempts) + random.uniform(3, 6)  # Экспоненциальная задержка с рандомизацией
                    print(f"429 Too Many Requests on attempt {attempts + 1}, waiting {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                    attempts += 1
                else:
                    response.raise_for_status()  # Обработка ошибок 4XX/5XX
                    return response
            except requests.exceptions.RequestException as e:
                retry_delay = (2 ** attempts) + random.uniform(2, 5)
                print(f"Request error: {e}, retrying in {retry_delay:.2f} seconds...")
                time.sleep(retry_delay)
                attempts += 1
        raise Exception(f"Failed to retrieve the page after {max_attempts} attempts")

    def parse_list_offers_page(self, html, page_number: int, count_of_pages: int, attempt_number: int):
        headers = {
            'User-Agent': get_random_user_agent(),
            'Referer': 'https://google.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
            'Connection': 'keep-alive'
        }

        # Преобразуем HTML в объект BeautifulSoup
        list_soup = bs4.BeautifulSoup(html, 'html.parser')

        # Проверка на Captcha
        if list_soup.text.find("Captcha") > 0:
            print(f"\r{page_number} page: CAPTCHA detected... failed to parse page...")
            return False, attempt_number + 1, True

        header = list_soup.select("div[data-name='HeaderDefault']")
        if len(header) == 0:
            return False, attempt_number + 1, False

        offers = list_soup.select("article[data-name='CardComponent']")
        print("")
        print(f"\r {page_number} page: {len(offers)} offers", end="\r", flush=True)

        if page_number == self.start_page and attempt_number == 0:
            print("Collecting information from pages with list of offers")

        for ind, offer in enumerate(offers):
            self.parse_offer(offer=offer)
            self.print_parse_progress(page_number=page_number, count_of_pages=count_of_pages, offers=offers, ind=ind)

            # Пауза между запросами для каждого объявления
            time.sleep(random.uniform(3, 6))  # Случайная задержка между объявлениями

        # Дополнительная задержка между страницами
        time.sleep(random.uniform(5, 10))
        return True, 0, False

    def build_file_path(self):
        now_time = datetime.now().strftime("%d_%b_%Y_%H_%M_%S_%f")
        file_name = FILE_NAME_FLAT_FORMAT.format(
            self.accommodation_type, self.deal_type, self.start_page, self.end_page,
            translit(self.location_name.lower(), reversed=True), now_time
        )
        return pathlib.Path(pathlib.Path.cwd(), file_name.replace("'", ""))

    def parse_offer(self, offer):
        # print('Parse offer func...')
        # print('Offer:', offer)
        common_data = dict()
        common_data["url"] = offer.select("div[data-name='LinkArea']")[0].select("a")[0].get('href')
        common_data["location"] = self.location_name
        common_data["deal_type"] = self.deal_type
        common_data["accommodation_type"] = self.accommodation_type

        author_data = define_author(block=offer)
        location_data = define_location_data(block=offer, is_sale=self.is_sale())
        price_data = define_price_data(block=offer)
        specification_data = define_specification_data(block=offer)

        if define_deal_url_id(common_data["url"]) in self.result_set:
            return

        page_data = dict()
        if self.with_extra_data:
            flat_parser = FlatPageParser(session=self.session, url=common_data["url"], deal_type=common_data["deal_type"])
            page_data = flat_parser.parse_page()
            time.sleep(4)

        self.count_parsed_offers += 1
        self.define_average_price(price_data=price_data)
        self.result_set.add(define_deal_url_id(common_data["url"]))
        self.result.append(union_dicts(author_data, common_data, specification_data, price_data, page_data, location_data))

        if self.with_saving_csv:
            self.save_results()
