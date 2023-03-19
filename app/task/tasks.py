from celery import Celery, current_task
from app.client.page import DyPage
from app.client.websocket import DyWss
from loguru import logger
from app.task.config import beat_schedule
from app.task.scrapy import download_flv
from datetime import datetime
import uuid

app = Celery('tasks')
app.conf.broker_url = 'redis://localhost:6379/0'

app.conf.CELERY_ENABLE_UTC = True
app.conf.timezone = 'Asia/Shanghai'
app.conf.result_expires = 60 * 60 * 24
app.conf.beat_schedule = beat_schedule

TIME_LIMIT = 3600*23.5 # 监控时间
TIME_SCRAPY = 3600 # 真实抓取时间

from func_timeout import func_timeout, func_set_timeout, FunctionTimedOut

@func_set_timeout(TIME_SCRAPY)
def run_wss_by_time(wss_url, ttwid, file):
    wss = DyWss(wss_url, ttwid, file)
    wss.long_live_run()


@func_set_timeout(TIME_SCRAPY)
def run_download_by_time(flv, file):
    download_flv(flv, file)

@app.task(soft_time_limit=TIME_LIMIT, time_limit=TIME_LIMIT, default_retry_delay=600, max_retries=None)
def task_chat_message(name: str):
    page = DyPage()
    task_id = current_task.request.id
    id = page.get_author_id_by_name(name)
    room = page.get_living_room_id(id)
    info = page.room_info(room)
    logger.debug(f"{name} 开播信息：{info}")
    
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    try:
        run_wss_by_time(info['wss_url'], info['ttwid'], f'data/chat_{name}_{now}_{task_id}.log')
    except FunctionTimedOut:
        logger.debug(f"{name}: 已经监控一个小时，结束")
        return True
    except Exception as e:
        raise e

@app.task(soft_time_limit=TIME_LIMIT, time_limit=TIME_LIMIT, default_retry_delay=600, max_retries=None)
def task_download_flv(name: str):
    page = DyPage()
    task_id = current_task.request.id
    id = page.get_author_id_by_name(name)
    room = page.get_living_room_id(id)
    info = page.room_info(room)
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    try:
        run_download_by_time(info['flv'], f'data/flv_{name}_{now}_{task_id}.flv')
    except FunctionTimedOut:
        logger.debug(f"{name}:已经下载一个小时，结束")
        return True
    except Exception as e:
        raise e