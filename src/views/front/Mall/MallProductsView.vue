<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import categoriesData from './data/categories.json';
import productsData from './data/MallProduct.json';

const router = useRouter();
const categories = ref(categoriesData.categories);
const products = ref(productsData);
const selectedCategory = ref('');
const selectedBrand = ref('');

// Banner輪播相關
const currentBannerIndex = ref(0);
const banners = [
  {
    image: 'https://images.pexels.com/photos/1687845/pexels-photo-1687845.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2',
    title: '露營裝備特賣',
    description: '全館商品限時優惠中'
  },
  {
    image: 'https://images.pexels.com/photos/1008155/pexels-photo-1008155.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2',
    title: '戶外用品展',
    description: '新品上市'
  },
  {
    image: 'https://images.pexels.com/photos/356056/pexels-photo-356056.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2',
    title: '手機充電配件',
    description: '歡迎參觀選購'
  }
];

// 輪播控制
function nextBanner() {
  currentBannerIndex.value = (currentBannerIndex.value + 1) % banners.length;
}

function prevBanner() {
  currentBannerIndex.value = (currentBannerIndex.value - 1 + banners.length) % banners.length;
}

function setCurrentBanner(index: number) {
  currentBannerIndex.value = index;
}

// 自動輪播
onMounted(() => {
  setInterval(nextBanner, 10000);
  // 執行品牌匹配分析
  analyzeBrandMatching();

  // 新增：從 URL 參數中獲取類別和品牌
  const urlParams = new URLSearchParams(window.location.search);
  selectedCategory.value = urlParams.get('category') || '';
  selectedBrand.value = urlParams.get('brand') || '';
})

// 分頁相關
const currentPage = ref(1);
const pageSize = ref(20); // 每頁顯示20個商品
const inputPage = ref(''); // 新增：輸入頁碼

// 價格範圍暫存
const tempPriceRange = ref({
  min: null as number | null,
  max: null as number | null,
});

// 實際用於篩選的價格範圍
const priceRange = ref({
  min: null as number | null,
  max: null as number | null,
});

// 排序選項
const sortOption = ref('default');

// 切換分類
function toggleCategory(categoryId: string) {
  if (selectedCategory.value === categoryId) {
    selectedCategory.value = '';
    selectedBrand.value = '';
  }
  else {
    selectedCategory.value = categoryId;
    selectedBrand.value = '';
  }
}

// 選擇品牌
function selectBrand(categoryId: string, brand: string) {
  selectedCategory.value = categoryId;
  selectedBrand.value = brand;
}

// 套用價格過濾
function applyPriceFilter() {
  priceRange.value.min = tempPriceRange.value.min;
  priceRange.value.max = tempPriceRange.value.max;
}

// 套用排序
function applySorting() {
  // 排序邏輯已整合到 computed 屬性中
}

// 新增：品牌別名映射
const brandAliases: { [key: string]: string } = {
  px大通: 'px',
  gigastone立達國際: 'gigastone立達',
  gigastone: 'gigastone立達',
  立達國際: 'gigastone立達',
  philips飛利浦: 'philips',
  飛利浦: 'philips',
  adam亞果元素: 'adam',
  亞果元素: 'adam',
  acer宏碁: 'acer',
  宏碁: 'acer',
  asus華碩: 'asus',
  華碩: 'asus',
  apple蘋果: 'apple',
  蘋果: 'apple',
  samsung三星: 'samsung',
  三星: 'samsung',

  // 帳篷品牌別名
  skt: '速可搭',
  outdoorbase: '野道家',
  mountainman: '山林者',
  outdoorexpert: '戶外專家',
  campingace: '大營家',
  wildfun: '野放',
  wildpath: '野道',
  wildplay: '野遊',

  // 充電器品牌別名
  baseus倍思: 'baseus',
  倍思: 'baseus',
  huawei華為: 'huawei',
  華為: 'huawei',
  lenovo聯想: 'lenovo',
  聯想: 'lenovo',
  lg樂金: 'lg',
  樂金: 'lg',
  zmi紫米: 'zmi紫米',
  紫米: 'zmi紫米',
  logitech羅技: '羅技',
  gigabyte技嘉: '技嘉',
  teco東元: '東元',
  probox普羅: 'probox',
  uag都會: 'uag',
  ugreen綠聯: 'ugreen',
  xmart安心亞: 'xmart'
};

