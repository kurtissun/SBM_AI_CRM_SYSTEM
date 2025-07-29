import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Language = 'en' | 'zh'

interface LanguageState {
  language: Language
  setLanguage: (language: Language) => void
  t: (key: string) => string
}

// Translation dictionary
const translations = {
  en: {
    // Login
    'login.title': 'Welcome to SBM AI CRM',
    'login.subtitle': 'Enterprise Customer Intelligence Platform',
    'login.email': 'Email Address or Username',
    'login.password': 'Password',
    'login.rememberMe': 'Remember me',
    'login.forgotPassword': 'Forgot password?',
    'login.signIn': 'Sign in',
    'login.signingIn': 'Signing in...',
    'login.createAccount': 'Create Account',
    'login.demoCredentials': 'Demo credentials: admin@sbm.com / admin123',
    'login.invalidCredentials': 'Invalid email/username or password',
    'login.accountCreated': 'Account created successfully!',
    
    // Common
    'common.loading': 'Loading...',
    'common.save': 'Save',
    'common.cancel': 'Cancel',
    'common.delete': 'Delete',
    'common.edit': 'Edit',
    'common.view': 'View',
    'common.export': 'Export',
    'common.import': 'Import',
    'common.search': 'Search',
    'common.filter': 'Filter',
    'common.add': 'Add',
    'common.create': 'Create',
    'common.update': 'Update',
    'common.confirm': 'Confirm',
    'common.yes': 'Yes',
    'common.no': 'No',
    
    // Navigation
    'nav.dashboard': 'Dashboard',
    'nav.customers': 'Customer Intelligence',
    'nav.campaigns': 'Campaign Center',
    'nav.segmentation': 'Segmentation Studio',
    'nav.analytics': 'Analytics & Insights',
    'nav.journeys': 'Journey & Automation',
    'nav.aiAssistant': 'AI Assistant',
    'nav.operations': 'Operations Center',
    'nav.reports': 'Reports Studio',
    'nav.mallOps': 'Mall Operations',
    'nav.camera': 'Camera Intelligence',
    'nav.chineseMarket': 'Chinese Market',
    'nav.loyalty': 'Loyalty & VIP',
    'nav.retail': 'Retail Intelligence',
    'nav.simulator': 'Economic Simulator',
    'nav.voice': 'Voice of Customer',
    'nav.admin': 'Admin Center',
    
    // Dashboard
    'dashboard.welcome': 'Welcome back',
    'dashboard.overview': 'Business Overview',
    'dashboard.totalCustomers': 'Total Customers',
    'dashboard.activeToday': 'Active Today',
    'dashboard.revenue': 'Revenue',
    'dashboard.growthRate': 'Growth Rate',
    
    // Hero Section
    'hero.title': 'Intelligent CRM for Modern Retail',
    'hero.subtitle': 'Harness the power of AI to transform your customer relationships',
    'hero.aiInsights': 'AI-Powered Insights',
    'hero.aiInsightsDesc': '22 AI engines for predictive analytics',
    'hero.realtime': 'Real-time Analytics',
    'hero.realtimeDesc': 'Monitor performance as it happens',
    'hero.personalization': 'Hyper-Personalization',
    'hero.personalizationDesc': 'Tailored experiences for every customer',
    
    // Refresh Key
    'refreshKey.title': 'Refresh Key',
    'refreshKey.current': 'Current Key',
    'refreshKey.generate': 'Generate New Key',
    'refreshKey.expires': 'Expires',
    'refreshKey.description': 'This 8-character key refreshes weekly and provides secure access.',
  },
  zh: {
    // 登录
    'login.title': '欢迎使用 SBM AI CRM',
    'login.subtitle': '企业级客户智能平台',
    'login.email': '邮箱地址或用户名',
    'login.password': '密码',
    'login.rememberMe': '记住我',
    'login.forgotPassword': '忘记密码？',
    'login.signIn': '登录',
    'login.signingIn': '登录中...',
    'login.createAccount': '创建账户',
    'login.demoCredentials': '演示账户: admin@sbm.com / admin123',
    'login.invalidCredentials': '邮箱/用户名或密码无效',
    'login.accountCreated': '账户创建成功！',
    
    // 通用
    'common.loading': '加载中...',
    'common.save': '保存',
    'common.cancel': '取消',
    'common.delete': '删除',
    'common.edit': '编辑',
    'common.view': '查看',
    'common.export': '导出',
    'common.import': '导入',
    'common.search': '搜索',
    'common.filter': '筛选',
    'common.add': '添加',
    'common.create': '创建',
    'common.update': '更新',
    'common.confirm': '确认',
    'common.yes': '是',
    'common.no': '否',
    
    // 导航
    'nav.dashboard': '仪表板',
    'nav.customers': '客户智能',
    'nav.campaigns': '营销中心',
    'nav.segmentation': '分群工作室',
    'nav.analytics': '分析洞察',
    'nav.journeys': '客户旅程与自动化',
    'nav.aiAssistant': 'AI 助手',
    'nav.operations': '运营中心',
    'nav.reports': '报表工作室',
    'nav.mallOps': '商场运营',
    'nav.camera': '摄像头智能',
    'nav.chineseMarket': '中国市场',
    'nav.loyalty': '忠诚度与VIP',
    'nav.retail': '零售智能',
    'nav.simulator': '经济模拟器',
    'nav.voice': '客户之声',
    'nav.admin': '管理中心',
    
    // 仪表板
    'dashboard.welcome': '欢迎回来',
    'dashboard.overview': '业务概览',
    'dashboard.totalCustomers': '总客户数',
    'dashboard.activeToday': '今日活跃',
    'dashboard.revenue': '营收',
    'dashboard.growthRate': '增长率',
    
    // 主页内容
    'hero.title': '现代零售智能CRM',
    'hero.subtitle': '利用AI力量变革您的客户关系',
    'hero.aiInsights': 'AI驱动洞察',
    'hero.aiInsightsDesc': '22个AI引擎预测分析',
    'hero.realtime': '实时分析',
    'hero.realtimeDesc': '实时监控业务表现',
    'hero.personalization': '超个性化',
    'hero.personalizationDesc': '为每位客户定制专属体验',
    
    // 刷新密钥
    'refreshKey.title': '刷新密钥',
    'refreshKey.current': '当前密钥',
    'refreshKey.generate': '生成新密钥',
    'refreshKey.expires': '过期时间',
    'refreshKey.description': '这个8字符的密钥每周刷新一次，提供安全访问。',
  }
}

export const useLanguageStore = create<LanguageState>()(
  persist(
    (set, get) => ({
      language: 'en',
      setLanguage: (language: Language) => set({ language }),
      t: (key: string) => {
        const { language } = get()
        const translation = translations[language]?.[key] || translations.en[key] || key
        return translation
      }
    }),
    {
      name: 'language-storage',
    }
  )
)