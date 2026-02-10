from storage.repository import DatabaseRepository
from etl.extractor import PedidoPDFExtractor
from config import PATH_INPUT
from ui.app  import LogosBIApp
from ui.state import AppState
from storage.inspec_data import InspectData

def main():
    repository = DatabaseRepository()
    repository.connect()
    repository.create_schema()
    AppState.repository = repository

    
    
    """print(f'este pedido tem os itens{data["itens"]}\n')
    print(f'É do cliente: {data["cliente"]}\n')
    print(f'Foi emitido por{data["emitente"]}\n')
    print(f'Esta são as informações do pedido: {data["pedido"]}\n')
    print(f'O valor total do pedido é: {data["total"]}\n')
    """
    # depois: ETL, UI
    

if __name__ == "__main__":
    main()
    app = LogosBIApp()
    app.run()
    inspector = InspectData()
    inspector.connect()
    inspector.inpsect_db()
    inspector.close()
    
#Reminder bptao de importar funcionando, mas adiciona o mesmo pedido diversas vezes, o cliente e o emitente não