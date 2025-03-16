from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .forms import PasswordResetRequestForm, VerificationCodeForm, SetPasswordForm
from .models import PasswordResetToken
from .utils import generate_verification_code, send_verification_email, create_email_template_fallback

User = get_user_model()

@require_http_methods(["GET", "POST"])
def password_reset_request(request):
    """
    處理密碼重設請求
    顯示密碼重設表單，接收電子郵件地址，發送驗證碼
    """
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            
            # 生成驗證碼
            code = generate_verification_code()
            
            # 創建密碼重設令牌
            reset_token = PasswordResetToken.objects.create(user=user)
            
            # 將驗證碼存儲在會話中，與令牌相關聯
            request.session[f'reset_code_{reset_token.token}'] = code
            request.session[f'reset_email_{reset_token.token}'] = email
            
            # 嘗試創建電子郵件模板（如果不存在）
            create_email_template_fallback()
            
            # 發送驗證碼
            success = send_verification_email(email, code, user.username)
            
            if success:
                messages.success(request, f'驗證碼已發送到 {email}。請檢查您的收件箱。')
                return redirect(reverse('password_reset_verify') + f'?token={reset_token.token}')
            else:
                messages.error(request, '發送驗證碼時出錯，請稍後再試。')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'password_reset/request.html', {'form': form})

@require_http_methods(["GET", "POST"])
def password_reset_verify(request):
    """
    驗證使用者輸入的驗證碼
    """
    token_uuid = request.GET.get('token')
    if not token_uuid:
        messages.error(request, '無效的請求。')
        return redirect('password_reset_request')
    
    try:
        token = PasswordResetToken.objects.get(token=token_uuid, is_used=False)
        if not token.is_valid:
            messages.error(request, '重設連結已過期，請重新申請。')
            return redirect('password_reset_request')
    except PasswordResetToken.DoesNotExist:
        messages.error(request, '無效的重設令牌。')
        return redirect('password_reset_request')
    
    if request.method == 'POST':
        form = VerificationCodeForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['code']
            stored_code = request.session.get(f'reset_code_{token_uuid}')
            
            if stored_code and entered_code == stored_code:
                return redirect(reverse('password_reset_confirm') + f'?token={token_uuid}')
            else:
                messages.error(request, '驗證碼不正確，請重新輸入。')
    else:
        form = VerificationCodeForm()
    
    return render(request, 'password_reset/verify.html', {
        'form': form,
        'token': token_uuid
    })

@require_http_methods(["GET", "POST"])
def password_reset_confirm(request):
    """
    確認密碼重設，設置新密碼
    """
    token_uuid = request.GET.get('token')
    if not token_uuid:
        messages.error(request, '無效的請求。')
        return redirect('password_reset_request')
    
    try:
        token = PasswordResetToken.objects.get(token=token_uuid, is_used=False)
        if not token.is_valid:
            messages.error(request, '重設連結已過期，請重新申請。')
            return redirect('password_reset_request')
    except PasswordResetToken.DoesNotExist:
        messages.error(request, '無效的重設令牌。')
        return redirect('password_reset_request')
    
    stored_email = request.session.get(f'reset_email_{token_uuid}')
    if not stored_email:
        messages.error(request, '會話已過期，請重新申請密碼重設。')
        return redirect('password_reset_request')
    
    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password1']
            
            # 重設密碼
            user = token.user
            user.set_password(password)
            user.save()
            
            # 標記令牌為已使用
            token.is_used = True
            token.save()
            
            # 清除會話數據
            if f'reset_code_{token_uuid}' in request.session:
                del request.session[f'reset_code_{token_uuid}']
            if f'reset_email_{token_uuid}' in request.session:
                del request.session[f'reset_email_{token_uuid}']
            
            messages.success(request, '密碼重設成功！您現在可以使用新密碼登入。')
            return redirect('login')  # 假設 'login' 是您的登入頁面名稱
    else:
        form = SetPasswordForm()
    
    return render(request, 'password_reset/confirm.html', {'form': form})

@csrf_exempt
def password_reset_request_api(request):
    """
    API 接口: 處理密碼重設請求
    """
    if request.method != 'POST':
        return JsonResponse({'error': '僅接受 POST 請求'}, status=405)
    
    email = request.POST.get('email')
    if not email:
        return JsonResponse({'error': '請提供電子郵件地址'}, status=400)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'error': '此電子郵件未註冊'}, status=404)
    
    # 生成驗證碼
    code = generate_verification_code()
    
    # 創建密碼重設令牌並存儲驗證碼
    reset_token = PasswordResetToken.objects.create(
        user=user,
        verification_code=code  # 直接將驗證碼存儲在數據庫中
    )
    
    # 嘗試創建電子郵件模板（如果不存在）
    create_email_template_fallback()
    
    # 發送驗證碼
    success = send_verification_email(email, code, user.username)
    
    if success:
        return JsonResponse({
            'success': True,
            'message': f'驗證碼已發送到 {email}',
            'token': str(reset_token.token)
        })
    else:
        # 發送失敗時，刪除剛創建的令牌
        reset_token.delete()
        return JsonResponse({
            'error': '發送驗證碼時出錯，請稍後再試'
        }, status=500)

@csrf_exempt
def verify_code_api(request):
    """
    API 接口: 驗證驗證碼
    """
    if request.method != 'POST':
        return JsonResponse({'error': '僅接受 POST 請求'}, status=405)
    
    token_uuid = request.POST.get('token')
    code = request.POST.get('code')
    
    if not token_uuid or not code:
        return JsonResponse({'error': '請提供令牌和驗證碼'}, status=400)
    
    try:
        # 查詢並獲取 token 記錄
        token = PasswordResetToken.objects.get(token=token_uuid, is_used=False)
        
        # 檢查令牌是否有效
        if not token.is_valid:
            return JsonResponse({'error': '令牌已過期'}, status=400)
        
        # 檢查驗證碼是否匹配
        if token.verification_code != code:
            return JsonResponse({'error': '驗證碼不正確'}, status=400)
            
    except PasswordResetToken.DoesNotExist:
        return JsonResponse({'error': '無效的令牌'}, status=404)
    
    return JsonResponse({
        'success': True,
        'message': '驗證碼正確',
        'token': token_uuid
    })

@csrf_exempt
def reset_password_api(request):
    """
    API 接口: 重設密碼
    """
    if request.method != 'POST':
        return JsonResponse({'error': '僅接受 POST 請求'}, status=405)
    
    token_uuid = request.POST.get('token')
    password = request.POST.get('password')
    
    if not token_uuid or not password:
        return JsonResponse({'error': '請提供令牌和新密碼'}, status=400)
    
    try:
        token = PasswordResetToken.objects.get(token=token_uuid, is_used=False)
        if not token.is_valid:
            return JsonResponse({'error': '令牌已過期'}, status=400)
    except PasswordResetToken.DoesNotExist:
        return JsonResponse({'error': '無效的令牌'}, status=404)
    
    # 重設密碼
    user = token.user
    user.set_password(password)
    user.save()
    
    # 標記令牌為已使用
    token.is_used = True
    token.save()
    
    return JsonResponse({
        'success': True,
        'message': '密碼重設成功'
    }) 