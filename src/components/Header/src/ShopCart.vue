<script setup lang="ts">
import {
  ShoppingCartOutlined,
} from '@vicons/material';
import type { TooltipProps } from 'naive-ui';
import { NBadge, NButton, NCard, NDrawer, NDrawerContent, NEmpty, NIcon, NList, NListItem, NScrollbar, NThing, NTooltip } from 'naive-ui';
import { RouterLink, onBeforeRouteUpdate } from 'vue-router';
import { reactive } from 'vue';
import type { Cart, DrawerActive } from '@/types';

type TooltipThemeOverrides = NonNullable<TooltipProps['themeOverrides']>

defineProps<{
  totalNum: number
  cartList: Cart[]
  isMobile: boolean
}>();

const emit = defineEmits<{
  (e: 'active', target: string): void
}>();

const tooltipThemeOverrides: TooltipThemeOverrides = {
  padding: '0px',
  color: '#fff',
};

const activate: DrawerActive = reactive({
  active: false,
  placement: 'bottom',
});

function toggleActive() {
  if (!activate.active)
    emit('active', 'cart');

  activate.active = !activate.active;
};

const closeActive = () => activate.active = false;

onBeforeRouteUpdate(() => {
  closeActive();
})

defineExpose({
  closeActive,
});
</script>

<template>
  <NTooltip
    v-if="!isMobile"
    placement="bottom"
    trigger="hover"
    :theme-overrides="tooltipThemeOverrides"
    :style="{ width: '400px' }"
  >
    <template #trigger>
      <NBadge color="#EE5220" :max="99" :value="totalNum">
        <NIcon size="24" color="white" class="cursor-pointer">
          <ShoppingCartOutlined />
        </NIcon>
      </NBadge>
    </template>
    <NCard
      embedded
      :bordered="false"
      :segmented="{
        content: true,
        footer: 'soft',
      }"
      size="small"
    >
      <template v-if="totalNum">
        <NScrollbar style="max-height: 340px">
          <NList hoverable clickable>
            <template
              v-for="item in cartList"
              :key="item.product_id"
            >
              <NListItem>
                <template #prefix>
                  <div class="w-14 aspect-square">
                    <img class="img" :src="item.product?.imageUrl" :alt="item.product?.title">
                  </div>
                </template>
                <NThing :title="item.product?.title">
                  <template #description>
                    <div class="flex flex-col gap-1">
                      <span class="text-sm text-gray-500">數量: {{ item.qty }}</span>
                      <span class="text-sm font-medium text-green-600">
                        NT$ {{ item.final_total }}
                      </span>
                    </div>
                  </template>
                </NThing>
              </NListItem>
            </template>
          </NList>
        </NScrollbar>
      </template>
      <NEmpty v-else description="您的購物車是空的" />
      <template #footer>
        <div class="flex items-center justify-between">
          <span class="text-sm text-gray-600">共 {{ totalNum }} 件商品</span>
          <RouterLink
            to="/cart"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
          >
            前往購物車
          </RouterLink>
        </div>
      </template>
    </NCard>
  </NTooltip>
  <template v-else>
    <NButton text @click="toggleActive">
      <NBadge color="#EE5220" :max="99" :value="totalNum">
        <NIcon size="24" color="white" class="cursor-pointer">
          <ShoppingCartOutlined />
        </NIcon>
      </NBadge>
    </NButton>
    <NDrawer
      v-model:show="activate.active"
      style="top: 64px"
      height="undefined"
      :show-mask="false"
      :mask-closable="false"
      :placement="activate.placement"
    >
      <NDrawerContent title="購物車" footer-style="justify-content: space-between; align-items: center;">
        <template v-if="totalNum">
          <NList hoverable clickable>
            <template
              v-for="item in cartList"
              :key="item.product_id"
            >
              <RouterLink
                v-slot="{ navigate }"
                custom
                :to="{ name: 'MallProductDetail', params: { id: item.product_id } }"
              >
                <NListItem
                  class="py-5 flex gap-5 cursor-pointer"
                  @click="navigate"
                >
                  <template #prefix>
                    <div class="w-28 aspect-square rounded-m overflow-hidden">
                      <img class="img" :src="item.product?.imageUrl" :alt="item.product?.title">
                    </div>
                  </template>
                  <NThing :title="item.product?.title">
                    <template #description>
                      <div class="flex flex-col gap-1">
                        <span class="text-sm text-gray-500">數量: {{ item.qty }}</span>
                        <span class="text-sm font-medium text-green-600">
                          NT$ {{ item.final_total }}
                        </span>
                      </div>
                    </template>
                  </NThing>
                </NListItem>
              </RouterLink>
            </template>
          </NList>
        </template>
        <NEmpty v-else description="您的購物車是空的" />
        <template #footer>
          <span class="text-sm text-gray-600">共 {{ totalNum }} 件商品</span>
          <RouterLink
            to="/cart"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
          >
            前往購物車
          </RouterLink>
        </template>
      </NDrawerContent>
    </NDrawer>
  </template>
</template>

<style scoped>
.img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
