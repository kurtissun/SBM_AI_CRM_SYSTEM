# 🤖 Local LLM Customer Segmentation Guide

## Overview

This system now supports **cost-free, generative customer segmentation** using local Large Language Models (LLMs). Instead of using expensive cloud APIs, the system runs intelligent analysis directly on your machine.

## ✨ Key Features

- **🆓 Zero Cost**: No API fees or subscription costs
- **🧠 Intelligent Segmentation**: LLM-generated segment names and insights
- **🇨🇳 Chinese Market Aware**: Understands Chinese retail and shopping behaviors
- **🔒 Privacy First**: All data processing happens locally
- **⚡ Fast & Flexible**: Adapts to your specific customer patterns
- **🔄 Automatic Fallback**: Falls back to traditional clustering if LLM unavailable

## 🚀 Quick Setup

### Option 1: Automatic Setup (Recommended)
```bash
./setup_local_llm.sh
```

### Option 2: Manual Setup
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start service
ollama serve &

# Download models (choose one)
ollama pull llama3.2:3b      # Recommended: Fast and efficient
ollama pull qwen2.5:3b       # Alternative: Good for Chinese text

# Install Python requirements
pip install -r requirements_llm.txt
```

## 📊 How It Works

### Traditional vs LLM Segmentation

| **Traditional Clustering** | **LLM-Powered Segmentation** |
|---------------------------|--------------------------------|
| Segment 0, 1, 2, 3... | "Young Tech Enthusiasts", "Premium Shoppers" |
| Statistical patterns only | Contextual understanding |
| Generic insights | Business-relevant recommendations |
| Fixed segment definitions | Dynamic, adaptive segments |

### The LLM Process

1. **📈 Data Analysis**: System analyzes customer patterns (age, spending, location, etc.)
2. **🤖 LLM Generation**: Local LLM creates intelligent segment definitions
3. **👥 Customer Assignment**: Assigns customers based on LLM-generated rules
4. **💡 Insight Generation**: Creates actionable business recommendations
5. **🎯 Enhancement**: Combines LLM insights with traditional analytics

## 🎯 Generated Segment Examples

The LLM creates segments like:

### "年轻科技达人" (Young Tech Enthusiasts)
- **Characteristics**: Age < 30, high digital engagement, convenience focused
- **Motivations**: Innovation, social status, convenience
- **Channels**: Mobile app, social media, online platforms
- **Marketing**: Digital-first, trendy campaigns
- **Revenue Potential**: High

### "家庭消费者" (Family Shoppers)  
- **Characteristics**: Age 30-45, family focused, value conscious
- **Motivations**: Family needs, value for money, quality
- **Channels**: In-store, family apps, loyalty programs
- **Marketing**: Family-focused, value-driven
- **Revenue Potential**: Medium

### "高端消费者" (Premium Customers)
- **Characteristics**: High spending, quality focused, service oriented
- **Motivations**: Exclusivity, premium experience, status
- **Channels**: Premium services, VIP programs, personal shopping
- **Marketing**: Exclusive, personalized service
- **Revenue Potential**: High

## 🔧 Configuration

### Model Selection
The system automatically tries models in this order:
1. `llama3.2:3b` (Primary - fast and efficient)
2. `qwen2.5:3b` (Backup - good for Chinese text)
3. Rule-based fallback (if no LLM available)

### Performance Tuning
- **Small datasets (< 50 customers)**: Uses rule-based segmentation
- **Medium datasets (50-500)**: LLM segmentation with 3-5 segments
- **Large datasets (500+)**: LLM segmentation with 4-6 segments

## 📋 Usage Instructions

### 1. Upload Customer Data
- Use the dual upload interface
- Select "Auto-segment customers" checkbox
- Upload your CSV file

### 2. Monitor Processing
Watch for these indicators:
- 🤖 "Attempting generative LLM segmentation..."
- ✨ "LLM segmentation successful - applying intelligent segments"
- 🔄 "Falling back to adaptive clustering..." (if LLM unavailable)

### 3. Review Results
The upload will show either:
- **AI-Powered Segmentation**: LLM-generated segments with intelligent names
- **Traditional Segmentation**: Numeric clusters with statistical analysis

## 💡 Advanced Features

### Custom Business Context
The LLM understands:
- **Business Types**: 零售 (Retail), 餐饮 (F&B), 娱乐 (Entertainment)
- **Membership Tiers**: 橙卡会员, 金卡会员, 钻卡会员
- **Chinese Cities**: Beijing, Shanghai, Guangzhou, Shenzhen, Chengdu
- **Shopping Behaviors**: Mobile payments, social commerce, experience-focused

### Intelligent Insights
For each segment, the LLM generates:
- **Marketing Strategy**: Specific campaign approaches
- **Product Recommendations**: What to offer this segment
- **Customer Experience**: How to improve their journey
- **Revenue Opportunities**: Upselling and cross-selling tactics
- **Retention Strategy**: How to keep them loyal
- **Seasonal Timing**: When to run campaigns

## 🔍 Troubleshooting

### LLM Not Working?
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart service
killall ollama
ollama serve

# Test model
ollama run llama3.2:3b "Hello world"
```

### Segmentation Falling Back?
- Check system logs for "LLM segmentation..." messages
- Ensure you have at least 10 customers for segmentation
- Verify model is downloaded: `ollama list`

### Performance Issues?
- Use smaller model: `ollama pull qwen2.5:1.5b`
- Reduce temperature in code (line 1230): `temperature=0.5`
- Limit concurrent requests

## 📊 System Requirements

### Minimum
- **RAM**: 4GB available
- **Storage**: 2GB for model files
- **CPU**: Modern x86_64 or ARM64

### Recommended
- **RAM**: 8GB+ available
- **Storage**: 5GB for multiple models
- **CPU**: Multi-core with good single-thread performance

## 🔧 Technical Integration

### Adding Custom Segments
Modify `local_llm_segmentation.py`:
```python
def _generate_fallback_segments(self, data_summary):
    return {
        "custom_segment": {
            "name": "Custom Segment Name",
            "chinese_name": "自定义细分",
            "characteristics": ["your criteria"],
            "assignment_rules": {
                "age_range": [25, 45],
                "membership_levels": ["金卡会员"]
            }
        }
    }
```

### Customizing LLM Prompts
Edit the prompt in `_llm_generate_segments()` method to:
- Add your specific business context
- Include custom segment criteria
- Modify output format requirements

## 🚀 Next Steps

1. **Run Setup**: Execute `./setup_local_llm.sh`
2. **Test Upload**: Use `sample_chinese_data.csv` for testing
3. **Review Segments**: Check the generated segments and insights
4. **Customize**: Modify prompts and fallback rules as needed
5. **Scale**: Deploy to production with monitoring

## 🆘 Support

### Common Issues
- **Model download timeout**: Use smaller models or retry
- **Memory errors**: Close other applications or use lighter models
- **Permission errors**: Ensure Ollama has proper system permissions

### Getting Help
- Check logs in `/Users/kurtis/SBM_AI_CRM_SYSTEM/logs/`
- Review Ollama logs: `ollama logs`
- Test individual components with sample data

---

**🎉 Congratulations!** You now have a sophisticated, cost-free customer segmentation system that combines the power of local LLMs with traditional analytics. The system intelligently generates meaningful segments while preserving privacy and eliminating API costs.