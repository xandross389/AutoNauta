import ctypes
import threading
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
import json
from time import sleep
import time
from nautasdk.exceptions import NautaLoginException, NautaLogoutException, NautaException, NautaPreLoginException
from nautasdk.utils import is_time_between, curr_datetime_str
from router import Router
from configuration_manager import ConfigurationManager, Configuration
from nautasdk.nauta_api import NautaClient, NautaProtocol
from nautasdk import utils
from kivy.clock import Clock, mainthread


stop_threads = False

class MainWindow(FloatLayout):
    stop = threading.Event()
    # monitor_conn_status_thread = threading.Thread(target=self.monitor_connection_status, args=())

    # Global vars
    RUNNING_TEXT = '*** Monitoreando conexión (Presione Ctrl + C para detener y cerrar sesión) ***'
    config_manager = ConfigurationManager()
    config = config_manager.get_config()
    # global router object to manage router
    router = Router(ip_address=config.router_ip, username=config.router_username,
                    password=config.router_password)
    # global nauta client object to manage sessions
    nauta_client = NautaClient(user=config.credentials[0]['username'],
                               password=config.credentials[0]['password'],
                               default_check_page=config.check_connection_page)
    # Header panel
    ti_admin_user = ObjectProperty(None)
    ti_admin_pass = ObjectProperty(None)
    tgl_btn_active = ObjectProperty(None)
    # Status tab
    lbl_conn_status = ObjectProperty(None)
    lbl_connected_user = ObjectProperty(None)
    lbl_time_connected = ObjectProperty(None)
    lbl_time_remaining = ObjectProperty(None)
    ti_status_console = ObjectProperty(None)
    # Configuration tab
    configuration_layout = ObjectProperty(None)
    ti_nauta_user_1 = ObjectProperty(None)
    ti_nauta_user_2 = ObjectProperty(None)
    ti_nauta_user_3 = ObjectProperty(None)
    ti_nauta_pass_1 = ObjectProperty(None)
    ti_nauta_pass_2 = ObjectProperty(None)
    ti_nauta_pass_3 = ObjectProperty(None)
    ti_start_time = ObjectProperty(None)
    ti_end_time = ObjectProperty(None)
    ti_check_online_frec = ObjectProperty(None)
    ti_check_offline_frec = ObjectProperty(None)
    ti_disconn_retry_times = ObjectProperty(None)
    ti_check_ping_host = ObjectProperty(None)
    ti_router_pass = ObjectProperty(None)
    ti_router_ip = ObjectProperty(None)
    ti_router_user = ObjectProperty(None)
    sw_auto_conn = ObjectProperty(None)
    sw_force_disconnect = ObjectProperty(None)
    sw_auto_disconn = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)

        self.monitor_conn_status_thread = threading.Thread(target=self.monitor_connection_status, args=())
        self.monitor_conn_status_thread.daemon = True

        self.init_visual_objects()

    def init_visual_objects(self):
        self.disable_configuration_layout()

        self.set_config_params_from_config(self.config)

    def disable_configuration_layout(self, disabled=True):
        self.configuration_layout.disabled = disabled

    def set_config_params_from_config(self, config: Configuration):
        if config:
            # Configuration tab
            try:
                self.ti_nauta_user_1.text = config.credentials[0]['username']
                self.ti_nauta_pass_1.text = config.credentials[0]['password']
            except:
                self.print(f"Al parecer no tiene credenciales nauta configuradas. Agréguelas !!!")
                return

            try:
                self.ti_nauta_user_2.text = config.credentials[1]['username']
                self.ti_nauta_pass_2.text = config.credentials[1]['password']
            except:
                self.print(f"Usted puede agregar hasta 3 credenciales nauta")

            try:
                self.ti_nauta_user_3.text = config.credentials[2]['username']
                self.ti_nauta_pass_3.text = config.credentials[2]['password']
            except:
                pass

            self.ti_start_time.text = str(config.connection_begin_time)
            self.ti_end_time.text = str(config.connection_end_time)
            self.ti_check_online_frec.text = str(config.connection_check_frequency)
            self.ti_check_offline_frec.text = str(config.disconnection_check_frequency)
            self.ti_disconn_retry_times.text = str(config.disconnection_retry_times)
            self.ti_check_ping_host.text = str(config.check_ping_host)
            self.ti_router_pass.text = str(config.router_password)
            self.ti_router_ip.text = str(config.router_ip)
            self.ti_router_user.text = str(config.router_username)
            self.sw_force_disconnect.active = bool(config.force_connection_close)
            self.sw_auto_disconn.active = bool(config.auto_disconnect)
            self.sw_auto_conn.active = bool(config.auto_connect)

    @mainthread
    def print(self, text: str):
        self.ti_status_console.text = self.ti_status_console.text + f"{text}\n"

    @mainthread
    def clear(self):
        pass
        # self.ti_status_console.text = ''

    @mainthread
    def set_lbl_conn_status_text(self, status_text: str):
        self.lbl_conn_status.text = status_text

    def monitor_connection_status(self):
        while self.tgl_btn_active.state == "down":
            if self.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                return

            global stop_threads
            if stop_threads:
                print("stop!!!")
                raise KeyboardInterrupt

            print('init done')
            self.print_status_text()

            if self.must_be_connected():

                try:
                    if not NautaProtocol.ping(host=self.config.check_ping_host):
                        self.connect(client=self.nauta_client)
                    else:
                        sleep(self.config.connection_check_frequency_in_secs)
                except NautaPreLoginException as ex:
                    self.print(f'Error antes de iniciar la sesión: ({ex})')
                except NautaLoginException as ex:
                    self.print(f'Error iniciando sesión: ({ex})')
                except NautaException as ex:
                    self.print(f'Error de Nauta: ({ex})')
                except Exception as ex:
                    self.print(f'Error de conexión. Asegurese de estar conectado a la red ({ex})')
                except KeyboardInterrupt:
                    pass

            if not self.must_be_connected():
                connected = NautaProtocol.ping(host=self.config.check_ping_host)

                if connected:
                    for i in range(self.config.disconnection_retry_times):
                        self.print(f'Intentando desconectar ({i + 1} of {self.config.disconnection_retry_times})')

                        try:
                            if self.disconnect(client=self.nauta_client):
                                connected = NautaProtocol.ping(host=self.config.check_ping_host)
                                break
                        except NautaLogoutException as ex:
                            self.print(f'Error cerrando sesión ({ex})')
                        except NautaException as ex:
                            self.print(f'Error de Nauta ({ex})')
                        except Exception as ex:
                            self.print(f'Error de conexión. Asegurese de estar conectado a la red ({ex})')

                        sleep(10)

                    if connected and not self.must_be_connected() and self.config.force_connection_close:
                        self.print(
                            'Usted está conectado y la conexión debe ser cerrada. El router será reiniciando!!!\n')

                        try:
                            if self.router.console_restart(debug=False, timeout=10):
                                self.print('Router reiniciado satisfactoriamente')
                            else:
                                self.print('Fallo reiniciando el router')
                        except Exception as ex:
                            self.print(f"Ha ocurrido un error intentando reiniciar el router ({ex})")
                        finally:
                            self.print_status_text()
                else:
                    self.clear()
                    self.print_status_text()
                    sleep(self.config.disconnection_check_frequency_in_secs)
        else:
            # global stop_threads
            if stop_threads:
                print("stop!!!")
                raise KeyboardInterrupt


    def connect(self, client=None):

        if client:
            self.print(
                "Conectando usuario: {}".format(
                    client.user,
                )
            )

            with client.login():
                self.clear()
                self.print_status_text()

                login_time = int(time.time())
                self.print("[sesión iniciada]")
                self.print(f"Usuario: {client.user}")
                self.print("Tiempo restante: {}".format(utils.val_or_error(lambda: client.remaining_time)))
                self.print("Presione Ctrl+C para desconectarse")

                try:
                    global stop_threads
                    while True:
                        if stop_threads:
                            break

                        if not client.is_logged_in or not NautaProtocol.ping(host=self.config.check_ping_host):
                            break

                        if not self.must_be_connected():
                            break

                        elapsed = int(time.time()) - login_time

                        self.print(
                            "\rTiempo de conexion: {}.".format(
                                utils.seconds2strtime(elapsed)
                            ),
                            end=""
                        )
                        time.sleep(2)
                except KeyboardInterrupt:
                    pass
                finally:
                    self.print("\n\nCerrando sesión ...")
                    self.print("Tiempo restante: {}".format(utils.val_or_error(lambda: client.remaining_time)))

            self.print("sesión cerrada con exito.")
            self.print("Credito: {}".format(
                utils.val_or_error(lambda: client.user_credit)
            ))
            sleep(5)
            self.clear()
            self.print_status_text()
        else:
            raise NautaPreLoginException("No se especificó ningún usuario para conectar")

    def disconnect(self, client=None):
        # client = NautaClient(user=config.credentials[0]['username'], password=config.credentials[0]['password'],
        #                      default_check_page=config.check_connection_page)
        if client:
            if client.is_logged_in:
                client.load_last_session()
                client.logout(max_disconnect_attempts=self.config.disconnection_retry_times)
            #     self.print("sesión cerrada con exito")
            # else:
            #     self.print("No hay ninguna sesión activa")
            sleep(1)
            return not NautaProtocol.ping(host=self.config.check_ping_host)
        else:
            raise NautaLogoutException("No se especificó ningún usuario para desconectar")

    def is_online(self):
        online = False
        try:
            online = NautaProtocol.is_connected(ping_host=self.config.check_ping_host)
        except ConnectionRefusedError as ex:
            self.print('La conexión fue rechazada por el host remoto - ' + str(ex))
        except ConnectionResetError as ex:
            self.print('La conexión fue reiniciada por el host remoto - ' + str(ex))
        except ConnectionAbortedError as ex:
            self.print('La conexión fue abortada por el host remoto - ' + str(ex))
        except ConnectionError as ex:
            self.print('Error de conexión. Asegurese de estar conectado a una red - ' + str(ex))
        except Exception as ex:
            self.print('Ha ocurrido un error intentando determinar el estado de la conexión - ' + str(ex))
        finally:
            return online

    def must_be_connected(self):
        return is_time_between(self.config.connection_begin_time, self.config.connection_end_time)

    def enough_user_remaining_time(self, client=None, threshold=1):
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

    def print_status_text(self):
        self.print(self.RUNNING_TEXT)
        status = 'DESCONECTADO |---X---|'
        if self.is_online():
            status = 'CONECTADO |<---->|'
            self.set_lbl_conn_status_text(status_text="ONLINE")
        else:
            self.set_lbl_conn_status_text(status_text="OFFLINE")
        self.print(f'Usted esta {status}')

    def on_press_authenticate_button(self):
        if self.ti_admin_user.text == 'admin' and self.ti_admin_pass.text == 'admin':
            self.print(f"User {self.ti_admin_user.text} logged in successfully [{curr_datetime_str()}]")
            self.disable_configuration_layout(False)
        else:
            self.print(f"User {self.ti_admin_user.text} logged in failed [{curr_datetime_str()}]")

    def on_press_cancel_button(self):
        # TODO: restore changes from json
        self.disable_configuration_layout(True)
        self.print(f"Configuration change cancelled by {self.ti_admin_user.text} user [{curr_datetime_str()}]")

    def on_press_save_button(self):
        # TODO: save changes to json, reload processes
        self.disable_configuration_layout(True)
        self.print(f"Configuration changed by {self.ti_admin_user.text} user [{curr_datetime_str()}]")

    def on_press_active_toggle_button(self):
        if self.tgl_btn_active.state == "down":
            self.print(f"Monitor started [{curr_datetime_str()}]")
            # threading.Thread(target=self.monitor_connection_status, args=()).start()

            self.monitor_conn_status_thread.start()
        else:
            global stop_threads
            stop_threads = True
            self.print(f"Monitor stopped [{curr_datetime_str()}]")
            self.lbl_conn_status.text = "OFFLINE"
            return

