<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import Banner from '@/components/Banner.vue';
import { apiImageSearch } from '@/utils/api';

const title = ref('商城中心');
const router = useRouter();

// AI圖像搜索相關
const isImageSearchLoading = ref(false);
const imageSearchResults = ref<any[]>([]);
const showImageSearchResults = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);
const previewImage = ref<string | null>(null);
const searchError = ref<string | null>(null);
const dropActive = ref(false);

// 觸發文件選擇
function triggerFileInput() {
  if (fileInputRef.value) {
    fileInputRef.value.click();
  }
}

// 重置圖像搜索
function resetImageSearch() {
  showImageSearchResults.value = false;
  imageSearchResults.value = [];
  previewImage.value = null;
  searchError.value = null;
  if (fileInputRef.value) {
    fileInputRef.value.value = '';
  }
}

// 處理圖片上傳和AI搜索
async function handleImageSearch(event: Event): Promise<void> {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  // 驗證文件類型
  if (!file.type.startsWith('image/')) {
    searchError.value = '請上傳圖片文件（JPG、PNG、GIF等）';
    return;
  }

  // 清除之前的錯誤
  searchError.value = null;

  // 顯示預覽
  const reader = new FileReader();
  reader.onload = (e: ProgressEvent<FileReader>) => {
    previewImage.value = e.target?.result as string || null;
  };
  reader.readAsDataURL(file);

  isImageSearchLoading.value = true;
  showImageSearchResults.value = true;
  
  try {
    // 壓縮圖片以提高上傳速度
    const compressedFile = await compressImage(file);
    
    apiImageSearch(compressedFile)
      .then(response => {
        console.log('圖像搜索結果:', response);
        if (response?.success) {
          // 檢查debug_info是否存在並輸出偵錯資訊
          if (response.debug_info) {
            console.log('偵錯資訊:', response.debug_info);
          }
          
          // 檢查message是否存在
          if (response.message) {
            console.log('API消息:', response.message);
          }
          
          if (Array.isArray(response.products)) {
            imageSearchResults.value = response.products;
            if (response.products.length === 0) {
              searchError.value = response.message || '未找到相似商品，請嘗試其他圖片';
            }
          } else {
            console.error('返回的products不是數組:', response.products);
            imageSearchResults.value = [];
            searchError.value = '返回數據格式錯誤，請聯繫管理員';
          }
        } else {
          console.error('圖像搜索失敗:', response?.error || '無法解析返回數據');
          imageSearchResults.value = [];
          searchError.value = response?.error || '圖像搜索失敗，請稍後再試';
        }
      })
      .catch(error => {
        console.error('圖像搜索請求失敗:', error);
        imageSearchResults.value = [];
        searchError.value = '網絡錯誤，請檢查網絡連接並稍後再試';
      })
      .finally(() => {
        isImageSearchLoading.value = false;
      });
  } catch (error) {
    console.error('圖像處理錯誤:', error);
    imageSearchResults.value = [];
    searchError.value = '圖像處理失敗，請嘗試其他圖片';
    isImageSearchLoading.value = false;
  }
}

// 圖像壓縮函數
async function compressImage(file: File): Promise<File> {
  return new Promise((resolve, reject) => {
    try {
      const maxWidth = 1024; // 最大寬度
      const maxHeight = 1024; // 最大高度
      const maxSizeMB = 1; // 最大文件大小（MB）
      const maxSize = maxSizeMB * 1024 * 1024; // 轉換為字節
      
      // 如果文件小於最大大小，直接返回
      if (file.size <= maxSize) {
        return resolve(file);
      }
      
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          let width = img.width;
          let height = img.height;
          
          // 計算縮放比例
          if (width > maxWidth) {
            const ratio = maxWidth / width;
            width = maxWidth;
            height = height * ratio;
          }
          
          if (height > maxHeight) {
            const ratio = maxHeight / height;
            height = maxHeight;
            width = width * ratio;
          }
          
          // 創建Canvas元素
          const canvas = document.createElement('canvas');
          canvas.width = width;
          canvas.height = height;
          
          // 繪製圖像
          const ctx = canvas.getContext('2d');
          if (!ctx) {
            return reject(new Error('無法創建Canvas上下文'));
          }
          
          ctx.drawImage(img, 0, 0, width, height);
          
          // 轉換為Blob
          canvas.toBlob((blob) => {
            if (!blob) {
              return reject(new Error('圖像壓縮失敗'));
            }
            
            // 創建新的File對象
            const compressedFile = new File([blob], file.name, {
              type: 'image/jpeg',
              lastModified: Date.now()
            });
            
            console.log(`圖像已壓縮: ${file.size} -> ${compressedFile.size} 字節`);
            resolve(compressedFile);
          }, 'image/jpeg', 0.7); // 0.7是品質係數，可以調整
        };
        
        img.onerror = () => {
          reject(new Error('圖像載入失敗'));
        };
        
        img.src = e.target?.result as string;
      };
      
      reader.onerror = () => {
        reject(new Error('讀取文件失敗'));
      };
      
      reader.readAsDataURL(file);
    } catch (error) {
      reject(error);
    }
  });
}