// 新增：標準化品牌名稱的函數
function normalizedBrandName(brand: string): string {
  if (!brand)
    return '';
  return brand.toLowerCase()
    .replace(/\s+/g, '') // 移除所有空格
    .replace(/[-_]/g, '') // 移除破折號和底線
    .replace(/（/g, '(')
    .replace(/）/g, ')')
    .replace(/\./g, '') // 移除點號
    .trim();
}

// 新增：商品型別定義
interface Product {
  id: number;
  name: string;
  category: string;
  price: string;
  description: string;
  stock: number;
  is_active: boolean;
  image_url: string;
  created_at: string;
  updated_at: string;
  matchedBrands?: string[];
}

// 修改：檢查商品名稱中的品牌
function findBrandInProductName(product: Product): string[] {
  const matchedBrandsSet = new Set<string>();
  const searchText = `${product.name} ${product.description} ${product.category}`.toLowerCase();

  categories.value.forEach((category) => {
    category.brands.forEach((brand) => {
      // 標準化當前品牌名稱
      const normalizedBrand = normalizedBrandName(brand);
      const brandLower = brand.toLowerCase();

      // 檢查原始品牌名稱
      if (searchText.includes(brandLower))
        matchedBrandsSet.add(brand);

      // 檢查標準化後的品牌名稱
      if (searchText.includes(normalizedBrand))
        matchedBrandsSet.add(brand);

      // 檢查品牌別名
      Object.entries(brandAliases).forEach(([alias, mainBrand]) => {
        if (searchText.includes(alias.toLowerCase())
          && (normalizedBrandName(mainBrand) === normalizedBrand || mainBrand === brand)) {
          matchedBrandsSet.add(brand)
        }
      });

      // 特殊處理：如果商品的 category 完全匹配品牌名稱
      if (product.category) {
        const productCategory = normalizedBrandName(product.category);
        if (productCategory === normalizedBrand
          || brandAliases[productCategory] === brand
          || brandAliases[normalizedBrand] === product.category) {
          matchedBrandsSet.add(brand)
        }
      }
    });
  })

  return Array.from(matchedBrandsSet);
}

// 新增：檢查商品是否屬於特定類別的函數
function isProductInCategory(product: any, categoryId: string): boolean {
  const categoryKeywords: { [key: string]: string[] } = {
    air_mattresses: ['充氣床', '充氣墊', '睡墊', '充氣床墊', 'air bed', 'airbed'],
    camping_tables: ['桌', '餐桌', '露營桌', '摺疊桌', '折疊桌', '戶外桌', '野餐桌', '茶几', '邊桌'],
    camping_tents: ['帳篷', '天幕', '帳棚', '炊事帳', '客廳帳', '遮陽帳', 'tent', '蒙古包'],
    chargers: [
      '充電器',
      '充電頭',
      '變壓器',
      '充電線',
      '快充',
      '電源供應器',
      '充電座',
      '充電組',
      '行動電源',
      'PD充電',
      'QC充電',
      'GaN充電',
      '氮化鎵充電',
      '萬用充電',
      'Type-C',
      'USB充電',
      '多孔充電',
      '快速充電'
    ],
    hiking_backpacks: [
      '背包',
      '登山包',
      '後背包',
      '雙肩包',
      '背囊',
      '運動背包',
      '戶外包',
      '旅行包',
      '行山包',
      '健行包',
      '登山背包'
    ],
    hiking_poles: [
      '登山杖',
      '手杖',
      '拐杖',
      '健走杖',
      '登山手杖',
      '登山棍',
      '健行杖',
      '登山拐杖',
      '避震杖',
      '碳纖維登山杖',
      '鋁合金登山杖'
    ],
    phones: [
      '手機',
      'iPhone',
      'smartphone',
      '智慧型手機',
      '智慧手機',
      '5G手機',
      '4G手機',
      '平板手機',
      '折疊手機',
      'OPPO',
      'vivo',
      'realme',
      'POCO',
      'Redmi',
      '紅米',
      '小米手機',
      '三星手機',
      'Samsung',
      'ASUS',
      '華碩手機',
      'ROG Phone',
      'HTC',
      '宏達電'
    ],
    luggage: [
      '行李箱',
      '旅行箱',
      '拉桿箱',
      '登機箱',
      '托運箱',
      '硬殼箱',
      '軟殼箱',
      '萬向輪',
      '箱子',
      '旅行箱',
      '旅行袋',
      '行李包'
    ],
    gas_stoves: [
      '爐',
      '瓦斯爐',
      '卡式爐',
      '瓦斯烤爐',
      '露營爐',
      '戶外爐具',
      '野炊爐',
      '便攜爐',
      '登山爐',
      '卡式瓦斯爐',
      '攜帶式瓦斯爐'
    ]
  };

  const keywords = categoryKeywords[categoryId] || [];
  const productText = `${product.name} ${product.description}`.toLowerCase();
  const brandText = product.category ? product.category.toLowerCase() : '';

  // 檢查品牌名稱是否包含在關鍵字中
  const brandMatch = keywords.some(keyword => brandText.includes(keyword.toLowerCase()));
  // 檢查商品名稱和描述是否包含關鍵字
  const contentMatch = keywords.some(keyword => productText.includes(keyword.toLowerCase()));

  return brandMatch || contentMatch;
}

