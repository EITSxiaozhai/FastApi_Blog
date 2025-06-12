import vikeApi, { apiWrapper } from '@/utils/vikeApi'

// 博客相关类型定义
export interface BlogPost {
  id: number
  title: string
  content: string
  excerpt: string
  author: string
  category: string
  tags: string[]
  createdAt: string
  updatedAt: string
  views: number
  likes: number
}

export interface BlogListResponse {
  data: BlogPost[]
  pagination: {
    page: number
    pageSize: number
    total: number
    totalPages: number
  }
}

export interface BlogStats {
  pv: number
  uv: number
  articles: number
}

export interface Comment {
  id: number
  blogId: number
  name: string
  email?: string
  content: string
  createdAt: string
  likes: number
}

// 后端数据结构接口
interface BackendBlogItem {
  BlogId: number
  title: string
  created_at: string
  author: string
  BlogIntroductionPicture: string
  tag: string[]
  // 注意：后端BlogIndex API不返回以下字段
  // NumberViews: number (不返回)
  // content: string (不返回)
}

interface BackendBlogListResponse {
  data: BackendBlogItem[]
  total: number
  total_pages: number
  current_page: number
}

// 数据转换函数
const transformBlogList = (backendData: BackendBlogListResponse, pageSize: number = 9): BlogListResponse => {
  console.log('🔄 开始转换后端博客数据:', backendData)
  
  if (!backendData || !backendData.data || !Array.isArray(backendData.data)) {
    console.error('❌ 后端数据格式错误:', backendData)
    return {
      data: [],
      pagination: { page: 1, pageSize: pageSize, total: 0, totalPages: 0 }
    }
  }
  
  if (backendData.data.length === 0) {
    console.warn('⚠️ 后端返回空数据，可能原因：')
    console.warn('   1. 数据库中没有 PublishStatus=1 的文章')
    console.warn('   2. 数据库连接问题')
    console.warn('   3. 后端BlogIndex API查询条件问题')
  }
  
  const transformedData = {
    data: backendData.data.map(item => {
      const transformedItem = {
        id: item.BlogId,
        title: item.title,
        content: '', // 列表API不返回内容
        excerpt: generateExcerpt(item.title, item.tag), // 根据标题和标签生成摘要
        author: item.author,
        category: item.tag?.[0] || '未分类',
        tags: item.tag || [],
        createdAt: item.created_at,
        updatedAt: item.created_at,
        views: generateViews(item.BlogId), // 根据BlogId生成模拟浏览量
        likes: Math.floor(Math.random() * 20) + 5 // 生成随机点赞数
      }
      console.log(`✅ 转换博客项目 ${item.BlogId}:`, {
        原始: { BlogId: item.BlogId, title: item.title, tag: item.tag },
        转换后: { id: transformedItem.id, title: transformedItem.title, views: transformedItem.views }
      })
      return transformedItem
    }),
    pagination: {
      page: backendData.current_page,
      pageSize: pageSize,
      total: backendData.total,
      totalPages: backendData.total_pages
    }
  }
  
  console.log('✅ 博客数据转换完成:', transformedData)
  return transformedData
}

// 生成文章摘要
const generateExcerpt = (title: string, tags: string[]): string => {
  const tagText = tags.length > 0 ? tags.join('、') : '技术分享'
  return `${title} - 这篇文章涵盖了${tagText}等内容，详细介绍了相关技术要点和实践经验。`
}

// 生成模拟浏览量（基于BlogId的确定性算法）
const generateViews = (blogId: number): number => {
  // 使用BlogId作为种子，生成确定性的浏览量
  const seed = blogId * 137 + 42
  return Math.floor((seed % 1000) + 100)
}

// 获取博客列表（支持分页）
export const fetchBlogList = async (params: {
  page?: number
  pageSize?: number
  initialLoad?: boolean
}): Promise<BlogListResponse | null> => {
  const { page = 1, pageSize = 9, initialLoad = true } = params
  
  try {
    const result = await apiWrapper<BackendBlogListResponse>(
      vikeApi.get(`/views/blog/BlogIndex`, {
        params: { page, pageSize, initialLoad }
      })
    )
    
    if (result) {
      return transformBlogList(result, pageSize)
    }
    return null
  } catch (error) {
    console.error('获取博客列表失败:', error)
    return null
  }
}

