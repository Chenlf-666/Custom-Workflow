export const sideBarList = [
    {
      icon: 'HomeFilled',
      index: '/dashboard',
      title: '系统首页',
      permission: '1'
    },
    {
      icon: 'Tickets',
      index: '3',
      title: '审批流程',
      permission: '1',
      subs: [
      ]
    },
    {
      icon: 'Management',
      index: '2',
      title: '管理中心',
      permission: '1',
      subs: [
        {
          index: '/worksheet',
          title: '工单管理',
          permission: '1'
        }
      ]
    },
    {
      icon: 'Tools',
      index: '5',
      title: '系统配置',
      permission: '1',
      subs: [
        {
          index: '/users',
          title: '用户管理',
          permission: '1'
        },
        {
          index: '/permission',
          title: '权限管理',
          permission: '9'
        },
        {
          index: '/log',
          title: '日志管理',
          permission: '9'
        },
        {
          index: '/customWorkflows',
          title: '工作流管理',
          permission: '1'
        }
      ]
    }
  ];

  export const breadcrumbs = [
    { name: '系统首页', url: '/dashboard' },
    { name: '管理中心', url: '/1' },
    { name: '系统配置', url: '/5' },
    { name: '用户管理', url: '/users' },
    { name: '权限管理', url: '/permission' },
    { name: '日志管理', url: '/log' },
    { name: '工作台', url: '/6' },
    { name: '工作流管理', url: '/customWorkflows'},
    { name: '工单管理', url: '/worksheet'},
  ]