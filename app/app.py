from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId  # Importar ObjectId
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

    # Verificar si 'productos' está presente y es una lista
    if 'productos' not in data or not isinstance(data['productos'], list):
        return jsonify({'error': 'Se debe proporcionar un array de productos'}), 400

    # Validar cada producto en la lista
    for producto in data['productos']:
        # Verificar si 'nombre' está presente en cada producto
        if 'nombre' not in producto:
            return jsonify({'error': 'El nombre es requerido en todos los productos'}), 400

        # Verificar si 'precio' está presente en cada producto
        if 'precio' not in producto:
            return jsonify({'error': 'El precio es requerido en todos los productos'}), 400

        # Intentar convertir el 'precio' a float y validar
        try:
            precio = float(producto.get('precio'))  # Convertir a float
        except ValueError:
            return jsonify({'error': 'El precio debe ser un número válido en todos los productos'}), 400

        # Validar si el precio es positivo y entero
        if precio < 0 or precio % 1 != 0:
            return jsonify({'error': 'El precio debe ser un número entero positivo en todos los productos'}), 400

    # Insertar todos los productos en la base de datos
    result = mongo.db.products.insert_many(data['productos'])

    return jsonify({'message': 'Productos creados', 'ids': [str(id) for id in result.inserted_ids]}), 201

@app.route('/products/<id>', methods=['GET'])
def get_product(id):
    product = mongo.db.products.find_one({'_id': ObjectId(id)})

    if product:
        product['id'] = str(product['_id'])  # Convertir ObjectId a string
        product.pop('_id', None)  # Opcional: Eliminar el campo '_id' si no lo necesitas
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

    # Convierte el ObjectId a string
    product['_id'] = str(product['_id'])
    
    return jsonify(product)


@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    result = mongo.db.products.delete_one({'_id': ObjectId(id)})

    if result.deleted_count > 0:
        return jsonify({'message': 'Producto eliminado'}), 200
    return jsonify({'error': 'Producto no encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)