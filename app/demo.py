from app.client.page import DyPage
from app.client.websocket import DyWss
from loguru import logger

if __name__ == '__main__':
    name = '李宁官方直播间'
    page = DyPage()
    id = page.get_author_id_by_name(name)
    room = page.get_living_room_id(id)
    info = page.room_info(room)
    logger.debug(info)
    #wss = DyWss(info['wss_url'], info['ttwid'], 'output.log')
    #wss.long_live_run()
    