// 過濾和排序商品
const filteredProducts = computed(() => {
  let filteredResult = products.value as Product[];

  // 為每個商品添加匹配的品牌信息
  filteredResult = filteredResult.map(product => ({
    ...product,
    matchedBrands: findBrandInProductName(product)
  }));

  // 類別過濾
  if (selectedCategory.value) {
    filteredResult = filteredResult.filter(product =>
      isProductInCategory(product, selectedCategory.value)
    );
  }

  // 品牌過濾
  if (selectedBrand.value) {
    filteredResult = filteredResult.filter((product) => {
      const normalizedProductCategory = normalizedBrandName(product.category);
      const normalizedSelectedBrand = normalizedBrandName(selectedBrand.value);

      // 檢查直接匹配
      if (normalizedProductCategory === normalizedSelectedBrand)
        return true;

      // 檢查品牌別名
      for (const [alias, mainBrand] of Object.entries(brandAliases)) {
        const normalizedAlias = normalizedBrandName(alias);
        const normalizedMainBrand = normalizedBrandName(mainBrand);

        if ((normalizedProductCategory === normalizedAlias || normalizedProductCategory === normalizedMainBrand)
          && (normalizedSelectedBrand === normalizedAlias || normalizedSelectedBrand === normalizedMainBrand)) {
          return true
        }
      }

      return false;
    })
  }

  // 價格範圍過濾
  if (priceRange.value.min !== null || priceRange.value.max !== null) {
    filteredResult = filteredResult.filter((product) => {
      const price = Number.parseFloat(product.price);
      const minOk = priceRange.value.min === null || price >= priceRange.value.min;
      const maxOk = priceRange.value.max === null || price <= priceRange.value.max;
      return minOk && maxOk;
    })
  }

  // 排序
  switch (sortOption.value) {
    case 'price-asc':
      return [...filteredResult].sort((a, b) => Number.parseFloat(a.price) - Number.parseFloat(b.price));
    case 'price-desc':
      return [...filteredResult].sort((a, b) => Number.parseFloat(b.price) - Number.parseFloat(a.price));
    case 'name-asc':
      return [...filteredResult].sort((a, b) => a.name.localeCompare(b.name));
    case 'name-desc':
      return [...filteredResult].sort((a, b) => b.name.localeCompare(a.name));
    default:
      return filteredResult;
  }
});

// 計算總頁數
const totalPages = computed(() => Math.ceil(filteredProducts.value.length / pageSize.value));

// 當前頁面的商品
const currentPageProducts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredProducts.value.slice(start, end);
})

// 切換頁面
function changePage(page: number | string) {
  if (typeof page === 'number')
    currentPage.value = page;
}

// 查看商品詳情
function viewProductDetail(productId: number) {
  router.push({ name: 'MallProductDetail', params: { id: productId } });
}

