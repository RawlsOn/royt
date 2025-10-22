from django.conf import settings

import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models import QuerySet

import common.util.datetime_util as datetime_util
import common.util.str_util as str_util
from common.util.logger import RoLogger
logger = RoLogger()
from argparse import Namespace
from bs4 import BeautifulSoup
from django.apps import apps

import rawarticle.models as rawarticle_models
import core.models as core_models

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
# import chromedriver_autoinstaller
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller as chromedriver

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

class ArticleHtmlGetter(object):

    def __init__(self, args={}):
        self.args = args
        print('prepare selenium')
        chromedriver.install()
        options = Options()
        options.add_argument('--headless=new')
        # driver = webdriver.Chrome(
        #     service=Service(ChromeDriverManager().install()),
        #     options= options
        # )
        # driver = webdriver.Chrome(
        #     service=Service(ChromeDriverManager(version='114.0.5735.90').install()),
        #     options= options
        # )
        self.driver = webdriver.Chrome(options= options)

    def run(self, article_id):
        driver = self.driver
        target_url = 'https://m.land.naver.com/article/info/' + article_id + '?newMobile'
        print('target_url', target_url)
        driver.get(target_url)
        page_source = driver.page_source
        with open(f'{article_id}_page_source.html', 'w') as f:
            f.write(page_source)

        delay = 2
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print('wait ' + str(delay) + ' seconds')
        time.sleep(delay)
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'detail_facilities')))
        html = driver.find_element(By.CLASS_NAME, 'wrap_detail')
        real = html.get_attribute('innerHTML')

        with open(f'{article_id}_real.html', 'w') as f:
            f.write(real)

        return real

