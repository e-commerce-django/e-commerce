from celery import shared_task
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import Product, Bidder, Bid
from .views import get_imp_token
import requests

@shared_task
def try_payment(bidder_id, product_id, bid_price, billing_key):
    try:
        product = Product.objects.get(pk=product_id)
        token = get_imp_token()  # 토큰 가져오기

        url = "https://api.iamport.kr/subscribe/payments/again"
        data = {
            'customer_uid': billing_key,
            'merchant_uid': f"{product_id}_{bidder_id}",
            'amount': bid_price
        }
        headers = {
            'Authorization': token
        }
        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result['code'] == 0:
            product.product_status = True
            product.present_max_bid_price = bid_price
            product.present_max_bidder_id = bidder_id
            product.save()

            Bid.objects.create(
                bidder_id=bidder_id,
                product=product,
                bid_result=True,
                bid_price=bid_price,
                bid_time=timezone.now()
            )

            send_payment_email.delay(bidder_id, product_id, True)  # 결제 성공 이메일 보내기
            return True
        else:
            failure_reason = result['message']['fail_reason']
            send_payment_email.delay(bidder_id, product_id, False, failure_reason)  # 결제 실패 이메일 보내기
            return False
    except Exception as e:
        # 예외 처리
        print(f"Error in try_payment: {e}")
        return False

@shared_task
def complete_auction():
    try:
        products = Product.objects.filter(auction_end_time__lte=timezone.now(), product_status=False)
        for product in products:
            bidders = Bidder.objects.filter(product=product).order_by('-bid_price')
            if bidders.exists():
                bidder = bidders.first()
                try_payment.delay(bidder.bidder_id, product.id, bidder.bid_price, bidder.billing_key)
    except Exception as e:
        # 예외 처리
        print(f"Error in complete_auction: {e}")

@shared_task
def send_payment_email(bidder_id, product_id, success, failure_reason=None):
    try:
        bidder = Bidder.objects.get(pk=bidder_id)
        product = Product.objects.get(pk=product_id)

        if success:
            subject = "결제 완료 안내"
            message = f"축하합니다! {product.name} 상품의 결제가 성공적으로 완료되었습니다."
        else:
            subject = "결제 실패 안내"
            if failure_reason == "CARD_EXPIRED":
                message = f"죄송합니다. {product.name} 상품의 결제가 실패하였습니다. 카드의 유효기간이 만료되었습니다."
            elif failure_reason == "INSUFFICIENT_BALANCE":
                message = f"죄송합니다. {product.name} 상품의 결제가 실패하였습니다. 카드 잔액이 부족합니다."
            else:
                message = f"죄송합니다. {product.name} 상품의 결제가 실패하였습니다. 다른 이유로 결제가 실패하였습니다."

        from_email = settings.EMAIL_HOST_ID
        msg = EmailMultiAlternatives(subject, message, from_email, [bidder.email])
        msg.send()
    except Exception as e:
        # 예외 처리
        print(f"Error in send_payment_email: {e}")
