import request from '@/utils/request'

export function Postlist(data) {
  return request({
    url: '/blog/AdminBlogIndex',
    method: 'get',
    data
  })
}

// 前端请求函数
export function BlogDetails(blog_id) {
  return request({
    url: `/blog/Blogid?blog_id=${blog_id}`, // 构建 URL 参数
    method: 'post' // 使用 GET 请求
  })
}

export function BlogDetailsedit(blog_id, data) {
  return request({
    url: `/blog/Blogedit/?blog_id=${blog_id}`, // 构建 URL 参数
    method: 'post', // 使用 GET 请求
    data
  })
}