// 新增分頁相關的計算屬性
const displayedPages = computed(() => {
  const total = totalPages.value;
  const current = currentPage.value;
  const pages = [];

  if (total <= 7) {
    // 如果總頁數小於等於7，顯示所有頁碼
    for (let i = 1; i <= total; i++) pages.push(i);
  } else {
    // 總是顯示第一頁
    pages.push(1);

    if (current <= 3) {
      // 當前頁在前面時
      for (let i = 2; i <= 5; i++) pages.push(i);
      pages.push('...');
      pages.push(total);
    } else if (current >= total - 2) {
      // 當前頁在後面時
      pages.push('...');
      for (let i = total - 4; i <= total; i++) pages.push(i);
    } else {
      // 當前頁在中間時
      pages.push('...');
      for (let i = current - 1; i <= current + 1; i++) pages.push(i);
      pages.push('...');
      pages.push(total);
    }
  }
  return pages;
})

// 新增：跳轉到指定頁面
function jumpToPage() {
  const pageNum = Number.parseInt(inputPage.value);
  if (!Number.isNaN(pageNum) && pageNum >= 1 && pageNum <= totalPages.value) {
    currentPage.value = pageNum;
    inputPage.value = '';
  }
}

// 新增：重置所有篩選
function resetFilters() {
  selectedCategory.value = '';
  selectedBrand.value = '';
}

// 新增：計算每個類別下有效的品牌列表
const availableBrands = computed(() => {
  const brandMap = new Map();

  categories.value.forEach((category) => {
    const validBrands = category.brands.filter((brand) => {
      // 檢查是否有該品牌的商品
      return products.value.some((product) => {
        // 首先檢查商品是否屬於當前類別
        const belongsToCategory = isProductInCategory(product, category.id);
        if (!belongsToCategory)
          return false;

        // 然後檢查品牌是否匹配
        const productBrandNorm = normalizedBrandName(product.category || '');
        const brandNorm = normalizedBrandName(brand);
        return productBrandNorm === brandNorm
          || brandAliases[productBrandNorm] === brandNorm
          || brandAliases[brandNorm] === productBrandNorm;
      })
    });
    brandMap.set(category.id, validBrands);
  })

  return brandMap;
})

// 修改：分析品牌匹配情況的函數
function analyzeBrandMatching() {
  interface BrandStats {
    total: number;
    products: string[];
    category: string;
  }

  interface UnmatchedProduct {
    id: number;
    name: string;
    category: string;
    description: string;
  }

  interface MultipleMatchProduct {
    id: number;
    name: string;
    category: string;
    matchedBrands: string[];
  }

  const brandStats = new Map<string, BrandStats>();
  const unmatchedProducts: UnmatchedProduct[] = [];
  const multipleMatchProducts: MultipleMatchProduct[] = [];

  // 初始化品牌統計
  categories.value.forEach((category) => {
    category.brands.forEach((brand) => {
      brandStats.set(brand, {
        total: 0,
        products: [],
        category: category.name
      });
    })
  });

  // 分析每個商品
  products.value.forEach((product) => {
    const matchedBrands = findBrandInProductName(product);

    if (matchedBrands.length === 0) {
      unmatchedProducts.push({
        id: product.id,
        name: product.name,
        category: product.category,
        description: product.description
      });
    } else if (matchedBrands.length > 1) {
      multipleMatchProducts.push({
        id: product.id,
        name: product.name,
        category: product.category,
        matchedBrands
      });
    }

    // 更新品牌統計
    matchedBrands.forEach((brand) => {
      const stats = brandStats.get(brand);
      if (stats) {
        stats.total++;
        stats.products.push(product.name);
      }
    });
  })

  // 找出沒有匹配到任何商品的品牌
  const unusedBrands = Array.from(brandStats.entries())
    .filter(([_, stats]) => stats.total === 0)
    .map(([brand, stats]) => ({
      brand,
      category: stats.category
    }));

  // 輸出分析結果
  console.log('=== 品牌匹配分析 ===');
  console.log(`總商品數: ${products.value.length}`);
  console.log(`未匹配任何品牌的商品數: ${unmatchedProducts.length}`);
  console.log(`匹配多個品牌的商品數: ${multipleMatchProducts.length}`);
  console.log('\n=== 未使用的品牌 ===');
  console.table(unusedBrands);
  console.log('\n=== 未匹配品牌的商品 ===');
  console.table(unmatchedProducts);
  console.log('\n=== 匹配多個品牌的商品 ===');
  console.table(multipleMatchProducts);
  console.log('\n=== 品牌使用統計 ===');
  const brandUsageStats = Array.from(brandStats.entries())
    .map(([brand, stats]) => ({
      brand,
      category: stats.category,
      matchCount: stats.total
    }))
    .sort((a, b) => b.matchCount - a.matchCount);
  console.table(brandUsageStats);
}
</script>

