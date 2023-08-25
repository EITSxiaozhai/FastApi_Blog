import request from '@/utils/request'

export function Postlist(data) {
  return request({
    url: '/blog/AdminBlogIndex',
    method: 'get',
    data
  })
}
