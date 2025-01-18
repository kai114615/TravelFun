export const sidebarConfig = {
  items: [
    {
      title: '儀表板',
      icon: DashboardIcon,
      path: '/dashboard'
    },
    {
      title: '系統管理',
      icon: SettingsIcon,
      children: [
        {
          title: '用戶管理',
          path: '/users'
        },
        {
          title: '權限設置',
          path: '/permissions'
        }
      ]
    }
  ]
} 