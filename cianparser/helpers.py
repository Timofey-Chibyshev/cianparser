import re
import itertools
from cianparser.constants import STREET_TYPES, NOT_STREET_ADDRESS_ELEMENTS, FLOATS_NUMBERS_REG_EXPRESSION
import random
import requests
from bs4 import BeautifulSoup


def union_dicts(*dicts):
    return dict(itertools.chain.from_iterable(dct.items() for dct in dicts))


def define_rooms_count(description):
    if "1-комн" in description or "Студия" in description:
        rooms_count = 1
    elif "2-комн" in description:
        rooms_count = 2
    elif "3-комн" in description:
        rooms_count = 3
    elif "4-комн" in description:
        rooms_count = 4
    elif "5-комн" in description:
        rooms_count = 5
    else:
        rooms_count = -1

    return rooms_count


def define_deal_url_id(url: str):
    url_path_elements = url.split("/")
    if len(url_path_elements[-1]) > 3:
        return url_path_elements[-1]
    if len(url_path_elements[-2]) > 3:
        return url_path_elements[-2]

    return "-1"


def define_author(block):
    spans = block.select("div")[0].select("span")

    author_data = {
        "author": "",
        "author_type": "",
    }

    for index, span in enumerate(spans):
        if "Агентство недвижимости" in span:
            author_data["author"] = spans[index + 1].text.replace(",", ".").strip()
            author_data["author_type"] = "real_estate_agent"
            return author_data

    for index, span in enumerate(spans):
        if "Собственник" in span:
            author_data["author"] = spans[index + 1].text
            author_data["author_type"] = "homeowner"
            return author_data

    for index, span in enumerate(spans):
        if "Риелтор" in span:
            author_data["author"] = spans[index + 1].text
            author_data["author_type"] = "realtor"
            return author_data

    for index, span in enumerate(spans):
        if "Ук・оф.Представитель" in span:
            author_data["author"] = spans[index + 1].text
            author_data["author_type"] = "official_representative"
            return author_data

    for index, span in enumerate(spans):
        if "Представитель застройщика" in span:
            author_data["author"] = spans[index + 1].text
            author_data["author_type"] = "representative_developer"
            return author_data

    for index, span in enumerate(spans):
        if "Застройщик" in span:
            author_data["author"] = spans[index + 1].text
            author_data["author_type"] = "developer"
            return author_data

    for index, span in enumerate(spans):
        if "ID" in span.text:
            author_data["author"] = span.text
            author_data["author_type"] = "unknown"
            return author_data

    return author_data


def parse_location_data(block):
    general_info_sections = block.select_one("div[data-name='LinkArea']").select(
        "div[data-name='GeneralInfoSectionRowComponent']")

    location_data = dict()
    location_data["district"] = ""
    location_data["street"] = ""
    location_data["house_number"] = ""
    location_data["metros"] = []  # Список станций метро

    for section in general_info_sections:
        geo_labels = section.select("a[data-name='GeoLabel']")
        metro_info = dict()  # Для хранения информации по каждой станции метро

        for index, label in enumerate(geo_labels):
            if "м. " in label.text:
                metro_info["underground"] = label.text.strip()

            if "р-н" in label.text or "поселение" in label.text:
                location_data["district"] = label.text

            if any(street_type in label.text.lower() for street_type in STREET_TYPES):
                location_data["street"] = label.text

                if len(geo_labels) > index + 1 and any(chr.isdigit() for chr in geo_labels[index + 1].text):
                    location_data["house_number"] = geo_labels[index + 1].text

        # Парсим время до каждой станции метро на основе иконок
        svg_icons = section.select("svg")
        for svg in svg_icons:
            # Если иконка машинки
            if "d='m14 7-.84-4.196A1 1 0 0 0 12.18 2H3.82a1 1 0 0 0-.98.804L2 7 1 8v4a1 1 0 0 0 1 1v1a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1v-1h6v1a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1V8l-1-1Z'" in \
                    svg['d']:
                # Извлекаем текстовое значение времени до метро на машине
                time_to_metro_by_car = section.text.strip().split()[0]
                metro_info["time_to_metro_by_car"] = time_to_metro_by_car

            # Если иконка пешехода
            elif "d='M8.67 4.471c.966 0 1.75-.778 1.75-1.738S9.636.993 8.67.993c-.967 0-1.75.78-1.75 1.74A1.74 1.74 0 0 0 8.142 4.39L3.743 5.68 2.605 8.65l1.868.715.783-2.045 1.12-.328L3.449 15h2.13l.094-.259-.017-.006 2.557-6.937.258-.707L9.662 8H13V6h-2.662L8.275 4.427c.127.03.26.044.395.044Z'" in \
                    svg['d']:
                # Извлекаем текстовое значение времени до метро пешком
                time_to_metro_on_foot = section.text.strip().split()[0]
                metro_info["time_to_metro_on_foot"] = time_to_metro_on_foot

        # Если найдена информация о станции метро
        if metro_info.get("underground"):
            # Добавляем время пешком или на машине только если оно указано
            metro_info["time_to_metro_by_car"] = metro_info.get("time_to_metro_by_car", None)
            metro_info["time_to_metro_on_foot"] = metro_info.get("time_to_metro_on_foot", None)
            # Добавляем информацию о станции в список
            location_data["metros"].append(metro_info)

    print("LOCATION DATA:", location_data)
    return location_data


