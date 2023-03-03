from app import app
import ssl

app = app.create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', ssl_context='adhoc')
