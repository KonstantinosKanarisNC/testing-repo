from dotenv import load_dotenv
import os, json, http.client

#------------------------- ACCESS CONTROL -------------------------#
# The access_requirements dictionary represents your access control rules.
access_requirements = {
    'random_status': [{'role': 'alpha', 'power': 'muscles'},
                      {'role': 'alpha', 'power': 'clever'},
                      {'role': 'alpha', 'power': 'all'}],
    'random_sleep': [{'role': 'bravo', 'power': 'muscles'},
                     {'role': 'bravo', 'power': 'clever'},
                     {'role': 'bravo', 'power': 'all'}],
    'error_test': [{'role': 'alpha', 'power': 'all'},
                        {'role': 'bravo', 'power': 'clever'},
                        {'role': 'bravo', 'power': 'all'}],
    # Add more endpoints as needed...
}

#------------------------- CONFIGURATION -------------------------#

class AppConfig:
    def __init__(self):
        # the .env should be on gitignore
        self.env_path = ".env"
        self.app_name = None
        # zitadel related configurations
        self.project_id = None
        self.zitadel_domain = None
        self.client_id = None
        self.client_secret = None
        self.zitadel_introspection_url = None
        self.api_client_id = None
        self.api_client_secret = None
        self.algorithm = None
        self.http_client_url = None
        self.http_client_keys_endpoint = None
        self.http_client_token = None
        self.jwk_data = None
        # observability configuration
        self.environment = None
        self.otlp_grpc_endpoint = None
        self.port = None

    def load(self):
        if os.environ.get("APP_NAME") is None:
            # Get the directory of the current script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Construct the path to the .env file
            env_path = os.path.join(current_dir, self.env_path)
            load_dotenv(env_path)

        self.app_name = os.environ.get("APP_NAME")
        # Zitadel related configurations
        self.project_id = os.environ.get("PROJECT_ID")
        self.zitadel_domain = os.environ.get("ZITADEL_DOMAIN")
        self.client_id = os.environ.get("CLIENT_ID")
        self.client_secret = os.environ.get("CLIENT_SECRET")
        self.algorithm = os.environ.get("ALGORITHM")
        self.http_client_url = os.environ.get("HTTP_CLIENT_URL")
        self.http_client_keys_endpoint = os.environ.get("HTTP_CLIENT_KEYS_ENDPOINT")
        self.http_client_token = os.environ.get("HTTP_CLIENT_TOKEN")
        # observability configuration
        self.environment = os.environ.get("ENVIRONMENT", "development")
        self.otlp_grpc_endpoint = os.environ.get("OTLP_GRPC_ENDPOINT", "http://tempo:4317")
        self.logger_name = f'{self.app_name}-logger'
        self.port = os.environ.get("PORT", "8000")

        # retrieve jwk_keys directly on load
        self.jwk_data = self.get_keys_from_jwks()
        # sanity check for the configuration 
        self.sanity_check()

    def sanity_check(self):
        """
        Check if essential variables are set. Raise an exception if any is missing.
        """
        if not self.app_name:
            raise ValueError("APP_NAME is not set. Set it in the environment or .env file.")

        if not self.zitadel_domain:
            raise ValueError("Zitadel domain is not set. Set it in the environment or .env file.")

        if not self.project_id :
            raise ValueError("The zitadel project id is not set. Set them in the environment or .env file.")
        if not self.jwk_data:
            raise ValueError("ZWK failed to be imported.")

    def get_keys_from_jwks(self):
        '''Retrieves the keys from the JWKS endpoint and returns them as a dictionary
        
        Returns:
            dict: The keys from the JWKS endpoint
        '''

        # Define the URL and endpoint
        url = self.http_client_url
        endpoint = self.http_client_keys_endpoint

        # Establish a connection
        conn = http.client.HTTPSConnection(url, timeout=10)

        # Send a GET request
        conn.request("GET", endpoint)

        # Get the response
        response = conn.getresponse()

        if response.status == 200:
            # Read the response data
            data = response.read().decode('utf-8')
            # Parse JSON data
            json_data = json.loads(data)
        else:
            print("Failed to retrieve data. Status code:", response.status)

        # Close the connection
        conn.close()

        return json_data

app_config = AppConfig()
app_config.load()