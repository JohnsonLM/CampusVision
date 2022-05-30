# improt app
from app import app

# initilize app
app = app.create_app()

# run app
if __name__ == "__main__":
    app.run()
