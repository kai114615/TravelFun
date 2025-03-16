<script setup lang="ts">
import { ref } from 'vue';
import { NAvatar, NButton, NCard, NIcon, NInput, NScrollbar } from 'naive-ui';
import { ChatOutlined, CloseOutlined, SendOutlined, SupportAgentOutlined } from '@vicons/material';

const API_KEY = 'AIzaSyC635p-y4wQsJNce61fIe7HIIaFaF1fBOY';
const messages = ref<Array<{ role: string, content: string }>>([]);
const inputMessage = ref('');
const isLoading = ref(false);
const chatContainer = ref(null);
const isChatOpen = ref(false);
const isThinking = ref(false);
const apiTestResult = ref('');
const showDebugInfo = ref(false);

const systemPrompt = `你是旅遊趣網站的專業旅遊顧問。請使用繁體中文回覆。回答範圍包括：台灣景點介紹、交通建議、美食推薦、住宿選擇和行程規劃。回答要詳細實用，並友善專業。`;

/**
 * 帶重試功能的 fetch 請求
 * @param {string} url - API URL
 * @param {Object} options - fetch 選項
 * @param {number} maxRetries - 最大重試次數
 * @returns {Promise<Response>} - fetch 回應
 */
async function fetchWithRetry(url, options, maxRetries = 2) {
  let lastError;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      console.log(`嘗試 API 請求 (${i + 1}/${maxRetries})`);
      const response = await fetch(url, options);
      
      if (response.ok) {
        return response;
      }
      
      lastError = await response.text();
      console.warn(`嘗試 ${i + 1}/${maxRetries} 失敗: ${response.status} - ${lastError}`);
      
      // 如果是認證錯誤，不再重試
      if (response.status === 401 || response.status === 403) {
        throw new Error(`認證失敗 (${response.status}): ${lastError}`);
      }
    } catch (error) {
      lastError = error;
      console.warn(`嘗試 ${i + 1}/${maxRetries} 發生錯誤:`, error);
    }
    
    // 等待短暫時間後重試
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  throw new Error(`重試 ${maxRetries} 次後失敗: ${lastError}`);
}

