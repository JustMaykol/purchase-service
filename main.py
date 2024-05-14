from uuid import uuid4
from pydantic import BaseModel

from fastapi import FastAPI
from pymongo import MongoClient

app = FastAPI(
    title='Purchase API',
    description='Purchase API with FastAPI and MongoDB',
)


class Purchase(BaseModel):
    user_id: str
    car_id: str

    user_name: str
    car_name: str

    price: int
    discount: int


client = MongoClient('mongodb://localhost:27017/')
db = client['current']['purchase']


# purchase crud

@app.post('/purchase', description='Method to create a new Purchase')
async def create_purchase(purchase: Purchase):
    db.insert_one({
        '_id': str(uuid4()),

        'user_id': purchase.user_id,
        'car_id': purchase.car_id,

        'user_name': purchase.user_name,
        'car_name': purchase.car_name,

        'price': purchase.price,
        'discount': purchase.discount
    })

    return {'message': 'created'}, 200


@app.get('/purchase/{_id}', description='Method to read a Purchase by id')
async def read_purchase(_id: str):
    document = db.find_one({'_id': _id})

    if not document:
        return {'message': 'purchase not found'}, 404

    return document, 200


@app.put('/purchase/{_id}', description='Method to update a Purchase by id')
async def update_purchase(_id: str, purchase: Purchase):
    document = db.find_one({'_id': _id})

    if not document:
        return {'message': 'purchase not found'}, 404

    db.update_one({'_id': _id}, {
        '$set': {
            'user_id': purchase.user_id,
            'car_id': purchase.car_id,

            'user_name': purchase.user_name,
            'car_name': purchase.car_name,

            'price': purchase.price,
            'discount': purchase.discount
        }
    })

    return {'message': 'updated'}, 200


@app.delete('/purchase/{_id}', description='Method to delete a Purchase by id')
async def delete_purchase(_id):
    document = db.find_one({'_id': _id})

    if not document:
        return {'message': 'purchase not found'}, 404

    db.delete_one({'_id': _id})

    return {'message': 'deleted'}, 200


# purchases search


@app.get('/purchase', description='Method to collect all purchases')
async def read_purchase():
    purchases = list(db.find())

    if not purchases:
        return {'message': 'empty'}, 404

    return purchases
