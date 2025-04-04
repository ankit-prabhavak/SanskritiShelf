from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime  # for date conversion


# Insert sample books into the database (for testing)
def add_sample_books():
    # Sample books to add to the database
    sample_books = [
        Book(title="The Great Gatsby", author="F. Scott Fitzgerald", publisher="Scribner", price=10.99, stock=5, 
             image_url="book1.jpg"),  # Relative path to static/images/
        Book(title="1984", author="George Orwell", publisher="Secker & Warburg", price=8.99, stock=10, 
             image_url="book2.jpg"),  # Relative path to static/images/
        Book(title="To Kill a Mockingbird", author="Harper Lee", publisher="J.B. Lippincott & Co.", price=12.99, stock=8,
             image_url="book3.jpg"),  # Relative path to static/images/
        Book(title="Pride and Prejudice", author="Jane Austen", publisher="T. Egerton", price=7.99, stock=4, 
             image_url="book4.jpg"),  # Relative path to static/images/
        Book(title="The Catcher in the Rye", author="J.D. Salinger", publisher="Little, Brown and Company", price=9.99, stock=7,
             image_url="book5.jpg")  # Relative path to static/images/
    ]
    
    if Book.query.count() == 0:  # If there are no books in the database, add the sample books
        db.session.add_all(sample_books)
        db.session.commit()
        print("Sample books added to the database!")



# Initialize Flask App and Extensions
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change to a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'  # Using SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Login Manager
login_manager = LoginManager(app)
login_manager.login_view = "login"  # Redirect to login page if not logged in

# Define the Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)  # Image URL for the book

    def __repr__(self):
        return f"<Book {self.title}>"


# Define the User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(150), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    dob = db.Column(db.Date, nullable=False)  # Date field for Date of Birth
    languages = db.Column(db.String(150), nullable=True)
    address = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

# Define the Subscriber model for subscription functionality
class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<Subscriber {self.email}>"

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables and add sample books if needed
@app.before_request
def create_tables():
    db.create_all()  # Creates the tables if not already created
    add_sample_books()  # Add sample books if none exist in the database


# Homepage route
@app.route('/')
def index():
    return render_template("index.html")

# Add this route in app.py
@app.route('/home_description')
def home_description():
    return render_template("home_description.html")  # Create the template home_description.html

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))  # Redirect to dashboard if already logged in

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Authenticate user
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            # After successful login, log the user in
            login_user(user)  # This will start the user session

            # Redirect to the page they were trying to access (or dashboard by default)
            next_page = request.args.get('next', url_for('dashboard'))  # Get 'next' or default to dashboard
            return redirect(next_page)

        else:
            flash("Invalid username or password. Please try again.")
    
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    # Now current_user is automatically available in the template
    return render_template("dashboard.html")

# Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        phone = request.form["phone"]
        gender = request.form["gender"]
        dob = request.form["dob"]  # Date as string from form
        address = request.form["address"]

        # Convert the dob string to a datetime.date object
        dob = datetime.strptime(dob, '%Y-%m-%d').date()  # This works now with the import

        # Get languages from the form (multiple checkboxes)
        languages = ",".join(request.form.getlist("languages"))

        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for('register'))

        # Check if the email already exists (optional)
        if User.query.filter_by(email=email).first():
            flash("Email already exists. Please choose a different one.")
            return redirect(url_for('register'))

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Create the new user
        new_user = User(
            username=username,
            password=hashed_password,
            email=email,
            phone=phone,
            gender=gender,
            dob=dob,  # Store the date object here
            languages=languages,
            address=address,
            name=name
        )

        # Add the user to the database and commit
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/profile")
@login_required
def profile():
    # You can pass additional user data if needed
    return render_template("profile.html", user=current_user)

@app.route('/catalogue')
def catalogue():
    books = Book.query.all()  # Fetch all books from the database
    
    # Ensure image URLs are properly formatted
    for book in books:
        if not book.image_url.startswith("http"):  # If not an external link
            book.image_url = url_for('static', filename=f'images/{book.image_url}')  # Prepend static folder
    
    return render_template("catalogue.html", books=books)


# Add to cart route
@app.route('/add_to_cart/<int:book_id>', methods=['GET', 'POST'])
def add_to_cart(book_id):
    book = Book.query.get(book_id)
    if book:
        # Initialize cart if it doesn't exist, or update it
        cart = session.get('cart', {})
        
        # Ensure we're using integers for both book_id and quantity
        cart[book_id] = cart.get(book_id, 0) + 1
        
        session['cart'] = cart
        flash(f'Added {book.title} to your cart.')
    else:
        flash('Sorry, this book is no longer available.')
    return redirect(url_for('catalogue'))



@app.route('/remove_from_cart/<int:book_id>')
def remove_from_cart(book_id):
    cart = session.get('cart', {})
    if book_id in cart:
        del cart[book_id]
        session['cart'] = cart  # Update the session with the new cart
        flash('Book removed from cart!')
    else:
        flash('Book not found in cart.')

    return redirect(url_for('cart'))  # Ensure this is pointing to the cart route




# Checkout route - Displays the cart and processes the checkout
@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    if request.method == "POST":
        flash("Checkout successful! Thank you for your purchase.")
        session.pop('cart', None)  # Clear the cart after successful checkout
        return redirect(url_for("index"))

    # Fetch books from the cart
    cart = session.get('cart', {})
    cart_books = [Book.query.get(book_id) for book_id in cart.keys()]
    total_price = sum(book.price * cart[book.id] for book in cart_books)

    return render_template("checkout.html", books=cart_books, total_price=total_price)

@app.route('/cart')
@login_required
def cart():
    cart = session.get('cart', {})
    book_ids = cart.keys()

    # Fetch books based on the cart data
    books = Book.query.filter(Book.id.in_(book_ids)).all()

    # Create a dictionary to access books by their IDs quickly
    books_dict = {book.id: book for book in books}

    # Check if any book in the cart has been removed or doesn't exist
    for book_id in list(cart.keys()):
        if book_id not in books_dict:
            del cart[book_id]  # Remove the book from the cart
            session['cart'] = cart
            flash(f'Book with ID {book_id} was removed as it no longer exists.')

    return render_template("cart.html", books_dict=books_dict)




# Logout route
@app.route('/logout')
@login_required
def logout():
    # Log the user out
    logout_user()

    # Redirect to the index (home) page after logging out
    return redirect(url_for('home_description'))  # Make sure 'index' is the correct name of your homepage route

# Subscription route
@app.route("/subscribe", methods=["POST"])
def subscribe():
    # Get the email address from the form
    email = request.form.get("email")
    
    # Check if the email already exists
    existing_subscriber = Subscriber.query.filter_by(email=email).first()
    if existing_subscriber:
        flash("You are already subscribed!", "warning")
        return redirect(url_for("home_description"))
    
    # Add the new subscriber to the database
    new_subscriber = Subscriber(email=email)
    db.session.add(new_subscriber)
    db.session.commit()
    
    flash("Thank you for subscribing to our newsletter!", "success")
    return redirect(url_for("home_description"))

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)

