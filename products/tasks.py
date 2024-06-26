from celery import Celery, shared_task
from celery.schedules import crontab
from django.utils import timezone
from .models import Product, Bid
from config.celery import app
from django.db.models import Q
from accounts.models import User
import logging
import traceback
from datetime import timedelta
from django.core.mail import send_mail, EmailMultiAlternatives
from products.models import Bid, Product, Bidder
from .models import User
from django.http import JsonResponse
import random
import os
import requests 
from dotenv import load_dotenv
from .payment import process_payment
load_dotenv()

# 로거 설정
logger = logging.getLogger(__name__)

@app.task(name="update_product_status")
def update_product_status():
    try:
        current_time = timezone.now()
        logger.info("Updating product status...")

        # 시간 체크, 이메일 전송 처리
        intervals = [24, 12, 6, 1]
        for hours in intervals:
            time_threshold = current_time + timedelta(hours=hours)
            ongoing_email_products = Product.objects.filter(
                auction_end_time__lte=time_threshold + timedelta(seconds=5),
                auction_end_time__gte=time_threshold - timedelta(seconds=5),
                product_status=True
            )
            for product in ongoing_email_products:
                send_auction_alert_emails(product, hours)

        # 경매 종료된 상품 처리
        expired_products = Product.objects.filter(
            auction_end_time__lt=current_time,
            product_status=True
        )
        for product in expired_products:
            send_auction_alert_emails(product, 0)
            product.product_status = False
            product.save()
            logger.info(f"Updated product {product.id} status to False.")

            # 입찰 정보가 있는 경우
            if product.present_max_bid_price is not None and product.present_max_bidder_id is not None:
                try:
                    bidder = User.objects.get(id=product.present_max_bidder_id)

                    success = process_payment(    # 상품 결제
                        customer_uid=bidder.id,  # 사용자의 고유 customer_uid
                        merchant_uid=f"payment-{product.id}",  # 주문 고유 번호
                        product_name=product.name,
                        amount=product.present_max_bid_price  # 결제할 금액
                    )
                    if success:
                        # 결제 성공 시 입찰 정보 생성
                        new_bid = Bid(
                          bidder=bidder,
                          product=product,
                          bid_result=True,
                          bid_price=product.present_max_bid_price,
                          bid_time=product.auction_end_time
                      )
                        new_bid.save()
                        logger.info(f"New bid created for product {product.id} by bidder {bidder.id}.")
                    else:
                        logger.error(f"Failed to process payment for product {product.id}.")
                    
                except User.DoesNotExist:
                    logger.error(f"No user found with ID {product.present_max_bidder_id} for product {product.id}.")
                    logger.error(traceback.format_exc())

            # 입찰 정보가 없는 경우
            else:
                new_bid = Bid(
                    bidder=None,
                    product=product,
                    bid_result=False,
                    bid_price=None,
                    bid_time=product.auction_end_time
                )
                new_bid.save()
                logger.info(f"New bid created with no bidder for product {product.id}.")

        # 경매가 진행 중인 상품 처리
        ongoing_products = Product.objects.filter(
            auction_start_time__lte=current_time,
            auction_end_time__gte=current_time,
            product_status=False
        )
        for product in ongoing_products:
            product.product_status = True
            product.save()
            logger.info(f"Updated product {product.id} status to True.")
            
    except Exception as e:
        logger.error('Error in update_product_status task: {}'.format(str(e)))
        logger.error(traceback.format_exc())
        raise e

def send_auction_alert_emails(product, hours):
    bidders = Bidder.objects.filter(product_id=product)

    # 최고 입찰자가 있는 경우
    winner = None
    if product.present_max_bidder_id is not None:
        winner = User.objects.get(id=product.present_max_bidder_id)

    recipient_emails = [bidder.bidder_id.email for bidder in bidders if bidder.bidder_id is not None and  bidder.bidder_id.id != product.present_max_bidder_id]

    #모든 입찰자에게 이메일 전송
    if recipient_emails:
        send_email(recipient_emails, product, hours)

    # 최고 입찰자에게 이메일 전송
    if winner:
        send_winner_email(winner.email, product, hours)
    
    

