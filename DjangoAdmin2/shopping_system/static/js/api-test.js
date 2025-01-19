// 獲取 Token 的輔助函數
function getToken() {
    return document.cookie.replace(/(?:(?:^|.*;\s*)token\s*=\s*([^;]*).*$)|^.*$/, '$1');
}

// 獲取 CSRF Token 的輔助函數
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// API 請求處理函數
async function testApi(method) {
    console.log(`開始執行 ${method} 請求`);
    
    const apiUrl = document.getElementById('apiUrl').value;
    const productId = document.getElementById('productId').value.trim();
    const requestForm = document.getElementById('requestForm');
    const apiResponse = document.getElementById('apiResponse');
    
    try {
        // 構建請求 URL
        let url = apiUrl;
        if (productId && (method === 'GET' || method === 'PUT' || method === 'DELETE')) {
            url += productId + '/';
        }
        
        // 構建請求選項
        const options = {
            method: method,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Accept': 'application/json',
                'Authorization': `Bearer ${getToken()}`  // 添加 JWT token
            }
        };
        
        // 如果是 POST 或 PUT 請求，添加請求體
        if (method === 'POST' || method === 'PUT') {
            options.headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify({
                name: document.getElementById('name').value,
                category: document.getElementById('category').value,
                price: parseFloat(document.getElementById('price').value),
                stock: parseInt(document.getElementById('stock').value),
                description: document.getElementById('description').value,
                is_active: document.getElementById('is_active').checked
            });
        }
        
        console.log(`發送請求到: ${url}`);
        console.log('請求選項:', options);  // 添加日誌
        
        const response = await fetch(url, options);
        const contentType = response.headers.get('content-type');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            apiResponse.textContent = JSON.stringify(data, null, 2);
        } else {
            const text = await response.text();
            apiResponse.textContent = text;
        }
        
        console.log(`請求完成，狀態碼: ${response.status}`);
    } catch (error) {
        console.error('API 請求出錯:', error);
        apiResponse.textContent = `錯誤: ${error.message}`;
        
        // 如果是認證錯誤，提示用戶重新登入
        if (error.message.includes('401')) {
            alert('認證已過期，請重新登入');
            window.location.href = '/login/';
        }
    }
}

// 更新完整 URL 顯示
function updateFullUrl() {
    const baseUrl = window.location.origin;
    const apiUrl = document.getElementById('apiUrl').value;
    const productId = document.getElementById('productId').value.trim();
    const fullUrlElement = document.getElementById('fullUrl');
    
    let fullUrl = baseUrl + apiUrl;
    if (productId) {
        fullUrl += productId + '/';
    }
    
    fullUrlElement.textContent = fullUrl;
}

// 初始化函數
export function initializeApiTest() {
    console.log('初始化 API 測試頁面');
    
    // 檢查是否已登入
    const token = getToken();
    if (!token) {
        alert('請先登入');
        window.location.href = '/login/';
        return;
    }
    
    // 初始化剪貼簿功能
    new ClipboardJS('#copyUrl');
    
    // 綁定按鈕點擊事件
    const buttons = document.querySelectorAll('[data-method]');
    buttons.forEach(button => {
        button.addEventListener('click', (e) => {
            const method = e.target.dataset.method;
            const requestForm = document.getElementById('requestForm');
            
            // 顯示/隱藏請求表單
            requestForm.style.display = 
                (method === 'POST' || method === 'PUT') ? 'block' : 'none';
            
            testApi(method);
        });
    });
    
    // 監聽產品 ID 輸入變化
    const productIdInput = document.getElementById('productId');
    productIdInput.addEventListener('input', updateFullUrl);
    
    // 初始顯示完整 URL
    updateFullUrl();
    
    console.log('API 測試頁面初始化完成');
} 