
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
# Flask application ka basic structure banaya hai
import mysql.connector
from flask import session, jsonify

app = Flask(__name__) # Flask application ka instance banaya hai
app.secret_key = 'your_secret_key'  # koi bhi random string de sakte ho


# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'root', 
    'password': '123456789', 
    'database': 'myapp'  
}

@app.route('/') 
def home():
    user_email = session.get('user_email')
    username = session.get('username') 
    cart_count = 0
    if user_email:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantity) FROM cart WHERE user_email = %s", (user_email,))
        result = cursor.fetchone()
        cart_count = result[0] if result[0] else 0
        cursor.close()
        conn.close()
    return render_template('index.html', cart_count=cart_count, username=username)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        conform_password = request.form['conform_password']
        if password != conform_password:
            flash("❌ Passwords do not match. Please try again.")
            return redirect(url_for('register'))
        # MySQL me data insert karna
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, email, password))
        conn.commit()
        cursor.close()
        conn.close()
        # 🔁 Redirect to login page
        flash("✅ Registration successful. Please login.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT username FROM users WHERE email = %s AND password = %s"
    
        cursor.execute("SELECT username, email FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
             session['username'] = user[0]       # ✅ username
             session['user_email'] = user[1]     # ✅ email
             return redirect(url_for('home'))
        else:
            # return "❌ Invalid email or password."
             flash("Invalid email or password.")
             return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None) 
    return redirect(url_for('home'))

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return redirect(url_for('home'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM products
        WHERE product_name LIKE %s OR description LIKE %s
    """, (f"%{query}%", f"%{query}%"))
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('search_results.html', query=query, products=products)

@app.route('/profile')
def profile():
    user_email = session.get('user_email')
    username = session.get('username')
    if not user_email:
        return redirect('/login')
    return render_template('profile.html', username=username, user_email=user_email)

@app.route('/orders')
def orders():
    user_email = session.get('user_email')
    if not user_email:
        return redirect('/login')
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    # cursor.execute("SELECT * FROM orders WHERE user_email = %s ORDER BY order_date DESC", (user_email,))
    cursor.execute("SELECT * FROM orders WHERE user_email = %s", (user_email,))
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('orders.html', orders=orders)

# Show Wishlist
@app.route('/wishlist')
def wishlist():
    user_email = session.get('user_email')
    if not user_email:
        return redirect('/login')
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM wishlist WHERE user_email = %s", (user_email,))
    wishlist_items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('wishlist.html', wishlist=wishlist_items)

# Add to Wishlist
@app.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
    user_email = session.get('user_email')
    product_id = request.form['product_id']
    product_name = request.form['product_name']
    price = request.form['price']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO wishlist (user_email, product_id, product_name, price)
        VALUES (%s, %s, %s, %s)
    """, (user_email, product_id, product_name, price))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/wishlist')

# Remove from Wishlist
@app.route('/remove_from_wishlist', methods=['POST'])
def remove_from_wishlist():
    wishlist_id = request.form['wishlist_id']
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wishlist WHERE id = %s", (wishlist_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/wishlist')

 
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    user_email = session.get('user_email')
    if not user_email:
        return redirect('/login')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Get user info from DB
    cursor.execute("SELECT username, email FROM users WHERE email = %s", (user_email,))
    user_data = cursor.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Update query
        if password:
            cursor.execute("UPDATE users SET username = %s, email = %s, password = %s WHERE email = %s",
                           (name, email, password, user_email))
        else:
            cursor.execute("UPDATE users SET username = %s, email = %s WHERE email = %s",
                           (name, email, user_email))
        conn.commit()
        flash('Account updated successfully!')

        # update session too (if email changed)
        session['user_email'] = email
        session['username'] = name

        return redirect('/settings')

    cursor.close()
    conn.close()

    # 👇 Pass user dictionary to template
    return render_template('settings.html', user={
        'name': user_data['username'],
        'email': user_data['email']
    })


@app.route('/cart')
def cart():
    user_email = session.get('user_email')  # if your cart is user-based
    if not user_email:
      return redirect('/login')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Fetch all items in the cart
    cursor.execute("SELECT id, product_name, price, image_url, quantity FROM cart WHERE user_email = %s", (user_email,))
    items = cursor.fetchall()

    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in items)

    cursor.close()
    conn.close()

    return render_template('cart.html', items=items, total=total)


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    try:
        data = request.get_json(force=True)
        print("🛒 Add to cart request:", data)

        user_email = session.get('user_email')
        if not user_email:
            return jsonify({'success': False, 'error': 'User not logged in'}), 401

        product_name = data.get('product_name')
        price = data.get('price')
        image = data.get('image')

        if not all([product_name, price, image]):
            return jsonify({'success': False, 'error': 'Missing product data'}), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO cart (user_email, product_name, price, image_url, quantity)
            VALUES (%s, %s, %s, %s, 1)
        """, (user_email, product_name, price, image))
        conn.commit()
        cursor.close()
        conn.close()

        # ✅ Get updated cart count
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantity) FROM cart WHERE user_email = %s", (user_email,))
        result = cursor.fetchone()
        cart_count = result[0] if result[0] else 0
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Item added to cart',
            'cart_count': cart_count
        }), 200

    except Exception as e:
        print("❌ ERROR in /add-to-cart:", e)
        return jsonify({'success': False, 'error': 'Server error'}), 500

@app.route('/cart_count')
def cart_count_ajax():
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'count': 0})
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(quantity) FROM cart WHERE user_email = %s", (user_email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify({'count': result[0] if result[0] else 0})


@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    item_id = request.form['item_id']
    quantity = request.form['quantity']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE cart SET quantity = %s WHERE id = %s", (quantity, item_id))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/cart')

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    item_id = request.form['item_id']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE id = %s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/cart')

@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    order_id = request.form.get('order_id')
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
    conn.commit()
    
    cursor.close()
    conn.close()

    flash("❌ Order cancelled successfully.")
    return redirect('/orders')

@app.route('/checkout', methods=['POST'])
def checkout():
    user_email = session.get('user_email')
    if not user_email:
        return redirect('/login')

    address = request.form.get('address')
    payment_method = request.form.get('payment_method')

    if not address or not payment_method:
        flash("Please fill in all fields.")
        return redirect('/checkout_page')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # 1. Get cart items
    cursor.execute("SELECT product_name, price, quantity FROM cart WHERE user_email = %s", (user_email,))
    cart_items = cursor.fetchall()

    if not cart_items:
        flash("Cart is empty.")
        return redirect('/cart')

    # 2. Insert each cart item as a separate order entry
    for item in cart_items:
        cursor.execute("""
            INSERT INTO orders (user_email, product_name, price, quantity, address, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user_email,
            item['product_name'],
            item['price'],
            item['quantity'],
            address,
            payment_method
        ))

    # 3. Clear the cart
    cursor.execute("DELETE FROM cart WHERE user_email = %s", (user_email,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("✅Order placed successfully!")
    return redirect('/orders')  # This page should exist or be handled


@app.route('/checkout_page', methods=['GET'])
def checkout_page():
    if 'user_email' not in session:
        return redirect('/login')
    return render_template('checkout_page.html')  # This will render the form page

# hero section ka shop button
@app.route('/shop')
def shop():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('shop.html', products=products)



if __name__ == '__main__':
    app.run(debug=True)
