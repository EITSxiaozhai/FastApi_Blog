import request from '@/utils/request'

export function Crawlersubmitbutton() {
  return request({
    url: '/blogseo/googleoauth2',
    method: 'get'
  })
}
