import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  ArrowLeft, ArrowRight, Users, Target, Calendar, DollarSign, 
  Image, Video, FileText, Settings, Sparkles, Brain, Check,
  ChevronDown, Plus, X, Upload, Eye, Play, BarChart3
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { useTranslation } from '@/contexts/TranslationContext'
import { useCampaignStore } from '@/stores/campaignStore'

interface CampaignFormData {
  name: string
  objective: string
  audience: {
    demographics: string[]
    interests: string[]
    behaviors: string[]
    customSegments: string[]
  }
  budget: {
    type: 'daily' | 'lifetime'
    amount: number
    bidStrategy: string
  }
  schedule: {
    startDate: string
    endDate: string
    timezone: string
  }
  creatives: {
    images: File[]
    videos: File[]
    copy: {
      headline: string
      description: string
      cta: string
    }
  }
}

export const CreateCampaign: React.FC = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { addCampaign } = useCampaignStore()
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState<CampaignFormData>({
    name: '',
    objective: '',
    audience: {
      demographics: [],
      interests: [],
      behaviors: [],
      customSegments: []
    },
    budget: {
      type: 'daily',
      amount: 1000,
      bidStrategy: 'automatic'
    },
    schedule: {
      startDate: new Date().toISOString().split('T')[0],
      endDate: '',
      timezone: 'Asia/Shanghai'
    },
    creatives: {
      images: [],
      videos: [],
      copy: {
        headline: '',
        description: '',
        cta: ''
      }
    }
  })

  const steps = [
    {
      id: 'objective',
      title: t('campaign.campaignObjective'),
      subtitle: t('campaign.objectiveSubtitle'),
      icon: Target
    },
    {
      id: 'audience',
      title: t('campaign.audienceTargeting'),
      subtitle: t('campaign.audienceSubtitle'),
      icon: Users
    },
    {
      id: 'budget',
      title: t('campaign.budgetSchedule'),
      subtitle: t('campaign.budgetSubtitle'),
      icon: DollarSign
    },
    {
      id: 'creative',
      title: t('campaign.creativeAssets'),
      subtitle: t('campaign.creativeSubtitle'),
      icon: Image
    },
    {
      id: 'review',
      title: t('campaign.reviewLaunch'),
      subtitle: t('campaign.reviewSubtitle'),
      icon: Check
    }
  ]

  const objectives = [
    { id: 'awareness', label: t('campaign.brandAwareness'), description: t('campaign.awarenessDesc'), icon: Eye },
    { id: 'traffic', label: t('campaign.websiteTraffic'), description: t('campaign.trafficDesc'), icon: BarChart3 },
    { id: 'engagement', label: t('campaign.engagement'), description: t('campaign.engagementDesc'), icon: Target },
    { id: 'leads', label: t('campaign.leadGeneration'), description: t('campaign.leadsDesc'), icon: Users },
    { id: 'sales', label: t('campaign.sales'), description: t('campaign.salesDesc'), icon: DollarSign },
    { id: 'app', label: t('campaign.appPromotes'), description: t('campaign.appDesc'), icon: Play }
  ]

  const demographics = [
    { id: 'age_18_24', label: '18-24', type: 'age' },
    { id: 'age_25_34', label: '25-34', type: 'age' },
    { id: 'age_35_44', label: '35-44', type: 'age' },
    { id: 'age_45_54', label: '45-54', type: 'age' },
    { id: 'age_55_plus', label: '55+', type: 'age' },
    { id: 'male', label: t('campaign.male'), type: 'gender' },
    { id: 'female', label: t('campaign.female'), type: 'gender' },
    { id: 'tier1', label: t('campaign.tier1Cities'), type: 'location' },
    { id: 'tier2', label: t('campaign.tier2Cities'), type: 'location' },
    { id: 'tier3', label: t('campaign.tier3Cities'), type: 'location' }
  ]

  const interests = [
    'Fashion & Style', 'Technology', 'Travel', 'Food & Dining', 'Fitness & Health',
    'Business & Finance', 'Entertainment', 'Sports', 'Automotive', 'Home & Garden',
    'Beauty & Cosmetics', 'Education', 'Art & Culture', 'Music', 'Photography'
  ]

  const behaviors = [
    t('campaign.onlineShoppers'), t('campaign.premiumBrands'), t('campaign.mobileFocused'),
    t('campaign.socialActive'), t('campaign.earlyAdopters'), t('campaign.priceConscious'),
    t('campaign.brandLoyal'), t('campaign.impulseBuyers')
  ]

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleLaunchCampaign = () => {
    toast.success(t('campaign.campaignCreating'))
    
    // Generate campaign name if not provided
    const campaignName = formData.name || `${objectives.find(o => o.id === formData.objective)?.label || 'New'} Campaign`
    
    // Create comprehensive campaign object with all customizations
    const campaignData = {
      name: campaignName,
      objective: formData.objective,
      status: 'active' as const,
      budget: {
        type: formData.budget.type,
        amount: formData.budget.amount,
        spent: 0,
        bidStrategy: formData.budget.bidStrategy
      },
      audience: {
        size: Math.floor(Math.random() * 100000) + 50000, // Mock audience size
        demographics: formData.audience.demographics,
        interests: formData.audience.interests,
        behaviors: formData.audience.behaviors,
        customSegments: formData.audience.customSegments
      },
      performance: {
        impressions: 0,
        clicks: 0,
        conversions: 0,
        ctr: 0,
        cpc: 0,
        roi: 0
      },
      schedule: formData.schedule,
      creatives: {
        copy: formData.creatives.copy,
        mediaCount: {
          images: formData.creatives.images.length,
          videos: formData.creatives.videos.length
        }
      },
      createdBy: 'User',
      settings: {
        aiGenerated: {
          copyGenerated: !!(formData.creatives.copy.headline || formData.creatives.copy.description),
          audienceSuggestions: formData.audience.customSegments.length > 0
        }
      }
    }
    
    setTimeout(() => {
      // Save campaign to store
      addCampaign(campaignData)
      toast.success(t('campaign.campaignCreated'))
      navigate('/campaigns')
    }, 2000)
  }

  const handleSaveDraft = () => {
    toast.success(t('campaign.draftSaved'))
  }

  const generateAICopy = () => {
    toast.success(t('campaign.generatingCreatives'))
    
    // Generate contextual copy based on selected options
    setTimeout(() => {
      const objective = objectives.find(o => o.id === formData.objective)
      const selectedDemographics = formData.audience.demographics
      const selectedInterests = formData.audience.interests
      const budgetAmount = formData.budget.amount
      
      // AI-generated copy templates based on campaign parameters
      const copyTemplates = {
        awareness: {
          headlines: [
            'Discover the Future of Innovation',
            'Experience Premium Quality Like Never Before',
            'Introducing Revolutionary Solutions for Modern Life'
          ],
          descriptions: [
            'Join thousands of satisfied customers who trust our brand for exceptional quality and innovation.',
            'Experience cutting-edge technology designed to enhance your daily life and exceed your expectations.',
            'Discover why leading experts choose our premium products for unmatched performance and reliability.'
          ]
        },
        traffic: {
          headlines: [
            'Explore Our Complete Collection Online',
            'Browse Thousands of Premium Products',
            'Visit Our Store for Exclusive Deals'
          ],
          descriptions: [
            'Browse our extensive collection online and discover amazing deals on premium products with fast, free shipping.',
            'Visit our website to explore exclusive collections, read customer reviews, and find your perfect match.',
            'Discover our user-friendly online store featuring detailed product guides and expert recommendations.'
          ]
        },
        engagement: {
          headlines: [
            'Join Our Growing Community Today',
            'Connect with Like-Minded Enthusiasts',
            'Share Your Story with Our Community'
          ],
          descriptions: [
            'Join our vibrant community of passionate users and share your experiences with thousands of members.',
            'Connect with fellow enthusiasts, share tips, and discover new ways to make the most of your experience.',
            'Become part of our exclusive community and enjoy member-only benefits, events, and special offers.'
          ]
        },
        leads: {
          headlines: [
            'Get Your Free Consultation Today',
            'Unlock Exclusive Insights and Tips',
            'Start Your Journey with Expert Guidance'
          ],
          descriptions: [
            'Get personalized recommendations from our experts and receive a complimentary consultation tailored to your needs.',
            'Sign up for exclusive insights, expert tips, and early access to new products and special promotions.',
            'Connect with our specialists for a free consultation and discover solutions perfectly matched to your requirements.'
          ]
        },
        sales: {
          headlines: [
            'Limited Time: Up to 50% Off Premium Products',
            'Shop Now and Save on Best-Selling Items',
            'Exclusive Deals on Top-Rated Products'
          ],
          descriptions: [
            'Shop our exclusive sale featuring premium products at unbeatable prices. Limited time offer with free shipping over ¥200.',
            'Don\'t miss out on incredible savings on our most popular items. Premium quality, exceptional value, guaranteed satisfaction.',
            'Take advantage of our special promotion and save big on top-rated products trusted by thousands of customers.'
          ]
        },
        app: {
          headlines: [
            'Download Our App for Exclusive Features',
            'Get the App and Unlock Premium Benefits',
            'Experience More with Our Mobile App'
          ],
          descriptions: [
            'Download our free app and enjoy exclusive features, personalized recommendations, and member-only deals.',
            'Get instant access to premium features, real-time updates, and seamless shopping experience on your mobile device.',
            'Download now and discover enhanced functionality, offline access, and exclusive app-only promotions.'
          ]
        }
      }
      
      // Select appropriate template based on objective
      const templates = copyTemplates[formData.objective as keyof typeof copyTemplates] || copyTemplates.sales
      
      // Customize based on audience demographics
      let audienceContext = ''
      if (selectedDemographics.includes('age_18_24') || selectedDemographics.includes('age_25_34')) {
        audienceContext = 'young professionals and trendsetters'
      } else if (selectedDemographics.includes('age_35_44') || selectedDemographics.includes('age_45_54')) {
        audienceContext = 'experienced professionals and families'
      } else if (selectedDemographics.includes('vip_segment')) {
        audienceContext = 'VIP customers and premium members'
      }
      
      // Customize based on interests
      let interestContext = ''
      if (selectedInterests.includes('Technology')) {
        interestContext = 'tech-savvy individuals'
      } else if (selectedInterests.includes('Fashion & Style')) {
        interestContext = 'style-conscious consumers'
      } else if (selectedInterests.includes('Business & Finance')) {
        interestContext = 'business professionals'
      }
      
      // Select random template and customize
      const randomHeadline = templates.headlines[Math.floor(Math.random() * templates.headlines.length)]
      const randomDescription = templates.descriptions[Math.floor(Math.random() * templates.descriptions.length)]
      
      // Determine CTA based on objective
      const ctaMapping = {
        awareness: 'learn_more',
        traffic: 'shop_now',
        engagement: 'sign_up',
        leads: 'contact_us',
        sales: 'shop_now',
        app: 'download'
      }
      
      setFormData(prev => ({
        ...prev,
        creatives: {
          ...prev.creatives,
          copy: {
            headline: randomHeadline,
            description: randomDescription,
            cta: ctaMapping[formData.objective as keyof typeof ctaMapping] || 'learn_more'
          }
        }
      }))
      
      toast.success(t('campaign.creativesGenerated'))
    }, 2000)
  }

  const renderObjectiveStep = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('campaign.whatIsGoal')}</h2>
        <p className="text-gray-600">{t('campaign.selectObjective')}</p>
      </div>
      
      {/* Campaign Name */}
      <div className="max-w-md mx-auto mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-2">Campaign Name</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter campaign name (optional)"
        />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {objectives.map((objective) => (
          <button
            key={objective.id}
            onClick={() => setFormData(prev => ({ ...prev, objective: objective.id }))}
            className={`p-6 border-2 rounded-xl text-left transition-all hover:shadow-md ${
              formData.objective === objective.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-start space-x-4">
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                formData.objective === objective.id ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600'
              }`}>
                <objective.icon className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">{objective.label}</h3>
                <p className="text-sm text-gray-600">{objective.description}</p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  )

  const renderAudienceStep = () => (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('campaign.whoIsAudience')}</h2>
        <p className="text-gray-600">{t('campaign.defineAudience')}</p>
      </div>

      {/* AI Audience Suggestions */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border border-purple-200">
        <div className="flex items-start space-x-4">
          <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-2">{t('campaign.aiAudienceInsights')}</h3>
            <p className="text-sm text-gray-600 mb-4">{t('campaign.aiAudienceDesc')}</p>
            <div className="flex flex-wrap gap-2">
              {['VIP Customers (1.2K)', 'Premium Shoppers (4.8K)', 'Weekend Browsers (2.3K)'].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => {
                    setFormData(prev => ({
                      ...prev,
                      audience: {
                        ...prev.audience,
                        customSegments: [...prev.audience.customSegments, suggestion]
                      }
                    }))
                    toast.success(`Added ${suggestion} to targeting`)
                  }}
                  className="px-3 py-1 bg-white border border-purple-200 rounded-full text-sm hover:bg-purple-50 hover:border-purple-300 transition-colors"
                >
                  <Plus className="w-3 h-3 inline mr-1" />
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Demographics */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-4">{t('campaign.demographics')}</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {demographics.map((demo) => (
            <button
              key={demo.id}
              onClick={() => {
                const isSelected = formData.audience.demographics.includes(demo.id)
                setFormData(prev => ({
                  ...prev,
                  audience: {
                    ...prev.audience,
                    demographics: isSelected
                      ? prev.audience.demographics.filter(d => d !== demo.id)
                      : [...prev.audience.demographics, demo.id]
                  }
                }))
              }}
              className={`p-3 border rounded-lg text-sm text-center transition-colors ${
                formData.audience.demographics.includes(demo.id)
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {demo.label}
            </button>
          ))}
        </div>
      </div>

      {/* Interests */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-4">{t('campaign.interests')}</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {interests.map((interest) => (
            <button
              key={interest}
              onClick={() => {
                const isSelected = formData.audience.interests.includes(interest)
                setFormData(prev => ({
                  ...prev,
                  audience: {
                    ...prev.audience,
                    interests: isSelected
                      ? prev.audience.interests.filter(i => i !== interest)
                      : [...prev.audience.interests, interest]
                  }
                }))
              }}
              className={`p-3 border rounded-lg text-sm text-center transition-colors ${
                formData.audience.interests.includes(interest)
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {interest}
            </button>
          ))}
        </div>
      </div>

      {/* Behaviors */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-4">{t('campaign.behaviors')}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {behaviors.map((behavior) => (
            <button
              key={behavior}
              onClick={() => {
                const isSelected = formData.audience.behaviors.includes(behavior)
                setFormData(prev => ({
                  ...prev,
                  audience: {
                    ...prev.audience,
                    behaviors: isSelected
                      ? prev.audience.behaviors.filter(b => b !== behavior)
                      : [...prev.audience.behaviors, behavior]
                  }
                }))
              }}
              className={`p-3 border rounded-lg text-sm text-left transition-colors ${
                formData.audience.behaviors.includes(behavior)
                  ? 'border-purple-500 bg-purple-50 text-purple-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {behavior}
            </button>
          ))}
        </div>
      </div>
    </div>
  )

  const renderBudgetStep = () => (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('campaign.setBudgetSchedule')}</h2>
        <p className="text-gray-600">{t('campaign.budgetScheduleDesc')}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Budget Settings */}
        <div className="space-y-6">
          <h3 className="font-semibold text-gray-900">{t('campaign.budgetSettings')}</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t('campaign.budgetType')}</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setFormData(prev => ({ ...prev, budget: { ...prev.budget, type: 'daily' } }))}
                className={`p-4 border rounded-lg text-center transition-colors ${
                  formData.budget.type === 'daily'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Calendar className="w-6 h-6 mx-auto mb-2" />
                <div className="font-medium">{t('campaign.dailyBudget')}</div>
                <div className="text-xs text-gray-500">{t('campaign.dailyBudgetDesc')}</div>
              </button>
              <button
                onClick={() => setFormData(prev => ({ ...prev, budget: { ...prev.budget, type: 'lifetime' } }))}
                className={`p-4 border rounded-lg text-center transition-colors ${
                  formData.budget.type === 'lifetime'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <DollarSign className="w-6 h-6 mx-auto mb-2" />
                <div className="font-medium">{t('campaign.lifetimeBudget')}</div>
                <div className="text-xs text-gray-500">{t('campaign.lifetimeBudgetDesc')}</div>
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {formData.budget.type === 'daily' ? t('campaign.dailyAmount') : t('campaign.totalAmount')}
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">¥</span>
              <input
                type="number"
                value={formData.budget.amount}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  budget: { ...prev.budget, amount: parseInt(e.target.value) || 0 }
                }))}
                className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="1000"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t('campaign.bidStrategy')}</label>
            <select
              value={formData.budget.bidStrategy}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                budget: { ...prev.budget, bidStrategy: e.target.value }
              }))}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="automatic">{t('campaign.automaticBidding')}</option>
              <option value="manual">{t('campaign.manualBidding')}</option>
              <option value="target_cost">{t('campaign.targetCost')}</option>
            </select>
          </div>
        </div>

        {/* Schedule Settings */}
        <div className="space-y-6">
          <h3 className="font-semibold text-gray-900">{t('campaign.scheduleSettings')}</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t('campaign.startDate')}</label>
            <input
              type="date"
              value={formData.schedule.startDate}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                schedule: { ...prev.schedule, startDate: e.target.value }
              }))}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t('campaign.endDate')}</label>
            <input
              type="date"
              value={formData.schedule.endDate}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                schedule: { ...prev.schedule, endDate: e.target.value }
              }))}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t('campaign.timezone')}</label>
            <select
              value={formData.schedule.timezone}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                schedule: { ...prev.schedule, timezone: e.target.value }
              }))}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="Asia/Shanghai">{t('campaign.chinaStandardTime')}</option>
              <option value="Asia/Hong_Kong">{t('campaign.hongKongTime')}</option>
              <option value="Asia/Taipei">{t('campaign.taipeiTime')}</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  )

  const renderCreativeStep = () => (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('campaign.uploadCreatives')}</h2>
        <p className="text-gray-600">{t('campaign.creativesDesc')}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Media Upload */}
        <div className="space-y-6">
          <h3 className="font-semibold text-gray-900">{t('campaign.mediaAssets')}</h3>
          
          {/* Image Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t('campaign.images')}</label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">{t('campaign.dragDropImages')}</p>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                {t('campaign.browseImages')}
              </button>
            </div>
          </div>

          {/* Video Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t('campaign.videos')}</label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
              <Video className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">{t('campaign.dragDropVideos')}</p>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                {t('campaign.browseVideos')}
              </button>
            </div>
          </div>
        </div>

        {/* Ad Copy */}
        <div className="space-y-6">
          <h3 className="font-semibold text-gray-900">{t('campaign.adCopy')}</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t('campaign.headline')}</label>
            <input
              type="text"
              value={formData.creatives.copy.headline}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                creatives: {
                  ...prev.creatives,
                  copy: { ...prev.creatives.copy, headline: e.target.value }
                }
              }))}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={t('campaign.headlinePlaceholder')}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t('campaign.description')}</label>
            <textarea
              value={formData.creatives.copy.description}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                creatives: {
                  ...prev.creatives,
                  copy: { ...prev.creatives.copy, description: e.target.value }
                }
              }))}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={t('campaign.descriptionPlaceholder')}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t('campaign.callToAction')}</label>
            <select
              value={formData.creatives.copy.cta}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                creatives: {
                  ...prev.creatives,
                  copy: { ...prev.creatives.copy, cta: e.target.value }
                }
              }))}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">{t('campaign.selectCTA')}</option>
              <option value="learn_more">{t('campaign.learnMore')}</option>
              <option value="shop_now">{t('campaign.shopNow')}</option>
              <option value="sign_up">{t('campaign.signUp')}</option>
              <option value="download">{t('campaign.download')}</option>
              <option value="contact_us">{t('campaign.contactUs')}</option>
            </select>
          </div>

          {/* AI Creative Suggestions */}
          <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6 border border-green-200">
            <div className="flex items-start space-x-4">
              <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-blue-500 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-2">{t('campaign.aiCreativeSuggestions')}</h4>
                <p className="text-sm text-gray-600 mb-3">{t('campaign.aiCreativeDesc')}</p>
                <button
                  onClick={() => generateAICopy()}
                  className="px-4 py-2 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-lg hover:from-green-600 hover:to-blue-600 transition-all"
                >
                  {t('campaign.generateCopy')}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderReviewStep = () => (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('campaign.reviewCampaign')}</h2>
        <p className="text-gray-600">{t('campaign.reviewDesc')}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Campaign Summary */}
        <div className="space-y-6">
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <h3 className="font-semibold text-gray-900 mb-4">{t('campaign.campaignSummary')}</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">{t('campaign.objective')}:</span>
                <span className="font-medium">{objectives.find(o => o.id === formData.objective)?.label || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">{t('campaign.audienceSize')}:</span>
                <span className="font-medium">~127K {t('campaign.people')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">{t('campaign.budgetType')}:</span>
                <span className="font-medium">{formData.budget.type === 'daily' ? t('campaign.daily') : t('campaign.lifetime')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">{t('campaign.amount')}:</span>
                <span className="font-medium">¥{formData.budget.amount.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">{t('campaign.duration')}:</span>
                <span className="font-medium">
                  {formData.schedule.startDate} - {formData.schedule.endDate || t('campaign.ongoing')}
                </span>
              </div>
            </div>
          </div>

          {/* AI Performance Prediction */}
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border border-purple-200">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-2">{t('campaign.aiPredictions')}</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-gray-600">{t('campaign.expectedReach')}</div>
                    <div className="font-bold text-blue-600">89K - 127K</div>
                  </div>
                  <div>
                    <div className="text-gray-600">{t('campaign.expectedCTR')}</div>
                    <div className="font-bold text-green-600">2.3% - 3.8%</div>
                  </div>
                  <div>
                    <div className="text-gray-600">{t('campaign.expectedCPC')}</div>
                    <div className="font-bold text-purple-600">¥12 - ¥18</div>
                  </div>
                  <div>
                    <div className="text-gray-600">{t('campaign.expectedROI')}</div>
                    <div className="font-bold text-orange-600">156% - 189%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Creative Preview */}
        <div className="space-y-6">
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <h3 className="font-semibold text-gray-900 mb-4">{t('campaign.creativePreview')}</h3>
            <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <div className="space-y-3">
                <div className="w-full h-32 bg-gray-200 rounded-lg flex items-center justify-center">
                  <Image className="w-8 h-8 text-gray-400" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">
                    {formData.creatives.copy.headline || t('campaign.headlinePlaceholder')}
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">
                    {formData.creatives.copy.description || t('campaign.descriptionPlaceholder')}
                  </p>
                </div>
                <button className="w-full py-2 bg-blue-600 text-white rounded-lg text-sm font-medium">
                  {formData.creatives.copy.cta ? 
                    t(`campaign.${formData.creatives.copy.cta}`) : 
                    t('campaign.callToAction')
                  }
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 0:
        return renderObjectiveStep()
      case 1:
        return renderAudienceStep()
      case 2:
        return renderBudgetStep()
      case 3:
        return renderCreativeStep()
      case 4:
        return renderReviewStep()
      default:
        return renderObjectiveStep()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/campaigns')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            <div>
              <h1 className="text-xl font-bold text-gray-900">{t('campaign.createNew')}</h1>
              <p className="text-sm text-gray-600">{steps[currentStep].subtitle}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleSaveDraft}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              {t('campaign.saveDraft')}
            </button>
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                index <= currentStep
                  ? 'border-blue-500 bg-blue-500 text-white'
                  : 'border-gray-300 bg-white text-gray-400'
              }`}>
                {index < currentStep ? (
                  <Check className="w-5 h-5" />
                ) : (
                  <step.icon className="w-5 h-5" />
                )}
              </div>
              <div className="ml-3">
                <p className={`text-sm font-medium ${
                  index <= currentStep ? 'text-blue-600' : 'text-gray-400'
                }`}>
                  {step.title}
                </p>
              </div>
              {index < steps.length - 1 && (
                <div className={`w-16 h-0.5 mx-4 ${
                  index < currentStep ? 'bg-blue-500' : 'bg-gray-300'
                }`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {renderCurrentStep()}
          </motion.div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className="flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            {t('campaign.previous')}
          </button>
          
          <div className="flex items-center space-x-3">
            {currentStep === steps.length - 1 ? (
              <button
                onClick={handleLaunchCampaign}
                className="flex items-center px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <Target className="w-4 h-4 mr-2" />
                {t('campaign.launch')}
              </button>
            ) : (
              <button
                onClick={handleNext}
                className="flex items-center px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {t('campaign.next')}
                <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CreateCampaign