import request from '@/utils/request'

export function checkRefreshToken() {
  return request({
    url: '/admin/user/refreshtoken',
    method: 'post'
  })
}
