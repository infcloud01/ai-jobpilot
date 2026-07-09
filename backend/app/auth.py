import os
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

security = HTTPBearer()

# Your Google OAuth Client ID will be injected via environment variables
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")

def verify_google_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Validates an incoming Google JWT from the authorization header.
    Returns the parsed user profile information if valid.
    """
    token = credentials.credentials
    try:
        # Verify the token using Google's public keys
        # This checks expiration, signature, and audience targets automatically
        id_info = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Multi-Tenant Guardrail: Ensure the user's profile is fully populated
        if not id_info.get("sub"):
            raise HTTPException(status_code=401, detail="Invalid token payload: missing subject ID.")
            
        return {
            "user_id": id_info["sub"],
            "email": id_info.get("email"),
            "name": id_info.get("name"),
            "picture": id_info.get("picture")
        }
        
    except ValueError as e:
        # Triggered if token is expired, modified, or has an invalid signature
        raise HTTPException(status_code=401, detail=f"Invalid or expired Google Token: {str(e)}")
