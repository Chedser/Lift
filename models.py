from db_connection import *
from enums import *


class DBManager(object):

    # Запись в бд
    @staticmethod
    def write(code: DBCode, login=""):
        with sqlite3.connect('database.db') as con:
            mappings = {
                DBCode.THREAD_SWITCHED: 'Поток запущен',
                DBCode.LIFT_SWITCHED: 'Лифт запущен',
                DBCode.CLIENT_CONNECTED: 'Клиент подключен',
                DBCode.CLIENT_IS_ADDED_IN_LIST: 'Клиент добавлен в список',
                DBCode.CLIENT_IS_IN_LIST: 'Клиент уже есть в списке',
                DBCode.CLIENT_DISCONNECT: 'Клиент отключен',
                DBCode.LIFT_IS_EMPTY: 'Лифт пуст',
                DBCode.LIFT_STOPPED: 'Лифт остановлен',
                DBCode.FLOOR_IS_IN_LIST: 'Этаж уже есть в списке',
                DBCode.WRONG_FLOOR: 'Неверный этаж',
                DBCode.EMPTY: 'Тест'
            }

        try:
            msg = mappings[code]
            cur = con.cursor()
            cur.execute("INSERT INTO logs (login,code,text) VALUES (?,?,?)", (login, code, msg))
            con.commit()
            cur.close()
        except sqlite3.Error as error:
            con.rollback()
            print("DataBase error {0}".format(error))
        except KeyError as error:
            print("KeyError: {0}. Method DBManager.write()".format(error))


class Lift(object):
    __FLOORS_COUNT = 9  # Количество этажей
    FLOOR_DEFAULT = 0  # Этаж на котором изначально стоит лифт и куда едет если пустой
    __FLOOR_LAST = __FLOORS_COUNT - 1
    floor_current = 0  # Этаж на который в данный момент едет лифт
    state = LiftState.NEUTRAL  # Текущее состояние лифта
    clients = list()

    def __init__(self):
        self.floor_nearest = 0  # Этаж назначения близжайший
        self.floors = [-1, -1, -1, -1, -1, -1, -1, -1, -1]# Этажи назначения
        self.floor_dest = 0

        print("Lift is created")
        DBManager.write(DBCode.LIFT_SWITCHED)

    def add_client(self, client):
        if client.floor_to == client.floor_dest: return

        #self.clients.append(client.login)
        self.clients.append(client)

        for i, floor in enumerate(self.floors):
            if client.floor_dest == i:
                self.floors[i] = client.floor_to

    def delete_client(self, login):
        self.clients.pop(login)

    def delete_clients(self):
        self.clients.clear()

    def get_floors(self):
        return self.floors

    def is_free(self) -> bool:
        return self.floors.count(-1) == self.__FLOORS_COUNT

    def set_state(self, state: LiftState):
        self.state = state

    #Поиск ближайшего этажа
    def update_floor_nearest(self):

        found_indexes = list()

        for i, floor in enumerate(self.floors):
            if floor == -1:
                continue
            found_indexes.append(i)

        if len(found_indexes) == 0:
            self.floor_dest = 0
            return

        found = found_indexes[0]
        for item in found_indexes:
            if abs(item - self.floor_current) < abs(found - self.floor_current):
                    found = item
        self.floor_dest = found

    def go_to_next_floor(self):
        if self.floor_current < self.floor_dest:
            self.__going_up()
        elif self.floor_current > self.floor_dest:
            self.__going_down()

    def __going_up(self):
        if self.floor_current < self.floor_dest and self.floor_current != self.__FLOOR_LAST:
            self.floor_current += 1
            self.state = LiftState.GOING_UP

    def __going_down(self):
        if self.floor_current > self.floor_dest and self.floor_current != self.FLOOR_DEFAULT:
            self.floor_current -= 1
            self.state = LiftState.GOING_DOWN

    def update_floor_dest(self):

        if self.floors[self.floor_current] != -1: #Вызов на этом этаже есть

            dest = self.floors[self.floor_current]
            self.floors[dest] = -2
            self.floors[self.floor_current] = -1 #Вызова уже нет
            self.floor_dest = dest

    def reached_dest_client_floor(self):
        for client in self.clients:
            if int(client.floor_to) + 1 == self.floor_current:
                return self.floor_current
        return None

# Клиент
class Client(object):

    def __init__(self, login, floor_to:int, floor_dest:int):
        self.login = login
        self.floor_to = floor_to
        self.floor_dest = floor_dest

    def get_json(self):
        return {"login": self.login, "floor_to": self.floor_to, "floor_dest": self.floor_dest}

    def get_floor_to(self):
        return self.floor_to

    def get_floor_dest(self):
        return self.floor_dest


class Pair(object):
    def __init__(self, index, value):
        self.index = index
        self.value = value

