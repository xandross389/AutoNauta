import json
import os

DEFAULT_CONFIG_FILENAME = './config.json'


class ConfigurationException(Exception):
    pass


class CredentialsDictException(ConfigurationException):
    pass


class Configuration:
    def __init__(self, check_conn_page='http://www.google.com.cu/', conn_check_freq=30,                 
                 router_ip='192.168.1.1', router_username='admin', router_password='admin', check_ping_host='8.8.8.8'):
        self._credentials = list()
        self._router_ip = router_ip
        self._router_username = router_username
        self._router_password = router_password
        self._check_connection_page = check_conn_page
        self._check_ping_host = check_ping_host
        # self._connection_begin_time = conn_begin_time
        # self._connection_end_time = conn_end_time
        # self._force_connection_close = force_connection_close  # restarts router if True
        self._connection_check_frequency = conn_check_freq  # frequency in minutes
        # self._disconnection_check_frequency = disconn_check_freq  # frequency in minutes
        # self._disconnection_retry_times = disconnection_retry_times

    def update_credentials(self, credentials):
        """
        Updates password if finds the username or adds new credentials to dictionary list if not exists
        :param credentials: credentials dictionary with username and password like {'username': "user1@nauta.com.cu", 'password': "userpass"}
        :return: updated credentials dictionary list
        """
        if len(credentials) == 2 and 'username' in credentials.keys() and 'password' in credentials.keys():
            for i in range(len(self._credentials)):
                if self._credentials[i]['username'] == credentials['username']:
                    self._credentials[i]['password'] = credentials['password']
                    return self._credentials

            self._credentials.append(credentials)
            return self._credentials
        else:
            raise CredentialsDictException("Credentials dict must contains username and password keys only")

    def delete_credentials(self, credentials):
        """
        Deletes credentials from dictionary list (match username and password is needed)
        :param credentials: credentials dictionary with username and password
        like {'username': "user1@nauta.com.cu", 'password': "user1pass"} to delete
        :return: updated credentials dictionary list
        """
        if len(credentials) == 2 and 'username' in credentials.keys() and 'password' in credentials.keys():
            for i in range(len(self._credentials)):
                if self._credentials[i]['username'] == credentials['username'] and self._credentials[i]['password'] == credentials['password']:
                    del self._credentials[i]
            return self._credentials
        else:
            raise CredentialsDictException("Credentials dict must contains username and password keys only")

    @property
    def credentials(self):
        return self._credentials

    # @property
    # def connection_begin_time(self):
    #     return self._connection_begin_time

    # @property
    # def connection_end_time(self):
    #     return self._connection_end_time

    @property
    def connection_check_frequency(self):
        return self._connection_check_frequency

    @property
    def connection_check_frequency_in_secs(self):
        return self.connection_check_frequency * 60

    # @property
    # def disconnection_check_frequency(self):
    #     return self._disconnection_check_frequency

    # @property
    # def disconnection_check_frequency_in_secs(self):
    #     return self.disconnection_check_frequency * 60

    @property
    def router_ip(self):
        return self._router_ip

    @property
    def router_username(self):
        return self._router_username

    @property
    def router_password(self):
        return self._router_password

    @property
    def check_connection_page(self):
        return self._check_connection_page

    @property
    def check_ping_host(self):
        return self._check_ping_host

    # @property
    # def force_connection_close(self):
    #     return self._force_connection_close

    # @property
    # def disconnection_retry_times(self):
    #     return self._disconnection_retry_times

    @credentials.setter
    def credentials(self, credentials):
        self._credentials = credentials

    @router_ip.setter
    def router_ip(self, value):
        self._router_ip = value

    @router_username.setter
    def router_username(self, value):
        self._router_username = value

    @router_password.setter
    def router_password(self, value):
        self._router_password = value

    @check_ping_host.setter
    def check_ping_host(self, value):
        self._check_ping_host = value

    # @connection_begin_time.setter
    # def connection_begin_time(self, value):
    #     self._connection_begin_time = value

    # @connection_end_time.setter
    # def connection_end_time(self, value):
    #     self._connection_end_time = value

    # @force_connection_close.setter
    # def force_connection_close(self, value):
    #     self._force_connection_close = value

    # @disconnection_retry_times.setter
    # def disconnection_retry_times(self, value):
    #     self._disconnection_retry_times = value

    # @disconnection_check_frequency.setter
    # def disconnection_check_frequency(self, value):
    #     self._disconnection_check_frequency = value

    @check_connection_page.setter
    def check_connection_page(self, value):
        self._check_connection_page = value

    @connection_check_frequency.setter
    def connection_check_frequency(self, value):
        self._connection_check_frequency = value


class ConfigurationManager:
    def __init__(self, config_file=DEFAULT_CONFIG_FILENAME):
        self._config_file = config_file
        self._config = Configuration()

    def config(self):
        return self._config

    def create_default_configuration_file(self):
        config = {
            'credentials': [
                {'username': "", 'password': ""},
            ],
            'router_ip': self._config.router_ip,
            'router_username': self._config.router_username,
            'router_password': self._config.router_password,
            'check_connection_page': self._config.check_connection_page,
            'check_ping_host': self._config.check_ping_host,
            # 'connection_begin_time': self._config.connection_begin_time,
            # 'connection_end_time': self._config.connection_end_time,
            # 'force_connection_close': self._config.force_connection_close,
            'connection_check_frequency': self._config.connection_check_frequency,
            # 'disconnection_check_frequency': self._config.disconnection_check_frequency,
            # 'disconnection_retry_times': self._config.disconnection_retry_times
        }

        with open(self._config_file, 'w') as outfile:
            json.dump(config, outfile, sort_keys=True, indent=4)

    def load_configuration(self):
        if not os.path.isfile(self._config_file):
            self.create_default_configuration_file()

        try:
            with open(self._config_file, "r") as read_file:
                config_string = json.load(read_file)

                try:
                    self._config.credentials = config_string['credentials']
                    self._config.router_ip = config_string['router_ip']
                    self._config.router_username = config_string['router_username']
                    self._config.router_password = config_string['router_password']
                    self._config.check_connection_page = config_string['check_connection_page']
                    self._config.check_ping_host = config_string['check_ping_host']
                    # self._config.connection_begin_time = config_string['connection_begin_time']
                    # self._config.connection_end_time = config_string['connection_end_time']
                    # self._config.force_connection_close = config_string['force_connection_close']
                    self._config.connection_check_frequency = config_string['connection_check_frequency']
                    # self._config.disconnection_check_frequency = config_string['disconnection_check_frequency']
                    # self._config.disconnection_retry_times = config_string['disconnection_retry_times']
                except Exception as assign_error:
                    print('Error assigning json field - ' + str(assign_error))
        except Exception as file_err:
            print('Err loading json from file - ' + str(file_err))
        finally:
            read_file.close()
            return self._config

    def get_config(self, config_file=DEFAULT_CONFIG_FILENAME):
        self._config_file = config_file

        return self.load_configuration()


