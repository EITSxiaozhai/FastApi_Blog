import request from '@/utils/request'

export function uploadImg(data) {
  return request({
    url: '/admin/markdown/uploadimg/',
    method: 'post',
    data
  })
}
