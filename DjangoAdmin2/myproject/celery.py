import os
from celery import Celery

# 設置默認Django設置模塊
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')

# 使用字符串表示，這樣worker不用序列化配置對象
app.config_from_object('django.conf:settings', namespace='CELERY')

# 從所有已註冊的app中加載任務模塊
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 