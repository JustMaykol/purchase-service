import httpx

from uuid import uuid4
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pymongo import MongoClient

app = FastAPI(
    title='Purchase API',
    description='Purchase API with FastAPI and MongoDB',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

CAR_API = 'http://127.0.0.1:8000/car/'


class Purchase(BaseModel):
    user_id: str
    car_id: str

    user_name: str
    car_name: str

    price: int


try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['purchase']['production']
except Exception as exception:
    print(f"Error connecting to MongoDB: {exception}")


# purchase crud

@app.post(
    '/purchase',
    description='Create a new purchase record and update the availability status of the car.',
    response_description='A message indicating the creation status of the purchase record.'
)
async def create_purchase(purchase: Purchase):
    purchase_id = str(uuid4())

    db.insert_one({
        '_id': purchase_id,

        'user_id': purchase.user_id,
        'car_id': purchase.car_id,

        'user_name': purchase.user_name,
        'car_name': purchase.car_name,

        'price': purchase.price,
    })

    try:
        async with httpx.AsyncClient() as client:
            get_response = await client.get(f'{CAR_API}{purchase.car_id}')
            get_response.raise_for_status()

            car = get_response.json()
            car['available'] = False

            put_response = await client.put(f'{CAR_API}{purchase.car_id}', json=car)
            put_response.raise_for_status()

            return {'message': f'created: {purchase_id}'}, 200
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))


@app.get(
    '/purchase/{purchase_id}',
    description='Retrieve a purchase record by its ID.',
    response_description='The purchase record if found, or a message indicating it was not found.'
)
async def read_purchase(purchase_id: str):
    document = db.find_one({'_id': purchase_id})

    if not document:
        return {'message': f'purchase \'{purchase_id}\'  not found'}, 404

    return document, 200


@app.put(
    '/purchase/{purchase_id}',
    description='Update an existing purchase record by its ID.',
    response_description='A message indicating the update status of the purchase record.'
)
async def update_purchase(purchase_id: str, purchase: Purchase):
    document = db.find_one({'_id': purchase_id})

    if not document:
        return {'message': f'purchase \'{purchase_id}\'  not found'}, 404

    db.update_one({'_id': purchase_id}, {
        '$set': {
            'user_id': purchase.user_id,
            'car_id': purchase.car_id,

            'user_name': purchase.user_name,
            'car_name': purchase.car_name,

            'price': purchase.price,
        }
    })

    return {'message': f'updated: {purchase_id}'}, 200


@app.delete(
    '/purchase/{purchase_id}',
    description='Delete a purchase record by its ID.',
    response_description='A message indicating the deletion status of the purchase record.'
)
async def delete_purchase(purchase_id):
    document = db.find_one({'_id': purchase_id})

    if not document:
        return {'message': f'purchase \'{purchase_id}\'  not found'}, 404

    db.delete_one({'_id': purchase_id})

    return {'message': f'deleted: {purchase_id}'}, 200


# purchases search


@app.get(
    '/purchases',
    description='Retrieve all purchase records.',
    response_description='A list of all purchase records, or a message indicating that there are no records.'
)
async def read_purchase():
    purchases = list(db.find())

    if not purchases:
        return {'message': 'empty'}, 404

    return purchases


@app.get(
    '/purchases/{user_id}',
    description='Retrieve all purchase records for a specific user.',
    response_description='A list of purchase records for the specified user, or a message indicating that no records were found.'
)
async def read_purchase(user_id: str):
    purchases = list(db.find({'user_id': user_id}))

    if not purchases:
        return {'message': f'purchases for \'{user_id}\' not found'}, 404

    return purchases, 200