// 處理拖拽事件
function handleDragEnter(e: DragEvent): void {
  e.preventDefault();
  e.stopPropagation();
  dropActive.value = true;
}

function handleDragOver(e: DragEvent): void {
  e.preventDefault();
  e.stopPropagation();
  dropActive.value = true;
}

function handleDragLeave(e: DragEvent): void {
  e.preventDefault();
  e.stopPropagation();
  dropActive.value = false;
}

async function handleDrop(e: DragEvent): Promise<void> {
  e.preventDefault();
  e.stopPropagation();
  dropActive.value = false;
  
  const files = e.dataTransfer?.files;
  if (files && files.length > 0) {
    const file = files[0];
    if (file.type.startsWith('image/')) {
      // 創建預覽
      const reader = new FileReader();
      reader.onload = (e) => {
        previewImage.value = e.target?.result as string || null;
      };
      reader.readAsDataURL(file);
      
      // 清除之前的錯誤
      searchError.value = null;
      isImageSearchLoading.value = true;
      showImageSearchResults.value = true;
      
      try {
        // 壓縮圖片
        const compressedFile = await compressImage(file);
        apiImageSearch(compressedFile)
          .then(response => {
            console.log('圖像搜索結果(拖放上傳):', response);
            if (response?.success) {
              // 檢查debug_info是否存在並輸出偵錯資訊
              if (response.debug_info) {
                console.log('偵錯資訊:', response.debug_info);
              }
              
              // 檢查message是否存在
              if (response.message) {
                console.log('API消息:', response.message);
              }
              
              if (Array.isArray(response.products)) {
                imageSearchResults.value = response.products;
                if (response.products.length === 0) {
                  searchError.value = response.message || '未找到相似商品，請嘗試其他圖片';
                }
              } else {
                console.error('返回的products不是數組:', response.products);
                imageSearchResults.value = [];
                searchError.value = '返回數據格式錯誤，請聯繫管理員';
              }
            } else {
              console.error('圖像搜索失敗:', response?.error || '無法解析返回數據');
              imageSearchResults.value = [];
              searchError.value = response?.error || '圖像搜索失敗，請稍後再試';
            }
          })
          .catch(error => {
            console.error('圖像搜索請求失敗:', error);
            imageSearchResults.value = [];
            searchError.value = '網絡錯誤，請檢查網絡連接並稍後再試';
          })
          .finally(() => {
            isImageSearchLoading.value = false;
          });
      } catch (error) {
        console.error('圖像處理錯誤:', error);
        imageSearchResults.value = [];
        searchError.value = '圖像處理失敗，請嘗試其他圖片';
        isImageSearchLoading.value = false;
      }
    } else {
      searchError.value = '請上傳圖片文件（JPG、PNG、GIF等）';
    }
  }
}

