import { fetchBlogList, getBingWallpaper, fetchBlogStats } from '@/api/vikeBlogs'

// 获取随机诗句
const getRandomVerse = async (retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch('https://v1.jinrishici.com/rensheng/shiguang', {
        headers: {
          'Accept': 'application/json',
          'X-User-Token': 'jinrishici-token-xxx' // 可选：如果需要的话可以添加token
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      if (data && data.content) {
        return data.content
      }
      throw new Error('Invalid response format')
    } catch (error) {
      if (import.meta.env?.DEV) {
        console.error(`获取诗句失败 (尝试 ${i + 1}/${retries}):`, error)
      }
      if (i === retries - 1) {
        return '探索技术 · 分享知识 · 记录成长' // 所有重试都失败后返回默认值
      }
      // 等待一段时间后重试
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
  }
  return '探索技术 · 分享知识 · 记录成长'
}

export async function data(pageContext) {
  try {
    // 只在开发环境中显示调试日志
    if (import.meta.env?.DEV) {
      console.log('🔧 服务器端渲染 - pageContext:', pageContext)
      console.log('🔧 服务器端渲染 - pageProps:', pageContext.pageProps)
      console.log('🔧 服务器端渲染 - data:', pageContext.data)
      console.log('🔧 服务器端渲染 - routeParams:', pageContext.routeParams)
      console.log('🔧 服务器端渲染 - urlPathname:', pageContext.urlPathname)
    }
    
    // 从URL查询参数获取页码
    const urlParsed = pageContext.urlParsed
    const searchParams = new URLSearchParams(urlParsed.search)
    const page = parseInt(searchParams.get('page')) || 1
    const pageSize = 9
    
    if (import.meta.env?.DEV) {
      console.log('📄 请求页码:', page)
    }
    
    // 并行获取所有数据
    const [blogResponse, wallpaperData, verse, statsData] = await Promise.all([
      fetchBlogList({ page: page, pageSize: pageSize }),
      getBingWallpaper(),
      getRandomVerse(),
      fetchBlogStats()
    ])
    
    if (import.meta.env?.DEV) {
      console.log('✅ 获取博客统计数据成功:', statsData)
      console.log('📄 博客API完整响应:', JSON.stringify(blogResponse, null, 2))
      console.log('📄 分页信息详细:', {
        current: blogResponse?.current_page,
        total: blogResponse?.total,
        pages: blogResponse?.total_pages,
        dataLength: blogResponse?.data?.length,
        原始分页对象: blogResponse?.pagination
      })
    }
    
    // 更新统计数据
    const stats = {
      pv: statsData?.pv || 0,
      uv: statsData?.uv || 0,
      articles: blogResponse?.total || blogResponse?.pagination?.total || 0  // 尝试多个字段
    }
    
    if (import.meta.env?.DEV) {
      console.log('📊 最终统计数据:', stats)
    }
    
    // 构建分页信息，尝试多种数据源
    const paginationInfo = {
      page: blogResponse?.current_page || blogResponse?.pagination?.page || 1,
      pageSize: pageSize,
      total: blogResponse?.total || blogResponse?.pagination?.total || 0,
      totalPages: blogResponse?.total_pages || blogResponse?.pagination?.totalPages || 1
    }
    
    if (import.meta.env?.DEV) {
      console.log('📄 构建的分页信息:', paginationInfo)
    }
    
    return {
      articles: blogResponse?.data || [],
      stats: stats,
      wallpaper: wallpaperData?.url || null,
      verse: verse,
      pagination: paginationInfo
    }
  } catch (error) {
    if (import.meta.env?.DEV) {
      console.error('获取页面数据失败:', error)
    }
    return {
      articles: [],
      stats: { pv: 0, uv: 0, articles: 0 },
      wallpaper: null,
      verse: '出现错误，请稍后重试',
      pagination: { page: 1, pageSize: 9, total: 0, totalPages: 1 }
    }
  }
} 