def define_location_data(block, is_sale):
    elements = block.select_one("div[data-name='LinkArea']").select("div[data-name='GeneralInfoSectionRowComponent']")

    location_data = dict()
    location_data["district"] = ""
    location_data["street"] = ""
    location_data["house_number"] = ""
    location_data["underground"] = ""

    if is_sale:
        location_data["residential_complex"] = ""

    for index, element in enumerate(elements):
        if ("ЖК" in element.text) and ("«" in element.text) and ("»" in element.text):
            location_data["residential_complex"] = element.text.split("«")[1].split("»")[0]

        if "р-н" in element.text and len(element.text) < 250:
            address_elements = element.text.split(",")
            if len(address_elements) < 2:
                continue

            if "ЖК" in address_elements[0] and "«" in address_elements[0] and "»" in address_elements[0]:
                location_data["residential_complex"] = address_elements[0].split("«")[1].split("»")[0]

            if ", м. " in element.text:
                location_data["underground"] = element.text.split(", м. ")[1]
                if "," in location_data["underground"]:
                    location_data["underground"] = location_data["underground"].split(",")[0]

            if (any(chr.isdigit() for chr in address_elements[-1]) and "жк" not in address_elements[-1].lower() and
                not any(street_type in address_elements[-1].lower() for street_type in STREET_TYPES)) and len(
                address_elements[-1]) < 10:
                location_data["house_number"] = address_elements[-1].strip()

            for ind, elem in enumerate(address_elements):
                if "р-н" in elem:
                    district = elem.replace("р-н", "").strip()

                    location_data["district"] = district

                    if "ЖК" in address_elements[-1]:
                        location_data["residential_complex"] = address_elements[-1].strip()

                    if "ЖК" in address_elements[-2]:
                        location_data["residential_complex"] = address_elements[-2].strip()

                    for street_type in STREET_TYPES:
                        if street_type in address_elements[-1]:
                            location_data["street"] = address_elements[-1].strip()
                            if street_type == "улица":
                                location_data["street"] = location_data["street"].replace("улица", "")
                            return location_data

                        if street_type in address_elements[-2]:
                            location_data["street"] = address_elements[-2].strip()
                            if street_type == "улица":
                                location_data["street"] = location_data["street"].replace("улица", "")

                            return location_data

                    for k, after_district_address_element in enumerate(address_elements[ind + 1:]):
                        if len(list(set(after_district_address_element.split(" ")).intersection(
                                NOT_STREET_ADDRESS_ELEMENTS))) != 0:
                            continue

                        if len(after_district_address_element.strip().replace(" ", "")) < 4:
                            continue

                        location_data["street"] = after_district_address_element.strip()

                        return location_data

            return location_data

    if location_data["district"] == "":
        for index, element in enumerate(elements):
            if ", м. " in element.text and len(element.text) < 250:
                location_data["underground"] = element.text.split(", м. ")[1]
                if "," in location_data["underground"]:
                    location_data["underground"] = location_data["underground"].split(",")[0]

                address_elements = element.text.split(",")

                if len(address_elements) < 2:
                    continue

                if "ЖК" in address_elements[-1]:
                    location_data["residential_complex"] = address_elements[-1].strip()

                if "ЖК" in address_elements[-2]:
                    location_data["residential_complex"] = address_elements[-2].strip()

                if (any(chr.isdigit() for chr in address_elements[-1]) and "жк" not in address_elements[
                    -1].lower() and
                    not any(
                        street_type in address_elements[-1].lower() for street_type in STREET_TYPES)) and len(
                    address_elements[-1]) < 10:
                    location_data["house_number"] = address_elements[-1].strip()

                for street_type in STREET_TYPES:
                    if street_type in address_elements[-1]:
                        location_data["street"] = address_elements[-1].strip()
                        if street_type == "улица":
                            location_data["street"] = location_data["street"].replace("улица", "")
                        return location_data

                    if street_type in address_elements[-2]:
                        location_data["street"] = address_elements[-2].strip()
                        if street_type == "улица":
                            location_data["street"] = location_data["street"].replace("улица", "")
                        return location_data

            for street_type in STREET_TYPES:
                if (", " + street_type + " " in element.text) or (" " + street_type + ", " in element.text):
                    address_elements = element.text.split(",")

                    if len(address_elements) < 3:
                        continue

                    if (any(chr.isdigit() for chr in address_elements[-1]) and "жк" not in address_elements[
                        -1].lower() and
                        not any(
                            street_type in address_elements[-1].lower() for street_type in STREET_TYPES)) and len(
                        address_elements[-1]) < 10:
                        location_data["house_number"] = address_elements[-1].strip()

                    if street_type in address_elements[-1]:
                        location_data["street"] = address_elements[-1].strip()
                        if street_type == "улица":
                            location_data["street"] = location_data["street"].replace("улица", "")

                        location_data["district"] = address_elements[-2].strip()

                        return location_data

                    if street_type in address_elements[-2]:
                        location_data["street"] = address_elements[-2].strip()
                        if street_type == "улица":
                            location_data["street"] = location_data["street"].replace("улица", "")

                        location_data["district"] = address_elements[-3].strip()

                        return location_data
    print("location_data:", location_data)
    return location_data


