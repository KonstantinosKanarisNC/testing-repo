import jwt, logging
import jwt.algorithms as algorithms
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer
from starlette.status import HTTP_403_FORBIDDEN
from app.config import app_config
from app.core.zitadel.access_control import authorize_access

# Create an instance of the HTTPBearer class
oauth2_scheme = HTTPBearer()

def authorize_with_keys(keys, token, jwt_options, endpoint):
    '''
    This function authorizes the user with the given keys

    Parameters:
        keys (list): The list of keys to be used for authorization
        token (str): The token to be checked
        jwt_options (dict): The options to be used for the JWT
        endpoint (str): The endpoint to be checked

    Returns:
        bool: True if the authorization is successful, False otherwise
    '''
    for i,key in enumerate(keys):
        public_key = algorithms.RSAAlgorithm.from_jwk(key)
        try:
            decoded_token = jwt.decode(
                token, public_key, audience=app_config.project_id,
                algorithms=app_config.algorithm, verify=True, options=jwt_options
            )
            return decoded_token  # Authorization successful
            # return authorize_access(endpoint.__name__, decoded_token)
        
        except jwt.ExpiredSignatureError as e:
            logging.error(f"Token has expired: {e}")
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Token has expired")
        except jwt.InvalidSignatureError as e:
            continue  # Try the next key
        except jwt.InvalidTokenError as e:
            if i == len(keys) - 1:
                logging.error(f"Invalid token: {e}")
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid token")
    return False  # Authorization faileds

def get_current_user( request: Request, token: str = Depends(oauth2_scheme)):
    '''
    This function decodes the user's token and checks if it is valid

    Parameters:
        token (str): The token to be checked
        request (Request): The request object

    Returns:
        bool: True if the authorization is successful, False otherwise
    ''' 

    jwt_options = {
        'verify_signature': True,
        'verify_exp': True,
        'verify_nbf': False,
        'verify_iat': True,
        'verify_aud': False
    }

    # Get the endpoint name
    endpoint = request.scope.get("endpoint")
    token = token.credentials
    keys = app_config.jwk_data["keys"]
    
    # Attempt to authorize with the current keys
    decoded_token = authorize_with_keys(keys, token, jwt_options, endpoint)
    if decoded_token is not False:
        return decoded_token  # Authorization successful
    else:
        logging.info("Refreshing keys")
        keys = app_config.get_keys_from_jwks()["keys"]
        decoded_token = authorize_with_keys(keys, token, jwt_options, endpoint)
        if decoded_token is not False:
            return decoded_token  # Authorization successful
        else:
            # If all keys still fail, raise the exception
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid signature")