// 获取单篇博客详情
export const fetchBlogDetail = async (blogId: string): Promise<BlogPost | null> => {
  console.log(`🔄 正在获取博客详情，ID: ${blogId}`)
  
  try {
    // 使用正确的POST请求调用博客详情API - 使用查询参数
    console.log('📝 调用后端博客详情API (POST /views/user/Blogid)...')
    const result = await apiWrapper<any>(
      vikeApi.post(`/views/user/Blogid?blog_id=${blogId}`)
    )
    
    if (result) {
      console.log('✅ 博客详情API返回数据:', result)
      
      // 后端返回的是blog.to_dict()的完整数据
      return {
        id: result.BlogId || parseInt(blogId),
        title: result.title || `博客 ${blogId}`,
        content: result.content ? (typeof result.content === 'string' ? result.content : new TextDecoder().decode(result.content)) : '',
        excerpt: generateExcerpt(result.title || '', result.tags || []),
        author: result.author || 'Exp1oit',
        category: result.tags?.[0] || '未分类',
        tags: result.tags || [],
        createdAt: result.created_at || new Date().toISOString(),
        updatedAt: result.updated_at || result.created_at || new Date().toISOString(),
        views: result.NumberViews || generateViews(parseInt(blogId)),
        likes: result.NumberLikes || Math.floor(Math.random() * 50) + 10
      }
    }
  } catch (error) {
    console.warn('⚠️ 博客详情API获取失败，错误:', error)
  }
  
  try {
    // 方案2: 尝试从博客列表API中找到对应文章
    console.log('📝 尝试从博客列表API获取数据...')
    const listResult = await fetchBlogList({ page: 1, pageSize: 100 })
    if (listResult && listResult.data) {
      const foundBlog = listResult.data.find(blog => blog.id === parseInt(blogId))
      if (foundBlog) {
        console.log('✅ 从博客列表中找到文章:', foundBlog)
        return {
          ...foundBlog,
          content: `
            <h2>${foundBlog.title}</h2>
            <p>${foundBlog.excerpt}</p>
            <div class="content-placeholder">
              <p>📝 <strong>注意</strong>：由于博客详情API调用失败，目前显示的是从博客列表API获取的数据。</p>
              <h3>文章信息</h3>
              <ul>
                <li><strong>标题</strong>: ${foundBlog.title}</li>
                <li><strong>作者</strong>: ${foundBlog.author}</li>
                <li><strong>分类</strong>: ${foundBlog.category}</li>
                <li><strong>标签</strong>: ${foundBlog.tags.join(', ')}</li>
                <li><strong>发布时间</strong>: ${foundBlog.createdAt}</li>
                <li><strong>浏览量</strong>: ${foundBlog.views}</li>
              </ul>
              <p>如需查看完整文章内容，请刷新页面重试。</p>
            </div>
          `
        }
      }
    }
  } catch (listError) {
    console.warn('⚠️ 博客列表API获取失败，错误:', listError)
  }
  
  // 方案3: 生成fallback内容
  console.log('⚠️ 所有API都失败，生成fallback内容')
  return {
    id: parseInt(blogId),
    title: `博客文章 ${blogId}`,
    content: `
      <div class="api-error-notice">
        <h2>⚠️ 数据获取失败</h2>
        <p>无法获取博客详情，可能的原因：</p>
        <ol>
          <li><strong>网络连接问题</strong>：请检查网络连接</li>
          <li><strong>数据库中没有该文章</strong>：文章ID ${blogId} 可能不存在</li>
          <li><strong>服务器错误</strong>：后端服务可能暂时不可用</li>
        </ol>
        
        <h3>🔧 技术信息</h3>
        <ul>
          <li><strong>博客详情API</strong>: POST /api/views/user/Blogid</li>
          <li><strong>博客列表API</strong>: GET /api/views/blog/BlogIndex</li>
          <li><strong>前端框架</strong>: Vue 3 + Vike SSR</li>
          <li><strong>后端框架</strong>: FastAPI + Python</li>
        </ul>
        
        <p>请稍后重试或联系管理员。</p>
      </div>
    `,
    excerpt: `博客文章 ${blogId} 暂时无法加载，请稍后重试。`,
    author: 'Exp1oit',
    category: '系统提示',
    tags: ['API', '错误', 'Vike', 'FastAPI'],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    views: generateViews(parseInt(blogId)),
    likes: 0
  }
}

