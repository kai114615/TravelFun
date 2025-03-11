<script setup lang="ts">
import { NButton } from 'naive-ui';
import { RouterLink } from 'vue-router';
import { cityData, cityMap, cityPos } from '@/utils/context';

const place_data=[
  {
   tag: "taipei_city",
   place: "臺北市",
   presentation: "台灣首都，融合現代與歷史，擁有台北101與故宮博物院。",
   route: "/travel/city/臺北市",
   picture:new URL('@/assets/台灣圖片/台北市.jpg', import.meta.url).href
  },
  {
   tag: "new_taipei_city",
   place: "新北市",
   presentation: "環繞台北市，擁有美麗的海岸線與山脈，是都市與自然的結合。",
   route: "/travel/city/新北市",
   picture:new URL('@/assets/台灣圖片/新北市.jpg', import.meta.url).href
  },

  {
   tag: "taichung_city",
   place: "臺中市",
   presentation: "文化藝術之都，擁有許多博物館與自然景點。",
   route: "/travel/city/臺中市",
   picture:new URL('@/assets/台灣圖片/台中市.jpg', import.meta.url).href

   
  },

  {
   tag: "tainan_city",
   place: "臺南市",
   presentation: "台灣歷史悠久的城市，擁有古老的廟宇與美食。",
   route: "/travel/city/臺南市",
   picture:new URL('@/assets/台灣圖片/台南市.jpg', import.meta.url).href

  },

  {
   tag: "kaohsiung_city",
   place: "高雄市",
   presentation: "南部大城市，擁有台灣最大的港口及繁華的夜市。",
   route: "/travel/city/高雄市",
   picture:new URL('@/assets/台灣圖片/高雄市.jpg', import.meta.url).href

  },

  {
   tag: "keelung_city",
   place: "基隆市",
   presentation: "位於台灣北端，擁有繁忙的港口及美麗的海景。",
   route: "/travel/city/基隆市",
   picture:new URL('@/assets/台灣圖片/基隆市.jpg', import.meta.url).href

  },

  {
   tag: "taoyuan_country",
   place: "桃園市",
   presentation: "擁有台灣主要國際機場，是重要的交通樞紐。",
   route: "/travel/city/桃園市",
   picture:new URL('@/assets/台灣圖片/桃園市.jpg', import.meta.url).href

  },

  

  {
   tag: "hsinchu_country",
   place: "新竹縣",
   presentation: "科技園區與古老文化相結合，擁有豐富的歷史景點。",
   route: "/trravel/city/新竹縣",
   picture:new URL('@/assets/台灣圖片/新竹縣.jpg', import.meta.url).href

  },

  {
   tag: "miaoli_country",
   place: "苗栗縣",
   presentation: "擁有美麗的山區風光與豐富的客家文化",
   route: "/travel/city/苗栗縣",
   picture:new URL('@/assets/台灣圖片/苗栗縣.jpg', import.meta.url).href

  },

  {
   tag: "changhua_country",
   place: "彰化縣",
   presentation: "以傳統工藝和文化著名，擁有古老的廟宇。",
   route: "/travel/city/彰化縣",
   picture:new URL('@/assets/台灣圖片/彰化縣.jpg', import.meta.url).href

  },

  {
   tag: "nantou_country",
   place: "南投縣",
   presentation: "以日月潭為代表的美麗湖泊與山區風景。",
   route: "/travel/city/南投縣",
   picture:new URL('@/assets/台灣圖片/南投縣.jpg', import.meta.url).href

  },

  {
   tag: "yunlin_country",
   place: "雲林縣",
   presentation: "農業重鎮，擁有豐富的自然資源與文化遺產。",
   route: "/travel/city/雲林縣",
   picture:new URL('@/assets/台灣圖片/雲林縣.jpg', import.meta.url).href

  },


  {
   tag: "chiayi_country",
   place: "嘉義縣",
   presentation: "擁有美麗的山脈與豐富的農業資源。",
   route: "/travel/city/嘉義縣",
   picture:new URL('@/assets/台灣圖片/嘉義縣.jpg', import.meta.url).href

  },

  {
   tag: "pingtung_country",
   place: "屏東縣",
   presentation: "台灣最南端，擁有美麗的海灘與自然景點。",
   route: "/travel/city/屏東縣",
   picture:new URL('@/assets/台灣圖片/屏東縣.jpg', import.meta.url).href

  },

  {
   tag: "yilan_country",
   place: "宜蘭縣",
   presentation: "風景如畫，擁有美麗的海岸線與溫泉。",
   route: "/travel/city/宜蘭縣",
   picture:new URL('@/assets/台灣圖片/宜蘭縣.jpg', import.meta.url).href

  },

  {
   tag: "hualien_country",
   place: "花蓮縣",
   presentation: "擁有壯麗的太魯閣峽谷與美麗的海岸。",
   route: "/travel/city/花蓮縣",
   picture:new URL('@/assets/台灣圖片/花蓮縣.jpg', import.meta.url).href

  },

  {
   tag: "taitung_country",
   place: "臺東縣",
   presentation: "自然景觀豐富，是台灣東部的度假天堂。",
   route: "/travel/city/臺東縣",
   picture:new URL('@/assets/台灣圖片/台東縣.jpg', import.meta.url).href

  },

  {
   tag: "penghu_country",
   place: "澎湖縣",
   presentation: "由多個小島組成，擁有美麗的沙灘與海洋生態",
   route: "/travel/city/澎湖縣",
   picture:new URL('@/assets/台灣圖片/澎湖縣.jpg', import.meta.url).href

  },

  {
   tag: "kinmen_country",
   place: "金門縣",
   presentation: "具有豐富歷史背景，擁有古老的軍事遺跡與美麗的海景。",
   route: "/travel/city/金門縣"
  },

  {
   tag: "lienchiang_country",
   place: "連江縣",
   presentation: "位於台灣海峽，擁有傳統的閩南文化與風光明媚的海島景致。",
   route: "/travel/city/連江縣"
   
  },
];

const matchCityName = (name1: string, name2: string): boolean => {
  // 取前兩個字進行比對
  const first2Chars1 = name1.slice(0, 2);
  const first2Chars2 = name2.slice(0, 2);
  
  // 處理臺/台互換的情況
  const normalized1 = first2Chars1.replace('臺', '台');
  const normalized2 = first2Chars2.replace('臺', '台');
  
  return normalized1 === normalized2;
};

const findRouteByCity = (cityName: string): string => {
  const matchedCity = place_data.find(item => matchCityName(item.place, cityName));
  return matchedCity?.route || '/';
};
</script>

<template>
  <div class="flex flex-col gap-3 px-4 py-3">
    <template v-for="(citys, key) in cityData" :key="key">
      <div class="text-sm-content">
        <p class="w-full py-1 text-cc-accent border-b border-cc-accent">
          {{ cityPos.get(key) }}
        </p>
        <div class="my-2 flex items-center gap-4 flex-wrap">
          <template v-for="cityName in citys" :key="cityName">
            <RouterLink v-slot="{ navigate }" custom :to="findRouteByCity(cityMap.get(cityName) || '')">
              <NButton text @click="navigate">
                {{ cityMap.get(cityName) }}
              </NButton>
            </RouterLink>
          </template>
        </div>
      </div>
    </template>
  </div>
</template>