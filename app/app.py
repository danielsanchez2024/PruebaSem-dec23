from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import os

app = Flask(__name__)

app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://database:27017/mydb')
mongo = PyMongo(app)

@app.route('/products', methods=['GET'])
def get_products():
    product = mongo.db.products.find()
    return jsonify([{'id': str(product['_id']), 'nombre': product['nombre'], 'precio': product['precio']} for product in product])

@app.route('/product', methods=['POST'])
def create_product():
    data = request.json

    if 'nombre' not in data:
        return jsonify({'error': 'nombre es requerido'}), 400

    if 'precio' not in data:
        return jsonify({'error': 'precio es requerido'}), 400

    if data.get('precio') < 0 or data.get('precio') % 1 != 0:
        return jsonify({'error': 'el precio no es entero positivo o flotante positivo'}), 400

    result = mongo.db.products.insert_one(data)
    return jsonify({'message': 'Producto creado', 'id': str(result.inserted_id)}), 201

@app.route('/products/<id>', methods=['GET'])
def get_product(id):
    product = mongo.db.products.find_one({'_id': ObjectId(id)})

    if product:
        product['id'] = str(product['_id'])
        return jsonify(product), 200
    return jsonify({'error': 'Producto no encontrado'}), 404

@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
    data = request.json
    product = mongo.db.products.find_one({'_id': ObjectId(id)})

    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404

    if 'nombre' not in data:
        return jsonify({'error': 'nombre es requerido'}), 400

    if 'precio' not in data:
        return jsonify({'error': 'precio es requerido'}), 400

    if data.get('precio') < 0 or data.get('precio') % 1 != 0:
        return jsonify({'error': 'el precio no es entero positivo o flotante positivo'}), 400

    mongo.db.products.update_one({'_id': ObjectId(id)}, {'$set': data})
    product = mongo.db.products.find_one({'_id': ObjectId(id)})
    return jsonify(product)

@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    result = mongo.db.products.delete_one({'_id': ObjectId(id)})

    if result.deleted_count > 0:
        return jsonify({'message': 'Producto eliminado'}), 200
    return jsonify({'error': 'Producto no encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)