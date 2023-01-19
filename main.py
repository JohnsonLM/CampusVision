from app import app

app = app.create_app()

if __name__ == "__main__":
    # remove host and port on deployment?
    app.run(host='0.0.0.0', port='80')
