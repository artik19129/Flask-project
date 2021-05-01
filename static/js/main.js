btn_auth = document.getElementById('btn_auth')
bth_reg = document.getElementById('btn_reg')

btn_auth.onclick = function () {
    window.location.href = '/auth';
}

bth_reg.onclick = function () {
    window.location.href = '/reg';
}