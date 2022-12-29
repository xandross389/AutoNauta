from dis import findlinestarts
import json
from time import sleep
import time
from nautasdk.exceptions import NautaLoginException, NautaLogoutException, NautaException, NautaPreLoginException
from nautasdk.utils import clear, is_time_between
from router import Router
from configuration_manager import ConfigurationManager, Configuration
from nautasdk.nauta_api import NautaClient, NautaProtocol
from nautasdk import utils
import asyncio
from termcolor import colored

# internal constants
IS_ONLINE = False
KEEP_MONITORING = True
RUNNING_TEXT = colored('*** Monitoreando conexión (Presione Ctrl + C para detener y cerrar sesión) ***', 'yellow')
config_manager = ConfigurationManager()
config = config_manager.get_config()

# global router object to manage router
router = Router(ip_address=config.router_ip, username=config.router_username, password=config.router_password)
# global nauta client object to manage sessions
nauta_client = NautaClient(user=config.credentials[0]['username'], password=config.credentials[0]['password'], default_check_page=config.check_connection_page)

async def online_monitor():
    global IS_ONLINE
    while True:
        check_online = asyncio.create_task(is_online()) #init the other task
        await asyncio.sleep(5)
        clear()
        print_status_text()
        if not IS_ONLINE: #is_online():
            try:
                connect(client=nauta_client)
            except Exception as e:
                print(f"Error connecting to nauta: {e}")
        await asyncio.sleep(config.connection_check_frequency_in_secs) #waits 2 secs in the main thread (you can delte this line if your iteration delays making computation)
        check_online.cancel()
        print_status_text()

async def is_online() -> bool:
    global IS_ONLINE
    IS_ONLINE = NautaProtocol.ping(config.check_ping_host, 1)
    await asyncio.sleep(1)

def print_status_text():
    print(RUNNING_TEXT)
    status = colored('DESCONECTADO |---X---|', 'red')
    # if is_online():
    if IS_ONLINE:
        status = colored('CONECTADO |<---->|', 'green')
    print(f'Usted está {status}')

async def monitor_connection_status():
    clear()
    print_status_text()
    if not IS_ONLINE: #is_online():
        connect(client=nauta_client)
    else:
        sleep(config.connection_check_frequency_in_secs) 

def connect(client=None):
    if client:
        print(
            "Conectando usuario: {}".format(
                client.user,
            )
        )

        with client.login():
            clear()
            print_status_text()

            login_time = int(time.time())
            print("[sesión iniciada]")
            print(f"Usuario: {client.user}")
            print("Tiempo restante: {}".format(utils.val_or_error(lambda: client.remaining_time)))
            print("Presione Ctrl+C para desconectarse")

            try:
                while True:
                    if not client.is_logged_in or not NautaProtocol.ping(host=config.check_ping_host):
                        break

                    elapsed = int(time.time()) - login_time

                    print(
                        "\rTiempo de conexion: {}.".format(
                            utils.seconds2strtime(elapsed)
                        ),
                        end=""
                    )
                    time.sleep(2)
            except KeyboardInterrupt:
                pass
            finally:
                print("\n\nCerrando sesión ...")
                print("Tiempo restante: {}".format(utils.val_or_error(lambda: client.remaining_time)))

        print("sesión cerrada con exito.")
        print("Credito: {}".format(
            utils.val_or_error(lambda: client.user_credit)
        ))
        sleep(5)
        clear()
        print_status_text()
    else:
        raise NautaPreLoginException("No se especificó ningún usuario para conectar")

def disconnect(client=None):
    # client = NautaClient(user=config.credentials[0]['username'], password=config.credentials[0]['password'],
    #                      default_check_page=config.check_connection_page)
    if client:
        if client.is_logged_in:
            client.load_last_session()
            client.logout(max_disconnect_attempts=config.disconnection_retry_times)
        #     print("sesión cerrada con exito")
        # else:
        #     print("No hay ninguna sesión activa")
        sleep(1)
        return not NautaProtocol.ping(host=config.check_ping_host)
    else:
        raise NautaLogoutException("No se especificó ningún usuario para desconectar")

def must_be_connected():
    return is_time_between(config.connection_begin_time, config.connection_end_time)

def enough_user_remaining_time(client=None, threshold=1):
    """
    :param client: Nauta client object, default is None
    :param threshold: Threshold for remaining time in seconds to assume that is enough left time or not, default is 1
    :returns True or False if user have enough time balance or not
    """
    enough = False
    if client:
        if utils.strtime2seconds(client.remaining_time) >= threshold:
            enough = True
    return enough

if __name__ == '__main__':
    asyncio.run(online_monitor())