from utils import ping
from ipaddress import ip_address
from utils import ping
from time import sleep
from telnetlib import Telnet

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# modelo del router tplink td-w8961n


class Router:
    """
    Router class implementation for router control automation
    """
    # Global variables
    # Web ralated vars
    CHROMIUM_BINARY_PATH = '.\\chromedriver\\chromedriver.exe'
    HEADLESS_BROWSING = True
    LOGIN_URL = '/rpSys.html'
    XPATH_LOGIN_USERNAME_LOCATOR = '/html/body/form/table/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr[2]/td[2]/input'
    XPATH_LOGIN_PASSWORD_LOCATOR = '/html/body/form/table/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr[4]/td[2]/input'
    XPATH_LOGIN_BUTTON_LOCATOR = '/html/body/form/table/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr[5]/td/input'
    XPATH_MAINTENANCE_SHEET_LOCATOR = '/html/body/div/table/tbody/tr/td[2]/table[1]/tbody/tr/td[5]'
    XPATH_RESTART_BUTTON_LOCATOR = '/html/body/div/table/tbody/tr/td[2]/table[3]/tbody/tr/td[7]/a'
    # Console
    CONSOLE_USERNAME_TEXT = 'Username:'
    CONSOLE_PASSWORD_TEXT = 'Password:'
    CONSOLE_SUCCESS_SHELL_TEXT = '>'
    CONSOLE_TERMINAL_TYPE = 'vt100'
    CONSOLE_RESTART_COMMAND = 'sys restart'
    CONSOLE_RESTART_CONFIRMATION_TEXT = 'System will reboot! Continue?[Y/N]:'
    CONSOLE_RESTART_CONFIRMATION_COMMAND = ''

    def __init__(self, ip_address='', username='', password='', vendor='TP-LINK', model='TD-W8961N'):
        self.web_driver = self.get_web_driver()
        self.ip_address = ip_address  # '192.168.0.1'
        self.username = username  # 'admin'
        self.password = password  # 'Momi@1234'
        self.vendor = vendor
        self.model = model

    @staticmethod
    def get_web_driver(headless=HEADLESS_BROWSING, chromium_binary_path=CHROMIUM_BINARY_PATH, options=None):
        if not options:
            # OBFUSCATE SELENIUM CLIENT
            options = webdriver.ChromeOptions()
            # Removes navigator.webdriver flag
            # For older ChromeDriver under version 79.0.3945.16
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            # For ChromeDriver version 79.0.3945.16 or over
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument("start-maximized")
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/74.0.3729.169 Safari/537.36")
            options.headless = headless

        # Open Browser
        driver = webdriver.Chrome(executable_path=chromium_binary_path, options=options)
        driver.set_page_load_timeout(500)
        # driver.implicitly_wait(0.5)

        return driver

    def ping(self):
        return ping(self.ip_address)

    def web_restart(self, debug=False):
        if self.model in ['TD-W8961N']:
            self.web_driver.get('http:/' + self.ip_address + self.LOGIN_URL)
            sleep(3)

            # username
            print('Writing username...') if debug else None
            self.web_driver.find_element_by_xpath(self.XPATH_LOGIN_USERNAME_LOCATOR).send_keys(self.username)

            # passwd
            print('Writing password...') if debug else None
            self.web_driver.find_element_by_xpath(self.XPATH_LOGIN_PASSWORD_LOCATOR).send_keys(self.password)

            # login button click
            print('Clicking login button...') if debug else None
            self.web_driver.find_element_by_xpath(self.XPATH_LOGIN_BUTTON_LOCATOR).click()
            sleep(2)

            # maintain sheet
            # seq = web_driver.find_elements_by_tag_name('frame')
            # print("No of frames present in the web page are: ", len(seq))
            print('Changing to navigation iframe...') if debug else None
            iframe = self.web_driver.find_element_by_name('navigation')

            # change to naviation iframe
            print('Changing to maintenance iframe...') if debug else None
            self.web_driver.switch_to.frame(iframe)
            sleep(1)
            print('Clicking maintenance sheet...') if debug else None
            self.web_driver.find_element_by_xpath(self.XPATH_MAINTENANCE_SHEET_LOCATOR).click()
            # sysrestart
            sleep(2)
            self.web_driver.find_element_by_xpath(self.XPATH_RESTART_BUTTON_LOCATOR).click()

        sleep(5)
        return not self.ping()

    def console_restart(self, debug=False):
        if self.model in ['TD-W8961N']:
            telnet = Telnet()
            telnet.open(self.ip_address)

            print("waiting username ask") if debug else None
            # telnet.read_until(b"Username:")
            telnet.read_until(bytes(self.CONSOLE_USERNAME_TEXT))
            print("sending username") if debug else None
            telnet.write(self.username.encode('ascii'))

            print("waiting password ask") if debug else None
            # telnet.read_until(b"Password:")
            telnet.read_until(bytes(self.CONSOLE_PASSWORD_TEXT))
            print("sending password") if debug else None
            telnet.write(self.password.encode('ascii'))

            print("waiting loggin success") if debug else None
            # telnet.read_until(b">")
            telnet.read_until(bytes(self.CONSOLE_SUCCESS_SHELL_TEXT))
            print("login successfull") if debug else None
            sleep(1)

            print("setting terminal type to vt100") if debug else None
            # telnet.write("vt100\n".encode('ascii'))
            telnet.write(bytes(self.CONSOLE_TERMINAL_TYPE)+"\n".encode('ascii'))

            # try logout
            try:
                print("Sending restart command")
                # telnet.write("sys restart\n".encode('ascii'))
                telnet.write(bytes(self.CONSOLE_RESTART_COMMAND) + "\n".encode('ascii'))

                # telnet.read_until(b'System will reboot! Continue?[Y/N]:')
                telnet.read_until(bytes(self.CONSOLE_RESTART_CONFIRMATION_TEXT))
                # telnet.write(b"Y\n")
                telnet.write(self.CONSOLE_RESTART_CONFIRMATION_COMMAND.encode('ascii') + "\n".encode('ascii'))
                sleep(3)

                while True:
                    message = telnet.read_until(b'\n', timeout=0.2)
                    if message == b'':
                        break
                    print(message)
            except EOFError:
                print("Connection closed") if debug else None
            finally:
                telnet.close()

        sleep(5)
        return not self.ping()

