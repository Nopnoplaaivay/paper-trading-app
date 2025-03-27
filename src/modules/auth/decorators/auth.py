from fastapi import Depends, Request

def Payload(request: Request):
    return request.state.user