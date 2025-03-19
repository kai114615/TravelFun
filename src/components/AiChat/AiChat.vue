<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue';
import { NAvatar, NButton, NCard, NIcon, NInput, NScrollbar } from 'naive-ui';
import { ChatOutlined, CloseOutlined, SendOutlined, SupportAgentOutlined } from '@vicons/material';
import axios from 'axios';

// 類型定義
interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ApiResponse {
  candidates?: Array<{
    content?: {
      parts?: Array<{ text?: string }>;
      text?: string;
    };
    output?: string;
  }>;
  predictions?: Array<{ content?: string }>;
  text?: string;
  error?: { code?: number; message?: string };
}

interface ApiErrorResult {
  success: boolean;
  errorType?: string;
  message?: string;
}

// 變數設定
const API_KEY = 'AIzaSyDA_p2JzWp-CluDxjSFd9cP393FHEGmhKs';
const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${API_KEY}`;
const MAX_RETRIES = 2;
const MAX_OUTPUT_TOKENS = 1024;
const BASE_SYSTEM_PROMPT = `你是旅遊趣網站的專業旅遊顧問。請使用繁體中文回覆。回答範圍包括：全臺景點與活動介紹、交通建議和行程規劃。回答要清楚且實用，友善並專業。優先推薦正在進行或即將開始的活動，除非用戶明確詢問，否則避免推薦已結束或未知的活動。`;
let SYSTEM_PROMPT = BASE_SYSTEM_PROMPT;

// UI 狀態變數
const messages = ref<Message[]>([]);
const inputMessage = ref('');
const isLoading = ref(false);
const chatContainer = ref(null);
const isChatOpen = ref(false);
const isThinking = ref(false);
const apiTestResult = ref('');
const showDebugInfo = ref(false);
const localTravelData = ref<any>(null);
const hasRanApiTest = false; // 追蹤是否已執行API測試
const isInitialized = ref(false);
const entertainmentData = ref<any>(null);

/**
 * 帶重試功能的 fetch 請求
 */
async function fetchWithRetry(
  url: string,
  options: RequestInit,
  maxRetries: number = MAX_RETRIES
): Promise<Response> {
  let lastError: unknown;

  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);
      if (response.ok) return response;

      lastError = await response.text();

      // 驗證錯誤不再重試
      if (response.status === 401 || response.status === 403) {
        throw new Error(`驗證失敗 (${response.status}): ${lastError}`);
      }
    } catch (error) {
      lastError = error;
    }
    // 短暫等待後重試
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  throw new Error(`重試 ${maxRetries} 次後失敗: ${lastError}`);
}

/**
 * 從主題育樂資料庫獲取資料
 */
async function fetchEntertainmentData(query: string): Promise<any> {
  try {
    // 使用環境變數或預設值
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const apiUrl = `${baseUrl}/theme_entertainment/api/entertainment-data-for-ai/`;

    console.log(`正在請求主題育樂資料: ${apiUrl}, query=${query}`);

    const response = await axios.get(apiUrl, {
      params: { q: query, limit: 10 }
    });

    if (response.data) {
      console.log('獲取主題育樂資料成功:', response.data);

      // 記錄數據概述
      const categories = response.data;
      const counts: { [key: string]: number } = {};

      Object.entries(categories).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          counts[key] = value.length;
        }
      });

      console.log('資料分類統計:', counts);
    } else {
      console.log('API 回應成功但沒有資料');
    }

    return response.data;
  } catch (error: any) {
    console.error('獲取主題育樂資料失敗:', error);
    if (error.response) {
      console.error('錯誤狀態碼:', error.response.status);
      console.error('錯誤資訊:', error.response.data);
    } else if (error.request) {
      console.error('未收到回應:', error.request);
    } else {
      console.error('錯誤信息:', error.message);
    }
    return null;
  }
}

/**
 * 將主題育樂資料格式化為文字提示
 */
function formatEntertainmentData(data: any): string {
  if (!data) {
    console.log('沒有主題育樂資料可格式化');
    return '';
  }

  console.log('正在格式化主題育樂資料:', data);

  let formattedData = '【主題育樂資料庫】\n\n';
  let totalItems = 0;

  // 整合資料類別
  const categories = {
    '特色活動': data.activities || [],
    '只限今日': data.today_only_activities || [],
    '即將結束': data.ending_soon_activities || [],
    '進行中': data.ongoing_activities || [],
    '即將開始': data.upcoming_activities || [],
    '未開始': data.not_started_activities || [],
    '已結束': data.ended_activities || [],
    '運動活動': data.sports || [],
    '宗教活動': data.religions || [],
    '表演活動': data.shows || [],
    '藝術展覽': data.arts || [],
    '電影活動': data.cinemas || []
  };

  // 計算資料總量
  Object.values(categories).forEach(items => {
    totalItems += items.length;
  });

  if (totalItems === 0) {
    console.log('主題育樂資料為空');
    return '';
  }

  console.log(`找到 ${totalItems} 筆相關資料`);

  // 建立概覽摘要
  formattedData += `找到 ${totalItems} 筆相關資料，分類如下：\n\n`;
  const categorySummary = Object.entries(categories)
    .filter(([_, items]) => items.length > 0)
    .map(([category, items]) => `${category}(${items.length}筆)`);

  formattedData += `資料分類：${categorySummary.join('、')}\n\n`;

  // 格式化每個類別的資料
  for (const [category, items] of Object.entries(categories)) {
    if (items.length > 0) {
      formattedData += `=== ${category} ===\n`;

      items.forEach((item: any, index: number) => {
        formattedData += `[${index + 1}] ${item.activity_name || "無標題"}\n`;

        // 時間資訊
        if (item.start_date || item.end_date) {
          let timeInfo = '  時間: ';
          if (item.start_date) timeInfo += `${item.start_date}`;
          if (item.start_date && item.end_date) timeInfo += ' 至 ';
          if (item.end_date) timeInfo += `${item.end_date}`;
          formattedData += `${timeInfo}\n`;
        }

        // 各種詳細資訊
        if (item.location) formattedData += `  地點: ${item.location}\n`;
        if (item.ticket_price) formattedData += `  票價: ${item.ticket_price}\n`;

        // 處理描述 - 提取關鍵資訊
        if (item.description) {
          let desc = extractImportantInfo(item.description);
          formattedData += `  簡介: ${desc}\n`;
        }

        // 地址
        if (item.address && item.address !== '無資料') {
          formattedData += `  地址: ${item.address}\n`;
        }

        formattedData += '\n';
      });
    }
  }

  // 回答指引
  formattedData += "回答指引：\n";
  formattedData += "1. 優先使用上述資料回答用戶問題\n";
  formattedData += "2. 特別注意「只限今日」、「進行中」、「即將結束」和「即將開始」等分類，提供最相關的時間建議\n";
  formattedData += "3. 根據地點、經緯度、地址提供附近景點的建議\n";
  formattedData += "4. 除非用戶明確詢問，否則不要推薦「已結束」或「未知」的活動\n";
  formattedData += "5. 如果用戶提問的內容不在上述資料中，可補充其他你知道的資訊\n";
  formattedData += "6. 回答時先直接回應用戶問題，再提供相關資訊和建議\n";

  return formattedData;
}

/**
 * 提取文本中的重要資訊
 */
function extractImportantInfo(description: string): string {
  if (description.length <= 120) return description;

  // 重要標記關鍵詞
  const keyPhrases = ["特色", "推薦", "適合", "著名", "知名", "必去", "值得", "特點", "亮點"];
  const sentences = description.split(/[。！？.!?]/);

  // 尋找關鍵句
  let extractedSentences: string[] = [];
  for (const phrase of keyPhrases) {
    const matchingSentences = sentences.filter(s => s && typeof s === 'string' && s.includes(phrase));
    extractedSentences = extractedSentences.concat(matchingSentences);
    if (extractedSentences.length >= 2) break;
  }

  // 若無關鍵句，取前兩句
  if (extractedSentences.length === 0) {
    extractedSentences = sentences.slice(0, 2).filter(s => typeof s === 'string');
  }

  // 組合並截斷
  let result = extractedSentences.join("。");
  if (result.length > 120) {
    result = result.substring(0, 120) + "...";
  }

  return result + "。";
}

/**
 * 更新系統提示以提供更好的回應
 */
function updateSystemPrompt(userMessage: string): string {
  // 重置為基本提示詞
  let updatedPrompt = BASE_SYSTEM_PROMPT;

  console.log('更新系統提示詞，entertainmentData:', entertainmentData.value);

  if (entertainmentData.value) {
    const formattedData = formatEntertainmentData(entertainmentData.value);
    if (formattedData) {
      console.log('添加主題育樂資料到提示詞');
      updatedPrompt += '\n\n' + formattedData;
    } else {
      console.log('主題育樂資料格式化後為空');
    }
  } else {
    console.log('無 entertainmentData 可添加到提示詞');
  }

  // 關鍵詞分類表
  const keywordCategories = {
    '景點': ['景點', '景區', '公園', '紀念館', '博物館', '文化', '地標', '自然', '名勝', '古蹟', '步道', '展覽', '遊樂場'],
    '活動': ['活動', '展覽', '節慶', '展會', '表演', '音樂會', '歌劇', '戲劇', '舞蹈', '文化節', '運動賽事'],
    '交通': ['交通', '運輸', '捷運', '公車', '巴士', '火車', '高鐵', '台鐵', '自行車', '共享單車', '計程車', '公共交通'],
    '飲食': ['美食', '餐廳', '小吃', '夜市', '飲料', '咖啡', '甜點', '早餐', '午餐', '晚餐', '宵夜', '饗宴'],
    '住宿': ['住宿', '飯店', '旅館', '民宿', '青年旅舍', '渡假村', '旅店'],
    '時間': ['時間', '季節', '早上', '下午', '晚上', '週末', '假日', '平日', '特定時段', '日期', '時段', '春天', '夏天', '秋天', '冬天', '未開始', '已結束', '只限今日', '即將結束', '即將開始', '進行中'],
    '規劃': ['規劃', '行程', '路線', '建議', '推薦', '指南', '一日遊', '二日遊', '導覽', '旅遊路線'],
    '問答': ['如何', '怎麼', '是否', '有沒有', '能不能', '可以嗎', '何時', '何地', '多少', '多遠', '多久']
  };

  // 添加詳細指引
  updatedPrompt += '\n\n【回應指引】\n';

  // 特別觀察用戶查詢意圖
  updatedPrompt += '請觀察用戶的查詢內容，並給予最相關的回應：\n';

  // 如果用戶查詢觀光景點
  updatedPrompt += '如果用戶正在尋找景點資訊：推薦熱門景點，提供開放時間、門票、交通資訊和遊覽建議，可補充附近的其他景點和美食。\n';

  // 如果用戶查詢主題育樂活動
  updatedPrompt += '如果用戶正在尋找活動資訊：優先推薦今日活動、即將結束、和進行中的活動，清楚說明活動時間、地點和內容特色。\n';

  // 如果用戶查詢時間相關資訊
  updatedPrompt += '如果用戶正在尋找時間相關資訊：推薦最符合時間需求的活動，優先考慮「只限今日」、「即將結束」、「進行中」、「即將開始」和「未開始」的活動，並根據用戶需求提供適當的行程安排建議。\n';

  // 如果用戶查詢飲食
  updatedPrompt += '如果用戶正在尋找美食資訊：推薦特色餐廳或小吃，提供價格範圍、營業時間和用餐環境描述，可補充附近景點資訊。\n';

  // 如果用戶查詢交通
  updatedPrompt += '如果用戶正在尋找交通資訊：提供詳細的公共交通選擇、路線和換乘建議，包含預估時間和票價資訊。\n';

  // 如果用戶在規劃行程
  updatedPrompt += '如果用戶正在規劃行程：提供合理的行程安排，考慮交通時間、景點開放時間和用餐時段，建議最佳參觀順序。\n';

  return updatedPrompt;
}

/**
 * 分析用戶意圖
 */
function analyzeUserIntent(message: string) {
  // 關鍵詞分類
  const keywordCategories = {
    景點: ['景點', '景區', '勝地', '名勝', '古蹟', '遺址', '博物館', '美術館', '展覽館', '公園', '花園', '步道', '海灘', '溫泉'],
    活動: ['活動', '展覽', '演唱會', '表演', '藝術節', '嘉年華', '節慶', '市集', '體驗', '工作坊'],
    時間: ['今天', '今日', '週末', '明天', '下週', '即將', '進行中', '最近', '近期', '現在', '幾號', '何時', '日期', '時間', '結束', '開始', '未開始', '已結束', '只限今日', '即將結束', '即將開始'],
    交通: ['交通', '怎麼去', '如何到達', '巴士', '公車', '捷運', '火車', '高鐵', '客運', '船', '計程車', '自行車', '租車', '停車'],
    飲食: ['美食', '餐廳', '小吃', '夜市', '特色菜', 'local food', '早餐', '午餐', '晚餐', '甜點', '飲料', '咖啡廳'],
    住宿: ['住宿', '飯店', '旅館', '民宿', '青年旅舍', '渡假村', '營地', '露營', '帳篷'],
    規劃: ['行程', '規劃', '安排', '幾天', '一日遊', '二日遊', '自由行', '跟團', '半日遊'],
    問答: ['推薦', '建議', '哪裡好玩', '值得去', '必去', '人氣', '熱門', '隱藏版', '私房', '在地', '道地']
  };

  // 紀錄匹配的類別和關鍵詞
  const matches: Record<string, string[]> = {};
  let totalMatches = 0;

  // 檢查每個類別的關鍵詞
  for (const [category, keywords] of Object.entries(keywordCategories)) {
    const matchedKeywords = keywords.filter(keyword => message.includes(keyword));
    if (matchedKeywords.length > 0) {
      matches[category] = matchedKeywords;
      totalMatches += matchedKeywords.length;
    }
  }

  // 提取可能的地點名稱
  const commonPlaces = ['台北', '臺北', '新北', '桃園', '台中', '臺中', '台南', '臺南', '高雄', '基隆', '宜蘭', '花蓮', '台東', '臺東', '屏東', '南投', '雲林', '彰化', '嘉義', '苗栗', '新竹', '金門', '馬祖', '澎湖'];
  const mentionedPlaces = commonPlaces.filter(place => message.includes(place));

  return {
    isTravelRelated: totalMatches > 0,
    matchedCategories: Object.keys(matches),
    matchedKeywords: matches,
    locations: mentionedPlaces,
    queryFocus: mentionedPlaces.length > 0 ? mentionedPlaces[0] : null
  };
}

/**
 * 準備 API 請求內容
 */
function prepareRequestBody(userMessage: string) {
  return {
    contents: [{
      role: "user",
      parts: [{
        text: `${SYSTEM_PROMPT}\n\n用戶問題：${userMessage}`
      }]
    }],
    generationConfig: {
      temperature: 0.5,
      topK: 40,
      topP: 0.95,
      maxOutputTokens: MAX_OUTPUT_TOKENS
    }
  };
}

/**
 * 從 API 回應中提取文字
 */
function extractTextFromResponse(data: ApiResponse): string | null {
  // 處理 2024年最新的 API 回應格式
  if (data.candidates && data.candidates[0]?.content?.parts) {
    const text = data.candidates[0].content.parts
      .filter((part: any) => part.text)
      .map((part: any) => part.text)
      .join('\n');

    if (text) return text;
  }

  // 嘗試處理其他可能的格式
  if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text) {
    return data.candidates[0].content.parts[0].text;
  } else if (data.candidates && data.candidates[0]?.content?.text) {
    return data.candidates[0].content.text;
  } else if (data.candidates && data.candidates[0]?.output) {
    return data.candidates[0].output;
  } else if (data.predictions && data.predictions[0]?.content) {
    return data.predictions[0].content;
  } else if (data.text) {
    return data.text;
  }

  return null;
}

/**
 * 獲取友善的錯誤訊息
 */
function getErrorMessage(error: any): string {
  if (!error) return '未知錯誤';

  if (typeof error === 'string') return error;

  // 處理 Axios 錯誤
  if (error.response) {
    const status = error.response.status;
    if (status === 401 || status === 403) {
      return `API 金鑰授權錯誤: 請確認金鑰是否有效且已啟用 Gemini API`;
    } else if (status === 404) {
      return `API 端點不存在: 請確認 API 路徑是否正確`;
    } else if (status === 429) {
      return `API 配額超出限制: 請稍後再試，或考慮升級 API 方案`;
    } else if (status >= 500) {
      return `API 伺服器錯誤: 伺服器可能暫時無法使用，請稍後再試`;
    } else {
      return `API 錯誤 (${status}): ${error.response.data?.error?.message || '未知錯誤'}`;
    }
  }

  // 處理網路錯誤
  if (error.request) {
    return `網路連線錯誤: 請檢查您的網路連線或 API 端點是否正確`;
  }

  // 一般錯誤
  return error.message || '發生未知錯誤';
}

/**
 * 嘗試備用 API 格式
 */
async function tryBackupApiFormat(userMessage: string): Promise<string | null> {
  try {
    const backupRequestBody = {
      model: "gemini-pro",
      prompt: { text: `${SYSTEM_PROMPT}\n\n用戶問題：${userMessage}` },
      temperature: 0.7,
      maxOutputTokens: MAX_OUTPUT_TOKENS,
      safetySettings: []
    };

    const backupResponse = await fetchWithRetry(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(backupRequestBody)
    });

    const backupData = await backupResponse.json();
    return extractTextFromResponse(backupData);
  } catch (error) {
    return null;
  }
}

/**
 * 滾動聊天視窗到底部
 */
function scrollToBottom(): void {
  nextTick(() => {
    if (chatContainer.value) {
      const scrollbarInst = (chatContainer.value as any).scrollbarInstRef;
      if (scrollbarInst) {
        scrollbarInst.scrollTo({
          top: scrollbarInst.contentRef.scrollHeight,
          behavior: 'smooth'
        });
      }
    }
  });
}

/**
 * 發送訊息到 AI
 */
async function sendMessage(): Promise<void> {
  if (!inputMessage.value.trim() || isLoading.value) return;

  const userMessage = inputMessage.value;
  messages.value.push({ role: 'user', content: userMessage });
  inputMessage.value = '';
  isLoading.value = true;
  isThinking.value = true;

  scrollToBottom();

  // 顯示思考中
  messages.value.push({ role: 'assistant', content: '思考中.....' });
  scrollToBottom();

  try {
    // 更新系統提示詞並準備請求
    SYSTEM_PROMPT = updateSystemPrompt(userMessage);
    const requestBody = prepareRequestBody(userMessage);

    // 發送請求
    const response = await fetchWithRetry(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });

    // 解析回應
    const data: ApiResponse = await response.json();
    messages.value.pop(); // 移除"思考中"訊息

    // 處理回應文字
    const text = extractTextFromResponse(data);
      if (text) {
      messages.value.push({ role: 'assistant', content: text });
      scrollToBottom();
        return;
    }

    // 錯誤處理
    if (data.error) {
      throw new Error(`API 返回錯誤: ${data.error.message || JSON.stringify(data.error)}`);
    } else if (!data.candidates || data.candidates.length === 0) {
      throw new Error('API 回應中沒有候選答案');
    } else {
      throw new Error('API 回應格式異常，無法解析回答');
    }
  } catch (error) {
    // 嘗試備用 API 格式
    const backupText = await tryBackupApiFormat(userMessage);
    if (backupText) {
        messages.value.pop();
      messages.value.push({ role: 'assistant', content: backupText });
      scrollToBottom();
        return;
      }

    // 顯示錯誤訊息
    let errorMessage = getErrorMessage(error);
    messages.value.pop();
    messages.value.push({
      role: 'assistant',
      content: `抱歉，出現了錯誤：${errorMessage}\n\n技術詳情：${error instanceof Error ? error.message : '未知錯誤'}`
    });
    scrollToBottom();
  } finally {
    isLoading.value = false;
    isThinking.value = false;
  }
}

/**
 * 測試 API 金鑰有效性
 */
async function testApiKey(): Promise<boolean> {
  try {
    const testRequestBody = {
      contents: [{
          role: "user",
        parts: [{ text: '你好，這是 API 金鑰測試。請回覆 "API 金鑰有效"' }]
      }]
    };

    const response = await fetchWithRetry(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testRequestBody)
    }, 1);

    const data: ApiResponse = await response.json();

    // 判斷是否成功
    const text = extractTextFromResponse(data);
    return !!text;
  } catch (error) {
    return false;
  }
}

/**
 * 執行手動 API 測試
 */
async function runApiTest(): Promise<void> {
  apiTestResult.value = '正在測試 API 連線...';

  try {
    const testRequestBody = {
      contents: [{
        role: "user",
        parts: [{ text: '請用一句話回覆測試是否成功。' }]
      }]
    };

    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testRequestBody)
    });

    const data: ApiResponse = await response.json();

    if (!response.ok) {
      // API 回應錯誤
      const errorMessage = data.error?.message || `錯誤代碼: ${response.status}`;
      apiTestResult.value = `❌ API 測試失敗: ${errorMessage}`;

      // 添加錯誤解決建議
      if (response.status === 403 || data.error?.message?.includes('API key')) {
        apiTestResult.value += '\n\n可能原因: API 金鑰無效或未啟用 Gemini API。請確認金鑰是否正確，以及是否已在 Google AI Studio 啟用 Gemini API。';
      } else if (response.status === 429) {
        apiTestResult.value += '\n\n可能原因: API 配額已用盡。請等待配額重置或升級您的 API 方案。';
      }
    } else {
      // 提取回應文字
      const text = extractTextFromResponse(data);
      if (text) {
        apiTestResult.value = `✅ API 測試成功!\n\nAI 回應: "${text}"`;
      } else {
        apiTestResult.value = '⚠️ API 回應格式異常（無文字內容）';
      }
    }
  } catch (error) {
    apiTestResult.value = `❌ API 測試發生錯誤: ${error instanceof Error ? error.message : '未知錯誤'}`;
  }
}

/**
 * 處理聊天窗口開啟/關閉
 */
function toggleChat(): void {
  isChatOpen.value = !isChatOpen.value;

  if (isChatOpen.value) {
    apiTestResult.value = ''; // 重置測試結果

    // 初始化聊天機器人，獲取主題育樂資料
    if (!isInitialized.value) {
      initializeChatbot();
    }

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
        scrollToBottom();
      });
    } else {
      scrollToBottom();
    }
  }
}

/**
 * 處理按鍵事件 - Enter 發送
 */
function handleKeyPress(e: KeyboardEvent): void {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

/**
 * 切換顯示除錯資訊
 */
function toggleDebugInfo(): void {
  showDebugInfo.value = !showDebugInfo.value;
}

/**
 * 分析 API 回應
 */
function analyzeApiResponse(data: ApiResponse): ApiErrorResult {
  // 檢查是否為 API 限制或錯誤
  if (data.error) {
    const errorCode = data.error.code;
    const errorMessage = data.error.message || '';

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

/**
 * 初始化聊天機器人和測試連線
 */
async function initializeChatbot() {
  isLoading.value = true;

  try {
    // 連線測試請在生產環境中移除或關閉
    if (import.meta.env.DEV) {
      await runApiTest();
    }

    // 取得育樂資料
    try {
      const query = ""; // 使用空查詢獲取所有資料
      const data = await fetchEntertainmentData(query);
      entertainmentData.value = data;
    } catch (error) {
      console.error('獲取主題育樂資料失敗:', error);
    }

    isInitialized.value = true;
  } catch (error) {
    console.error(`初始化錯誤: ${getErrorMessage(error)}`);
  } finally {
    isLoading.value = false;
  }
}

// 元件掛載時初始化聊天機器人
onMounted(() => {
  // 當元件加載時初始化聊天機器人，確保資料預先準備好
  initializeChatbot();
});
</script>

<template>
  <div class="fixed bottom-10 right-4 z-50">
    <!-- 聊天按鈕 -->
    <NButton v-if="!isChatOpen" circle type="primary" size="large" class="shadow-xl chat-button border-0 hover-bounce"
      @click="toggleChat">
      <template #icon>
        <NIcon size="28">
          <ChatOutlined />
        </NIcon>
      </template>
    </NButton>

    <!-- 聊天視窗 -->
    <NCard v-else class="w-[500px] shadow-2xl rounded-2xl chat-window border-0 travel-card">
      <div class="flex flex-col h-[500px]">
        <!-- 標題列 -->
        <div class="flex justify-between items-center mb-3 pb-3 border-b border-blue-100">
          <div class="flex items-center gap-3">
            <NAvatar>
              <NIcon>
                <SupportAgentOutlined />
              </NIcon>
            </NAvatar>
            <span class="font-bold text-lg text-slate-700">旅遊趣顧問</span>
          </div>
          <div class="flex gap-2">
            <NButton size="small" class="bg-blue-50 hover:bg-blue-100 text-blue-600 border-0 shadow"
              @click="runApiTest">測試
              API</NButton>
            <NButton circle class="hover:bg-red-50 text-slate-500 hover:text-red-500 transition-colors" quaternary
              @click="toggleChat">
              <template #icon>
                <NIcon>
                  <CloseOutlined />
                </NIcon>
              </template>
            </NButton>
          </div>
        </div>

        <!-- API 測試結果 -->
        <div v-if="apiTestResult" class="mb-3 p-3 text-sm border rounded-lg" :class="{
          'bg-green-50 border-green-200 text-green-800': apiTestResult.includes('✅'),
          'bg-red-50 border-red-200 text-red-800': apiTestResult.includes('❌'),
          'bg-yellow-50 border-yellow-200 text-amber-800': apiTestResult.includes('⚠️'),
          'bg-blue-50 border-blue-200 text-blue-800': apiTestResult.includes('正在測試')
        }">
          <div class="whitespace-pre-line">{{ apiTestResult }}</div>
          <div v-if="apiTestResult.includes('❌')" class="mt-2 text-xs text-gray-700">
            <p>排查建議:</p>
            <ol class="list-decimal pl-4 mt-1">
              <li>確認 API 金鑰已正確輸入 (沒有多餘空格)</li>
              <li>確認金鑰已在 <a href="https://makersuite.google.com/" target="_blank" class="text-blue-600 underline">Google
                  AI Studio</a> 啟用</li>
              <li>確認 API 金鑰有足夠配額</li>
            </ol>
          </div>
        </div>

        <!-- 聊天內容 -->
        <NScrollbar ref="chatContainer" class="flex-1 mb-4 px-1">
          <div class="space-y-4">
            <template v-for="(msg, index) in messages" :key="index">
              <div class="flex" :class="msg.role === 'user' ? 'justify-end' : 'justify-start'">
                <div class="max-w-[85%] rounded-2xl p-3 px-4 shadow-sm" :class="[
                    msg.role === 'user'
                      ? 'bg-primary text-white'
                      : msg.content === '思考中.....'
                        ? 'bg-gray-50 text-gray-400'
                      : 'bg-gray-50 text-slate-700 border border-gray-100',
                    msg.content === '思考中.....' ? 'thinking-dots' : '',
                ]">
                  <div class="whitespace-pre-line">{{ msg.content }}</div>
                </div>
              </div>
            </template>
          </div>
        </NScrollbar>

        <!-- 輸入區域 -->
        <div class="flex gap-2 bg-gray-50 p-2 rounded-xl">
          <NInput v-model:value="inputMessage" type="textarea" :rows="1" class="input-travel" placeholder="請輸入您的問題..."
            @keypress="handleKeyPress" />
          <NButton circle type="primary" :disabled="isLoading" class="hover:shadow-lg transition-shadow"
            @click="sendMessage">
            <template #icon>
              <NIcon>
                <SendOutlined />
              </NIcon>
            </template>
          </NButton>
        </div>

        <!-- 除錯資訊按鈕 -->
        <div class="mt-2 text-xs text-right">
          <button @click="toggleDebugInfo" class="text-gray-400 hover:text-gray-700 transition">
            {{ showDebugInfo ? '隱藏除錯資訊' : '顯示除錯資訊' }}
          </button>
        </div>

        <!-- 除錯資訊 -->
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
  backdrop-filter: blur(8px);
  background-color: rgba(255, 255, 255, 0.95);
}

.travel-card {
  box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.15), 0 5px 15px -5px rgba(45, 212, 191, 0.1);
}

.input-travel :deep(textarea) {
  border-radius: 0.75rem;
  border-color: #e5e7eb;
  transition: all 0.2s;
}

.input-travel :deep(textarea):focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
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

.chat-button {
  width: 65px !important;
  height: 65px !important;
  font-size: 1.5rem !important;
  box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3), 0 4px 6px -2px rgba(59, 130, 246, 0.2) !important;
  transition: all 0.3s ease;
}

.hover-bounce:hover {
  animation: bounce 1s infinite;
}

@keyframes bounce {

  0%,
  100% {
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
  0% {
    content: '.';
  }

  33% {
    content: '..';
  }

  66% {
    content: '...';
  }

  100% {
    content: '.';
  }
}
</style>
