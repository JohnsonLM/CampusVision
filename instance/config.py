"""
config.py basic configuration
"""

# add a secure 256-bit key here using a key generator such as allkeysgenerator.com
SECRET_KEY = 'SuperSecureK3yHere'

# points the app the primary database
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'

# points the app to the upload folder within the static directory.
UPLOAD_FOLDER = '/uploads'

# sets the maximum bit length of uploads.
MAX_CONTENT_LENGTH = 50 * 1000 * 1000

# Allows template updates to be loaded without restarting the app.
TEMPLATES_AUTO_RELOAD = True

# Should be set false to prevent warnings.
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Insert an OpenWeatherMap API key here.
WEATHER_KEY = '99ec4e7d956393e48a8cda51317329c5'

# Sets what file types can be uploaded as slides
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4'}

# For pagination of the slide manager
POSTS_PER_PAGE = 10
