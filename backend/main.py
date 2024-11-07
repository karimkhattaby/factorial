# Default libs
import logging

# local imports
import user_actions
import Models.api_models

# FastAPI
from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from uvicorn.config import LOGGING_CONFIG as log_config

# 3rd Party libs
from asgi_logger import AccessLoggerMiddleware # asgi-logger
from dotenv import load_dotenv # python-dotenv

# ENV
load_dotenv('.env')

# Access logger format
AccessLoggerMiddleware.DEFAULT_FORMAT = '%(t)s %(client_addr)s - "%(request_line)s" %(status_code)s - %(M)s ms'

# App init
app = FastAPI(
    title='VaulFi API',
    version='1.0.0',
    middleware=[Middleware(AccessLoggerMiddleware)],
)

logger = None

@app.on_event("startup")
def startup():
    # Logger init
    global logger
    logger = logging.getLogger('uvicorn.error')
    logging.getLogger("uvicorn.access").handlers = [] # remove uvicorn's access logger

# CORS
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Endpoints
@app.get('/')
async def root():
    return {'status': 'Success'}

@app.get('/products')
async def get_products():
    return user_actions.get_products()

@app.get('/parts/{product_id}')
async def get_parts(product_id: str):
    return user_actions.get_parts(product_id)

@app.get('/variations/{part_id}')
async def get_variations(part_id: str):
    return user_actions.get_variations(part_id)

@app.post('/checkout')
async def checkout(details: api_models.OrderDetails, request: Request):
    pass

@app.put('/stock')
async def update_stock(variation_id: str, toggle: bool):
    pass