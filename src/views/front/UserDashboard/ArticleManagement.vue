<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NButton, NDataTable, NSpace, NPopconfirm, useMessage, NModal, NForm, NFormItem, NInput, NSelect } from 'naive-ui';
import { useUserStore } from '@/stores';
import axios from 'axios';

const message = useMessage();
const userStore = useUserStore();

// 文章列表數據
const articles = ref([]);
const loading = ref(false);

// 編輯相關
const showEditModal = ref(false);
const editingArticle = ref({
  id: null,
  title: '',
  content: '',
  category_id: null,
});

// 分類選項
const categoryOptions = ref([]);

// 表格列定義
const columns = [
  {
    title: '標題',
    key: 'title',
    width: 300,
  },
  {
    title: '分類',
    key: 'category',
    render: (row) => row.category?.name || '未分類',
  },
  {
    title: '發布時間',
    key: 'created_at',
    render: (row) => new Date(row.created_at).toLocaleString('zh-TW'),
  },
  {
    title: '觀看數',
    key: 'views',
    width: 100,
  },
  {
    title: '讚數',
    key: 'like_count',
    width: 100,
  },
  {
    title: '評論數',
    key: 'comment_count',
    width: 100,
  },
  {
    title: '操作',
    key: 'actions',
    width: 300,
    render: (row) => {
      return h(NSpace, null, {
        default: () => [
          h(
            NButton,
            {
              size: 'small',
              type: 'primary',
              onClick: () => handleView(row),
            },
            { default: () => '查看' }
          ),
          h(
            NButton,
            {
              size: 'small',
              type: 'info',
              onClick: () => handleEdit(row),
            },
            { default: () => '編輯' }
          ),
          h(
            NPopconfirm,
            {
              onPositiveClick: () => handleDelete(row.id),
            },
            {
              default: () => '確定要刪除這篇文章嗎？',
              trigger: () =>
                h(
                  NButton,
                  {
                    size: 'small',
                    type: 'error',
                  },
                  { default: () => '刪除' }
                ),
            }
          ),
        ],
      });
    },
  },
];

// 加載文章列表
async function loadArticles() {
  try {
    loading.value = true;
    const response = await axios.get('http://127.0.0.1:8000/user-dashboard/forum/articles/', {
      withCredentials: true  // 允許攜帶 cookies
    });

    if (response.data) {
      articles.value = response.data;
    }
  } catch (error) {
    console.error('加載文章列表失敗:', error);
    message.error('加載文章列表失敗');
  } finally {
    loading.value = false;
  }
}

// 加載分類列表
async function loadCategories() {
  try {
    const response = await axios.get('http://localhost:8000/api/public/categories/');
    if (response.data && Array.isArray(response.data)) {
      categoryOptions.value = response.data.map(category => ({
        label: category.name,
        value: category.id,
      }));
    }
  } catch (error) {
    console.error('加載分類列表失敗:', error);
    message.error('加載分類列表失敗');
  }
}

// 處理查看詳情
function handleView(article) {
  // 直接跳轉到後台的詳情頁面
  window.location.href = `http://127.0.0.1:8000/user-dashboard/forum/articles/${article.id}/`;
}

// 處理編輯
function handleEdit(article) {
  // 直接跳轉到後台的編輯頁面
  window.location.href = `http://127.0.0.1:8000/user-dashboard/forum/articles/${article.id}/edit/`;
}

// 保存編輯
async function handleSave() {
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.put(
      `http://127.0.0.1:8000/user-dashboard/forum/articles/${editingArticle.value.id}/edit/`,
      editingArticle.value,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (response.data) {
      message.success('文章更新成功');
      showEditModal.value = false;
      await loadArticles();
    }
  } catch (error) {
    console.error('更新文章失敗:', error);
    message.error('更新文章失敗');
  }
}

// 處理刪除
async function handleDelete(articleId) {
  try {
    // 獲取 CSRF token
    const csrftoken = document.cookie.split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];

    const response = await axios.post(
      `http://127.0.0.1:8000/user-dashboard/forum/articles/${articleId}/delete/`,
      {},  // 空的請求體
      {
        headers: {
          'X-CSRFToken': csrftoken,
        },
        withCredentials: true  // 允許攜帶 cookies
      }
    );

    if (response.status === 200) {
      message.success('文章刪除成功');
      await loadArticles();  // 重新加載文章列表
    }
  } catch (error) {
    console.error('刪除文章失敗:', error);
    message.error('刪除文章失敗，請稍後重試');
  }
}

onMounted(async () => {
  await Promise.all([loadArticles(), loadCategories()]);
});
</script>

<template>
  <div class="p-6">
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-800">我的文章管理</h2>
    </div>

    <!-- 文章列表 -->
    <NDataTable
      :columns="columns"
      :data="articles"
      :loading="loading"
      :pagination="{
        pageSize: 10
      }"
      :bordered="false"
      class="bg-white rounded-lg shadow"
    />

    <!-- 編輯文章彈窗 -->
    <NModal v-model:show="showEditModal">
      <NCard
        style="width: 800px"
        title="編輯文章"
        :bordered="false"
        size="huge"
        role="dialog"
        aria-modal="true"
      >
        <NForm :model="editingArticle">
          <NFormItem label="標題" required>
            <NInput v-model:value="editingArticle.title" placeholder="請輸入文章標題" />
          </NFormItem>
          <NFormItem label="分類" required>
            <NSelect
              v-model:value="editingArticle.category_id"
              :options="categoryOptions"
              placeholder="請選擇分類"
            />
          </NFormItem>
          <NFormItem label="內容" required>
            <NInput
              v-model:value="editingArticle.content"
              type="textarea"
              :rows="10"
              placeholder="請輸入文章內容"
            />
          </NFormItem>
        </NForm>
        <template #footer>
          <div class="flex justify-end gap-4">
            <NButton @click="showEditModal = false">取消</NButton>
            <NButton type="primary" @click="handleSave">保存</NButton>
          </div>
        </template>
      </NCard>
    </NModal>
  </div>
</template>

<style scoped>
.n-data-table {
  --n-merged-th-color: #f9fafb;
  --n-merged-td-color: #ffffff;
}
</style> 