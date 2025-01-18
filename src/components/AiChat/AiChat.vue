<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NButton, NInput, NCard, NScrollbar, NIcon, NAvatar } from 'naive-ui';
import { SendOutlined, SupportAgentOutlined, CloseOutlined, ChatOutlined } from '@vicons/material';

const API_KEY = 'AIzaSyCDj5Wg3ZOj4SXz5uiIPbewuuPd04Kp1vA';
const messages = ref<Array<{role: string, content: string}>>([]);
const inputMessage = ref('');
const isLoading = ref(false);
const chatContainer = ref(null);
const isChatOpen = ref(false);
const isThinking = ref(false);

const systemPrompt = `
你是旅遊趣網站的專業旅遊顧問。請注意以下規則：
1. 永遠使用繁體中文回覆
2. 回答範圍包括：
   - 所有與景點相關的問題（包括但不限於：海邊、山、河、湖、溫泉、瀑布、森林、公園等）
   - 台灣各地旅遊景點介紹和推薦
   - 景點的特色和最佳遊玩季節
   - 景點周邊的美食推薦
   - 如何前往景點的交通建議
   - 門票和預約相關資訊
   - 住宿推薦
   - 行程規劃建議
3. 回答特點：
   - 提供詳細的景點介紹
   - 包含實用的旅遊資訊（如開放時間、票價、交通等）
   - 根據季節和天氣給出合適的建議
   - 分享在地特色和小知識
4. 如果用戶提到任何與景點相關的關鍵字（如：海邊、山、河、湖等），一定要提供相關的旅遊建議
5. 保持專業、友善的態度
6. 回答要具體實用，可以適當舉例
`;

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return;
  
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

    await new Promise(resolve => setTimeout(resolve, 2000));

    const response = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + API_KEY, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: systemPrompt + "\n\n用戶問題：" + userMessage
          }]
        }]
      })
    });

    const data = await response.json();
    
    messages.value.pop();
    
    if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text) {
      messages.value.push({
        role: 'assistant',
        content: data.candidates[0].content.parts[0].text
      });
    }
  } catch (error) {
    console.error('Error:', error);
    messages.value.pop();
    messages.value.push({
      role: 'assistant',
      content: '抱歉，出現了一些錯誤。請稍後再試。'
    });
  } finally {
    isLoading.value = false;
    isThinking.value = false;
  }
};

const handleKeyPress = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
};

const toggleChat = () => {
  isChatOpen.value = !isChatOpen.value;
  if (isChatOpen.value && messages.value.length === 0) {
    messages.value.push({
      role: 'assistant',
      content: '您好！我是旅遊趣的旅遊顧問。我可以協助您：\n• 推薦各類景點（海邊、山、河、湖等）\n• 提供景點詳細資訊\n• 交通建議\n• 美食推薦\n• 住宿選擇\n• 行程規劃\n請問您想去哪裡玩呢？'
    });
  }
};
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
    <NCard v-else class="w-[300px] shadow-lg rounded-lg chat-window">
      <div class="flex flex-col h-[400px]">
        <!-- 标题栏 -->
        <div class="flex justify-between items-center mb-4 pb-2 border-b">
          <div class="flex items-center gap-2">
            <NAvatar>
              <NIcon>
                <SupportAgentOutlined />
              </NIcon>
            </NAvatar>
            <span class="font-medium">旅遊趣顧問</span>
          </div>
          <NButton circle quaternary @click="toggleChat">
            <template #icon>
              <NIcon>
                <CloseOutlined />
              </NIcon>
            </template>
          </NButton>
        </div>
        
        <!-- 聊天内容 -->
        <NScrollbar ref="chatContainer" class="flex-1 mb-4">
          <div class="space-y-3">
            <template v-for="(msg, index) in messages" :key="index">
              <div class="flex" :class="msg.role === 'user' ? 'justify-end' : 'justify-start'">
                <div
                  :class="[
                    'max-w-[85%] rounded-2xl p-2 px-3',
                    msg.role === 'user'
                      ? 'bg-primary text-white'
                      : msg.content === '思考中.....' 
                        ? 'bg-gray-50 text-gray-400'
                        : 'bg-gray-100 text-gray-800',
                    msg.content === '思考中.....' ? 'thinking-dots' : ''
                  ]"
                >
                  {{ msg.content }}
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