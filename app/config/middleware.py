import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.config.logger_config import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        logger.info(f"Request: method={request.method} url={request.url.path}")
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        logger.info(f"Response: status_code={response.status_code} duration={duration:.4f} seconds")
        
        return response
