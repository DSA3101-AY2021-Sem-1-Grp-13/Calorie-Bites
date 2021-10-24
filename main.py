from flask import render_template, redirect, request, url_for, session, Flask
from flask_sqlalchemy import SQLAlchemy

from algo import optimal_basket, change_product
from calories import optimal_calories

import pandas as pd
import os

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

class Cart(db.Model):
    product = db.Column(db.String(100), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    def __init__(self, product, quantity):
        self.product=product
        self.quantity=quantity

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'terry_jieyi_qiting_zhuolin_kaychi_zhongping_nigel'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app

# Read Data
basedir = os.path.abspath(os.path.dirname(__file__))
product_info = pd.read_csv(os.path.join(basedir, 'data', 'Categories_Info_with_Volume.csv'))
product_info['flag'] = False
all_prod = sorted(list(set(product_info['Product'])))
all_prod = list(map(lambda x: x.title(), all_prod))

substitute_df = pd.read_csv(os.path.join(basedir, 'data', 'Product Substitution.csv'))

main = create_app()
    
###################################
#                                 #
#            Main Page            #
#                                 #
###################################

def check_device():
    user_agent = request.headers.get('User-Agent')
    user_agent = user_agent.lower()
    #user_agent = "mobile"
    if "mobile" in user_agent:
        return 'mobile'
    else:
        return 'desktop'

@main.route('/', methods = ['GET', 'POST'])
def index():
    device_html = check_device() + ".index.html"

    query = Cart.query.all()
    data = list(map(lambda x: (x.product, x.quantity), query))
    data.sort(key=lambda x: x[0])
    
    return render_template(device_html, data=data, all_prod=all_prod)
        

@main.route('/add', methods = ['POST', 'GET'])
def add_to_cart():
    if request.method == 'POST':
        product = request.form.get("product_category")
        quantity = request.form.get("quantity")

        record = Cart.query.filter_by(product=product).first()
        
        if not record:
            new_record = Cart(product=product, quantity=quantity)
            db.session.add(new_record)
            db.session.commit()
        else:
            record.quantity = quantity
            db.session.commit()
        
    return redirect('/')

@main.route('/remove', methods = ['POST', 'GET'])
def remove_from_cart():
    if request.method == 'POST':
        data = request.get_json()
        product= data[0]['id']

        record = Cart.query.filter_by(product=product).first()
        db.session.delete(record)
        db.session.commit() 

    return redirect('/')

@main.route('/removeall', methods = ['POST', 'GET'])
def remove_all():
    if request.method == 'POST':
        db.session.query(Cart).delete()
        db.session.commit() 

    return redirect('/')

@main.route('/reset')
def reset():
    db.session.query(Cart).delete()
    db.session.commit() 

    return redirect('/')


#####################################
#                                   #
#            Result Page            #
#                                   #
#####################################
@main.route('/result', methods = ['POST'])
def result():
    # Retrieve inputs
    gender = request.form.get("gender")
    weight = int(request.form.get("weight"))
    age_group = int(request.form.get("age"))
    occ = int(request.form.get("activity"))

    #Calculate Optimal Calories
    opt = optimal_calories(gender, weight, age_group, occ)

    # Query Database and Format Query
    query = Cart.query.all()
    data = list(map(lambda x: (x.product, x.quantity), query))
    data.sort(key=lambda x: x[0])

    # Image filepath
    mapping = {'beer': url_for('static', filename='product_images/beer.png'), 
    'belacan': url_for('static', filename='product_images/belacan.png'),
    'bird nest': url_for('static', filename='product_images/bird_nest.png'),
    'biscuits': url_for('static', filename='product_images/biscuits.png'),
    'bouilon': url_for('static', filename='product_images/bouilon.png'),
    'butter': url_for('static', filename='product_images/butter.png'),
    'cake': url_for('static', filename='product_images/cake.png'),
    'canned product': url_for('static', filename='product_images/canned product.png'),
    'cereal beverage': url_for('static', filename='product_images/cereal beverage.png'),
    'cereals': url_for('static', filename='product_images/cereals.png'),
    'cheese': url_for('static', filename='product_images/cheese.png'),
    'chicken essence': url_for('static', filename='product_images/chicken essence.png'),
    'choc/nut spread': url_for('static', filename='product_images/nutella.png'),
    'chocolate': url_for('static', filename='product_images/chocolate.png'),
    'coconut milk': url_for('static', filename='product_images/coconut_milk.png'),
    'coffee': url_for('static', filename='product_images/coffee.png'),
    'condensed/evap milk': url_for('static', filename='product_images/condensed_milk.png'),
    'confectionery': url_for('static', filename='product_images/confectionary.png'),
    'cooking oils': url_for('static', filename='product_images/cooking_oil.png'),
    'cooking sauces': url_for('static', filename='product_images/cooking_sauce.png'),
    'cordials': url_for('static', filename='product_images/cordials.png'),
    'creamer': url_for('static', filename='product_images/creamer.png'),
    'csd': url_for('static', filename='product_images/csd.png'),
    'cultured milk': url_for('static', filename='product_images/cultured_milk.png'),
    'drinking water': url_for('static', filename='product_images/drinking_water.png'),
    'eggs': url_for('static', filename='product_images/eggs.png'),
    'energy drinks': url_for('static', filename='product_images/energy_drinks.png'),
    'flour': url_for('static', filename='product_images/flour.png'),
    'fronzen food': url_for('static', filename='product_images/frozen_food.png'),
    'fruit/veg juices': url_for('static', filename='product_images/fruit_juice.png'),
    'ghee' : url_for('static', filename='product_images/ghee.png'),
    'honey' : url_for('static', filename='product_images/honey.png'),
    'ice cream' : url_for('static', filename='product_images/ice-cream.png'),
    'instant noodles' : url_for('static', filename='product_images/instant_noodle.png'),
    'instant soup' : url_for('static', filename='product_images/instant_soup.png'),
    'isotonic drinks' : url_for('static', filename='product_images/isotonic_drinks.png'),
    'jam' : url_for('static', filename='product_images/jam.png'),
    'kaya' : url_for('static', filename='product_images/kaya.png'),
    'margarine' : url_for('static', filename='product_images/margarine.png'),
    'liquid milk' : url_for('static', filename='product_images/milk.png'),
    'milk powder-adult' : url_for('static', filename='product_images/milk_powder_adult.png'),
    'milk powder-infant' : url_for('static', filename='product_images/milk_powder_infant.png'),
    'milk powder-kids' : url_for('static', filename='product_images/milk_powder_kids.png'),
    'msg' : url_for('static', filename='product_images/msg.png'),
    'peanut butter' : url_for('static', filename='product_images/peanut butter.png'),
    'plant based milk' : url_for('static', filename='product_images/plant_based_milk.png'),
    'rice' : url_for('static', filename='product_images/rice.png'),
    'rtd coffee' : url_for('static', filename='product_images/rtd_coffee.png'),
    'rtd tea' : url_for('static', filename='product_images/rtd_tea.png'),
    'salad dressing' : url_for('static', filename='product_images/salad_dressing.png'),
    'savoury spread' : url_for('static', filename='product_images/savoury_spread.png'),
    'seasoning powder' : url_for('static', filename='product_images/seasoning_powder.png'),
    'snack' : url_for('static', filename='product_images/snack.png'),
    'soy milk' : url_for('static', filename='product_images/soy_milk.png'),
    'spagetti' : url_for('static', filename='product_images/spagetti.png'),
    'spirits' : url_for('static', filename='product_images/spirits.png'),
    'sugar' : url_for('static', filename='product_images/sugar.png'),
    'tea' : url_for('static', filename='product_images/tea.png'),
    'tonic food drink' : url_for('static', filename='product_images/tonic_food_drink.png'),
    'wine' : url_for('static', filename='product_images/wine.png'),
    'yoghurt drink' : url_for('static', filename='product_images/yoghurt_drink.png'),
    'yoghurts' : url_for('static', filename='product_images/yoghurt.png')}

    cart = list(map(lambda x: x + (mapping[x[0].lower()],), data))

    data = list(zip(*data))
    product, amt_each_product  = list(map(lambda x: list(x), data))
    product = list(map(lambda x: x.upper(), product))

    # Run Algorithm
    algo_result = optimal_basket(opt, product, amt_each_product, product_info, substitute_df)
    
    if type(algo_result) == tuple:
        indicator = None
        cal_to_print = None
        sub = None
        amt_sub = None
    else:
        indicator, cal_to_print, sub, amt_sub, algo_result = algo_result

    device_html = check_device() + ".result.html"

    session['opt'] = opt
    session['product'] = product
    session['amt_each_product'] = amt_each_product

    return render_template(device_html, opt=opt, data=algo_result, indicator=indicator, cal_to_print=cal_to_print, sub=sub, amt_sub=amt_sub, cart=cart)
        
    # Different cases:
    # Case 1: Basket <= Recommended Calories
    # Output: Tuple of 2 item containing total calories per day of basket and total price
    #
    # Case 2: Recommended Calories < Basket < Recommended Calories + 100
    # Output: Tuple of 3 items containing total calories per day of basket, amount exceeded and total price
    #
    # Case 3.1: Basket > Recommended Calories + 100, but healthier substitute exists
    # Output: List containing 5 items (indicator, calories, None, None, dictionary)
    #
    # Case 3.2: Basket > Recommended Calories + 100. Healthier substitute exists and reduce quantity
    # Output: List containing 5 items (indicator, calories, products to substitute, amount to substitute, dictionary)

    # Case 3.3: Basket > Recommended Calories + 100. Healthier substitute exists and reduce quantity, but hits limit
    # Output: List containing 5 items (indicator, calories, None, None, dictionary)

    # Case 3.4: Basket > Recommended Calories + 100. No healthier substitute exists, but reduce quantity
    # Output: List containing 5 items (indicator, calories, None, amount to substitute, dictionary)

    # Case 3.5: Basket > Recommended Calories + 100. No healthier substitute exists, but reduce quantity
    # Output: List containing 5 items (indicator, calories, None, None, dictionary)

###########################################
#                                         #
#            Modification Page            #
#                                         #
###########################################
@main.route('/change')
def change():

    query = Cart.query.all()
    data = list(map(lambda x: (x.product, x.quantity), query))
    data.sort(key=lambda x: x[0])

    opt = session.get('opt')
    product = session.get('product')
    amt_each_product = session.get('amt_each_product')

    algo_result = optimal_basket(opt, product, amt_each_product, product_info, substitute_df)
    sub = algo_result[2]
    sub = list(map(lambda x: x[1], sub))
    
    seq = range(len(sub))
    sub = list(zip(sub, seq))

    session['seq'] = len(sub)

    all_prod_copy = [x for x in all_prod if x not in sub]

    return render_template('change.html', sub=sub, all_prod=all_prod_copy)

@main.route('/resultchanged', methods = ['POST'])
def changed_result():
    seq = session.get('seq')
    new_prod = []

    for i in range(seq):
        val = request.form.get("product_category_{}".format(i))
        new_prod.append(val)

    reason = request.form.get("reason")

    opt = session.get('opt')
    product = session.get('product')
    amt_each_product = session.get('amt_each_product')

    algo_result = optimal_basket(opt, product, amt_each_product, product_info, substitute_df)
    indicator, cal_to_print, sub, amt_sub, algo_result = algo_result

    df = algo_result['dataframe']
    df = df[df.flag == True]

    current_total_price = algo_result['total_price']
    current_total_calorie = algo_result['total_calorie']
    recommended_calorie = algo_result['recommended_calorie']

    to_change = []
    for i in range(len(new_prod)):
        if new_prod[i] == "Yes":
            to_change.append(sub[i])

    to_change_old = list(map(lambda x: x[0], to_change))
    to_change_new= list(map(lambda x: x[1], to_change))

    idx = []
    for i in to_change_old:
        idx.append(product.index(i))

    new_amt = list(map(lambda x: amt_each_product[x], idx))

    new = list(zip(to_change_new, new_amt))
    products_to_change = list(map(lambda x: list(x), new))

    new_rec = change_product(algo_result['dataframe'], products_to_change, reason, current_total_price, current_total_calorie, recommended_calorie, product_info)
    replacements, error, recommended_calorie, total_price, basket_calorie = new_rec

    new_cart = list(df.Product)
    for i in replacements:
        a = new_cart.index(i[0])
        new_cart[a] = i[1]

    new_cart = list(zip(new_cart, amt_each_product))

    # Image filepath
    mapping = {'beer': url_for('static', filename='product_images/beer.png'), 
    'belacan': url_for('static', filename='product_images/belacan.png'),
    'bird nest': url_for('static', filename='product_images/bird_nest.png'),
    'biscuits': url_for('static', filename='product_images/biscuits.png'),
    'bouilon': url_for('static', filename='product_images/bouilon.png'),
    'butter': url_for('static', filename='product_images/butter.png'),
    'cake': url_for('static', filename='product_images/cake.png'),
    'canned product': url_for('static', filename='product_images/canned product.png'),
    'cereal beverage': url_for('static', filename='product_images/cereal beverage.png'),
    'cereals': url_for('static', filename='product_images/cereals.png'),
    'cheese': url_for('static', filename='product_images/cheese.png'),
    'chicken essence': url_for('static', filename='product_images/chicken essence.png'),
    'choc/nut spread': url_for('static', filename='product_images/nutella.png'),
    'chocolate': url_for('static', filename='product_images/chocolate.png'),
    'coconut milk': url_for('static', filename='product_images/coconut_milk.png'),
    'coffee': url_for('static', filename='product_images/coffee.png'),
    'condensed/evap milk': url_for('static', filename='product_images/condensed_milk.png'),
    'confectionery': url_for('static', filename='product_images/confectionary.png'),
    'cooking oils': url_for('static', filename='product_images/cooking_oil.png'),
    'cooking sauces': url_for('static', filename='product_images/cooking_sauce.png'),
    'cordials': url_for('static', filename='product_images/cordials.png'),
    'creamer': url_for('static', filename='product_images/creamer.png'),
    'csd': url_for('static', filename='product_images/csd.png'),
    'cultured milk': url_for('static', filename='product_images/cultured_milk.png'),
    'drinking water': url_for('static', filename='product_images/drinking_water.png'),
    'eggs': url_for('static', filename='product_images/eggs.png'),
    'energy drinks': url_for('static', filename='product_images/energy_drinks.png'),
    'flour': url_for('static', filename='product_images/flour.png'),
    'fronzen food': url_for('static', filename='product_images/frozen_food.png'),
    'fruit/veg juices': url_for('static', filename='product_images/fruit_juice.png'),
    'ghee' : url_for('static', filename='product_images/ghee.png'),
    'honey' : url_for('static', filename='product_images/honey.png'),
    'ice cream' : url_for('static', filename='product_images/ice-cream.png'),
    'instant noodles' : url_for('static', filename='product_images/instant_noodle.png'),
    'instant soup' : url_for('static', filename='product_images/instant_soup.png'),
    'isotonic drinks' : url_for('static', filename='product_images/isotonic_drinks.png'),
    'jam' : url_for('static', filename='product_images/jam.png'),
    'kaya' : url_for('static', filename='product_images/kaya.png'),
    'margarine' : url_for('static', filename='product_images/margarine.png'),
    'liquid milk' : url_for('static', filename='product_images/milk.png'),
    'milk powder-adult' : url_for('static', filename='product_images/milk_powder_adult.png'),
    'milk powder-infant' : url_for('static', filename='product_images/milk_powder_infant.png'),
    'milk powder-kids' : url_for('static', filename='product_images/milk_powder_kids.png'),
    'msg' : url_for('static', filename='product_images/msg.png'),
    'peanut butter' : url_for('static', filename='product_images/peanut butter.png'),
    'plant based milk' : url_for('static', filename='product_images/plant_based_milk.png'),
    'rice' : url_for('static', filename='product_images/rice.png'),
    'rtd coffee' : url_for('static', filename='product_images/rtd_coffee.png'),
    'rtd tea' : url_for('static', filename='product_images/rtd_tea.png'),
    'salad dressing' : url_for('static', filename='product_images/salad_dressing.png'),
    'savoury spread' : url_for('static', filename='product_images/savoury_spread.png'),
    'seasoning powder' : url_for('static', filename='product_images/seasoning_powder.png'),
    'snack' : url_for('static', filename='product_images/snack.png'),
    'soy milk' : url_for('static', filename='product_images/soy_milk.png'),
    'spagetti' : url_for('static', filename='product_images/spagetti.png'),
    'spirits' : url_for('static', filename='product_images/spirits.png'),
    'sugar' : url_for('static', filename='product_images/sugar.png'),
    'tea' : url_for('static', filename='product_images/tea.png'),
    'tonic food drink' : url_for('static', filename='product_images/tonic_food_drink.png'),
    'wine' : url_for('static', filename='product_images/wine.png'),
    'yoghurt drink' : url_for('static', filename='product_images/yoghurt_drink.png'),
    'yoghurts' : url_for('static', filename='product_images/yoghurt.png')}

    pic = []
    for i in new_cart:
        new_pic = mapping[i[0].lower()]
        pic.append(new_pic)

    final = []
    for i in range(len(new_cart)):
        x = new_cart[i]
        final.append(x+(pic[i],))

    new_cart = final
    print(new_cart)

    return render_template('resultchanged.html', replacements = replacements, error=error, recommended_calorie=recommended_calorie, total_price=total_price, basket_calorie=basket_calorie, cart=new_cart, pic=pic)