async function sendMessage () {
  if (!inputMessage.value.trim() || isLoading.value)
    return

  const userMessage = inputMessage.value;
  messages.value.push({ role: 'user', content: userMessage });
  inputMessage.value = '';
  isLoading.value = true;
  isThinking.value = true;

  try {
    messages.value.push({
      role: 'assistant',
      content: '思考中.....'
    });

    await new Promise(resolve => setTimeout(resolve, 1000));

    // 打印出使用的 API Key 用於調試
    console.log('使用的 API Key:', API_KEY.substring(0, 8) + '...');
    
    // 正確的 Gemini API 格式 (2024年最新格式)
    const apiUrl = `https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=${API_KEY}`;
    
    // 準備 API 請求內容
    const requestBody = {
      contents: [
        {
          role: "user",
          parts: [
            {
              text: `${systemPrompt}\n\n用戶問題：${userMessage}`
            }
          ]
        }
      ],
      generationConfig: {
        temperature: 0.7,
        topK: 40,
        topP: 0.95,
        maxOutputTokens: 1024
      }
    };
    
    console.log('API 請求內容:', JSON.stringify(requestBody));
    
    const response = await fetchWithRetry(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    const data = await response.json();
    console.log('API 回應數據:', data);

    messages.value.pop();

    // 處理 2024年最新的 API 回應格式
    if (data.candidates && data.candidates[0]?.content?.parts) {
      const text = data.candidates[0].content.parts
        .filter(part => part.text)
        .map(part => part.text)
        .join('\n');
      
      if (text) {
        messages.value.push({
          role: 'assistant',
          content: text
        });
        return;
      }
    }
    
    // 嘗試處理其他可能的格式
    if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text) {
      messages.value.push({
        role: 'assistant',
        content: data.candidates[0].content.parts[0].text
      });
    } else if (data.candidates && data.candidates[0]?.content?.text) {
      messages.value.push({
        role: 'assistant',
        content: data.candidates[0].content.text
      });
    } else if (data.predictions && data.predictions[0]?.content) {
      messages.value.push({
        role: 'assistant',
        content: data.predictions[0].content
      });
    } else if (data.error) {
      console.error('API 錯誤響應:', data.error);
      throw new Error(`API 返回錯誤: ${data.error.message || JSON.stringify(data.error)}`);
    } else if (!data.candidates || data.candidates.length === 0) {
      console.error('API 回應無候選答案:', data);
      throw new Error('API 回應中沒有候選答案');
    } else {
      console.error('未知格式的 API 回應:', data);
      throw new Error('API 回應格式異常，無法解析回答');
    }
  } catch (error) {
    console.error('AI Chat 錯誤詳情:', error);
    let errorMessage = '系統錯誤，請稍後再試';
    
    // 分析錯誤類型以提供更明確的錯誤訊息
    if (error.message.includes('403') || error.message.includes('401')) {
      errorMessage = 'API 金鑰授權錯誤: 請確認金鑰是否有效且已啟用 Gemini API';
    } else if (error.message.includes('429')) {
      errorMessage = 'API 配額超出限制: 請稍後再試，或考慮升級 API 計劃';
    } else if (error.message.includes('404')) {
      errorMessage = 'API 端點不存在: 請確認 API 路徑是否正確';
    } else if (error.message.includes('API 回應格式異常')) {
      errorMessage = 'API 回應格式異常: 無法解析回答，可能是 API 版本變更';
    }
    
    // 嘗試使用備用 API 格式 (2024年可能的備用格式)
    try {
      console.log('嘗試使用備用 API 格式...');
      const backupRequestBody = {
        model: "gemini-pro",
        prompt: {
          text: `${systemPrompt}\n\n用戶問題：${userMessage}`
        },
        temperature: 0.7,
        maxOutputTokens: 1024,
        safetySettings: []
      };
      
      const backupResponse = await fetchWithRetry(`https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=${API_KEY}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backupRequestBody)
      });
      
      const backupData = await backupResponse.json();
      console.log('備用 API 格式回應:', backupData);
      
      if (backupData.candidates && backupData.candidates[0]?.output) {
        messages.value.pop();
        messages.value.push({
          role: 'assistant',
          content: backupData.candidates[0].output
        });
        return;
      }
      
      // 再試另一種可能的格式
      if (backupData.text) {
        messages.value.pop();
        messages.value.push({
          role: 'assistant',
          content: backupData.text
        });
        return;
      }
    } catch (backupError) {
      console.error('備用 API 格式也失敗:', backupError);
    }
    
    messages.value.pop();
    messages.value.push({
      role: 'assistant',
      content: `抱歉，出現了錯誤：${errorMessage}\n\n技術詳情：${error.message}`
    });
  } finally {
    isLoading.value = false;
    isThinking.value = false;
  }
}

async function testApiKey() {
  try {
    console.log('正在測試 API 金鑰有效性...');
    const testRequestBody = {
      contents: [
        {
          role: "user",
          parts: [
            {
              text: '你好，這是 API 金鑰測試。請回覆 "API 金鑰有效"'
            }
          ]
        }
      ]
    };
    
    const response = await fetchWithRetry(`https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=${API_KEY}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testRequestBody)
    }, 1);
    
    const data = await response.json();
    console.log('API 金鑰測試結果:', data);
    
    // 檢查多種可能的回應格式
    if (data.candidates && data.candidates[0]?.content?.parts) {
      const text = data.candidates[0].content.parts
        .filter(part => part.text)
        .map(part => part.text)
        .join('\n');
      
      if (text) {
        console.log('API 金鑰測試成功');
        return true;
      }
    }
    
    if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text) {
      console.log('API 金鑰測試成功');
      return true;
    }
    
    console.error('API 金鑰測試失敗: 回應格式不符預期', data);
    return false;
  } catch (error) {
    console.error('API 金鑰測試失敗:', error);
    return false;
  }
}

