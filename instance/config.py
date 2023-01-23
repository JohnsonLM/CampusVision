import os

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

# Sets what file types can be uploaded as slides
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4'}

# Azure AD Config variables.
b2c_tenant = "testliveasbury.onmicrosoft.com"  # Find the tenant domain in the azure portal
signupsignin_user_flow = "B2C_1_signupsignin"
editprofile_user_flow = "B2C_1_profileediting"
resetpassword_user_flow = "B2C_1_passwordreset"
authority_template = "https://{tenant}.b2clogin.com/{tenant}.onmicrosoft.com/{user_flow}"

CLIENT_ID = "a1b519bf-a331-4e53-b164-3e22fb330533"  # Application (client) ID of app registration
# Use an environment variable as described in Flask's documentation for the client secret:
# https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
if not CLIENT_SECRET:
	raise ValueError("Need to define CLIENT_SECRET environment variable")

AUTHORITY = "https://login.microsoftonline.com/testliveasbury.onmicrosoft.com"

REDIRECT_PATH = "/getAToken"
# Used for forming an absolute URL to your redirect URI.
# The absolute URL must match the redirect URI you set
# in the app's registration in the Azure portal.

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
ENDPOINT = 'https://graph.microsoft.com/v1.0/users'  # This resource requires no admin consent

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All"]

SESSION_TYPE = "filesystem"  # Specifies the token cache should be stored in server-side session
