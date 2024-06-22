import csv
from .models import Product, UserAction

def export_product_data_to_csv():
    products = Product.objects.all()
    with open('products.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'name', 'description', 'category', 'tags', 'size'])
        for product in products:
            writer.writerow([product.id, product.name, product.description, product.category, product.tags, product.size])

def export_user_action_data_to_csv():
    user_actions = UserAction.objects.all()
    with open('user_actions.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['user_id', 'product_id', 'action_type', 'timestamp'])
        for action in user_actions:
            writer.writerow([action.user.id, action.product.id, action.action_type, action.timestamp])
