from celery import Celery
from celery.schedules import crontab
from django.utils import timezone
from .models import Product, Bid
from config.celery import app
from django.db.models import Q
from accounts.models import User
import logging
import traceback

# 로거 설정
logger = logging.getLogger(__name__)

@app.task(name="update_product_status")
def update_product_status():
    try:
        current_time = timezone.now()
        logger.info("Updating product status...")

        # 경매 종료된 상품 처리
        expired_products = Product.objects.filter(
            auction_end_time__lt=current_time,
            product_status=True
        )
        for product in expired_products:
            product.product_status = False
            product.save()
            logger.info(f"Updated product {product.id} status to False.")

            # 입찰 정보가 있는 경우
            if product.present_max_bid_price is not None and product.present_max_bidder_id is not None:
                try:
                    bidder = User.objects.get(id=product.present_max_bidder_id)
                    new_bid = Bid(
                        bidder=bidder,
                        product=product,
                        bid_result=True,
                        bid_price=product.present_max_bid_price,
                        bid_time=product.auction_end_time
                    )
                    new_bid.save()
                    logger.info(f"New bid created for product {product.id} by bidder {bidder.id}.")
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