def send_email(recipient_email, product, hours):
    if hours == 0:
        subject = f"{product.name} 상품의 입찰이 종료되었습니다."
        message = f"{product.name} 상품의 입찰이 종료되었습니다. 입찰에 실패하였습니다! 다음 기회를 노리세요!"
        from_email = os.getenv("EMAIL_HOST_ID")
    else:
        subject = f"{product.name} 상품의 입찰이 {hours}시간 남았습니다."
        message = f"{product.name} 상품의 입찰이 {hours}시간 남았습니다. 구매할 기회를 놓치지 마세요!"
        from_email = os.getenv("EMAIL_HOST_ID")
    msg = EmailMultiAlternatives(
          subject,
          message,
          from_email
      )
    msg.to = recipient_email
    try:
        msg.send()
        logger.info(f"Email sent to {recipient_email} for product {product.id}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email} for product {product.id}: {e}")
        logger.error(traceback.format_exc())

def send_winner_email(winner_email, product, hours):
    if hours == 0:
        subject = f"{product.name} 상품의 입찰이 종료되었습니다."
        message = f"{product.name} 상품의 입찰이 종료되었습니다. 축하합니다! 입찰에 성공하였습니다!"
        from_email = os.getenv("EMAIL_HOST_ID")
    else:
        subject = f"{product.name} 상품의 입찰이 {hours}시간 남았습니다."
        message = f"{product.name} 상품의 입찰이 {hours}시간 남았습니다. 현재 최고 입찰자입니다!"
        from_email = os.getenv("EMAIL_HOST_ID")
    
    from_email = os.getenv("EMAIL_HOST_ID")
    msg = EmailMultiAlternatives(
        subject,
        message,
        from_email
    )
    msg.to = [winner_email]
    try:
        msg.send()
        logger.info(f"Email sent to {winner_email} for product {product.id}")
    except Exception as e:
        logger.error(f"Failed to send email to {winner_email} for product {product.id}: {e}")
        logger.error(traceback.format_exc())


from celery import shared_task
import boto3
import botocore
@app.task(name="get-model-params-every-day")
def get_model_params():
    s3_uri = os.getenv("S3_MODEL_URI")
    bucket_name = s3_uri.split('/')[2]
    prefix = '/'.join(s3_uri.split('/')[3:])

    local_base_path = '../embedding_cache'

    session = boto3.Session()
    s3 = session.client('s3')

    if not os.path.exists(local_base_path):
        os.makedirs(local_base_path)

    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' not in response:
            return "No objects found in the specified S3 prefix."

        for obj in response['Contents']:
            s3_key = obj['Key']
            relative_path = os.path.relpath(s3_key, prefix)
            local_file_path = os.path.join(local_base_path, relative_path)

            local_dir = os.path.dirname(local_file_path)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)

            s3.download_file(bucket_name, s3_key, local_file_path)
            print(f'Downloaded {s3_key} to {local_file_path}')

        return f"All files downloaded successfully to {local_base_path}."
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return "The object does not exist."
        else:
            return f"Error occurred: {e}"

# # @shared_task
# @app.task(name="get-model-params-every-day")
# def get_model_params():

#     s3_uri = os.getenv("S3_MODEL_URI")

#     bucket_name = s3_uri.split('/')[2]
#     object_key = '/'.join(s3_uri.split('/')[3:])

#     local_model_path = '../bert_model.pth'

#     session = boto3.Session()

#     s3 = session.client('s3')

#     try:
#         s3.download_file(bucket_name, object_key, local_model_path)
#         return f"Model downloaded successfully to {local_model_path}."
#     except botocore.exceptions.ClientError as e:
#         if e.response['Error']['Code'] == "404":
#             return "The object does not exist."
#         else:
#             return "Error occurred: {}".format(e)