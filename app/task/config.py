from datetime import timedelta
from celery.schedules import crontab

# 指定消息代理的路径（和app.py中一致）


authors = [
    '小猪查理川式烤肉',
    '肯德基吃货福利社',
    '肯德基灵魂宵夜',
    '内蒙古麦当劳抖金店',
    '交个朋友直播间',
    '九田家黑牛烤肉料理',
    '吃货口袋（九田家料理烤肉专场直播）',
    '九田家料理烤肉（安徽总部）',
    'luckincoffee瑞幸咖啡',
    '瑞幸咖啡旗舰店',
]

beat_schedule = {}

for a in authors:
    
    beat_schedule[f'chat_{a}'] = {
        'task': 'app.task.tasks.task_chat_message',
        #'schedule': timedelta(seconds=120),
        'schedule': crontab(hour=13, minute=40),
        #'schedule': crontab(minute='*/60'),
        'args': (a,)
    }
    
    beat_schedule[f'flv_{a}'] = {
        'task': 'app.task.tasks.task_download_flv',
        #'schedule': timedelta(seconds=120),
        'schedule': crontab(hour=13, minute=40),
        #'schedule': crontab(minute='*/60'),
        'args': (a,)
    }
    