<template>
  <!-- Banner輪播區 -->
  <div class="relative h-[400px] overflow-hidden mb-8">
    <div
      class="absolute inset-0 flex transition-transform duration-500 ease-in-out"
      :style="{ transform: `translateX(-${currentBannerIndex * 100}%)` }"
    >
      <div
        v-for="(banner, index) in banners"
        :key="index"
        class="relative w-full h-full flex-shrink-0"
      >
        <img
          :src="banner.image"
          :alt="banner.title"
          class="w-full h-full object-cover"
        >
        <div class="absolute inset-0 bg-black bg-opacity-40 flex flex-col justify-center items-center text-white">
          <h2 class="text-4xl font-bold mb-4">
            {{ banner.title }}
          </h2>
          <p class="text-xl">
            {{ banner.description }}
          </p>
        </div>
      </div>
    </div>

    <!-- 輪播控制按鈕 -->
    <button
      class="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition-all"
      @click="prevBanner"
    >
      <span class="material-icons">上一項</span>
    </button>
    <button
      class="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition-all"
      @click="nextBanner"
    >
      <span class="material-icons">下一項</span>
    </button>

    <!-- 輪播指示點 -->
    <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
      <button
        v-for="(_, index) in banners"
        :key="index"
        class="w-3 h-3 rounded-full transition-all"
        :class="index === currentBannerIndex ? 'bg-white' : 'bg-white bg-opacity-50 hover:bg-opacity-75'"
        @click="setCurrentBanner(index)"
      />
    </div>
  </div>

  <div class="container mx-auto px-4 py-8">
    <div class="flex">
      <!-- 左側分類欄 -->
      <div class="w-1/4 pr-8 space-y-6">
        <!-- 商品分類 -->
        <div class="bg-white rounded-lg shadow p-4">
          <h2 class="text-xl font-bold mb-4">
            商品分類
          </h2>
          <!-- 所有商品按鈕 -->
          <button
            class="w-full text-left px-4 py-2 mb-4 rounded-lg transition-colors duration-200 bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium"
            @click="resetFilters"
          >
            所有商品
          </button>
          <!-- 第一階層分類按鈕 -->
          <div v-for="category in categories" :key="category.id" class="mb-4">
            <button
              class="w-full text-left px-4 py-2 rounded-lg transition-colors duration-200"
              :class="{
                'bg-green-600 text-white': selectedCategory === category.id,
                'hover:bg-green-100': selectedCategory !== category.id,
              }"
              @click="toggleCategory(category.id)"
            >
              {{ category.name }}
            </button>
            <!-- 第二階層品牌按鈕 -->
            <div
              v-if="selectedCategory === category.id && (availableBrands.get(category.id)?.length > 0)"
              class="ml-4 mt-2 space-y-2"
            >
              <button
                v-for="brand in availableBrands.get(category.id) || []"
                :key="brand"
                class="w-full text-left px-3 py-1 text-sm rounded transition-colors duration-200"
                :class="{
                  'bg-green-200 text-green-800': selectedBrand === brand,
                  'hover:bg-gray-100': selectedBrand !== brand,
                }"
                @click="selectBrand(category.id, brand)"
              >
                {{ brand }}
              </button>
            </div>
          </div>
        </div>

        <!-- 價格範圍 -->
        <div class="bg-white rounded-lg shadow p-4">
          <h2 class="text-xl font-bold mb-4">
            價格範圍
          </h2>
          <div class="space-y-4">
            <div>
              <label class="block text-sm text-gray-600 mb-1">最低價格</label>
              <input
                v-model.number="tempPriceRange.min"
                type="number"
                class="w-full px-3 py-2 border rounded focus:outline-none focus:border-green-500"
                placeholder="最低價格"
              >
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">最高價格</label>
              <input
                v-model.number="tempPriceRange.max"
                type="number"
                class="w-full px-3 py-2 border rounded focus:outline-none focus:border-green-500"
                placeholder="最高價格"
              >
            </div>
            <button
              class="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 transition-colors duration-200"
              @click="applyPriceFilter"
            >
              套用價格篩選
            </button>
          </div>
        </div>

        <!-- 排序方式 -->
        <div class="bg-white rounded-lg shadow p-4">
          <h2 class="text-xl font-bold mb-4">
            排序方式
          </h2>
          <select
            v-model="sortOption"
            class="w-full px-3 py-2 border rounded focus:outline-none focus:border-green-500"
            @change="applySorting"
          >
            <option value="default">
              預設排序
            </option>
            <option value="price-asc">
              價格由低到高
            </option>
            <option value="price-desc">
              價格由高到低
            </option>
            <option value="name-asc">
              名稱 A-Z
            </option>
            <option value="name-desc">
              名稱 Z-A
            </option>
          </select>
        </div>
      </div>

      <!-- 右側商品列表 -->
      <div class="w-3/4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="product in currentPageProducts"
            :key="product.id"
            class="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition-shadow duration-300"
          >
            <img
              :src="product.image_url"
              :alt="product.name"
              class="w-full h-48 object-cover"
            >
            <div class="p-4">
              <h3 class="text-lg font-semibold mb-2 line-clamp-2">
                {{ product.name }}
              </h3>
              <p class="text-gray-600 mb-2 line-clamp-2">
                {{ product.description }}
              </p>
              <!-- 添加匹配品牌顯示 -->
              <div v-if="product.matchedBrands && product.matchedBrands.length > 0" class="mb-2">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="brand in product.matchedBrands"
                    :key="brand"
                    class="inline-block px-2 py-1 text-xs bg-green-100 text-green-800 rounded"
                  >
                    {{ brand }}
                  </span>
                </div>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-green-600 font-bold">NT$ {{ product.price }}</span>
                <button
                  class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors duration-200"
                  @click="viewProductDetail(product.id)"
                >
                  查看詳情
                </button>
              </div>
            </div>
          </div>
        </div>
        <!-- 分頁功能 -->
        <div class="mt-8 space-y-4">
          <!-- 頁碼按鈕區 -->
          <div class="flex justify-center items-center space-x-2">
            <!-- 上一頁按鈕 -->
            <button
              class="px-4 py-2 rounded-lg transition-colors duration-200 flex items-center"
              :class="{
                'bg-gray-200 text-gray-400 cursor-not-allowed': currentPage === 1,
                'bg-green-600 text-white hover:bg-green-700': currentPage !== 1,
              }"
              :disabled="currentPage === 1"
              @click="currentPage > 1 && changePage(currentPage - 1)"
            >
              <span class="material-icons text-lg mr-1" />
              上一頁
            </button>

            <!-- 頁碼按鈕 -->
            <template v-for="page in displayedPages" :key="page">
              <template v-if="typeof page === 'number'">
                <button
                  class="min-w-[40px] h-10 rounded-lg transition-colors duration-200 font-medium"
                  :class="{
                    'bg-green-600 text-white hover:bg-green-700': currentPage === page,
                    'bg-gray-100 text-gray-700 hover:bg-gray-200': currentPage !== page,
                  }"
                  @click="changePage(page)"
                >
                  {{ page }}
                </button>
              </template>
              <span
                v-else
                class="px-2 text-gray-500"
              >
                {{ page }}
              </span>
            </template>

            <!-- 下一頁按鈕 -->
            <button
              class="px-4 py-2 rounded-lg transition-colors duration-200 flex items-center"
              :class="{
                'bg-gray-200 text-gray-400 cursor-not-allowed': currentPage === totalPages,
                'bg-green-600 text-white hover:bg-green-700': currentPage !== totalPages,
              }"
              :disabled="currentPage === totalPages"
              @click="currentPage < totalPages && changePage(currentPage + 1)"
            >
              下一頁
              <span class="material-icons text-lg ml-1" />
            </button>
          </div>

          <!-- 頁碼跳轉區 -->
          <div class="flex justify-center items-center space-x-2">
            <input
              v-model="inputPage"
              type="number"
              min="1"
              :max="totalPages"
              class="w-20 px-3 py-2 border rounded focus:outline-none focus:border-green-500 text-center"
              placeholder="頁碼"
              @keyup.enter="jumpToPage"
            >
            <button
              class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors duration-200"
              @click="jumpToPage"
            >
              跳轉
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