function handleKeyPress (e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function toggleChat () {
  isChatOpen.value = !isChatOpen.value;
  if (isChatOpen.value) {
    // 重置測試結果
    apiTestResult.value = '';
    
    if (messages.value.length === 0) {
      // 測試 API 金鑰
      testApiKey().then(isValid => {
        if (isValid) {
          messages.value.push({
            role: 'assistant',
            content: '您好！我是旅遊趣的旅遊顧問。我可以協助您：\n• 推薦各類景點\n• 提供景點詳細資訊\n• 交通建議\n• 美食推薦\n• 住宿選擇\n• 行程規劃\n請問您想去哪裡玩呢？'
          });
        } else {
          messages.value.push({
            role: 'assistant',
            content: '抱歉，AI 助手暫時無法使用。系統檢測到 API 金鑰可能無效或已過期，請聯絡網站管理員或點擊聊天視窗頂部的"測試 API"按鈕進行手動測試。'
          });
        }
      });
    }
  }
}

// 添加錯誤分析函數
function analyzeApiResponse(data) {
  // 檢查是否為 API 限制或錯誤
  if (data.error) {
    const errorCode = data.error.code;
    const errorMessage = data.error.message || '';
    
    console.log(`API 錯誤 (${errorCode}): ${errorMessage}`);
    
    if (errorMessage.includes('API key')) {
      return { 
        success: false, 
        errorType: 'API_KEY_ERROR', 
        message: 'API 金鑰無效或未授權' 
      };
    } else if (errorMessage.includes('quota') || errorCode === 429) {
      return { 
        success: false, 
        errorType: 'QUOTA_EXCEEDED', 
        message: 'API 配額已用盡' 
      };
    }
    
    return { 
      success: false, 
      errorType: 'API_ERROR', 
      message: errorMessage 
    };
  }
  
  // 正常回應
  return { success: true };
}

// 添加 API 測試函數
async function runApiTest() {
  apiTestResult.value = '正在測試 API 連接...';
  
  try {
    console.log('進行手動 API 測試...');
    const testRequestBody = {
      contents: [
        {
          role: "user",
          parts: [
            {
              text: '請用一句話回覆測試是否成功。'
            }
          ]
        }
      ]
    };
    
    const response = await fetch(`https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=${API_KEY}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testRequestBody)
    });
    
    const data = await response.json();
    console.log('手動 API 測試結果:', data);
    
    if (!response.ok) {
      // API 回應錯誤
      const errorMessage = data.error?.message || `錯誤代碼: ${response.status}`;
      apiTestResult.value = `❌ API 測試失敗: ${errorMessage}`;
      
      // 添加常見錯誤的解決建議
      if (response.status === 403 || data.error?.message?.includes('API key')) {
        apiTestResult.value += '\n\n可能原因: API 金鑰無效或未啟用 Gemini API。請確認金鑰是否正確，以及是否已在 Google AI Studio 啟用 Gemini API。';
      } else if (response.status === 429) {
        apiTestResult.value += '\n\n可能原因: API 配額已用盡。請等待配額重置或升級您的 API 計劃。';
      }
    } else if (data.candidates && data.candidates[0]?.content?.parts) {
      // 成功取得回應
      const text = data.candidates[0].content.parts
        .filter(part => part.text)
        .map(part => part.text)
        .join('\n');
      
      if (text) {
        apiTestResult.value = `✅ API 測試成功!\n\nAI 回應: "${text}"`;
      } else {
        apiTestResult.value = '⚠️ API 回應格式異常（無文字內容）';
      }
    } else {
      // 未知回應格式
      apiTestResult.value = '⚠️ API 回應格式異常，無法解析回答';
    }
  } catch (error) {
    console.error('手動 API 測試錯誤:', error);
    apiTestResult.value = `❌ API 測試發生錯誤: ${error.message}`;
  }
}

// 切換顯示調試信息
function toggleDebugInfo() {
  showDebugInfo.value = !showDebugInfo.value;
}
</script>

<template>
  <div class="fixed bottom-4 right-4 z-50">
    <!-- 聊天按钮 -->
    <NButton
      v-if="!isChatOpen"
      circle
      type="primary"
      size="large"
      class="shadow-lg animate-bounce"
      @click="toggleChat"
    >
      <template #icon>
        <NIcon>
          <ChatOutlined />
        </NIcon>
      </template>
    </NButton>

    <!-- 聊天窗口 -->
    <NCard v-else class="w-[350px] shadow-lg rounded-lg chat-window">
      <div class="flex flex-col h-[500px]">
        <!-- 标题栏 -->
        <div class="flex justify-between items-center mb-2 pb-2 border-b">
          <div class="flex items-center gap-2">
            <NAvatar>
              <NIcon>
                <SupportAgentOutlined />
              </NIcon>
            </NAvatar>
            <span class="font-medium">旅遊趣顧問</span>
          </div>
          <div class="flex gap-2">
            <NButton size="small" @click="runApiTest">測試 API</NButton>
            <NButton circle quaternary @click="toggleChat">
              <template #icon>
                <NIcon>
                  <CloseOutlined />
                </NIcon>
              </template>
            </NButton>
          </div>
        </div>
        
        <!-- API 測試結果 -->
        <div v-if="apiTestResult" class="mb-3 p-2 text-sm border rounded-lg" :class="{'bg-green-50 border-green-200': apiTestResult.includes('✅'), 'bg-red-50 border-red-200': apiTestResult.includes('❌'), 'bg-yellow-50 border-yellow-200': apiTestResult.includes('⚠️'), 'bg-blue-50 border-blue-200': apiTestResult.includes('正在測試')}">
          <div class="whitespace-pre-line">{{ apiTestResult }}</div>
          <div v-if="apiTestResult.includes('❌')" class="mt-2 text-xs text-gray-700">
            <p>排查建議:</p>
            <ol class="list-decimal pl-4 mt-1">
              <li>確認 API 金鑰已正確輸入 (沒有多餘空格)</li>
              <li>確認金鑰已在 <a href="https://makersuite.google.com/" target="_blank" class="text-blue-600 underline">Google AI Studio</a> 啟用</li>
              <li>確認 API 金鑰有足夠配額</li>
            </ol>
          </div>
        </div>

        <!-- 聊天内容 -->
        <NScrollbar ref="chatContainer" class="flex-1 mb-4">
          <div class="space-y-3">
            <template v-for="(msg, index) in messages" :key="index">
              <div class="flex" :class="msg.role === 'user' ? 'justify-end' : 'justify-start'">
                <div
                  class="max-w-[85%] rounded-2xl p-2 px-3" :class="[
                    msg.role === 'user'
                      ? 'bg-primary text-white'
                      : msg.content === '思考中.....'
                        ? 'bg-gray-50 text-gray-400'
                        : 'bg-gray-100 text-gray-800',
                    msg.content === '思考中.....' ? 'thinking-dots' : '',
                  ]"
                >
                  <div class="whitespace-pre-line">{{ msg.content }}</div>
                </div>
              </div>
            </template>
          </div>
        </NScrollbar>

        <!-- 输入区域 -->
        <div class="flex gap-2">
          <NInput
            v-model:value="inputMessage"
            type="textarea"
            :rows="1"
            placeholder="請輸入您的問題..."
            @keypress="handleKeyPress"
          />
          <NButton
            circle
            type="primary"
            :disabled="isLoading"
            @click="sendMessage"
          >
            <template #icon>
              <NIcon>
                <SendOutlined />
              </NIcon>
            </template>
          </NButton>
        </div>
        
        <!-- 調試信息按鈕 -->
        <div class="mt-2 text-xs text-right">
          <button @click="toggleDebugInfo" class="text-gray-400 hover:text-gray-700 transition">
            {{ showDebugInfo ? '隱藏調試信息' : '顯示調試信息' }}
          </button>
        </div>
        
        <!-- 調試信息 -->
        <div v-if="showDebugInfo" class="mt-2 text-xs text-gray-500 border-t pt-2">
          <div class="mb-1">API 金鑰: {{ API_KEY.substring(0, 8) + '...' }}</div>
          <div>API URL: generativelanguage.googleapis.com/v1/models/gemini-pro</div>
        </div>
      </div>
    </NCard>
  </div>
</template>

<style scoped>
.bg-primary {
  background-color: #18a058;
}

.chat-window {
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.animate-bounce {
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(-25%);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: translateY(0);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
}

.thinking-dots {
  position: relative;
  min-width: 60px;
}

.thinking-dots::after {
  content: '';
  animation: thinking 1.5s infinite;
}

@keyframes thinking {
  0% { content: '.'; }
  33% { content: '..'; }
  66% { content: '...'; }
  100% { content: '.'; }
}
</style>
