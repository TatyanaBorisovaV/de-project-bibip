from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
import os
from pathlib import Path


class CarService:  # Инициализирует пути к файлам, где будут храниться данные.
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        # Создаёт директорию, если её нет:
        Path(self.root_directory_path).mkdir(exist_ok=True)
        self.models_file = os.path.join(self.root_directory_path, "models.txt")
        self.cars_file = os.path.join(self.root_directory_path, "cars.txt")
        self.models_index_file = os.path.join(self.root_directory_path,
                                              "models_index.txt")
        self.cars_index_file = os.path.join(self.root_directory_path,
                                            "cars_index.txt")
        self.sales_file = os.path.join(self.root_directory_path, "sales.txt")
        self.sales_index_file = os.path.join(self.root_directory_path,
                                             "sales_index.txt")
        # На момент инициализации = 0, далее счётчик +1
        self.line_number_cars = 0
        self.line_number_models = 0
        self.line_number_sales = 0

        # Проверка существования файлов перед чтением и создание, если их нет
        for file_path in [
            self.models_file,
            self.cars_file,
            self.models_index_file,
            self.cars_index_file,
            self.sales_file,
            self.sales_index_file
        ]:
            if not os.path.exists(file_path):
                with open(file_path, 'w'):
                    pass  # Файл создан

    # Все пары ключи-индексы из файла считываются без пробелов и строк
    def _read_index(self, file_path):
        with open(file_path, 'r') as f:
            return [line.strip().split() for line in f.readlines()]

    # Метод сортировки и обновления индекса.
    def _sort_and_write_index(self, file_path):
        data = self._read_index(file_path)
        data.sort(key=lambda x: x[0])  # Отсортировали список по vin.
        # Теперь перезапишем заново в таблицу уже отсортированный список.
        with open(file_path, 'w') as f:
            for line in data:
                f.write(f'{line[0]} {line[1]}'.ljust(500) + '\n')

    def read_line(self, file_path, line):
        with open(file_path, 'r') as f:
            f.seek(int(line) * 502)
            return f.read(500)

    def find_index_by_key(self, key, file_path):
        # Находим индекс по ключу в файле index
        massive = self._read_index(file_path)
        for i in range(len(massive)):
            if massive[i][0] == key:
                return massive[i][1]  # Возвращает индекс.

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        formatted_line = (f'{model.id} {model.name} {model.brand}'
                          .ljust(500) + '\n')
        with open(self.models_file, 'r+', encoding='utf-8') as f_data:
            # длина строки 502, т.к. добавили символ перехода строки \n
            f_data.seek(self.line_number_models * (502))
            f_data.write(formatted_line)
        with open(self.models_index_file, 'a', encoding='utf-8') as f_index:
            f_index.write(f'{model.id} {self.line_number_models}'
                          .ljust(500) + '\n')
        self._sort_and_write_index(self.models_index_file)
        self.line_number_models += 1

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        formatted_line = (f'{car.vin} {car.model} {car.price} '
                          f'{car.date_start} {car.status}'.ljust(500) + '\n')
        with open(self.cars_file, 'r+', encoding='utf-8') as f_data:
            f_data.seek(self.line_number_cars * 502)
            f_data.write(formatted_line)
        with open(self.cars_index_file, 'a', encoding='utf-8') as f_index:
            f_index.write(f'{car.vin} {self.line_number_cars}'.
                          ljust(500) + '\n')
        self._sort_and_write_index(self.cars_index_file)
        self.line_number_cars += 1

    # Задание 2. Сохранение продаж.
    # Нужно реализовать запись о продаже: sales.txt, sales_index.txt
    # что в таблице cars необходимо изменить статус машины на sold.
    def sell_car(self, sale: Sale) -> Car:
        formatted_line = (f'{sale.sales_number} {sale.car_vin} {sale.cost} '
                          f'{sale.sales_date} {sale.is_deleted}'.ljust(500) + '\n')
        with open(self.sales_file, 'r+') as f:
            f.seek(self.line_number_sales * (502))
            f.write(formatted_line)
        with open(self.sales_index_file, 'a') as f:
            f.write(f'{sale.car_vin} {self.line_number_sales}'
                    .ljust(500) + '\n')
        self._sort_and_write_index(self.sales_index_file)
        self.line_number_sales += 1  # Увеличение кол-ва строк на 1.
        self.change_status_car(sale.car_vin, CarStatus.sold)

    # Метод для смены статуса машины и перезаписи файла cars.txt
    def change_status_car(self, vin, status: CarStatus):
        i = self.find_index_by_key(vin, self.cars_index_file)
        car_line_str = self.read_line(self.cars_file, i).strip().split()
        car_sale = Car(
            vin=car_line_str[0],
            model=car_line_str[1],
            price=car_line_str[2],
            date_start=car_line_str[3],
            status=status  # Указываем нужный статус машины.
        )
        self.write_car_to_file(self.cars_file, i, car_sale)

    def write_car_to_file(self, file_path: str, i: int, car: Car) -> None:
        formatted_line = (f'{car.vin} {car.model} {car.price} '
                          f'{car.date_start} {car.status}'.ljust(500) + '\n')
        with open(file_path, 'r+') as f:
            f.seek(int(i) * (502))
            f.write(formatted_line)

    def write_sale_to_file(self, file_path: str, i: int, sale: Sale) -> None:
        formatted_line = (f'{sale.sales_number} {sale.car_vin} {sale.cost} '
                          f'{sale.sales_date} {sale.is_deleted}'.ljust(500) + '\n')
        with open(file_path, 'r+') as f:
            f.seek(int(i) * (502))
            f.write(formatted_line)

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        list_status = []
        with open(self.cars_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.strip().split()[-1] == status:  # Ищем статус.
                    car = Car(
                        vin=line.strip().split()[0],
                        model=int(line.strip().split()[1]),
                        price=line.strip().split()[2],
                        date_start=line.strip().split()[3],
                        status=line.strip().split()[-1]
                    )
                    list_status.append(car)  # B добавляем в список.
        if not list_status:
            print('Нет моделей для продажи')
        # Сортировка по VIN-коду
        list_status_sorted = sorted(list_status, key=lambda x: x.vin)
        print(f'Список доступных машин: {list_status_sorted}')
        return list_status_sorted

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        # Читаем файл cars_index.txt.
        i = self.find_index_by_key(vin, self.cars_index_file)
        # Находим строку в файле cars.txt по номеру строки.
        line = self.read_line(self.cars_file, i)
        line_str = line.strip().split()
        # Читаем поле model в объекте car.
        model = line_str[1]
        # Узнаём индекс в файле конкретной модели
        row_num = self.find_index_by_key(model, self.models_index_file)
        line_model = self.read_line(self.models_file, row_num)
        line_model_str = line_model.strip().split()
        # Если машина не продана, то:
        sale_price = None
        sale_data = None
        if line_str[-1] == 'sold':
            ind = int(self.find_index_by_key(vin, self.sales_index_file))
            sale_line = self.read_line(self.sales_file, ind).strip().split()
            sale_price = sale_line[2]
            sale_data = sale_line[3]
        # Верните объект CarFullInfo с помощью выражения.
        return CarFullInfo(
            vin=vin,
            car_model_name=line_model_str[1],
            car_model_brand=line_model_str[2],
            price=line_str[2],
            date_start=line_str[3],
            status=line_str[-1],
            sales_date=sale_data,
            sales_cost=sale_price)

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        # Читаем файл cars_index.txt.
        i = self.find_index_by_key(vin, self.cars_index_file)
        # Находим строку в файле cars.txt по номеру строки.
        line = self.read_line(self.cars_file, i)
        line_str = line.strip().split()
        car = Car(
            vin=new_vin,
            model=line_str[1],
            price=line_str[2],
            date_start=line_str[3],
            status=line_str[-1]
        )
        # Перезаписали данные о машине с новым VIN в car.txt
        self.write_car_to_file(self.cars_file, i, car)
        # Считываем пары вин - индекс из файла cars_index_file
        index_massive = self._read_index(self.cars_index_file)
        for num_i in range(len(index_massive)):
            if index_massive[num_i][0] == vin:
                index_massive[num_i][0] = new_vin  # Заменяем на новый vin
        # Отсортировали список по первому ключу (vin)
        index_massive.sort(key=lambda x: x[0])
        # Теперь перезапишем заново в таблицу уже отсортированный список.
        with open(self.cars_index_file, 'w') as f:
            for line in index_massive:
                f.write(f'{line[0]} {line[1]}'.ljust(500) + '\n')

        # Обновим vin в поле ключевом файла о продажах.
        i = self.find_index_by_key(vin, self.sales_index_file)
        # Находим строку в файле sales.txt по номеру строки.
        line_sales = self.read_line(self.sales_file, i)
        line_sales_str = line_sales.strip().split()
        sale = Sale(
            sales_number=line_sales_str[0],
            car_vin=new_vin,
            sales_date=line_sales_str[3],
            cost=line_sales_str[2],
            is_deleted=line_sales_str[-1]
        )
        # Перезаписали данные о машине с новым VIN в sales.txt.
        self.write_sale_to_file(self.sales_file, i, sale)
        # Считываем пары вин - индекс из файла sales_index_file.
        index_massive_sales = self._read_index(self.sales_index_file)
        for num_i in range(len(index_massive_sales)):
            if index_massive_sales[num_i][0] == vin:
                index_massive_sales[num_i][0] = new_vin  # Заменяем vin.
        # Отсортировали список по первому ключу (vin)
        index_massive_sales.sort(key=lambda x: x[0])
        # Теперь перезапишем заново в таблицу уже отсортированный список.
        with open(self.sales_index_file, 'w') as f:
            for line in index_massive_sales:
                f.write(f'{line[0]} {line[1]}'.ljust(500) + '\n')
        return car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        vin = self.find_index_by_key(sales_number, self.sales_file)
        i = self.find_index_by_key(vin, self.sales_index_file)
        with open(self.sales_file, 'r+') as f:
            f.seek(int(i) * 502)
            line = f.read(500).strip().split()
            line[5] = True
            f.seek(int(i) * 502)
            f.write(f'{line[0]} {line[1]} {line[2]} {line[3]} {line[4]} '
                    f'{line[5]}'.ljust(500) + '\n')
        self.read_sales_no_deleted(self.sales_file)
        # Нужно вернуть статус для машины на avaliable.
        i_car = self.find_index_by_key(vin, self.cars_index_file)
        self.change_status_car(vin, CarStatus.available)
        # Читаем строчку из cars.txt c обновлённым статусом.
        result = self.read_line(self.cars_file, i_car).strip().split()
        return Car(
            vin=result[0],
            model=result[1],
            price=result[2],
            date_start=result[3],
            status=result[5]
        )

    def read_sales_no_deleted(self, file_path):
        sales_list = []
        with open(file_path, 'r') as f:
            for line in f:
                data = line.strip().split()
                if data[5] == 'False':
                    sales_list.append(data)
        return sales_list

    # Задание 7. Самые продаваемые
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        # Открываем список продаж без удалённых.
        sales_list = self.read_sales_no_deleted(self.sales_file)
        # Cписок для хранения продаж с полной информацией о машине.
        sales_model = []
        for sale in sales_list:
            # Получаем полную инфо о машине по VIN.
            info = self.get_car_info(sale[1])
            sales_model.append(info)
        # Подсчитываем количество и сумму продаж для каждой модели,
        # используя словарь с ключами модель, бренд
        model_counts = defaultdict(lambda: {'sales_count': 0,
                                            'total_price': 0})
        for car in sales_model:
            model_key = (car.car_model_name, car.car_model_brand)
            # Считаем кол-во продаж.
            model_counts[model_key]['sales_count'] += 1
            # Считаем сумму этих продаж.
            model_counts[model_key]['total_price'] += car.price
        results = []
        # Извлекаем из словаря инфо, записывая в виде ModelSaleStats.
        for (car_model_name, brand), counts in model_counts.items():
            result = ModelSaleStats(
                car_model_name=car_model_name,
                brand=brand,
                sales_number=counts['sales_count'],
                total_price=counts['total_price']
            )
            results.append(result)
        # Сортируем по количеству продаж и цене продаж.
        results.sort(key=lambda x: (-x.sales_number, -x.total_price))
        print(f'Список ТОП-3 самых продаваемых моделей: {results[:3]}')
        return results[:3]  # Возвращаем топ-3 модели


# Проверка кода записями из таблиц:
service = CarService('temdir')
models = [
    Model(id=1, name="Optima", brand="Kia"),
    Model(id=2, name="Sorento", brand="Kia"),
    Model(id=3, name="3", brand="Mazda"),
    Model(id=4, name="Pathfinder", brand="Nissan"),
    Model(id=5, name="Logan", brand="Renault")
]
# Запись в файл models добавляется по одной модели в цикле массива.
for model in models:
    service.add_model(model)

car = Car(vin="KNAGM4A77D5316538", model=1, price=Decimal("2000"),
          date_start=datetime(2024, 2, 8), status=CarStatus.available)
service.add_car(car)
car = Car(vin="5XYPH4A10GG021831", model=2, price=Decimal("2300"),
          date_start=datetime(2024, 2, 20), status=CarStatus.reserve)
service.add_car(car)
car = Car(vin="KNAGH4A48A5414970", model=1, price=Decimal("2100"),
          date_start=datetime(2024, 4, 4), status=CarStatus.available)
service.add_car(car)
car = Car(vin="JM1BL1TFXD1734246", model=3, price=Decimal("2276.65"),
          date_start=datetime(2024, 5, 17), status=CarStatus.available)
service.add_car(car)
car = Car(vin="JM1BL1M58C1614725", model=3, price=Decimal("2549.10"),
          date_start=datetime(2024, 5, 17), status=CarStatus.reserve)
service.add_car(car)
car = Car(vin="KNAGR4A63D5359556", model=1, price=Decimal("2376"),
          date_start=datetime(2024, 5, 17), status=CarStatus.available)
service.add_car(car)
car = Car(vin="5N1CR2MN9EC641864", model=4, price=Decimal("3100"),
          date_start=datetime(2024, 6, 1), status=CarStatus.available)
service.add_car(car)
car = Car(vin="JM1BL1L83C1660152", model=3, price=Decimal("2635.17"),
          date_start=datetime(2024, 6, 1), status=CarStatus.available)
service.add_car(car)
car = Car(vin="5N1CR2TS0HW037674", model=4, price=Decimal("3100"),
          date_start=datetime(2024, 6, 1), status=CarStatus.available)
service.add_car(car)
car = Car(vin="5N1AR2MM4DC605884", model=4, price=Decimal("3200"),
          date_start=datetime(2024, 7, 15), status=CarStatus.available)
service.add_car(car)
car = Car(vin="VF1LZL2T4BC242298", model=5, price=Decimal("2280.76"),
          date_start=datetime(2024, 8, 31), status=CarStatus.delivery)
service.add_car(car)

sales = [
    Sale(
        sales_number="20240903#KNAGM4A77D5316538",
        car_vin="KNAGM4A77D5316538",
        sales_date=datetime(2024, 9, 3),
        cost=Decimal("1999.09")
    ),
    Sale(
        sales_number="20240903#KNAGH4A48A5414970",
        car_vin="KNAGH4A48A5414970",
        sales_date=datetime(2024, 9, 4),
        cost=Decimal("2100")
    ),
    Sale(
        sales_number="20240903#KNAGR4A63D5359556",
        car_vin="KNAGR4A63D5359556",
        sales_date=datetime(2024, 9, 5),
        cost=Decimal("7623")
    ),
    Sale(
        sales_number="20240903#JM1BL1M58C1614725",
        car_vin="JM1BL1M58C1614725",
        sales_date=datetime(2024, 9, 6),
        cost=Decimal("2334")
    ),
    Sale(
        sales_number="20240903#JM1BL1L83C1660152",
        car_vin="JM1BL1L83C1660152",
        sales_date=datetime(2024, 9, 7),
        cost=Decimal("451")
    ),
    Sale(
        sales_number="20240903#5N1CR2TS0HW037674",
        car_vin="5N1CR2TS0HW037674",
        sales_date=datetime(2024, 9, 8),
        cost=Decimal("9876")
    ),
    Sale(
        sales_number="20240903#5XYPH4A10GG021831",
        car_vin="5XYPH4A10GG021831",
        sales_date=datetime(2024, 9, 9),
        cost=Decimal("1234")
    )
]
for sale in sales:
    service.sell_car(sale)

# вызов решения 3 задачи
service.get_cars(CarStatus.available)
# 4 задача: поиск информации о машине по vin
service.get_car_info('KNAGM4A77D5316538')
# 5 задача, апгрейд вин.
service.update_vin('KNAGM4A77D5316538', 'UPDGM4A77D5316538')
# 6 задача об удалении продажи
service.revert_sale('20240903#KNAGM4A77D5316538')
service.top_models_by_sales()  # 7 задача - топ3.
