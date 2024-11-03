from flask import Flask, render_template, request, send_file, redirect, url_for,session,jsonify
from pymongo import MongoClient
from analysis import perform_demand_analysis
from search import grover_search
from bson import ObjectId 
from demand import quan


app = Flask(__name__,template_folder='templates', static_folder='static')

app.secret_key = 'User'
active_sessions = {}

client = MongoClient('mongodb://localhost:27017/')
db = client['Warehouse']
collection = db['product']
collection_stack = db['stack']


@app.route('/')
def index():
     return render_template('index.html')

@app.route('/stack')
def stock():
    products = collection.find()
    return render_template('stack.html',products=products)

@app.route('/save_data', methods=['POST'])
def save_data():
    product_code = request.form.get('code')
    product_name = request.form.get('name')
    quantity = request.form.get('quantity')
    price = request.form.get('price')
    length = request.form.get('length')
    breadth = request.form.get('breadth')
    weight = request.form.get('weight')
    category = request.form.get('category')

    collection.insert_one({
        'code': product_code,
        'name': product_name,
        'quantity': quantity,
        'price': price,
        'length': length,
        'breadth': breadth,
        'weight':weight,
        'category': category    
    })
    return redirect('/stack')
@app.route('/edit/<product_id>')
def edit(product_id):
    product = collection.find_one({'_id': ObjectId(product_id)})
    return render_template('stack_edit.html', product=product)

@app.route('/update/<product_id>', methods=['POST'])
def update(product_id):
    product_code = request.form.get('code')
    product_name = request.form.get('name')
    quantity = request.form.get('quantity')
    price = request.form.get('price')
    length = request.form.get('length')
    breadth = request.form.get('breadth')
    weight = request.form.get('weight')
    category = request.form.get('category')
    
    collection.update_one({'_id': ObjectId(product_id)}, {'$set': {
        'code': product_code,
        'name': product_name,
        'quantity': quantity,
        'price': price,
        'length': length,
        'breadth': breadth,
        'weight':weight,
        'category': category  
    }})
    return redirect('/stack')

@app.route('/delete/<product_id>')
def delete(product_id):    
    collection.delete_one({'_id': ObjectId(product_id)})
    return redirect('/stack')



@app.route('/get_stack_data', methods=['POST'])
def get_stack_data():
    stack_id = request.json['stack_id']
    return redirect(url_for('stack_details', stack_id=stack_id))

@app.route('/stack_details/<stack_id>')
def stack_details(stack_id):
    stack_data = collection_stack.find_one({'stack_id': stack_id})
    return render_template('stack_details.html', stack_data=stack_data)


@app.route('/overview')
def overview():
    data_from_db = collection_stack.find()
    return render_template('blank.html',data=data_from_db)

@app.route('/analysis')
def analysis():
    plot_path = perform_demand_analysis()
    return render_template('analysis.html', plot_path=plot_path)

@app.route('/demand')
def demand():
    result, image_path = quan()
    data_from_db = collection_stack.find()
    return render_template('demand.html', result=result, image_path=image_path,data=data_from_db)

@app.route('/search', methods=['POST'])
def search():
    target_product = request.form['target_product']
    result = grover_search(target_product)
    return render_template('stack_search.html', result=result)

@app.route('/stockpick')
def stockpick():
    return render_template('stock_pick.html')

@app.route('/pic',methods=['POST'])
def pic():
    search = request.form.get('search')
    data_from_db = collection_stack.find()
    return render_template('pic.html', search=search,data=data_from_db)

if __name__ == '__main__':
    app.run(debug=True)