def define_price_data(block):
    elements = block.select("div[data-name='LinkArea']")[0]. \
        select("span[data-mark='MainPrice']")

    price_data = {
        "price_per_month": -1,
        "commissions": 0,
    }

    for element in elements:
        if "₽/мес" in element.text:
            price_description = element.text
            price_data["price_per_month"] = int(
                "".join(price_description[:price_description.find("₽/мес") - 1].split()))

            if "%" in price_description:
                price_data["commissions"] = int(
                    price_description[price_description.find("%") - 2:price_description.find("%")].replace(" ", ""))

            return price_data

        if "₽" in element.text and "млн" not in element.text:
            price_description = element.text
            price_data["price"] = int("".join(price_description[:price_description.find("₽") - 1].split()))

            return price_data

    return price_data


def define_specification_data(block):
    specification_data = dict()
    specification_data["floor"] = -1
    specification_data["floors_count"] = -1
    specification_data["rooms_count"] = -1
    specification_data["total_meters"] = -1

    title = block.select("div[data-name='LinkArea']")[0].select("div[data-name='GeneralInfoSectionRowComponent']")[
        0].text

    common_properties = block.select("div[data-name='LinkArea']")[0]. \
        select("div[data-name='GeneralInfoSectionRowComponent']")[0].text

    if common_properties.find("м²") is not None:
        total_meters = title[: common_properties.find("м²")].replace(",", ".")
        if len(re.findall(FLOATS_NUMBERS_REG_EXPRESSION, total_meters)) != 0:
            specification_data["total_meters"] = float(
                re.findall(FLOATS_NUMBERS_REG_EXPRESSION, total_meters)[-1].replace(" ", "").replace("-", ""))

    if "этаж" in common_properties:
        floor_per = common_properties[common_properties.rfind("этаж") - 7: common_properties.rfind("этаж")]
        floor_properties = floor_per.split("/")

        if len(floor_properties) == 2:
            ints = re.findall(r'\d+', floor_properties[0])
            if len(ints) != 0:
                specification_data["floor"] = int(ints[-1])

            ints = re.findall(r'\d+', floor_properties[1])
            if len(ints) != 0:
                specification_data["floors_count"] = int(ints[-1])

    specification_data["rooms_count"] = define_rooms_count(common_properties)

    return specification_data


def super_func_by_timosha(offer_url):
    headers = {
        'User-Agent': get_random_user_agent(),
        'Referer': 'https://google.com'
    }

    try:
        response = requests.get(offer_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка при отправке запроса: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # with open("parsed_page.html", "w", encoding="utf-8") as file:
    #     file.write(soup.prettify())

    station_list = soup.find('ul', class_='a10a3f92e9--undergrounds--sGE99')
    stations = station_list.find_all('li', class_='a10a3f92e9--underground--pjGNr')

    result = {}

    for station in stations:
        station_name = station.find('a', class_='a10a3f92e9--underground_link--VnUVj').text.strip()

        time_to_station = station.find('span', class_='a10a3f92e9--underground_time--YvrcI').text.strip()

        icon_svg = station.find('svg', class_='a10a3f92e9--container--xt4AF a10a3f92e9--display_inline-block--wFJ1O a10a3f92e9--color_gray_icons_100--iUfv9')
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

        result[station_name] = {
            'Время': time_to_station,
            'Способ передвижения': travel_mode
        }

    return result
