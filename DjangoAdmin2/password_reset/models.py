from django.db import models
from django.conf import settings
import uuid
from datetime import datetime, timedelta

class PasswordResetToken(models.Model):
    """
    密碼重設令牌模型
    用於儲存使用者密碼重設的令牌
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='password_reset_tokens',
        verbose_name='用戶'
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='重設令牌')
    verification_code = models.CharField(max_length=6, null=True, blank=True, verbose_name='驗證碼')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='創建時間')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')
    
    def __str__(self):
        return f"{self.user.username} - {self.token}"
    
    @property
    def is_valid(self):
        """檢查令牌是否仍然有效"""
        # 檢查令牌是否已使用
        if self.is_used:
            return False
        
        # 檢查令牌是否過期 (1小時)
        expiry_time = self.created_at + timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT)
        return datetime.now().replace(tzinfo=self.created_at.tzinfo) <= expiry_time
    
    class Meta:
        verbose_name = '密碼重設令牌'
        verbose_name_plural = '密碼重設令牌'
        ordering = ['-created_at'] 