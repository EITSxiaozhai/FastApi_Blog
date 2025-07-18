import { fetchBlogList, fetchBlogStats, getBingWallpaper } from '../../api/vikeBlogs'

export async function data(pageContext: any) {
  console.log('🔄 正在服务器端获取首页数据...')
  
  try {
    // 并行获取数据
    const [blogListResult, statsResult, wallpaperResult] = await Promise.allSettled([
      fetchBlogList({ page: 1, pageSize: 9, initialLoad: true }),
      fetchBlogStats(),
      getBingWallpaper(false) // 获取今日壁纸
    ])

    // 处理博客列表数据 - 使用已修复的API函数
    let blogList: any = { data: [], pagination: { page: 1, pageSize: 9, total: 0, totalPages: 0 } }
    if (blogListResult.status === 'fulfilled' && blogListResult.value) {
      console.log('✅ 博客列表API调用成功:', blogListResult.value)
      blogList = blogListResult.value
    } else {
      console.warn('⚠️ 博客列表API调用失败:', blogListResult.status === 'rejected' ? blogListResult.reason : '未知错误')
    }

    // 处理统计数据
    let stats: any = { pv: 0, uv: 0, articles: 0 }
    if (statsResult.status === 'fulfilled' && statsResult.value) {
      console.log('✅ 统计数据API调用成功:', statsResult.value)
      const rawStats: any = statsResult.value
      if (rawStats && rawStats.data) {
        stats = {
          pv: parseInt(rawStats.data.PV) || 0,
          uv: parseInt(rawStats.data.UV) || 0,
          articles: blogList.data.length
        }
      }
    } else {
      console.warn('⚠️ 统计数据API调用失败:', statsResult.status === 'rejected' ? statsResult.reason : '未知错误')
      // 提供基本统计信息
      stats = {
        pv: 1565,  // 默认值
        uv: 940,   // 默认值
        articles: blogList.data.length
      }
    }

    // 处理壁纸数据
    let wallpaper = null
    if (wallpaperResult.status === 'fulfilled' && wallpaperResult.value) {
      console.log('✅ 壁纸API调用成功')
      wallpaper = wallpaperResult.value
    } else {
      console.warn('⚠️ 壁纸API调用失败:', wallpaperResult.status === 'rejected' ? wallpaperResult.reason : '未知错误')
    }

    console.log('✅ 首页数据获取成功:', {
      articlesCount: blogList.data.length,
      stats,
      hasWallpaper: !!wallpaper
    })

    return {
      articles: blogList.data,
      pagination: blogList.pagination,
      stats,
      wallpaper: wallpaper?.url || null,
      wallpaperInfo: wallpaper
    }

  } catch (error) {
    console.error('❌ 首页数据获取失败:', error)
    
    // 返回默认数据，确保页面可以正常渲染
    return {
      articles: [],
      pagination: { page: 1, pageSize: 9, total: 0, totalPages: 0 },
      stats: { pv: 1565, uv: 940, articles: 0 },
      wallpaper: null,
      wallpaperInfo: null,
      error: '数据获取失败，请稍后重试'
    }
  }
} 