<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElForm, ElFormItem, ElInput, ElButton, ElDialog } from 'element-plus';
import axios from 'axios';
import { useUserStore } from '@/stores/user';
import Swal from 'sweetalert2';

const userStore = useUserStore();
const userInfo = ref(userStore.getUserInfo || null);

// 密碼表單參考
const passwordForm = ref(null);
const isChangingPassword = ref(false);
const showPasswordModal = ref(false);

// 密碼表單數據
const newPasswordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

// 密碼表單驗證規則
const passwordRules = {
  oldPassword: [
    { required: true, message: '請輸入當前密碼', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '請輸入新密碼', trigger: 'blur' },
    { 
      validator: (rule: any, value: string) => {
        // 檢查密碼長度至少8個字符
        if (value.length < 8) {
          return false;
        }
        // 檢查是否包含字母和數字
        const hasLetter = /[a-zA-Z]/.test(value);
        const hasNumber = /[0-9]/.test(value);
        return hasLetter && hasNumber;
      },
      message: '密碼須至少8個字符，並包含字母和數字',
      trigger: 'blur'
    }
  ],
  confirmPassword: [
    { required: true, message: '請再次輸入新密碼', trigger: 'blur' },
    {
      validator: (rule: any, value: string) => {
        return value === newPasswordForm.value.newPassword;
      },
      message: '兩次輸入的密碼不一致',
      trigger: 'blur'
    }
  ]
};

// 個人資料表單數據
const profileForm = ref({
  name: userInfo.value?.full_name || '',
  address: userInfo.value?.address || '',
  phone: userInfo.value?.phone || ''  // 確保使用正確的手機號碼，不是帳號
});

// 開啟密碼修改對話框
const openChangePasswordModal = () => {
  // 重置表單
  newPasswordForm.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  };
  showPasswordModal.value = true;
};

// 關閉密碼修改對話框
const closeChangePasswordModal = () => {
  showPasswordModal.value = false;
};

