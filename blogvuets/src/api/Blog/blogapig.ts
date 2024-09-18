import backApi  from "@/utils/backApi";

export function postBlogRatings(blogId: string, queryParams: URLSearchParams) {
  return backApi({
    url: `/views/blogs/${blogId}/ratings/?${queryParams.toString()}`,
    method: 'post'
  });
}

export function postUserBlogId(blogId: string) {
  return backApi({
    url: `/views/user/Blogid?blog_id=${blogId}`,
    method: 'post'
  });
}

export function getAverageRatingRequest(blogId: string) {
  return backApi({
    url: `/views/blogs/${blogId}/average-rating/`,
    method: 'get'
  });
}

export function postCommentList(blogId: string) {
  return backApi({
    url: `/generaluser/${blogId}/commentlist`,
    method: 'post'
  });
}


export function Postlist(blogId: string) {
  return backApi({
    url: `/views/blog/BlogIndex`,
    method: 'get'
  });
}


export function fetchBlogIndex({ page, pageSize }: { page: number; pageSize: number }) {
  return backApi({
    url: `/views/blog/BlogIndex?initialLoad=false&page=${page}&pageSize=${pageSize}`,
    method: 'get'
  });
}

export function GoogleUVPV(blogId: string) {
  return backApi({
    url: `/views/blogs/total_uvpv`,
    method: 'get'
  });
}


export function postCommentSave(blogId: string, str: string, token: string) {
  return backApi({
    url: `/generaluser/commentsave/vueblogid=${blogId}`,
    method: 'post',
    data: {
      content: str,
    },
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  });
}

