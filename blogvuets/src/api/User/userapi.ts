import backApi from "@/utils/backApi";

export function UserLogin(data: { data: any }) {
    return backApi({
        url: '/generaluser/login',
        method: 'post',
        data
    })
}


export function RegUser(data: { data: any }) {
    return backApi({
        url: '/generaluser/reguser',
        method: 'post',
        data
    })
}


export function CheckUserName(data: { data: any }) {
    return backApi({
        url: '/generaluser/check-username',
        method: 'post',
        data
    })
}

export function SentMailCod(data: { data: any }) {
    return backApi({
        url: '/generaluser/emailcod',
        method: 'post',
        data
    })
}

export function UploadUserAvatar(data: { data: any }) {
    return backApi({
        url: '/generaluser/reg',
        method: 'post',
        data
    })
}

export function CheckLogin(state: string) {
    return backApi({
        url: '/generaluser/check-login',
        method: 'get',
        params: { state }
    })
}

export function GetQrcode(data: { data: any }) {
    return backApi({
        url: '/generaluser/github-qrcode',
        method: 'get',
        data
    })
}