import { fetchBlogDetail, fetchComments, fetchBlogRating } from '../../../api/vikeBlogs'

export async function data(pageContext: any) {
  const blogId = pageContext.routeParams.blogId
  console.log('🔄 正在服务器端获取博客详情，ID:', blogId)
  
  try {
    // 并行获取博客详情和评论
    const [blogResult, commentsResult, ratingResult] = await Promise.allSettled([
      fetchBlogDetail(blogId),
      fetchComments(blogId),
      fetchBlogRating(blogId)
    ])

    // 处理博客详情
    let blog = blogResult.status === 'fulfilled' && blogResult.value
      ? blogResult.value
      : null

    // 如果后端没有返回数据，创建一个示例博客
    if (!blog) {
      console.warn('⚠️ 后端博客数据为空，使用示例数据，ID:', blogId)
      blog = {
        id: parseInt(blogId),
        title: `Vike + FastAPI 博客系统示例文章 ${blogId}`,
        content: `
          <h2>什么是Vike？</h2>
          <p>Vike是一个现代的、轻量级的Vue.js服务器端渲染(SSR)框架。与Nuxt.js不同，Vike更加灵活和可定制。</p>
          
          <h2>为什么选择Vike？</h2>
          <ul>
            <li><strong>轻量级</strong>：相比Nuxt.js更加简洁</li>
            <li><strong>灵活性</strong>：可以选择任何工具和库</li>
            <li><strong>性能优异</strong>：基于Vite的快速构建</li>
            <li><strong>渐进式</strong>：可以逐步迁移现有项目</li>
          </ul>
          
          <h2>技术栈</h2>
          <ol>
            <li>前端：Vue 3 + Vike + Element Plus</li>
            <li>后端：FastAPI + Python</li>
            <li>数据库：MySQL</li>
            <li>部署：Docker + Traefik</li>
          </ol>
          
          <h2>特色功能</h2>
          <p>本博客系统具有以下特色功能：</p>
          <ul>
            <li>🚀 服务器端渲染 (SSR)</li>
            <li>📱 响应式设计</li>
            <li>🔐 用户认证系统</li>
            <li>💬 评论互动功能</li>
            <li>🎨 现代化UI设计</li>
            <li>⚡ 快速加载体验</li>
          </ul>
          
          <h2>总结</h2>
          <p>通过使用Vike，我们成功创建了一个现代化的、高性能的博客系统。</p>
          
          <blockquote>
            <p>💡 <strong>提示</strong>：这是一个示例博客文章，展示了Vike SSR的强大功能。当后端API连接成功后，将显示真实的文章内容。</p>
          </blockquote>
        `,
        excerpt: '本文展示了使用Vike框架构建的现代化博客系统，包含服务器端渲染、用户认证、评论系统等完整功能。',
        author: 'Exp1oit',
        category: '技术分享',
                 tags: ['Vue', 'Vike', 'SSR', 'FastAPI'],
         createdAt: new Date(Date.now() - parseInt(blogId) * 24 * 60 * 60 * 1000).toISOString(),
         updatedAt: new Date(Date.now() - parseInt(blogId) * 12 * 60 * 60 * 1000).toISOString(),
         views: Math.floor(Math.random() * 1000) + parseInt(blogId) * 100,
         likes: Math.floor(Math.random() * 50) + parseInt(blogId) * 5
       }
    }

    // 处理评论数据
    const comments = commentsResult.status === 'fulfilled' && commentsResult.value
      ? commentsResult.value
      : []

    // 处理评分数据
    const rating = ratingResult.status === 'fulfilled' && ratingResult.value
      ? ratingResult.value
      : { rating: 0 }

    // 注意：用户访问记录已在 fetchBlogDetail API调用中自动处理

    console.log('✅ 博客详情获取成功:', {
      blogId: blog?.id,
      title: blog?.title,
      commentsCount: comments.length,
      rating: rating.rating
    })

    return {
      blog,
      comments,
      rating: rating.rating,
      blogId
    }

  } catch (error: any) {
    console.error('❌ 博客详情获取失败:', error)
    
    // 对于找不到的博客，返回特殊标记
    if (error?.message === 'Blog not found') {
      return {
        notFound: true,
        blogId,
        error: '博客文章不存在'
      }
    }
    
    // 其他错误返回默认数据
    return {
      blog: null,
      comments: [],
      rating: 0,
      blogId,
      error: '数据获取失败，请稍后重试'
    }
  }
} 