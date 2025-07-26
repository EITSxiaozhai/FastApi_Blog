import google.generativeai as genai
from typing import Optional
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置 Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

async def generate_blog_description(content: str, max_length: int = 160) -> Optional[str]:
    """
    使用 Gemini API 生成博客文章的描述
    
    Args:
        content: 博客文章内容
        max_length: 描述的最大长度（默认160字符，适合SEO）
    
    Returns:
        str: 生成的描述文本，如果生成失败则返回None
    """
    try:
        # 初始化 Gemini Pro 模型
        model = genai.GenerativeModel('gemini-pro')
        
        # 构建提示词
        prompt = f"""请为以下博客文章生成一个简洁的SEO描述，描述应该：
1. 概括文章的主要内容
2. 包含关键词
3. 长度不超过{max_length}个字符
4. 使用吸引人的语言

文章内容：
{content[:2000]}  # 只使用前2000个字符以避免超出token限制

请直接返回描述文本，不要包含任何其他内容。"""

        # 生成描述
        response = await model.generate_content(prompt)
        
        # 获取生成的文本
        description = response.text.strip()
        
        # 确保描述不超过最大长度
        if len(description) > max_length:
            description = description[:max_length-3] + "..."
            
        return description
        
    except Exception as e:
        print(f"生成描述时出错: {str(e)}")
        return None 