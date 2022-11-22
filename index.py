from routing import *
from flask_socketio import SocketIO, emit
from models import *

from threading import Thread, Event

socketio = SocketIO(app, logger=True, engineio_logger=True, async_mode=None)

thread = Thread()  # Поток для работы конечного автомата
thread_stop_event = Event()

lift = Lift()  # Объект конечного автомата

responsed = False  # Флаг ответа

def FSM():
    global lift
    global responsed

    with app.app_context():
        while not thread_stop_event.isSet():
            if lift.is_free():

                if not responsed:
                    lift.delete_clients()
                    print("Lift is free")
                    lift.set_state(LiftState.NEUTRAL)
                    lift_response_code = LiftResponseCode.LIFT_STOPPED
                    DBManager.write(DBCode.LIFT_STOPPED)

                    emit('lift_response',
                         {'code': lift_response_code, 'state': lift.state, 'floor_current': lift.floor_current + 1},
                         namespace='/', broadcast=True)
                responsed = True

            else:

                lift.go_to_next_floor()

                reached_dest_floor = -1
                if lift.reached_dest_client_floor():
                    reached_dest_floor = lift.reached_dest_client_floor()

                lift.update_floor_nearest()  # Незанятые этажи пропускаются

                lift.update_floor_dest()

                if lift.state == LiftState.GOING_DOWN or lift.state == LiftState.GOING_UP:
                    responsed = False
                    print("Lift on floor {0}".format(lift.floor_current + 1))
                    lift_response_code = LiftResponseCode.LIFT_CURRENT_FLOOR
                    emit('lift_response',
                         {'code': lift_response_code, 'state': lift.state, 'floor_current': lift.floor_current + 1, \
                          'reached_dest_floor': reached_dest_floor},
                         namespace='/', broadcast=True)

            socketio.sleep(1)


""" ////////////////////////////////////////////////////////////////////////////////////////////////////////// """
# Код ответа сокета
class ResponseCode(int, enum.Enum):
    CLIENT_IS_ADDED = 0  # Клиент добавлен
    CLIENT_IN_LIST = 1  # Клиент уже есть в списке
    WRONG_FLOOR = 2  # Неверный этаж
    FLOOR_EXISTS = 3  # Этаж уже есть в списке
    EMPTY = 4


""" СОБЫТИЯ СОКЕТА """
@socketio.on('connect', namespace='/')
def connect():
    global thread

    if not thread.isAlive() and request.cookies.get('user') is not None:  # Запускаем поток, если не запущен
        print("Thread switch {0}".format(request.cookies.get('user')))
        DBManager.write(DBCode.THREAD_SWITCHED, request.cookies.get('user'))
        thread = socketio.start_background_task(FSM)

    print("Client connected {0}".format(request.cookies.get('user')))
    DBManager.write(DBCode.CLIENT_CONNECTED, request.cookies.get('user'))
    emit('other_client_connect', {'client': request.cookies.get('user'), 'state': lift.state, 'floor_current': lift.floor_current + 1},
         namespace='/', broadcast=True)


@socketio.on('request', namespace='/')  # Клиент отправил номер этажа
def message_to_client(msg):
    errno = ResponseCode.EMPTY
    broadcast = True

    response = {}
    client = object()
    client_str = ""

    if (('floor_to' not in msg) or
            (msg['floor_to'] not in range(0, 9)) or
            ('floor_dest' not in msg) or
            (msg['floor_dest'] not in range(0, 9)) or
            (request.cookies.get('user') is None) or
            request.cookies.get(
                'user') is None):  # На случай, если кто-то умный захочет подключиться к сокету через другую прогу
        errno = ResponseCode.WRONG_FLOOR
        broadcast = False
        print("Hacker attack  {0}".format(request.cookies.get('user')))
        DBManager.write(DBCode.WRONG_FLOOR, request.cookies.get('user'))
    elif (msg['floor_to'] == msg['floor_dest']):  # Номера этажей совпадают
        errno = ResponseCode.FLOOR_EXISTS
        broadcast = False
        print("Floor numbers is equals {0}".format(request.cookies.get('user')))
        DBManager.write(DBCode.FLOOR_IS_IN_LIST)
    else:
        client_str = ""
        # Добавить в клиенты
        if msg['login'] not in lift.clients:  # Клиента нет в списке
            client = Client(msg['login'], int(msg['floor_to']), int(msg['floor_dest']))
            print(client.get_json())
            lift.add_client(client)
            errno = ResponseCode.CLIENT_IS_ADDED
            client_str = client.get_json()
            global responsed
            responsed = False
            print("Add new client {0}".format(request.cookies.get('user')))
            DBManager.write(DBCode.CLIENT_IS_ADDED_IN_LIST, request.cookies.get('user'))
        else:
            errno = ResponseCode.CLIENT_IN_LIST
            broadcast = False
            print("Floor numbers is equals {0}".format(request.cookies.get('user')))
            DBManager.write(DBCode.CLIENT_IS_IN_LIST, request.cookies.get('user'))

    response = {'errno': errno, 'client': client_str}
    emit('response', response, namespace='/', broadcast=broadcast)


@socketio.on('disconnect')  # Клиент отключен
def disconnect():
    if request.cookies.get('user') in lift.clients:
        lift.delete_client(request.cookies.get('user'))
    print("Client disconnect {0}".format(request.cookies.get('user')))
    DBManager.write(DBCode.CLIENT_DISCONNECT, request.cookies.get('user'))
    emit('other_client_disconnect', {'client': request.cookies.get('user'), 'floor_current': lift.floor_current + 1},
         namespace='/', broadcast=True)


@socketio.on_error_default  # Неизвестная ошибка
def default_error_handler(e):
    print("Unknown error {0}".format(e))

# ЗАПУСК СОКЕТА
if __name__ == '__main__':
    socketio.run(app, debug=True)
