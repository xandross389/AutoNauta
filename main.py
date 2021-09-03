from time import sleep
import time
# from datetime import datetime
from nautasdk.exceptions import NautaLoginException, NautaLogoutException, NautaException
from utils import clear, is_time_between
from nautasdk import utils
import os

from nautasdk.nauta_api import NautaClient, NautaProtocol
from nautasdk import utils

# Default configuration items, custom it through config.json file
USERNAME = 'cdn.espinf1@nauta.com.cu'
PASSWORD = 'Lqqdysh/*20*/'
# CHECK_CONNECTION_PAGE = 'http://192.168.1.188:8080/'
CHECK_CONNECTION_PAGE = 'http://www.cubadebate.cu/'
CONNECTION_BEGIN_TIME = '07:00'
CONNECTION_END_TIME = '23:30'
CONNECTION_CHECK_FRECUENCY = 12
DISCONNECTION_BEGIN_TIME = '00:00'
DISCONNECTION_END_TIME = '06:59'
DISCONNECTION_CHECK_FRECUENCY = 12
RUNNING_TEXT = '*** Monitoreando conexión (Presione Ctrl + C para detener y cerrar sesión) ***'


def load_configuration(config_file='./config.json'):
    if not os.path.isfile(config_file):
        create_default_configuration_file()
    else:
        pass
        # load configuration items
        # Default configuration items, custom it through config.json file
        # USERNAME = ''
        # PASSWORD = ''
        # CHECK_CONNECTION_PAGE = 'http://192.168.1.188:8080/'
        # CONNECTION_BEGIN_TIME = '07:00'
        # CONNECTION_END_TIME = '18:30'
        # CONNECTION_CHECK_FRECUENCY = 10
        # DISCONNECTION_BEGIN_TIME = '18:31'
        # DISCONNECTION_END_TIME = '06:59'
        # DISCONNECTION_CHECK_FRECUENCY = 10
        # RUNNING_TEXT = '*** Monitoreando conexión (Presione Ctrl + C para detener y cerrar sesión) ***'


def create_default_configuration_file():
    if not os.path.isfile('./config.json'):
        pass


def print_status_text():
    print(RUNNING_TEXT)
    # print('most be connected')
    status = 'DESCONECTADO'
    if is_online():
        status = 'CONECTADO'
    print(f'Usted esta {status}')


def monitor_connection_status():
    # clear()
    # print_status_text()

    if most_be_connected():
        print('most_be_connected()')
        clear()
        print_status_text()

        while not is_online():
            if not most_be_connected():
                break
            # sleep(CONNECTION_CHECK_FRECUENCY)
            # clear()
            # print_status_text()
            sleep(CONNECTION_CHECK_FRECUENCY)

            try:
                connect()
            except NautaLoginException as ex:
                print(f'Error iniciando de sesion: ({ex})')
            except NautaLogoutException as ex:
                print(f'Error cerrando de sesion ({ex})')
            except NautaException as ex:
                print(f'Error de Nauta: ({ex})')
            except Exception as ex:
                print(f'Error de conexión. Asegurese de estar conectado a la red ({ex})')
            # except KeyboardInterrupt:
            #     pass
            #     # print('most_be_connected()')
            finally:
                clear()
                print_status_text()
            # except KeyboardInterrupt:
            #     pass
            # finally:
            #     pass

    if most_be_disconnected():
        print('most_be_disconnected()')
        clear()
        print_status_text()

        while is_online():
            if not most_be_disconnected():
                break

            # clear()
            # print_status_text()
            sleep(DISCONNECTION_CHECK_FRECUENCY)

            try:
                disconnect()
            except NautaLoginException as ex:
                print(f'Error iniciando de sesion ({ex})')
            except NautaLogoutException as ex:
                print(f'Error cerrando de sesion ({ex})')
            except NautaException as ex:
                print(f'Error de Nauta ({ex})')
            except Exception as ex:
                print(f'Error de conexión. Asegurese de estar conectado a la red ({ex})')
                # pass
            # except KeyboardInterrupt:
            #     pass
                # print('most_be_disconnected()')
            # finally:
            #     sleep(DISCONNECTION_CHECK_FRECUENCY)
                # clear()
            # except KeyboardInterrupt:
            #     pass
            finally:
                clear()
                print_status_text()

    clear()
    print_status_text()
    print('=> Esperando planificación de conexión/desconexión')


def connect():
    client = NautaClient(user=USERNAME, password=PASSWORD, default_check_page=CHECK_CONNECTION_PAGE)

    print(
        "Conectando usuario: {}".format(
            client.user,
        )
    )

    # if args.batch:
    #     client.login()
    #     print("[Sesion iniciada]")
    #     print("Tiempo restante: {}".format(utils.val_or_error(lambda: client.remaining_time)))
    # else:
    with client.login():
        login_time = int(time.time())
        print("[Sesion iniciada]")
        print("Tiempo restante: {}".format(utils.val_or_error(lambda: client.remaining_time)))
        print(
            "Presione Ctrl+C para desconectarse"
            # ", o ejecute 'nauta down' desde otro terminal".format(
            #     prog_name
            # )
        )

        try:
            while True:
                if not client.is_logged_in:
                    break

                elapsed = int(time.time()) - login_time

                print(
                    "\rTiempo de conexion: {}.".format(
                        utils.seconds2strtime(elapsed)
                    ),
                    end=""
                )

                # if args.session_time:
                #     if args.session_time < elapsed:
                #         break
                #
                #     print(
                #         " La sesion se cerrara en {}.".format(
                #             utils.seconds2strtime(args.session_time - elapsed)
                #         ),
                #         end=""
                #     )

                time.sleep(2)
        except KeyboardInterrupt:
            pass
        finally:
            print("\n\nCerrando sesion ...")
            print("Tiempo restante: {}".format(utils.val_or_error(lambda: client.remaining_time)))

    print("Sesion cerrada con exito.")
    print("Credito: {}".format(
        utils.val_or_error(lambda: client.user_credit)
    ))


def disconnect():
    client = NautaClient(user=USERNAME, password=PASSWORD, default_check_page=CHECK_CONNECTION_PAGE)

    if client.is_logged_in:
        client.load_last_session()
        client.logout()
        print("Sesion cerrada con exito")
    else:
        print("No hay ninguna sesion activa")


def is_online():
    online = False
    try:
        online = NautaProtocol.is_connected(check_page=CHECK_CONNECTION_PAGE)
    except ConnectionRefusedError as ex:
        print('La conexión fue rechazada por el host remoto - ' + ex)
    except ConnectionResetError as ex:
        print('La conexión fue reiniciada por el host remoto - ' + ex)
    except ConnectionAbortedError as ex:
        print('La conexión fue abortada por el host remoto - ' + ex)
    except ConnectionError as ex:
        print('Error de conexión. Asegurese de estar conectado a una red - ' + ex)
    except Exception as ex:
        print('Ha ocurrido un error intentando determinar el estado de la conexión - ' + ex)
    finally:
        return online


def most_be_connected():
    return is_time_between(CONNECTION_BEGIN_TIME, CONNECTION_END_TIME)


def most_be_disconnected():
    return is_time_between(DISCONNECTION_BEGIN_TIME, DISCONNECTION_END_TIME)


if __name__ == '__main__':
    clear()
    print_status_text()
    while True:
        sleep(2)
        try:
            monitor_connection_status()
        except KeyboardInterrupt:
            # print('Presione nuevamente Crtl + C para cerrar sesión')
            pass
        finally:
            print('main loop done')
            # sleep(5)
            # clear()

