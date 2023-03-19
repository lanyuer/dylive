from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time, traceback
import json, re
from urllib.parse import unquote_plus, quote
from loguru import logger

class DyPage:
    """
    Client for making HTTP requests to Douyin's API
    """

    def __init__(
            self
    ):
        capabilities = DesiredCapabilities.CHROME
        # capabilities["loggingPrefs"] = {"performance": "ALL"}  # chromedriver < ~75
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # chromedriver 75+

        # 使用headless无界面浏览器模式
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless') #//增加无界面选项
        chrome_options.add_argument('--disable-gpu') #//如果不加这个选项，有时定位会出现问题
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension',False)

        self.driver = webdriver.Chrome(
            options=chrome_options,
            desired_capabilities=capabilities)


    def room_info(self, room_id: str) -> dict:
        
        """
        获取直播的流、wss链接、标题、在线人数等
        """
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',
                            {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})

        self.driver.get(f"https://live.douyin.com/{room_id}")
        time.sleep(10)
        perfs = self.driver.get_log("performance")
        
        wss_url = None
        for p in perfs:
            message = json.loads(p["message"])["message"]
            if not message["method"].startswith('Network.webSocketCreated'):
                continue
            
            logger.info(message)
            wss_url = message["params"]["url"] if message["params"]["url"].find('webcast/im/push/v2') != -1 else wss_url
        
        ttwid = [x for x in self.driver.get_cookies() if x['name'] == 'ttwid'][0]['value']
        data_string = re.findall(
            r'<script id="RENDER_DATA" type="application/json">(.*?)</script>', self.driver.page_source)[0]
        data_dict = json.loads(unquote_plus(data_string))

        room = data_dict['app']['initialState']['roomStore']['roomInfo']['room']
        #room_id = room['id_str']
        room_title = room['title']
        room_user_count = room['user_count_str']
        flv_urls = room['stream_url']['flv_pull_url']

        flv = ''
        for key in ['SD2', 'SD1', 'HD1', 'FULL_HD1']:
            if key in flv_urls:
                flv = flv_urls[key]
                break
        if not flv:
            logger.error(f"flv url miss: ROOMID={room_id}, FLVURLS={flv_urls}")

        return {
                'title': room_title,
                'user_count': room_user_count,
                'flv': flv,
                'ttwid': ttwid,
                'wss_url': wss_url,
        }
        
    def get_author_id_by_name(self, name: str):
        """
        Returns the author
        """
        #name = '抖音电商官方直播间'
        #name = '吉野家'

        url = 'https://www.douyin.com/search/' + \
            quote(name) + '?source=switch_tab&type=user'
        self.driver.get(url)

        id = False

        try:
            # buttonpath = '//*[@id="douyin-right-container"]/div[2]/div/div[3]/div[3]/ul/li[1]/div/a/div[1]/button'
            buttonpath = '//li[@class="aCTzxbOJ OPn2NCBX"][1]'
            WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((
                By.XPATH, buttonpath
            )))  # 显示等待视频标签出现
            # path = '//*[@id="douyin-right-container"]/div[2]/div/div[3]/div[3]/ul/li[1]/div'
            path = '//li[@class="aCTzxbOJ OPn2NCBX"][1]//a'
            WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((
                By.XPATH, path
            )))  # 显示等待视频标签出现
            a = self.driver.find_element(By.XPATH, path)

            matches = re.findall(r'//www.douyin.com/user/(.*?)\?',
                                 a.get_attribute('href'))

            if not matches or len(matches) < 1:
                logger.warning(f"Could not find user {name} from page")
                return False

            id = matches[0]

            logger.debug(f"Find user={name} , id={id}")
        except Exception as e:
            traceback.print_exc()
            logger.warning(f"Could not find user {name}, error: " + str(e))
            raise e
            

        return id

    def get_living_room_id(self, id: str):
        """通过作者id获取直播间url，如果没有开播返回false

        Args:
            id (str): _description_

        Returns:
            _type_: _description_
        """
        url = f'https://www.douyin.com/user/{id}'
        self.driver.get(url)
        roomid = False

        try:
            anchorpath = '//div[@class="x2yFtBWw Ll07vpAQ"]//a[1]'
            WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((
                By.XPATH, anchorpath
            )))  # 显示等待视频标签出现
            a = self.driver.find_element(By.XPATH,
                                          anchorpath)

            if not re.findall('直播中', a.text):
                raise Exception(f"User {id} Not online")

            matches = re.findall(r'https://live.douyin.com/(.*?)\?',
                                 a.get_attribute('href'))

            #if not matches or len(matches) < 1:
            #    logger.warning(f"Could not find room id {id} from page")
            #    return False

            roomid = matches[0]
            logger.debug(f"Find user={id} , roomid={roomid}")
        except Exception as e:
            logger.warning(
                f"Could not find livingroom for user:{id}")
            raise e
            
        return roomid