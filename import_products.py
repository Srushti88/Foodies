import json
import asyncio
import httpx

API_URL = "http://localhost:8000/products/"

async def import_products():
    with open("fast_food_products.json") as f:
        products = json.load(f)

    async with httpx.AsyncClient() as client:
        for product in products:
            response = await client.post(API_URL, json=product)
            if response.status_code == 200:
                print(f"Imported: {product['name']}")
            else:
                print(f"Failed: {product['name']} - {response.text}")
async def import_products():
    with open("fast_food_products.json") as f:
        products = json.load(f)

    async with httpx.AsyncClient() as client:
        for product in products:
            response = await client.post(API_URL, json=product)
            if response.status_code == 200:
                print(f"Imported: {product['name']}")
            elif response.status_code == 409:
                print(f"Already exists: {product['product_id']}")
            else:
                print(f"Failed: {product['name']} - {response.text}")

if __name__ == "__main__":
    asyncio.run(import_products())
