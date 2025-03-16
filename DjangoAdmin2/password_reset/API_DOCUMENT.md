# 密碼重設 API 文檔

本文檔描述了使用驗證碼重設密碼的 API 端點。

## 基本信息

- **基礎 URL**: `/password-reset/api/`
- **認證**: 不需要認證
- **響應格式**: JSON

## API 端點

### 1. 請求密碼重設

發送驗證碼到用戶的電子郵件。

- **URL**: `/password-reset/api/request/`
- **方法**: `POST`
- **請求參數**: 
  - `email` (必需): 用戶註冊的電子郵件地址

**請求示例**:

```
POST /password-reset/api/request/
Content-Type: application/x-www-form-urlencoded

email=user@example.com
```

**成功響應** (200 OK):

```json
{
  "success": true,
  "message": "驗證碼已發送到 user@example.com",
  "token": "a7e8f9c0-1b2d-3e4f-5a6b-7c8d9e0f1a2b"
}
```

**錯誤響應**:

- 404 Not Found: 電子郵件未註冊
```json
{
  "error": "此電子郵件未註冊"
}
```

- 400 Bad Request: 缺少必要參數
```json
{
  "error": "請提供電子郵件地址"
}
```

- 500 Internal Server Error: 發送郵件時出錯
```json
{
  "error": "發送驗證碼時出錯，請稍後再試"
}
```

### 2. 驗證驗證碼

驗證用戶輸入的驗證碼是否正確。

- **URL**: `/password-reset/api/verify/`
- **方法**: `POST`
- **請求參數**:
  - `token` (必需): 重設令牌
  - `code` (必需): 用戶收到的6位數驗證碼

**請求示例**:

```
POST /password-reset/api/verify/
Content-Type: application/x-www-form-urlencoded

token=a7e8f9c0-1b2d-3e4f-5a6b-7c8d9e0f1a2b&code=123456
```

**成功響應** (200 OK):

```json
{
  "success": true,
  "message": "驗證碼正確",
  "token": "a7e8f9c0-1b2d-3e4f-5a6b-7c8d9e0f1a2b"
}
```

**錯誤響應**:

- 400 Bad Request: 驗證碼不正確或令牌過期
```json
{
  "error": "驗證碼不正確"
}
```
或
```json
{
  "error": "令牌已過期"
}
```

- 404 Not Found: 無效的令牌
```json
{
  "error": "無效的令牌"
}
```

### 3. 重設密碼

設置新密碼。

- **URL**: `/password-reset/api/reset/`
- **方法**: `POST`
- **請求參數**:
  - `token` (必需): 重設令牌
  - `password` (必需): 新密碼

**請求示例**:

```
POST /password-reset/api/reset/
Content-Type: application/x-www-form-urlencoded

token=a7e8f9c0-1b2d-3e4f-5a6b-7c8d9e0f1a2b&password=new_password123
```

**成功響應** (200 OK):

```json
{
  "success": true,
  "message": "密碼重設成功"
}
```

**錯誤響應**:

- 400 Bad Request: 缺少必要參數或令牌過期
```json
{
  "error": "請提供令牌和新密碼"
}
```
或
```json
{
  "error": "令牌已過期"
}
```

- 404 Not Found: 無效的令牌
```json
{
  "error": "無效的令牌"
}
```

## 前端使用流程

1. 用戶輸入電子郵件地址，前端發送請求到 `/password-reset/api/request/`
2. 用戶收到驗證碼，輸入驗證碼，前端發送請求到 `/password-reset/api/verify/`
3. 驗證碼正確後，用戶輸入新密碼，前端發送請求到 `/password-reset/api/reset/`
4. 密碼重設成功後，引導用戶返回登入頁面

## 前端示例代碼 (Vue + Axios)

```javascript
// 使用 Axios 發送密碼重設請求
async function requestPasswordReset(email) {
  try {
    const formData = new FormData();
    formData.append('email', email);
    
    const response = await axios.post('/password-reset/api/request/', formData);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : { error: '網絡錯誤' };
  }
}

// 驗證驗證碼
async function verifyCode(token, code) {
  try {
    const formData = new FormData();
    formData.append('token', token);
    formData.append('code', code);
    
    const response = await axios.post('/password-reset/api/verify/', formData);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : { error: '網絡錯誤' };
  }
}

// 重設密碼
async function resetPassword(token, password) {
  try {
    const formData = new FormData();
    formData.append('token', token);
    formData.append('password', password);
    
    const response = await axios.post('/password-reset/api/reset/', formData);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : { error: '網絡錯誤' };
  }
}
``` 