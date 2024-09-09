from flask import Flask, render_template, request, redirect, url_for
from database import get_db
import transaction
from persistent.mapping import PersistentMapping
import uuid
from datetime import datetime
import transaction


app = Flask(__name__)

@app.route('/')
def index():
    db = get_db()
    connection = db._p_jar
    root = connection.root()

    # Obtendo apenas produtos e pedidos para a página inicial
    employees = root.get('employees', {})
    products = root.get('products', {})
    orders = root.get('orders', {})
    
    return render_template('index.html', products=products, orders=orders, employees=employees)

# Rotas para Gestão de Produtos
@app.route('/products')
def products():
    db = get_db()  # Obtém o banco de dados
    connection = db._p_jar  # Abre a conexão
    root = connection.root()  # Acessa a raiz do banco de dados

    # Recupera os produtos do banco de dados
    products = root.get('products', {})

    print("Products being sent to template:")
    for pid, product in products.items():
        print(f"ID: {pid}, Name: {product['name']}, Stock: {product['quantity']}")

    # Não fechar manualmente a conexão!
    return render_template('products.html', products=products)


@app.route('/add_product', methods=['POST'])
def add_product():
    db = get_db()  # Obtém o banco de dados
    connection = db._p_jar  # Abre a conexão
    root = connection.root()  # Acessa a raiz do banco de dados

    # Recebe os dados do formulário
    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])

    print(f"Adding product: {name}, {description}, {price}, {quantity}")

    # Verifica se a chave 'products' existe, se não, cria
    if 'products' not in root:
        root['products'] = PersistentMapping()

    products = root['products']

    # Gera um novo ID para o produto
    product_id = str(len(products) + 1)

    # Adiciona o produto ao banco
    products[product_id] = {
        'name': name,
        'description': description,
        'price': price,
        'quantity': quantity
    }

    # Salva a transação no banco de dados
    transaction.commit()  # Confirma a transação e deixa o ZODB gerenciar a conexão

    # Não fechar manualmente a conexão!
    return redirect(url_for('products'))


@app.route('/delete_product/<id>')
def delete_product(id):
    db = get_db()
    connection = db._p_jar
    root = connection.root()

    if 'products' in root:
        products = root['products']
        if id in products:
            del products[id]
            transaction.commit()

    return redirect(url_for('products'))

# Rotas para Gestão de Pedidos
@app.route('/orders')
def orders():
    db = get_db()
    connection = db._p_jar
    root = connection.root()

    # Abortamos qualquer transação pendente para garantir que o estado mais recente seja carregado
    transaction.abort()

    # Recupera os produtos e pedidos do banco de dados
    products = root.get('products', {})
    orders = root.get('orders', {})

    # Debug: Verificar se as ordens estão sendo recuperadas corretamente
    print("Orders being sent to template:")
    if not orders:
        print("No orders found")
    for oid, order in orders.items():
        product_name = products[order['product_id']]['name']
        print(f"Order ID: {oid}, Product: {product_name}, Quantity: {order['quantity']}, Total: {order['total_price']}")

    return render_template('orders.html', orders=orders, products=products)

from datetime import datetime  # Certifique-se de importar o módulo datetime

@app.route('/add_order', methods=['POST'])
def add_order():
    db = get_db()
    connection = db._p_jar
    root = connection.root()

    # Recebe os dados do formulário
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])

    products = root['products']
    product = products.get(product_id)

    # Verifica se o produto existe e se há estoque suficiente
    if not product or product['quantity'] < quantity:
        return redirect(url_for('orders', error="Insufficient stock or product not found"))

    total_price = product['price'] * quantity

    # Verifica se 'orders' já existe no banco de dados, se não, cria
    if 'orders' not in root:
        root['orders'] = PersistentMapping()

    orders = root['orders']

    # Gera um ID único para o novo pedido usando UUID
    order_id = str(uuid.uuid4())

    # Captura a data e hora atual
    current_datetime = datetime.now()

    # Cria o novo pedido com a data atual
    orders[order_id] = {
        'product_id': product_id,
        'quantity': quantity,
        'total_price': total_price,
        'date_created': current_datetime  # Adiciona a data de criação
    }

    # Atualiza o estoque do produto
    product['quantity'] -= quantity
    products[product_id] = product

    # Salva a transação no banco de dados
    transaction.commit()

    # Debug: Verificar se o pedido foi salvo corretamente com a data
    print(f"Order added with ID: {order_id}, Date: {current_datetime}, Product: {product['name']}, Quantity: {quantity}, Total: {total_price}")

    return redirect(url_for('orders'))


    # Fechar a conexão explicitamente após o commit
    connection.close()

    return redirect(url_for('orders'))

@app.route('/finalize_order/<order_id>')
def finalize_order(order_id):
    db = get_db()
    connection = db._p_jar
    root = connection.root()

    if 'orders' in root:
        orders = root['orders']
        if order_id in orders:
            orders[order_id]['finalized'] = True  # Marca o pedido como finalizado
            print(f"Order with ID {order_id} finalized.")
            transaction.commit()  # Confirma a atualização

    connection.close()
    return redirect(url_for('orders'))