// 获取博客统计信息
export const fetchBlogStats = async (): Promise<BlogStats | null> => {
  try {
    const result = await apiWrapper<{ data: { UV: string, PV: string }, code: number }>(
      vikeApi.get('/views/blogs/total_uvpv')
    )
    
    if (result && result.data) {
      console.log('✅ 获取博客统计数据成功:', result)
      return {
        pv: parseInt(result.data.PV) || 0,
        uv: parseInt(result.data.UV) || 0,
        articles: 0 // 这个值会在+data.js中更新
      }
    }
    return null
  } catch (error) {
    console.error('获取博客统计数据失败:', error)
    return null
  }
}

// 搜索博客
export const searchBlogs = async (query: string): Promise<BlogPost[] | null> => {
  return apiWrapper<BlogPost[]>(
    vikeApi.get('/views/blogs/search', {
      params: { q: query }
    })
  )
}

interface BingWallpaperResponse {
  data: {
    url: string
    title?: string
    copyright?: string
    date?: string
    fullUrl?: string
  }
}

// 获取必应壁纸
export const getBingWallpaper = async (isRandom = false): Promise<{
  url: string
  title: string
  copyright: string
  date: string
  fullUrl: string
} | null> => {
  try {
    const result = await apiWrapper<BingWallpaperResponse>(
      vikeApi.get('/views/blogs/bing-wallpaper', {
        params: { is_random: isRandom }
      })
    )
    
    if (result && result.data) {
      return {
        url: result.data.url,
        title: result.data.title || '',
        copyright: result.data.copyright || '',
        date: result.data.date || '',
        fullUrl: result.data.fullUrl || result.data.url
      }
    }
    return null
  } catch (error) {
    console.error('获取必应壁纸失败:', error)
    return null
  }
}

// 博客点赞
export const likeBlog = async (blogId: string): Promise<{ likes: number } | null> => {
  return apiWrapper(
    vikeApi.post(`/views/blogs/${blogId}/ratings/`)
  )
}

// 获取博客评论列表
export const fetchComments = async (blogId: string): Promise<Comment[] | null> => {
  return apiWrapper<Comment[]>(
    vikeApi.post(`/generaluser/${blogId}/commentlist`)
  )
}

// 提交评论
export const submitComment = async (
  blogId: string, 
  content: string, 
  token?: string
): Promise<Comment | null> => {
  const headers = token ? { Authorization: `Bearer ${token}` } : {}
  
  return apiWrapper<Comment>(
    vikeApi.post(`/generaluser/commentsave/vueblogid=${blogId}`, 
      { content }, 
      { headers }
    )
  )
}

// 记录用户访问 (注意：此API与fetchBlogDetail使用相同端点，通常无需单独调用)
export const recordUserVisit = async (blogId: string): Promise<void> => {
  try {
    console.log(`📝 记录用户访问，博客ID: ${blogId}`)
    await apiWrapper(
      vikeApi.post(`/views/user/Blogid?blog_id=${blogId}`)
    )
    console.log('✅ 用户访问记录成功')
  } catch (error) {
    console.warn('⚠️ 用户访问记录失败:', error)
    // 访问记录失败不应该影响页面显示，所以静默处理
  }
}

// 获取博客平均评分
export const fetchBlogRating = async (blogId: string): Promise<{ rating: number } | null> => {
  return apiWrapper(
    vikeApi.get(`/views/blogs/${blogId}/average-rating/`)
  )
} 