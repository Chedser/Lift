import enum

#Текущее состояние лифта
class LiftState(int, enum.Enum):
    NEUTRAL = 0
    GOING_DOWN = 1
    GOING_UP = 2


#Код ответа лифта
class LiftResponseCode(int, enum.Enum):
    LIFT_FREE = 0  # Список этажей пуст
    LIFT_STOPPED = 1  # Лифт остановлен
    LIFT_CURRENT_FLOOR = 2  # Текущий этаж
    CLIENT_IN = 3  # Клиент вошел
    CLIENT_OUT = 4  # Клиент вышел
    EMPTY = 5

class DBCode(int, enum.Enum):
    THREAD_SWITCHED = 0  # Поток запущен
    LIFT_SWITCHED = 1  # Лифт запущен
    CLIENT_CONNECTED = 2  # Клиент подключен
    CLIENT_IS_ADDED_IN_LIST = 3  # Клиент добавлен в список
    CLIENT_IS_IN_LIST = 4  # Клиент уже есть в списке
    CLIENT_DISCONNECT = 5  # Клиент отключен
    LIFT_IS_EMPTY = 6  # Лифт пуст
    LIFT_STOPPED = 7  # Лифт остановлен
    FLOOR_IS_IN_LIST = 8  # Этаж уже есть в списке
    WRONG_FLOOR = 9  # Неверный этаж
    EMPTY = 10