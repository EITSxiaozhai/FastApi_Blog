import request from '@/utils/request'

export function uploadImg(data) {
  return request({
    url: '/markdown/uploadimg/',
    method: 'post',
    data
  })
}
