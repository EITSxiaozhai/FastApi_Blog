import { fetchBlogList, fetchBlogStats, getBingWallpaper } from '../../api/vikeBlogs'

const DEFAULT_STATS = { pv: 1565, uv: 940, articles: 0 }
const STATS_TIMEOUT_MS = 800

const withTimeout = async <T>(promise: Promise<T>, timeoutMs: number, fallback: T): Promise<T> => {
  let timer: ReturnType<typeof setTimeout> | null = null

  try {
    return await Promise.race([
      promise,
      new Promise<T>((resolve) => {
        timer = setTimeout(() => resolve(fallback), timeoutMs)
      })
    ])
  } finally {
    if (timer) clearTimeout(timer)
  }
}

export async function data(pageContext: any) {
  console.log('🔄 正在服务器端获取首页数据...')
  
  try {
    // 统计接口慢时快速降级，避免阻塞SSR首屏
    const statsPromise = withTimeout(fetchBlogStats(), STATS_TIMEOUT_MS, null)

    // 并行获取数据
    const [blogListResult, statsResult, wallpaperResult] = await Promise.allSettled([
      fetchBlogList({ page: 1, pageSize: 9, initialLoad: true }),
      statsPromise,
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
    let stats: any = { ...DEFAULT_STATS, articles: blogList.data.length }
    if (statsResult.status === 'fulfilled' && statsResult.value) {
      console.log('✅ 统计数据API调用成功:', statsResult.value)
      const rawStats: any = statsResult.value
      // 兼容两种结构：{ pv, uv } 或 { data: { PV, UV } }
      if (rawStats?.pv !== undefined || rawStats?.uv !== undefined) {
        stats = {
          pv: Number(rawStats.pv) || DEFAULT_STATS.pv,
          uv: Number(rawStats.uv) || DEFAULT_STATS.uv,
          articles: blogList.data.length
        }
      } else if (rawStats?.data) {
        stats = {
          pv: parseInt(rawStats.data.PV) || DEFAULT_STATS.pv,
          uv: parseInt(rawStats.data.UV) || DEFAULT_STATS.uv,
          articles: blogList.data.length
        }
      }
    } else {
      console.warn('⚠️ 统计数据API调用失败:', statsResult.status === 'rejected' ? statsResult.reason : '未知错误')
      stats.articles = blogList.data.length
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
      stats: { ...DEFAULT_STATS },
      wallpaper: null,
      wallpaperInfo: null,
      error: '数据获取失败，请稍后重试'
    }
  }
} 