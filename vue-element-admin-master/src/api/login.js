import request from '@/utils/request'

export function checkRefreshToken() {
  return request({
    url: '/user/refreshtoken',
    method: 'post'
  })
}
