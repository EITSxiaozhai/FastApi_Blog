import request from '@/utils/request'

export function adminlist(data) {
  return request({
    url: '/user/adminlist',
    method: 'post',
    data
  })
}

