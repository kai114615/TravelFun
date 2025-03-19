from django.apps import AppConfig


class ThemeEntertainmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'theme_entertainment'

    def ready(self):
        """
        在應用啟動時註冊信號處理器
        """
        # 匯入信號模組以確保信號被註冊
        import theme_entertainment.signals
