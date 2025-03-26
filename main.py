from flask import Flask
from config import Config
from models import db
from src.routes import book_ride_bp, discounts_bp, home_bp, payment_bp, users_bp

app = Flask(__name__, template_folder='src/templates', static_folder='static')
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(book_ride_bp)
app.register_blueprint(discounts_bp)
app.register_blueprint(home_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(users_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)