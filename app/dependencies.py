from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

bearer_scheme = HTTPBearer()
# BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
# assert BEARER_TOKEN is not None


# def validate_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
#     if credentials.scheme != "Bearer" or credentials.credentials != BEARER_TOKEN:
#         raise HTTPException(status_code=401, detail="Invalid or missing token")
#     return credentials