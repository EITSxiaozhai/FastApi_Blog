import request from '@/utils/request'

export function Crawlersubmitbutton() {
  return request({
    url: '/blog/googleoauth2',
    method: 'get'
  })
}