// 處理粘貼事件
async function handlePaste(e: ClipboardEvent): Promise<void> {
  const items = e.clipboardData?.items;
  if (items) {
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const file = items[i].getAsFile();
        if (file) {
          // 創建預覽
          const reader = new FileReader();
          reader.onload = (e) => {
            previewImage.value = e.target?.result as string || null;
          };
          reader.readAsDataURL(file);
          
          // 清除之前的錯誤
          searchError.value = null;
          isImageSearchLoading.value = true;
          showImageSearchResults.value = true;
          
          try {
            // 壓縮圖片
            const compressedFile = await compressImage(file);
            apiImageSearch(compressedFile)
              .then(response => {
                console.log('圖像搜索結果(粘貼上傳):', response);
                if (response?.success) {
                  // 檢查debug_info是否存在並輸出偵錯資訊
                  if (response.debug_info) {
                    console.log('偵錯資訊:', response.debug_info);
                  }
                  
                  // 檢查message是否存在
                  if (response.message) {
                    console.log('API消息:', response.message);
                  }
                  
                  if (Array.isArray(response.products)) {
                    imageSearchResults.value = response.products;
                    if (response.products.length === 0) {
                      searchError.value = response.message || '未找到相似商品，請嘗試其他圖片';
                    }
                  } else {
                    console.error('返回的products不是數組:', response.products);
                    imageSearchResults.value = [];
                    searchError.value = '返回數據格式錯誤，請聯繫管理員';
                  }
                } else {
                  console.error('圖像搜索失敗:', response?.error || '無法解析返回數據');
                  imageSearchResults.value = [];
                  searchError.value = response?.error || '圖像搜索失敗，請稍後再試';
                }
              })
              .catch(error => {
                console.error('圖像搜索請求失敗:', error);
                imageSearchResults.value = [];
                searchError.value = '網絡錯誤，請檢查網絡連接並稍後再試';
              })
              .finally(() => {
                isImageSearchLoading.value = false;
              });
          } catch (error) {
            console.error('圖像處理錯誤:', error);
            imageSearchResults.value = [];
            searchError.value = '圖像處理失敗，請嘗試其他圖片';
            isImageSearchLoading.value = false;
          }
          break;
        }
      }
    }
  }
}

// 查看商品詳情
function viewProductDetail(productId: number) {
  router.push({ name: 'MallProductDetail', params: { id: productId } });
}
</script>

