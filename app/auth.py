from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi_jwt_auth import AuthJWT
import requests
import asyncio
from .config import settings

router = APIRouter()

# 웹소켓 서버 주소
WEBSOCKET_URL = "ws://localhost:7777"

async def send_email_to_websocket(email: str):
    # 웹소켓 서버에 이메일 전송
    async with WebSocket.connect(WEBSOCKET_URL) as websocket:
        await websocket.send(email)
        print(f"Email sent to WebSocket: {email}")

@router.get('/auth/google')
def google_login():
    return RedirectResponse(
        url=f'https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.google_client_id}&redirect_uri=https://auth.calibes.com/auth/google/callback&response_type=code&scope=openid email profile'
    )

@router.get('/auth/google/callback')
async def google_callback(code: str):
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'code': code,
        'client_id': settings.google_client_id,
        'client_secret': settings.google_client_secret,
        'redirect_uri': 'https://auth.calibes.com/auth/google/callback',
        'grant_type': 'authorization_code'
    }

    response = requests.post(token_url, data=token_data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed Google")
    
    token_response = response.json()
    access_token = token_response.get('access_token')

    if access_token:
        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_info_response.status_code != 200:
            raise HTTPException(status_code=user_info_response.status_code, detail="Failed Google")

        user_info = user_info_response.json()
        email = user_info['email']  # 이메일 가져오기
        jwt_token = AuthJWT().create_access_token(subject=email)
        
        # 이메일을 웹소켓 서버로 전송
        asyncio.create_task(send_email_to_websocket(email))
        
        return RedirectResponse(url=f'https://web.calibes.com/success?token={jwt_token}')
    
    raise HTTPException(status_code=400, detail="Failed")

@router.get('/auth/naver')
def naver_login():
    return RedirectResponse(
        url=f'https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={settings.naver_client_id}&redirect_uri=https://auth.calibes.com/auth/naver/callback'
    )

@router.get('/auth/naver/callback')
async def naver_callback(code: str):
    token_url = 'https://nid.naver.com/oauth2.0/token'
    token_data = {
        'client_id': settings.naver_client_id,
        'client_secret': settings.naver_client_secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'https://auth.calibes.com/auth/naver/callback'
    }
    
    response = requests.get(token_url, params=token_data)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed Naver")
    
    token_response = response.json()
    access_token = token_response.get('access_token')

    if access_token:
        user_info_response = requests.get(
            'https://openapi.naver.com/v1/nid/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_info_response.status_code != 200:
            raise HTTPException(status_code=user_info_response.status_code, detail="Failed Naver")
        
        user_info = user_info_response.json()
        email = user_info['response']['email']  # 이메일 가져오기
        jwt_token = AuthJWT().create_access_token(subject=email)

        # 이메일을 웹소켓 서버로 전송
        asyncio.create_task(send_email_to_websocket(email))

        return RedirectResponse(url=f'https://web.calibes.com/success?token={jwt_token}')
    
    raise HTTPException(status_code=400, detail="Failed")

@router.get('/auth/userinfo')
def user_info(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    current_user = Authorize.get_jwt_subject()
    return {"email": current_user}

@router.get('/auth/logout')
def logout(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        return {"msg": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
