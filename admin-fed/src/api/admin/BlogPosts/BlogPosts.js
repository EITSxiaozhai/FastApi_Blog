import request from '@/utils/request'

export function Postlist(data) {
  return request({
    url: '/admin/blog/AdminBlogIndex',
    method: 'get',
    data
  })
}

// 前端请求函数
export function BlogDetails(blog_id) {
  return request({
    url: `/admin/blog/Blogid?blog_id=${blog_id}`,
    method: 'post'
  })
}

export function BlogDetailsedit(blog_id, data) {
  return request({
    url: `/admin/blog/Blogedit?blog_id=${blog_id}`,
    method: 'post',
    data
  })
}

export function CreateContent(data) {
  return request({
    url: '/admin/blog/BlogCreate',
    method: 'post',
    data
  })
}

export function Updatehomepageimage(blog_id, data) {
  return request({
    url: `/admin/blog/Blogeditimg?blog_id=${blog_id}`,
    method: 'post',
    data
  })
}

export function DeletePost(blog_id, data) {
  return request({
    url: `/admin/blog/BlogDel?blog_id=${blog_id}`,
    method: 'delete',
    data
  })
}

export function BlogTagList(data) {
  return request({
    url: '/admin/Blogtaglist',
    method: 'post',
    data
  })
}

export function BlogTagCreate(data) {
  return request({
    url: '/admin/blog/BlogtagCreate',
    method: 'post',
    data
  })
}

export function BlogTagget(data) {
  return request({
    url: '/admin/blog/Blogtagget',
    method: 'post',
    data
  })
}

// 获取管理员ID
export function getAdminId(username) {
  return request({
    url: '/admin/blog/getAdminId',
    method: 'post',
    data: { username }
  })
}

