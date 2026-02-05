from storage.repository import DatabaseRepository


def main():
    repository = DatabaseRepository()
    repository.create_schema()
    # depois: ETL, UI
    

if __name__ == "__main__":
    main()
        
