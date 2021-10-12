import json
from time import sleep
import time
from nautasdk.exceptions import NautaLoginException, NautaLogoutException, NautaException
from nautasdk.utils import clear, is_time_between
from router import Router

from configuration_manager import ConfigurationManager, Configuration
from nautasdk.nauta_api import NautaClient, NautaProtocol
from nautasdk import utils

# internal constants
RUNNING_TEXT = '*** Monitoreando conexión (Presione Ctrl + C para detener y cerrar sesión) ***'
config_manager = ConfigurationManager()
config = config_manager.get_config()

router = Router(ip_address=config.router_ip, username=config.router_username, password=config.router_password)


def print_status_text():
    print(RUNNING_TEXT)
    status = 'DESCONECTADO'
    if is_online():
        status = 'CONECTADO'
    print(f'Usted esta {status}')


def monitor_connection_status():
    # while must_be_connected():
    if must_be_connected():

        try:
            if not NautaProtocol.ping(host=config.check_ping_host):
                connect()
            else:
                sleep(config.connection_check_frequency_in_secs)
        except NautaLoginException as ex:
            print(f'Error iniciando sesion: ({ex})')
        except NautaLogoutException as ex:
            print(f'Error cerrando sesion ({ex})')
        except NautaException as ex:
            print(f'Error de Nauta: ({ex})')
        except Exception as ex:
            print(f'Error de conexión. Asegurese de estar conectado a la red ({ex})')
        except KeyboardInterrupt:
            pass
    if not must_be_connected(): 
        if NautaProtocol.ping(host=config.check_ping_host):
            for i in range(config.disconnection_retry_times):
                print(f'Intentando desconectar ({i + 1} of {config.disconnection_retry_times})')

                try:
                    if disconnect():
                        break                
                except NautaLoginException as ex:
                    print(f'Error iniciando sesion ({ex})')
                except NautaLogoutException as ex:
                    print(f'Error cerrando sesion ({ex})')
                except NautaException as ex:
                    print(f'Error de Nauta ({ex})')
                except Exception as ex:
                    print(f'Error de conexión. Asegurese de estar conectado a la red ({ex})')

                sleep(10)

            if config.force_connection_close and NautaProtocol.ping(host=config.check_ping_host) and not must_be_connected():
                print('Usted esta conectado y la conexion debe ser cerrada. El router será reiniciando!!!\n')

                try:
                    if router.console_restart(debug=False, timeout=10):
                        print('Router reiniciado satisfactoriamente')
                    else:
                        print('Fallo reiniciando el router')
                except Exception as ex:
                    print('Ha ocurrido un error intentando reiniciar el router')
                # finally:
                #     print_status_text()
        
        else:
            sleep(config.disconnection_check_frequency_in_secs)       
    

def connect():
    client = NautaClient(user=config.credentials[0]['username'], password=config.credentials[0]['password'],
                         default_check_page=config.check_connection_page)

    print(
        "Conectando usuario: {}".format(
            client.user,
        )
    )

    with client.login():
        login_time = int(time.time())
        print("[Sesion iniciada]")
        print("Tiempo restante: {}".format(utils.val_or_error(lambda: client.remaining_time)))
        print("Presione Ctrl+C para desconectarse")
        
        try:
            while True:
                if not client.is_logged_in or not NautaProtocol.ping(host=config.check_ping_host):
                    break
                
                if not must_be_connected():
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
            print("\n\nCerrando sesion ...")
            print("Tiempo restante: {}".format(utils.val_or_error(lambda: client.remaining_time)))

    print("Sesion cerrada con exito.")
    print("Credito: {}".format(
        utils.val_or_error(lambda: client.user_credit)
    ))


def disconnect():
    client = NautaClient(user=config.credentials[0]['username'], password=config.credentials[0]['password'],
                         default_check_page=config.check_connection_page)

    if client.is_logged_in:
        client.load_last_session()
        client.logout()
    #     print("Sesion cerrada con exito")
    # else:
    #     print("No hay ninguna sesion activa")
    return not NautaProtocol.ping(host=config.check_ping_host)


def is_online():
    online = False
    try:
        online = NautaProtocol.is_connected(ping_host=config.check_ping_host)
    except ConnectionRefusedError as ex:
        print('La conexión fue rechazada por el host remoto - ' + str(ex))
    except ConnectionResetError as ex:
        print('La conexión fue reiniciada por el host remoto - ' + str(ex))
    except ConnectionAbortedError as ex:
        print('La conexión fue abortada por el host remoto - ' + str(ex))
    except ConnectionError as ex:
        print('Error de conexión. Asegurese de estar conectado a una red - ' + str(ex))
    except Exception as ex:
        print('Ha ocurrido un error intentando determinar el estado de la conexión - ' + str(ex))
    finally:
        return online


def must_be_connected():
    return is_time_between(config.connection_begin_time, config.connection_end_time)


if __name__ == '__main__':
    while True:
        clear()
        print_status_text()
        try:
            monitor_connection_status()
        except KeyboardInterrupt:
            pass
        finally:
            sleep(5)

