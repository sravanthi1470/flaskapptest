from flask import Flask, render_template, request, redirect, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flash messages


# Function to create a database connection
def create_connection():
    conn = sqlite3.connect('eatsure.db')
    return conn


# Function to create the necessary tables
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Create `users` table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Create `orders` table
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL
    )''')

    conn.commit()
    conn.close()


# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')


# Route for the About page
@app.route('/about')
def about():
    return render_template('about.html')


# Route for the Menu page
@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if request.method == 'POST':
        username = request.form.get('username')
        item_name = request.form.get('item_name')
        quantity = int(request.form.get('quantity'))

        # Calculate the price based on the item
        prices = {
            "Pizza": 200,
            "Pasta": 150,
            "Biryani": 120,
            "Shawarma": 90,
            "Dessert": 100,
            "Drink": 70,
            "Chocolate": 50
        }
        price = prices.get(item_name, 0) * quantity

        # Store order in the database
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT INTO orders (username, item_name, quantity, price)
                              VALUES (?, ?, ?, ?)''', (username, item_name, quantity, price))
            conn.commit()
            flash("Order placed successfully!", "success")
        except Exception as e:
            flash(f"Error placing order: {str(e)}", "danger")
        finally:
            conn.close()

        return redirect('/order')  # Redirect to thank you page

    return render_template('menu.html')



# Route for the Order confirmation page
@app.route('/order')
def order():
    return render_template('order.html')


# Route for the Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()

        if user:
            flash("Login successful!", "success")
            return redirect('/')
        else:
            flash("Invalid username or password.", "danger")

        conn.close()

    return render_template('login.html')


# Route for the Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = create_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            ''', (username, email, password))
            conn.commit()
            flash("Registration successful!", "success")
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash("Username or email already exists!", "danger")
        finally:
            conn.close()

    return render_template('register.html')



if __name__ == '__main__':
    create_tables()  # Ensure tables are created before running the app
    app.run(debug=True)