@app.route('/delete_order/<order_id>')
def delete_order(order_id):
    db = get_db()
    connection = db._p_jar
    root = connection.root()

    if 'orders' in root:
        orders = root['orders']
        if order_id in orders:
            del orders[order_id]  # Remove o pedido
            print(f"Order with ID {order_id} deleted.")
            transaction.commit()  # Confirma a exclusão

    connection.close()
    return redirect(url_for('orders'))


# Rotas para Employees
@app.route('/employees')
def employees():
    db = get_db()
    connection = db._p_jar
    root = connection.root()

    # Abortamos qualquer transação pendente para garantir que o estado mais recente seja carregado
    transaction.abort()

    # Recupera os funcionários do banco de dados
    employees = root.get('employees', {})

    # Debug: Verificar se os funcionários estão sendo recuperados corretamente
    print("Employees being sent to template:")
    if not employees:
        print("No employees found")
    for eid, employee in employees.items():
        print(f"Employee ID: {eid}, Name: {employee['name']}, Position: {employee['position']}, Salary: {employee['salary']}")

    # Fecha a conexão explicitamente após a leitura
    connection.close()

    return render_template('employees.html', employees=employees)


@app.route('/add_employee', methods=['POST'])
def add_employee():
    db = get_db()
    connection = db._p_jar
    root = connection.root()

    # Recebe os dados do formulário
    name = request.form['name']
    position = request.form['position']
    salary = float(request.form['salary'])

    # Captura a data e hora atual
    current_datetime = datetime.now()

    # Verifica se 'employees' já existe no banco de dados, se não, cria
    if 'employees' not in root:
        root['employees'] = PersistentMapping()

    employees = root['employees']

    # Gera um ID único para o novo funcionário
    employee_id = str(uuid.uuid4())

    # Adiciona o novo funcionário
    employees[employee_id] = {
        'name': name,
        'position': position,
        'salary': salary,
        'date_joined': current_datetime
    }

    # Salva a transação no banco de dados
    transaction.commit()

    # Debug: Verificar o estado completo dos funcionários após a adição
    print("Employees in the database after addition:")
    for eid, employee in employees.items():
        print(f"Employee ID: {eid}, Name: {employee['name']}, Position: {employee['position']}, Salary: {employee['salary']}")

    # Fecha a conexão explicitamente após o commit
    connection.close()

    return redirect(url_for('employees'))



@app.route('/delete_employee/<employee_id>')
def delete_employee(employee_id):
    db = get_db()
    connection = db._p_jar
    root = connection.root()

    if 'employees' in root:
        employees = root['employees']
        if employee_id in employees:
            del employees[employee_id]  # Remove o funcionário
            print(f"Employee with ID {employee_id} deleted.")
            transaction.commit()  # Confirma a exclusão

    connection.close()
    return redirect(url_for('employees'))


#Rota gestão controle de entradas
@app.route('/stock')
def stock_control():
    db = get_db()
    connection = db._p_jar
    root = connection.root()

    products = root.get('products', {})
    return render_template('stock_control.html', products=products)

@app.route('/update_stock/<product_id>', methods=['POST'])
def update_stock(product_id):
    db = get_db()
    connection = db._p_jar
    root = connection.root()

    new_quantity = int(request.form['quantity'])

    products = root['products']
    if product_id in products:
        product = products[product_id]
        product['quantity'] = new_quantity
        products[product_id] = product
        transaction.commit()

    return redirect(url_for('stock_control'))

@app.route('/increase_stock/<product_id>')
def increase_stock(product_id):
    db = get_db()
    connection = db._p_jar
    root = connection.root()

    if 'products' in root:
        products = root['products']
        if product_id in products:
            products[product_id]['quantity'] += 1  # Aumenta o estoque em 1
            print(f"Stock increased for product ID {product_id}. New stock: {products[product_id]['quantity']}")
            transaction.commit()  # Confirma a atualização

    connection.close()
    return redirect(url_for('stock_control'))

@app.route('/decrease_stock/<product_id>')
def decrease_stock(product_id):
    db = get_db()
    connection = db._p_jar
    root = connection.root()

    if 'products' in root:
        products = root['products']
        if product_id in products and products[product_id]['quantity'] > 0:
            products[product_id]['quantity'] -= 1  # Diminui o estoque em 1
            print(f"Stock decreased for product ID {product_id}. New stock: {products[product_id]['quantity']}")
            transaction.commit()  # Confirma a atualização

    connection.close()
    return redirect(url_for('stock_control'))

@app.route('/reports')
def reports():
    # Exemplo de dados do banco de dados (substitua pelos dados reais)
    sales_data = [1000, 1500, 1300, 1200, 1400, 1700]  # Dados de vendas
    stock_data = [500, 300, 600, 400, 200, 700]  # Dados de estoque
    employees_data = [10, 12, 11, 14, 13, 15]  # Dados de funcionários
    
    return render_template('reports.html', sales_data=sales_data, stock_data=stock_data, employees_data=employees_data)


@app.route('/dashboards')
def dashboards():
    # Dados fictícios, substitua pelos dados reais do banco de dados
    monthly_sales = [1200, 1500, 1300, 1700, 1900, 2100]
    stock_distribution = [20, 30, 15, 10, 25]
    employee_performance = [80, 90, 75, 85, 70]
    
    return render_template('dashboards.html',
                           monthly_sales=monthly_sales,
                           stock_distribution=stock_distribution,
                           employee_performance=employee_performance)


if __name__ == '__main__':
    app.run(debug=True)
