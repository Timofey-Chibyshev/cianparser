### Сбор данных с сайта объявлений об аренде и продаже недвижимости Циан

Cianparser - это библиотека Python 3 для парсинга сайта  [Циан](http://cian.ru).
С его помощью можно получить достаточно подробные и структурированные данные по краткосрочной и долгосрочной аренде, продаже квартир, домов, танхаусов итд.

### Установка
```bash
pip install cianparser
```

### Использование
```python
>>> import cianparser
    
>>> data = cianparser.parse(
        offer="rent_long",
        accommodation="flat",
        location="Москва",
        rooms=(2, 3),
        start_page=1,
        end_page=2,
        save_csv=True,
        is_latin=False,
    )

>>> print(data[0])
```

```
                  Collecting information from pages..

The absolute path to the file: 
 /Users/macbook/pythonProject/cian_parsing_result_1_2_1_2023-02-03 00:48:23.156342.csv
The page from which the collection of information begins: 
  https://cian.ru/cat.php?deal_type=rent&engine_version=2&p=1&region=1&offer_type=flat&type=4&room2=1&room3=1

Setting [=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>] 100%
1 page: [=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>] 100%
2 page: [=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>] 100%

{'accommodation': 'flat',
 'city': 'Москва',
 'district': 'Мещанский',
 'street': 'Гиляровского',
 'floor': 1,
 'all_floors': 16,
 'square_meters': 73,
 'kitchen_meters': 10,
 'how_many_rooms': 3,
 'year_of_construction': '1988',
 'price_per_month': 80000,
 'commissions': 50,
 'author': 'ID 413522',
 'link': 'https://www.cian.ru/rent/flat/282954651/',
}
```

### Конфигурация
Функция __*parse*__ имеет следующий аргументы:
* __offer__ - тип объявления, к примеру, долгосрочная, краткосрочная аренда, продажа _("rent_long", "rent_short", "sale")_
* __accommodation__ - вид жилья, к примеру, квартира, комната, дом, часть дома, таунхаус _("flat", "room", "house", "house-part", "townhouse")_
* __location__ - локация объявления, к примеру, Казань (для просмотра доступных мест используйте _cianparser.list_cities())_
* __rooms__ - количество комнат, к примеру, _1, (1,3, "studio"), "studio, "all"_; по умолчанию любое _("all")_
* __start_page__ - страница, с которого начинается сбор данных, по умолчанию, _1_
* __end_page__ - страница, с которого заканчивается сбор данных, по умолчанию, _10_
* __save_csv__ - необходимо ли сохранять данные (в реальном времени в процессе сбора данных) или нет, по умолчанию _False_
* __is_latin__ - необходимо ли преобразовывать встрещающиеся слова из кириллицы в латиницу, по умолчанию _False_

#### В настоящее время функция *parse* принимает *offer* и *accommodation* только с значениями "rent_long" и "flat", соответственно

### Признаки, получаемые в ходе сбора данных с предложений по долгосрочной аренде.
* __Link__ - ссылка на это объявление
* __District__ - район, в которой расположена недвижимость
* __Price per month__ - стоимость аренды в месяц
* __Commissions__ - комиссия, взымаемая в ходе первичной аренды
* __Author__ - автор объявления (id собственника, имя рилетора или наименование агента недвижимости)
* __How many rooms__ - количество комнат, от 1 до 5и (студия приравнивается к 1-ой квартире)
* __Kitchen meters__ - количество квадратных метров кухни
* __Square meters__ - общее количество квадратных метров
* __Street__ - улица, в которой расположена квартира
* __Floor__ - этаж, на котором расположена квартира
* __All floors__ - общее количество этажей в здании, на котором расположена квартира
* __Year of construction__ - год постройки здания, на котором расположена квартира

В процессе парсинга имеется возможность задать преобразывание любой встрещающейся __кириллицы__ в __латиницу__. 
Для этого необходимо подставить в аргументе __is_latin__ значение ___True___.

В некоторых объявлениях отсутсвуют данные по некоторым признакам (_год постройки, жилые кв метры, кв метры кухни_).
В этом случае проставляется значение -1.

### Сохранение данных
Имеется возможность сохранения собирающихся данных в режиме реального времени. Для этого необходимо подставить в аргументе 
__save_csv__ значение ___True___.

Пример получаемого файла:

```bash
cian_parsing_result_1_2_1_2023-02-03 00:48:23.156342.csv
```

### Примечание
Для отсутствия блокировки по IP в данном проекте задана пауза (в размере 5 секунд) после сбора информации с
каждой отдельной взятой страницы.

Данный парсер не будет работать в таком инструменте как [Google Colaboratory](https://colab.research.google.com/). 
См. [подробности](https://github.com/lenarsaitov/cianparser/issues/1)

### Пример исследования получаемых данных
В данном проекте можно увидеть некоторые результаты анализа полученных данных на примере сведений об объявленияъ по аренде недвижимости в городе Казань:

https://github.com/lenarsaitov/cian-data-analysis
