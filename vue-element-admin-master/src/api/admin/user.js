import request from '@/utils/request'

export function adminlist(data) {
  return request({
    url: '/admin/user/adminlist',
    method: 'post',
    data
  })
}

export function updateUser(data) {
  return request({
    url: '/admin/user/updateUser',
    method: 'post',
    data
  })
}

export function userprivileges(data) {
  return request({
    url: '/admin/user/userprivileges',
    method: 'post',
    data
  })
}
