from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId  # Importar ObjectId
import os

app = Flask(__name__)

app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://database:27017/mydb')
mongo = PyMongo(app)

@app.route('/products', methods=['GET'])
def get_products():
    products = mongo.db.products.find()
    # Convertir ObjectId a string en la respuesta
    return jsonify([{
        'id': str(product['_id']),
        'nombre': product['nombre'],
        'precio': product['precio']
    } for product in products])

@app.route('/product', methods=['POST'])
def create_product():
    data = request.json
  
    if isinstance(data, list): 
        productos = data
    elif isinstance(data, dict) and 'productos' in data and isinstance(data['productos'], list): 
        productos = data['productos']
    else: 
        productos = [data]

    ids_creados = []  

    for producto in productos:
        if 'nombre' not in producto:
            return jsonify({'error': 'The name is required for all products'}), 400

        if 'precio' not in producto:
            return jsonify({'error': 'The price is required for all products'}), 400

        try:
            precio = float(producto['precio']) 
        except ValueError:
            return jsonify({'error': 'The price must be a valid number for all products'}), 400

        if precio <= 0:
            return jsonify({'error': 'The price must be a positive number for all products'}), 400
        if precio % 1 != 0: 
            return jsonify({'error': 'The price must be a positive integer for all products'}), 400

        result = mongo.db.products.insert_one(producto)
        ids_creados.append(str(result.inserted_id)) 

    return jsonify({'message': 'Products created', 'ids': ids_creados}), 201


@app.route('/products/<id>', methods=['GET'])
def get_product(id):
    product = mongo.db.products.find_one({'_id': ObjectId(id)})

    if product:
        product['id'] = str(product['_id'])
        product.pop('_id', None)
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

    try:
        precio = float(data['precio'])
    except ValueError:
        return jsonify({'error': 'El precio debe ser un número válido'}), 400

    if precio < 0 or precio % 1 != 0:
        return jsonify({'error': 'el precio no es un número entero positivo'}), 400

    mongo.db.products.update_one({'_id': ObjectId(id)}, {'$set': data})
    updated_product = mongo.db.products.find_one({'_id': ObjectId(id)})
    updated_product['_id'] = str(updated_product['_id'])
    
    return jsonify(updated_product)

@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    result = mongo.db.products.delete_one({'_id': ObjectId(id)})

    if result.deleted_count > 0:
        return jsonify({'message': 'Producto eliminado'}), 200
    return jsonify({'error': 'Producto no encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
