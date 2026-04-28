from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import HashModel, Migrator
from starlette.requests import Request
import requests
from pydantic_settings import BaseSettings, SettingsConfigDict
from database import redis

class AppSettings(BaseSettings):
    app_redis_host: str = "localhost"
    app_redis_port: int = 6379
    app_redis_password: str = ""
    inventory_url: str = "http://localhost:8000"

    # Automatski će povući INVENTORY_URL iz docker-compose environment-a
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

app_settings = AppSettings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

# KLJUČNA IZMENA: Dodat index=True
class Order(HashModel, index=True):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str

    class Meta:
        database = redis

@app.get('/orders/{pk}')
def get(pk: str):
    return Order.get(pk)

@app.post('/orders')
async def create(request: Request):
    body = await request.json()

    # Koristimo URL iz podešavanja (u Dockeru će biti http://inventory-api:8000)
    req = requests.get(f'{app_settings.inventory_url}/products/{body["id"]}')
    req.raise_for_status() # Dobra praksa: izbaci grešku ako Inventory ne odgovori
    product = req.json()

    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2 * product['price'],
        total=1.2 * product['price'],
        quantity=body['quantity'],
        status='pending'
    )
    
    order.save()
    
    # Slanje događaja u Redis Stream
    redis.xadd('order_completed', order.dict(), '*')
    
    return order

# Neophodno da bi Redis-OM napravio indekse u bazi čim se aplikacija pokrene
Migrator().run()