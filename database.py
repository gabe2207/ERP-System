import ZODB, ZODB.FileStorage
import transaction
from persistent.mapping import PersistentMapping

db = None

def get_db():
    global db
    if db is None:
        # Inicializa o banco de dados ZODB com o arquivo de armazenamento
        storage = ZODB.FileStorage.FileStorage('erp_data.fs')
        db = ZODB.DB(storage)
    
    connection = db.open()
    root = connection.root()

    # Verifica se 'orders' e 'products' existem no banco, senão cria
    if 'products' not in root:
        root['products'] = PersistentMapping()
    if 'orders' not in root:
        root['orders'] = PersistentMapping()
    if 'employees' not in root:
        root['employees'] = PersistentMapping()
    return root
