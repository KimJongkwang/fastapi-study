"""상수"""
JWT_SECRET = "ABCD1234!"
JWT_ALGORITHM = "HS256"
EXCEPT_PATH_LIST = ["/", "/openapi.json"]
EXCEPT_PATH_REGEX = "^(/docs|/redoc|/api/auth)"
# EXCEPT_PATH_REGEX = "^(/redoc|/auth)"
MAX_API_KEY = 3
MAX_API_WHITELIST = 10
