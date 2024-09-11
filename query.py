# Imports necessários
import ZODB, ZODB.FileStorage
from datetime import datetime

# Função para conectar ao banco de dados ZODB
db = None  # Variável global para o banco de dados
def get_db():
    global db
    if db is None:
        storage = ZODB.FileStorage.FileStorage('erp_data.fs')
        db = ZODB.DB(storage)
    connection = db.open()
    return connection.root()

# Funções de queries
def query_list_products():
    root = get_db()  
    products = root.get('products', {})
    for product_id, product in products.items():
        print(f"Produto ID: {product_id}, Nome: {product['name']}, Estoque: {product['quantity']}")

def query_count_employees():
    root = get_db()  
    employees = root.get('employees', {})
    print(f"Total de funcionários: {len(employees)}")

def query_find_product_by_id(product_id='1'):
    root = get_db()  
    product = root['products'].get(product_id, None)
    if product:
        print(f"Nome: {product['name']}, Preço: {product['price']}, Estoque: {product['quantity']}")
    else:
        print("Produto não encontrado.")

def query_total_sales():
    root = get_db()  
    orders = root.get('orders', {})
    total_sales = sum(order['total_price'] for order in orders.values())
    print(f"Total de vendas: {total_sales}")

def query_orders_by_product(product_id='1'):
    root = get_db()  
    orders = root.get('orders', {})
    for order_id, order in orders.items():
        if order['product_id'] == product_id:
            print(f"Pedido ID: {order_id}, Quantidade: {order['quantity']}, Total: {order['total_price']}")

def query_employees_by_salary(salary_threshold=5000.00):
    root = get_db()  
    employees = root.get('employees', {})
    for employee_id, employee in employees.items():
        if employee['salary'] > salary_threshold:
            print(f"Funcionário: {employee['name']}, Salário: {employee['salary']}")

def query_avg_product_price():
    root = get_db()  
    products = root.get('products', {})
    avg_price = sum(product['price'] for product in products.values()) / len(products)
    print(f"Média de preço dos produtos: {avg_price}")

def query_orders_by_date(start_date=datetime(2023, 1, 1), end_date=datetime(2023, 12, 31)):
    root = get_db()  
    orders = root.get('orders', {})
    for order_id, order in orders.items():
        if start_date <= order['date_created'] <= end_date:
            print(f"Pedido ID: {order_id}, Data: {order['date_created']}, Total: {order['total_price']}")

def query_avg_stock_sold():
    root = get_db()  
    orders = root.get('orders', {})
    products = root.get('products', {})
    total_stock_used = 0
    total_products_sold = 0
    for order in orders.values():
        product_id = order['product_id']
        product = products[product_id]
        total_stock_used += product['quantity']
        total_products_sold += 1
    avg_stock = total_stock_used / total_products_sold if total_products_sold > 0 else 0
    print(f"Estoque médio dos produtos vendidos: {avg_stock}")

def query_orders_with_products_and_employees():
    root = get_db()  
    orders = root.get('orders', {})
    products = root.get('products', {})
    employees = root.get('employees', {})
    for order_id, order in orders.items():
        product = products.get(order['product_id'])
        employee = employees.get(order.get('employee_id'))
        print(f"Pedido {order_id}: Produto: {product['name']}, Quantidade: {order['quantity']}, "
              f"Vendido por: {employee['name'] if employee else 'Desconhecido'}")

# query_list_products()
# query_count_employees()
# query_find_product_by_id('1')
# query_total_sales()
# query_orders_by_product('1')
# query_employees_by_salary(5000.00)
# query_avg_product_price()
query_orders_by_date(datetime(2023, 1, 1), datetime(2024, 12, 31))
query_avg_stock_sold()
query_orders_with_products_and_employees()
