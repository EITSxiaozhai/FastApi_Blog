import request from '@/utils/request'

export function Crawlersubmitbutton() {
  return request({
    url: '/admin/blogseo/googleoauth2',
    method: 'get'
  })
}
