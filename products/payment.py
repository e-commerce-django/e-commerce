import os
import requests 
import logging
import traceback

# 로거 설정
logger = logging.getLogger(__name__)

# 토큰 발급
def get_access_token():
    token_url = "https://api.iamport.kr/users/getToken"


    # 환경 변수에서 Iamport API의 클라이언트 인증 정보를 가져옵니다
    imp_key = os.getenv("IAMPORT_API_KEY")
    imp_secret = os.getenv("IAMPORT_API_SECRET")

    auth_data = {
        'imp_key': imp_key,
        'imp_secret': imp_secret,
    }

    try:
        # 토큰 발급 요청
        response = requests.post(token_url, data=auth_data)
        response_data = response.json()

        if response.ok:
            access_token = response_data.get('response').get('access_token')
            token_type = response_data.get('response').get('token_type')
            expires_in = response_data.get('response').get('expires_in')

            print(f"Access Token: {access_token}")
            print(f"Token Type: {token_type}")
            print(f"Expires In: {expires_in} seconds")

            return access_token
        else:
            print(f"Failed to get access token: {response_data}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {str(e)}")
        return None


# 포트원 빌링키 결제 API 호출 함수
def process_payment(customer_uid, merchant_uid, product_name, amount):
    try:
        access_token = get_access_token()   
        if not access_token:
            logger.error("Unable to process payment due to missing access token.")
            return False
        
        api_url = "https://api.iamport.kr/subscribe/payments/again"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        data = {
            "customer_uid": customer_uid,
            "merchant_uid": merchant_uid,
            "name": product_name,
            "amount": {
                "total": amount,
            },
            "currency": "KRW",
        }
        response = requests.post(api_url, headers=headers, json=data)
        response_data = response.json()

        if response.ok:
            logger.info(f"Payment processed successfully: {response_data}")
            return True
        else:
            logger.error(f"Payment processing failed: {response_data}")
            return False

    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        logger.error(traceback.format_exc())
        return False
