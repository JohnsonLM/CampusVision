# import app
from app import app

# initialize app
app = app.create_app()

# run app
if __name__ == "__main__":
    app.run()