// 修改密碼方法 - 確保連接到正確API
const changePassword = async () => {
  if (!passwordForm.value) return;
  
  try {
    // 驗證密碼表單
    await passwordForm.value.validate();
    isChangingPassword.value = true;
    
    // 準備請求數據
    const passwordData = {
      current_password: newPasswordForm.value.oldPassword,
      new_password: newPasswordForm.value.newPassword,
      confirm_password: newPasswordForm.value.confirmPassword
    };
    
    // 獲取用戶ID
    const userId = userInfo.value?.id;
    console.log('獲取到用戶ID:', userId);
    
    console.log('嘗試使用密碼修改API');
    console.log('發送數據:', passwordData);
    
    // 嘗試多個可能的API端點
    let response;
    let error;
    
    // 嘗試不同的API路徑
    const apiUrls = [
      // 相對路徑
      `/api/user/update-password/`,
      `/api/u/update-password/`,
      userId ? `/api/u/update-password/${userId}/` : null,
      
      // 直接URL路徑
      `http://127.0.0.1:8000/api/user/update-password/`,
      `http://127.0.0.1:8000/api/u/update-password/`,
      userId ? `http://127.0.0.1:8000/api/u/update-password/${userId}/` : null
    ].filter(Boolean); // 移除null值
    
    console.log('將嘗試以下API路徑:', apiUrls);
    
    // 依次嘗試每個API路徑
    for (const apiUrl of apiUrls) {
      try {
        console.log(`嘗試API路徑: ${apiUrl}`);
        response = await axios({
          method: 'post',
          url: apiUrl,
          data: passwordData,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        
        // 如果成功則跳出循環
        if (response.status === 200 || response.status === 201) {
          console.log('密碼更新成功，使用的API路徑:', apiUrl);
          break;
        }
      } catch (err) {
        console.error(`使用API路徑 ${apiUrl} 更新密碼失敗:`, err);
        error = err;
      }
    }
    
    // 如果所有API路徑都失敗
    if (!response) {
      throw error || new Error('所有API路徑都請求失敗');
    }
    
    console.log('密碼更改API響應:', response.data);
    
    // 如果返回新的訪問令牌，則更新本地存儲
    if (response.data && response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      console.log('已更新訪問令牌');
    }
    
    if (response.data && response.data.refresh) {
      localStorage.setItem('refresh_token', response.data.refresh);
      console.log('已更新刷新令牌');
    }
    
    // 檢查響應
    if (response.data && response.data.success) {
      Swal.fire({
        icon: 'success',
        title: '成功',
        text: response.data.message || '密碼更改成功'
      });
      
      // 重置表單並關閉模態窗
      newPasswordForm.value.oldPassword = '';
      newPasswordForm.value.newPassword = '';
      newPasswordForm.value.confirmPassword = '';
      closeChangePasswordModal();
    } else {
      throw new Error(response.data?.message || '密碼更改失敗，請稍後重試');
    }
  } catch (error: any) {
    console.error('密碼更改出錯:', error);
    Swal.fire({
      icon: 'error',
      title: '錯誤',
      text: error.response?.data?.message || error.message || '密碼更改失敗，請檢查您的輸入'
    });
  } finally {
    isChangingPassword.value = false;
  }
};

// 更新個人資料
const updateProfile = async () => {
  try {
    const userId = userInfo.value?.id;
    if (!userId) {
      ElMessage.error('找不到用戶ID，請重新登入');
      return;
    }

    // 發送更新請求
    const response = await axios.post(
      `http://127.0.0.1:8000/api/member/profile/update/`,
      {
        name: profileForm.value.name,
        address: profileForm.value.address,
        phone: profileForm.value.phone
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    );

    if (response.data.success) {
      ElMessage.success('個人資料更新成功');
      // 更新本地用戶信息
      userStore.updateUserInfo({
        ...userInfo.value,
        full_name: profileForm.value.name,
        address: profileForm.value.address,
        phone: profileForm.value.phone
      });
    } else {
      ElMessage.error(response.data.message || '更新失敗');
    }
  } catch (error) {
    console.error('更新個人資料時出錯:', error);
  }
};

// 頁面載入時執行
onMounted(() => {
  console.log('個人資料頁面已載入');
  if (!userInfo.value) {
    // 嘗試獲取用戶資料
    userStore.fetchUserInfo();
  }
});
</script>

<template>
  <div class="profile-container">
    <div class="profile-card">
      <h2>個人資料</h2>
      
      <!-- 個人資料表單 -->
      <el-form :model="profileForm" label-width="100px">
        <el-form-item label="姓名" required>
          <el-input v-model="profileForm.name" placeholder="請輸入您的姓名" />
        </el-form-item>
        
        <el-form-item label="地址">
          <el-input v-model="profileForm.address" placeholder="請輸入您的地址" />
        </el-form-item>
        
        <el-form-item label="手機號碼">
          <el-input 
            v-model="profileForm.phone" 
            placeholder="請輸入您的手機號碼"
            maxlength="10"
            :formatter="value => value.replace(/[^0-9]/g, '')"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="updateProfile">更新資料</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 密碼修改按鈕 -->
      <div class="password-change-section">
        <h3>安全設定</h3>
        <el-button type="primary" @click="openChangePasswordModal">
          變更密碼
        </el-button>
      </div>
    </div>
    
    <!-- 密碼修改對話框 -->
    <el-dialog
      v-model="showPasswordModal"
      title="變更密碼"
      width="500px"
      :close-on-click-modal="false"
      :destroy-on-close="true"
    >
      <el-form
        ref="passwordForm"
        :model="newPasswordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="當前密碼" prop="oldPassword">
          <el-input
            v-model="newPasswordForm.oldPassword"
            type="password"
            placeholder="請輸入當前密碼"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密碼" prop="newPassword">
          <el-input
            v-model="newPasswordForm.newPassword"
            type="password"
            placeholder="密碼須至少8個字符，並包含字母和數字"
            show-password
          />
        </el-form-item>
        <el-form-item label="確認新密碼" prop="confirmPassword">
          <el-input
            v-model="newPasswordForm.confirmPassword"
            type="password"
            placeholder="請再次輸入新密碼"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeChangePasswordModal">取消</el-button>
        <el-button type="primary" :loading="isChangingPassword" @click="changePassword">
          確認修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.profile-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.password-change-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
</style> 