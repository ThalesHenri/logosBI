from storage.repository import DatabaseRepository
from ui.app  import LogosBIApp
from etl import PedidoPipeline
from ui.state import AppState


def main():
    repository = DatabaseRepository()
    repository.connect()
    repository.create_schema()
    pipeline = PedidoPipeline(repository)
    
    AppState.repository = repository
    AppState.pipeline = pipeline
    

    
    
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
    
    
