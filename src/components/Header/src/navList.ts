import { h } from 'vue';
import { RouterLink } from 'vue-router';
import type { CollapseProps } from 'naive-ui';
import { NCollapseItem, NIcon } from 'naive-ui';
import { 
  StorefrontOutlined,
  LocalActivityOutlined,
  ExploreOutlined,
  ForumOutlined,
  PersonOutlineOutlined,
  InfoOutlined
} from '@vicons/material';
import { Area, Menu } from './Area';
import router from '@/router/';
import { useUserStore } from '@/stores/user';

const routerlinkClass = 'flex items-center gap-2 whitespace-nowrap';
const routerlinkStyle = { writingMode: 'horizontal-tb' };
const mallRouterTo = { name: 'Mall' };
const activityRouterTo = { name: 'Activity' };
const tourRouterTo = { name: 'Country', params: { countryName: 'taiwan' } };
const forumRouterTo = { name: 'Forum' };
const memberRouterTo = { name: 'MemberDashboard' };
const aboutRouterTo = { name: 'About' };

export const handleItemHeaderClick: CollapseProps['onItemHeaderClick'] = ({
  name,
}) => {
  if (name === 'mall')
    router.push(mallRouterTo);
  else if (name === 'activity')
    router.push(activityRouterTo);
  else if (name === 'tours')
    router.push(tourRouterTo);
  else if (name === 'forum')
    router.push(forumRouterTo);
  else if (name === 'member')
    router.push(memberRouterTo);
  else if (name === 'about')
    router.push(aboutRouterTo);
};

export const createNavList = () => {
  const userStore = useUserStore();
  
  return [
    {
      id: 'area',
      title: '選地區',
      component: h(Area),
      mobileComponent: h(NCollapseItem,
        {
          name: 'area',
        },
        {
          default: () => h(Menu),
          header: () => h('div',
            {
              class: 'flex-1',
            },
            '選地區',
          ),
        },
      ),
    },
    {
      id: 'mall',
      title: '商城中心',
      component: h(RouterLink,
        {
          to: mallRouterTo,
          class: routerlinkClass,
          style: routerlinkStyle,
        },
        () => [
          h(NIcon, null, { default: () => h(StorefrontOutlined) }),
          '商城中心',
        ],
      ),
      mobileComponent: h(NCollapseItem,
        {
          name: 'mall',
        },
        {
          header: () => h('div', { class: 'flex-1' }, '商城中心'),
        },
      ),
    },
    {
      id: 'activity',
      title: '主題育樂',
      component: h(RouterLink,
        {
          to: activityRouterTo,
          class: routerlinkClass,
          style: routerlinkStyle,
        },
        () => [
          h(NIcon, null, { default: () => h(LocalActivityOutlined) }),
          '主題育樂',
        ],
      ),
      mobileComponent: h(NCollapseItem,
        {
          name: 'activity',
        },
        {
          header: () => h('div', { class: 'flex-1' }, '主題育樂'),
        },
      ),
    },
    {
      id: 'tours',
      title: 'AI推薦行程',
      component: h(RouterLink,
        {
          to: tourRouterTo,
          class: routerlinkClass,
          style: routerlinkStyle,
        },
        () => [
          h(NIcon, null, { default: () => h(ExploreOutlined) }),
          'AI推薦行程',
        ],
      ),
      mobileComponent: h(NCollapseItem,
        {
          name: 'tours',
        },
        {
          header: () => h('div', { class: 'flex-1' }, 'AI推薦行程'),
        },
      ),
    },
    {
      id: 'forum',
      title: '討論區',
      component: h(RouterLink,
        {
          to: forumRouterTo,
          class: routerlinkClass,
          style: routerlinkStyle,
        },
        () => [
          h(NIcon, null, { default: () => h(ForumOutlined) }),
          '討論區',
        ],
      ),
      mobileComponent: h(NCollapseItem,
        {
          name: 'forum',
        },
        {
          header: () => h('div', { class: 'flex-1' }, '討論區'),
        },
      ),
    },
    ...(userStore.loginStatus ? [{
      id: 'member',
      title: '會員中心',
      component: h(RouterLink,
        {
          to: memberRouterTo,
          class: routerlinkClass,
          style: routerlinkStyle,
          'active-class': 'text-cc-accent',
          'exact-active-class': 'text-cc-accent'
        },
        () => [
          h(NIcon, null, { default: () => h(PersonOutlineOutlined) }),
          '會員中心',
        ],
      ),
      mobileComponent: h(NCollapseItem,
        {
          name: 'member',
        },
        {
          header: () => h('div', { class: 'flex-1' }, '會員中心'),
        },
      ),
    }] : []),
    {
      id: 'about',
      title: '關於我們',
      component: h(RouterLink,
        {
          to: aboutRouterTo,
          class: routerlinkClass,
          style: routerlinkStyle,
        },
        () => [
          h(NIcon, null, { default: () => h(InfoOutlined) }),
          '關於我們',
        ],
      ),
      mobileComponent: h(NCollapseItem,
        {
          name: 'about',
        },
        {
          header: () => h('div', { class: 'flex-1' }, '關於我們'),
        },
      ),
    },
  ];
};

export default {};
