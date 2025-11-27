import base64
from fastapi import HTTPException
from app.config import access_requirements


# Custom dependency for access control
def authorize_access(endpoint: str, token: dict):
    '''
    This function checks the user's token to see if they have access to the requested endpoint

    Parameters:
        endpoint (str): The endpoint to be checked
        token (dict): The user's token from the get_current_user function
    
    Returns:
        bool: True if the user has access to the endpoint, False otherwise
    '''
    role = None
    power = None
    for claim, value in token.items():
        if ':power' in claim:
            role, _ = claim.split(':')
            power = base64.b64decode(value).decode('utf-8')
            break

    # If there's no role in the token, raise an HTTP exception
    if not role:
        raise HTTPException(status_code=403, detail={"message": "Missing role"})

    # If there's a role in the token but no experience level, default the experience level to 'muscles'
    if role and not power:
        power = 'muscles'

    # If there's no role or experience level in the token, raise an HTTP exception
    if not role or not power:
        raise HTTPException(status_code=403, detail={"message": "Missing role or power"})

    # Get the requirements for the requested endpoint
    endpoint_requirements = access_requirements.get(endpoint)

    # If the endpoint is not in the access control list, raise an HTTP exception
    if not endpoint_requirements:
        raise HTTPException(status_code=403, detail={"message": "Endpoint not found in access control list"})

    # Check if the user's role and experience level meet the requirements for the requested endpoint
    for requirement in endpoint_requirements:
        required_role = requirement['role']
        required_power = requirement['power']

        # Experience level hierarchy
        powers = ['muscles', 'clever', 'all']

        if role == required_role and powers.index(power) >= powers.index(required_power):
            return True

    # If the user doesn't meet the requirements, raise an HTTP exception
    raise HTTPException(status_code=403, detail={"message": f"Access denied! You are {role} with {power} power type and therefore cannot access {endpoint}"})
