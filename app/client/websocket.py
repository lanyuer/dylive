from app.douyin_pb2 import PushFrame, Response, ChatMessage, LiveShoppingMessage
import requests
from websocket import WebSocketApp
import gzip
from loguru import logger
import time, traceback

class DyWss:
    def __init__(self, wss_url: str, ttwid: str, output_file: str) -> None:
        self.__wss_url = wss_url
        self.__ttwid = ttwid
        self.__output_file = open(output_file, 'w', encoding='utf-8')
    
    def long_live_run(self):
        def on_open(ws):
            pass

        def on_message(ws, content):
            try:
                frame = PushFrame()
                frame.ParseFromString(content)

                # 消息默认是compressed
                origin_bytes = gzip.decompress(frame.payload)

                response = Response()
                response.ParseFromString(origin_bytes)

                if response.needAck:
                    s = PushFrame()
                    s.payloadType = "ack"
                    s.payload = response.internalExt.encode('utf-8')
                    s.logId = frame.logId

                    ws.send(s.SerializeToString())

                info = ''
                # 获取数据内容（需根据不同method，使用不同的结构对象对 数据 进行解析）
                #   注意：此处只处理 WebcastChatMessage ，其他处理方式都是类似的。
                for item in response.messagesList:
                    if item.method == 'WebcastLiveShoppingMessage':
                        message = LiveShoppingMessage()
                        message.ParseFromString(item.payload)
                        for id in message.updatedProductIdsList:
                            info = f"##system: {id}"
                    
                    elif item.method == "WebcastChatMessage":
                        message = ChatMessage()
                        message.ParseFromString(item.payload)
                        info = f"{message.user.nickName}】{message.user.id} {message.user.gender} {message.user.Level} {message.content} "
                        info = f"[{message.user.nickName}] {message.content} "

                    if info:
                        self.__output_file.writelines("\t".join([str(int(time.time())), info]) + "\n")
                        self.__output_file.flush()
                        logger.debug(info)
                        
            except Exception as e:
                traceback.print_exc()
                logger.warning(f"On message, error: " + str(e))

                
        def on_error(ws, exception):
            logger.error(f"on_error, {ws}, {exception}")

        def on_close(ws, code, msg):
            pass
            
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Host": "webcast3-ws-web-lq.douyin.com",
            "Origin": "https://live.douyin.com",
        }

        #logger.debug(f"开始连接：ROOMID={room_id}, TITLE={room_title}, ONLINE={room_user_count}")

        ws = WebSocketApp(
            url=self.__wss_url,
            header=headers,
            cookie=f"ttwid={self.__ttwid}",
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        ws.run_forever()