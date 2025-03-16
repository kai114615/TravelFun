import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def generate_verification_code(length=6):
    """
    生成指定長度的純數字驗證碼
    """
    return ''.join(random.choices(string.digits, k=length))

def send_verification_email(email, code, username=None):
    """
    發送包含驗證碼的電子郵件
    
    Args:
        email: 收件人電子郵件
        code: 驗證碼
        username: 收件人姓名或用戶名（可選）
    
    Returns:
        bool: 發送是否成功
    """
    subject = 'Travel Fun旅趣 - 密碼重設驗證碼'
    
    # 取得站點 URL
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    
    # 準備 HTML 內容
    html_message = render_to_string('password_reset/email_template.html', {
        'username': username or email.split('@')[0],
        'code': code,
        'validity': settings.PASSWORD_RESET_TIMEOUT // 60,  # 轉換為分鐘
        'site_name': 'Travel Fun旅趣',
        'site_url': site_url
    })
    
    # 純文字內容
    plain_message = strip_tags(html_message)
    
    # 發送郵件
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"發送電子郵件時出錯: {e}")
        return False

def create_email_template_fallback():
    """
    如果 email_template.html 不存在，則創建一個基本模板
    這個函數只在需要時調用
    """
    import os
    from django.template.loader import get_template
    
    template_dir = os.path.join(settings.BASE_DIR, 'templates', 'password_reset')
    template_path = os.path.join(template_dir, 'email_template.html')
    
    # 如果目錄不存在，創建目錄
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    # 如果模板文件不存在，創建文件
    if not os.path.exists(template_path):
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>密碼重設驗證碼</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@200;300;400;500;600;700;900&display=swap');
        
        body {
            font-family: 'Noto Serif TC', serif;
            line-height: 1.6;
            color: #2f4050;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }
        .container {
            border: 1px solid #ddd;
            border-radius: 12px;
            padding: 25px;
            background-color: #ffffff;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            background-image: url('https://img.freepik.com/free-vector/watercolor-world-map-background_52683-68651.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            position: relative;
            overflow: hidden;
        }
        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(255, 255, 255, 0.9);
            z-index: 0;
        }
        .content {
            position: relative;
            z-index: 1;
        }
        .header {
            background: linear-gradient(135deg, 
                rgba(28, 132, 198, 0.9) 0%, 
                rgba(35, 198, 200, 0.9) 100%);
            color: white;
            padding: 25px 15px;
            text-align: center;
            border-radius: 8px 8px 0 0;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }
        .header::after {
            content: '✈';
            position: absolute;
            top: 15px;
            right: 15px;
            font-size: 24px;
            opacity: 0.7;
        }
        .header::before {
            content: '🗺';
            position: absolute;
            bottom: 15px;
            left: 15px;
            font-size: 24px;
            opacity: 0.7;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            letter-spacing: 2px;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
        }
        .code {
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            padding: 20px 15px;
            margin: 30px 0;
            background: linear-gradient(to right, rgba(255,255,255,0.9), rgba(255,255,255,0.7), rgba(255,255,255,0.9));
            border-radius: 8px;
            letter-spacing: 10px;
            color: #1c84c6;
            font-family: 'Noto Serif TC', serif;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            border: 1px dashed #1c84c6;
            position: relative;
        }
        .code::before, .code::after {
            content: '🔑';
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            font-size: 18px;
        }
        .code::before {
            left: 10px;
        }
        .code::after {
            right: 10px;
        }
        .message {
            background-color: rgba(255,255,255,0.7);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .footer {
            margin-top: 30px;
            font-size: 12px;
            color: #777;
            text-align: center;
            border-top: 1px dashed #ddd;
            padding-top: 15px;
            font-family: 'Noto Serif TC', serif;
            background: linear-gradient(to right, transparent, rgba(28, 132, 198, 0.1), transparent);
            padding: 15px;
            border-radius: 0 0 8px 8px;
        }
        .highlight {
            color: #1c84c6;
            font-weight: bold;
        }
        h1, p, div {
            font-family: 'Noto Serif TC', serif;
        }
        .travel-icon {
            font-size: 16px;
            margin: 0 3px;
            vertical-align: middle;
        }
        .signature {
            text-align: center;
            margin: 25px 0;
            font-style: italic;
            color: #1c84c6;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <div class="header">
                <h1>旅途中的重要提醒 - 密碼重設</h1>
            </div>
            
            <div class="message">
                <p>親愛的 <span class="highlight">{{ username }}</span> 旅行者：</p>
                <p><span class="travel-icon">🌍</span> 我們收到了您在 Travel Fun旅趣 的帳號密碼重設請求。請使用以下驗證碼來完成您的旅程：</p>
                
                <div class="code">{{ code }}</div>
                
                <p><span class="travel-icon">⏱</span> 此驗證碼將在 <b>{{ validity }} 分鐘</b> 內有效，如同限時的旅行優惠。</p>
                <p><span class="travel-icon">🔒</span> 如果您沒有要求重設密碼，請忽略此電子郵件。您的帳號安全如常，可以繼續您的旅遊探索。</p>
            </div>
            
            <div class="signature">
                祝您旅途愉快，探索無限可能！
            </div>
            
            <p><span class="highlight">Travel Fun旅趣</span> 團隊 <span class="travel-icon">🧳</span></p>
            
            <div class="footer">
                <p>此為系統自動發送的電子郵件，請勿直接回覆。</p>
                <p>© Travel Fun旅趣 {% now "Y" %} <span class="travel-icon">🌴</span> <span class="travel-icon">🏝</span> <span class="travel-icon">🏞</span></p>
            </div>
        </div>
    </div>
</body>
</html>""") 