<template>
  <main>
    <Banner bg-url="/images/banner.jpg">
      <template #title>
        {{ title }}
      </template>
      <template #sec-title>
        使用AI智能圖像搜索找到你喜歡的商品
      </template>
    </Banner>

    <!-- AI圖像搜索功能 -->
    <div class="container mx-auto my-8 px-4">
      <div 
        class="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg shadow-lg p-6 text-white"
        :class="{ 'border-4 border-dashed border-white': dropActive }"
        @dragenter="handleDragEnter"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
        @paste="handlePaste"
      >
        <h2 class="text-3xl font-bold mb-4">AI智能圖像搜索</h2>
        <p class="mb-4 text-white text-lg">上傳一張圖片，AI會幫您找到相似的商品 - 立即體驗智能購物！</p>
        <p class="mb-4 text-white text-sm opacity-80">支持JPG、PNG、GIF等常見圖片格式，推薦使用清晰、主體明確的商品圖片獲得最佳搜索效果</p>
        
        <div class="flex flex-wrap items-center gap-4 mb-4">
          <input
            ref="fileInputRef"
            type="file"
            accept="image/*"
            class="hidden"
            @change="handleImageSearch"
          />
          <button
            @click="triggerFileInput"
            class="bg-white text-blue-600 hover:bg-gray-100 py-3 px-6 rounded-lg flex items-center font-bold text-lg shadow-md transition-all duration-200 transform hover:scale-105"
            :disabled="isImageSearchLoading"
          >
            <span v-if="!isImageSearchLoading">
              <i class="fas fa-camera mr-2"></i>上傳圖片搜索
            </span>
            <span v-else>處理中...</span>
          </button>
          
          <button
            v-if="showImageSearchResults"
            @click="resetImageSearch"
            class="bg-gray-200 hover:bg-gray-300 text-gray-800 py-3 px-6 rounded-lg font-medium"
          >
            清除結果
          </button>
        </div>
        
        <!-- 拖拽提示 -->
        <div class="text-center text-white bg-blue-500 bg-opacity-30 rounded-lg p-4 mb-4">
          <p class="text-lg">您也可以直接<strong>拖拽圖片</strong>到此區域或<strong>粘貼</strong>剪貼板中的圖片</p>
        </div>
        
        <!-- 圖片預覽 -->
        <div v-if="previewImage" class="mt-4 flex justify-center">
          <div class="relative group">
            <img 
              :src="previewImage" 
              alt="預覽圖片" 
              class="max-h-60 rounded-lg shadow-md border-2 border-white object-contain bg-white bg-opacity-20"
            />
            <div class="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity duration-200 rounded-lg">
              <button @click="resetImageSearch" class="text-white bg-red-500 py-1 px-3 rounded-md">
                移除
              </button>
            </div>
          </div>
        </div>
        
        <!-- 錯誤信息顯示 -->
        <div v-if="searchError" class="mt-4 bg-red-100 text-red-700 p-4 rounded-lg">
          <p class="font-medium">{{ searchError }}</p>
        </div>
      </div>
    </div>
    
    <!-- 顯示圖像搜索結果 -->
    <div v-if="showImageSearchResults" class="container mx-auto mb-8 px-4">
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-2xl font-bold mb-4 text-blue-600">圖像搜索結果</h3>
        
        <div v-if="isImageSearchLoading" class="flex flex-col justify-center items-center py-16">
          <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500 mb-4"></div>
          <p class="text-lg text-gray-600">AI正在分析您的圖像並尋找相似商品...</p>
        </div>
        
        <div v-else-if="imageSearchResults && imageSearchResults.length > 0" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div v-for="product in imageSearchResults" :key="product.id" class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
            <div class="relative">
              <img :src="product.image_url" :alt="product.name" class="w-full h-48 object-cover object-center" />
              <div class="absolute top-0 right-0 m-2 px-2 py-1 bg-blue-500 text-white text-xs rounded-md">
                AI推薦
              </div>
            </div>
            <div class="p-4">
              <h3 class="text-lg font-semibold mb-2 truncate">{{ product.name }}</h3>
              <p class="text-gray-600 text-sm mb-2 line-clamp-2">{{ product.description || '商品描述' }}</p>
              <div class="flex justify-between items-center">
                <div class="text-red-600 font-bold">$ {{ product.price }}</div>
                <button 
                  @click="viewProductDetail(product.id)"
                  class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md text-sm font-medium"
                >
                  查看詳情
        </button>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else-if="imageSearchResults && imageSearchResults.length === 0 && !searchError" class="py-12 text-center">
          <div class="text-6xl mb-4">🔍</div>
          <p class="text-gray-500 text-lg mb-4">未找到相似商品</p>
          <p class="text-gray-500">請嘗試上傳其他圖片，或者瀏覽我們的商品分類</p>
        </div>
      </div>
    </div>

    <div class="container mx-auto px-4 py-8">
      <div class="text-center">
        <h2 class="text-2xl font-bold mb-6">探索我們的商城</h2>
        <p class="text-gray-600 mb-8">
          使用上方的AI圖像搜索功能，或瀏覽我們的商品分類找到您需要的產品。
        </p>
        <button 
          @click="router.push({ name: 'MallProducts' })" 
          class="cta-button"
        >
          瀏覽所有商品
        </button>
      </div>
    </div>
  </main>
</template>

<style scoped>
.cta-button {
  background-color: green; /* 綠底 */
  color: white; /* 白字 */
  border: none; /* 無邊框 */
  border-radius: 8px; /* 圓角 */
  padding: 10px 20px; /* 內邊距 */
  font-size: 16px; /* 字體大小 */
  font-weight: bold;
  cursor: pointer; /* 鼠標指針 */
  margin-top: 0px; /* 按鈕與上方內容的間距 */
}

.cta-button:hover {
  background-color: darkgreen; /* 滑鼠懸停時的顏色 */
}

.image-search-button {
  background-color: #3b82f6; /* 藍底 */
  color: white; /* 白字 */
  border: none; /* 無邊框 */
  border-radius: 8px; /* 圓角 */
  padding: 10px 20px; /* 內邊距 */
  font-size: 16px; /* 字體大小 */
  font-weight: bold;
  cursor: pointer; /* 鼠標指針 */
  display: flex; /* 讓圖標和文字水平排列 */
  align-items: center; /* 垂直居中 */
}

.image-search-button:hover {
  background-color: #2563eb; /* 滑鼠懸停時的顏色 */
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
