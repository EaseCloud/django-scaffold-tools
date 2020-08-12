from django.http import JsonResponse


def response_success(msg='', *, data=None, silent=False):
    payload = dict(ok=True)
    if msg:
        payload['msg'] = msg
    if silent:
        payload['silent'] = True
    if data:
        payload['data'] = data
    return JsonResponse(payload)


def response_fail(msg='', errcode=0, *, status=400, data=None, silent=False):
    payload = dict(ok=False)
    if msg:
        payload['msg'] = msg
    if silent:
        payload['silent'] = True
    if data:
        payload['data'] = data
    if errcode:
        payload['errcode'] = errcode
    return JsonResponse(payload, status=status)


