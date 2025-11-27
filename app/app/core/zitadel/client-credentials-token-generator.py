import json
import http.client
import base64
from urllib.parse import urlencode
from app.config import app_config


# Encode the client ID and client secret in Base64
client_credentials = f"{app_config.client_id}:{app_config.client_secret}".encode("utf-8")
base64_client_credentials = base64.b64encode(client_credentials).decode("utf-8")

# Construct request body
data = {
    "grant_type": "client_credentials",
    "scope": f"openid profile email urn:zitadel:iam:org:project:id:{app_config.project_id}:aud urn:zitadel:iam:org:projects:roles urn:zitadel:iam:user:metadata"
}
encoded_data = urlencode(data)

# Construct request headers
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {base64_client_credentials}"
}

# Establish connection to ZITADEL_TOKEN_URL
conn = http.client.HTTPSConnection(app_config.http_client_url)

# Send POST request
conn.request("POST", app_config.http_client_token, encoded_data, headers)

# Get response
response = conn.getresponse()

if response.status == 200:
    # Read response data
    response_data = response.read()
    access_token = json.loads(response_data.decode())["access_token"]
    print(f"Response: {json.loads(response_data.decode())}")
    print(f"Access token: {access_token}")
else:
    print(f"Error: {response.status} - {response.reason}")

# Close connection
conn.close()