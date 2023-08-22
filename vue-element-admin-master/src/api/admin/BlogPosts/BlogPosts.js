import request from '@/utils/request'

export function Postlist(data) {
  return request({
    url: '/blog/adminlist',
    method: 'post',
    data
  })
}
