MENU_ITEMS = [
    {
        'name': '討論區管理',
        'icon': 'chat-square-text',  # Bootstrap Icons 的圖標名稱
        'children': [
            {
                'name': '文章列表',
                'url': '/user-dashboard/forum/posts',
                'icon': 'file-text'
            },
            {
                'name': '分類管理',
                'url': '/user-dashboard/forum/categories',
                'icon': 'tag'
            },
            {
                'name': '評論管理',
                'url': '/user-dashboard/forum/comments',
                'icon': 'chat-dots'
            }
        ]
    },
    {
        'name': 'API測試',
        'icon': 'code-slash',  # Bootstrap Icons 的圖標名稱
        'children': [
            {
                'name': '文章 API',
                'url': '/user-dashboard/api/posts/',
                'icon': 'file-code'
            },
            {
                'name': '分類 API',
                'url': '/user-dashboard/api/categories/',
                'icon': 'diagram-3'
            },
            {
                'name': '評論 API',
                'url': '/user-dashboard/api/comments/',
                'icon': 'chat-text'
            }
        ]
    }
] 