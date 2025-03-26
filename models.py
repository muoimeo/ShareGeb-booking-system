from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('user', 'driver', 'admin'), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    interests = db.Column(db.String(255), nullable=True)  # Stored as comma-separated values
    avatar = db.Column(db.String(255), default='basic_avatar.png')
    rating = db.Column(db.Float, default=0.0)
    ride_count = db.Column(db.Integer, default=0)

    # Relationships
    driver = db.relationship('Driver', backref='user', uselist=False, cascade="all, delete")
    ride_passengers = db.relationship('RidePassenger', backref='user', cascade="all, delete")
    notifications = db.relationship('Notification', backref='user', cascade="all, delete")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    @property
    def member_rank(self):
        if self.ride_count < 7:
            return 'Iron Member'
        elif self.ride_count < 20:
            return 'Bronze Member'
        elif self.ride_count < 40:
            return 'Silver Member'
        elif self.ride_count < 70:
            return 'Gold Member'
        elif self.ride_count < 100:
            return 'Diamond Member'
        else:
            return 'VIP Member'


class Driver(db.Model):
    __tablename__ = 'Drivers'
    driver_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete="CASCADE"), unique=True, nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.Enum('available', 'busy', 'inactive'), default='available')

    # Relationships
    vehicles = db.relationship('Vehicle', backref='driver', cascade="all, delete")
    rides = db.relationship('Ride', backref='driver', cascade="all, delete")


class Vehicle(db.Model):
    __tablename__ = 'Vehicles'
    vehicle_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('Drivers.driver_id', ondelete="CASCADE"), nullable=False)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    plate_number = db.Column(db.String(20), unique=True, nullable=False)


class Ride(db.Model):
    __tablename__ = 'Rides'
    ride_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('Drivers.driver_id', ondelete="SET NULL"))
    status = db.Column(db.Enum('requested', 'accepted', 'ongoing', 'completed', 'cancelled'), default='requested')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    cancellation_reason = db.Column(db.String(255), nullable=True)

    # Relationships
    passengers = db.relationship('RidePassenger', backref='ride', cascade="all, delete")
    ratings = db.relationship('Rating', backref='ride', cascade="all, delete")
    chat_messages = db.relationship('ChatMessage', backref='ride', cascade="all, delete")


class RidePassenger(db.Model):
    __tablename__ = 'Ride_Passengers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('Rides.ride_id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete="CASCADE"), nullable=False)
    pickup_location = db.Column(db.String(255), nullable=False)
    dropoff_location = db.Column(db.String(255), nullable=False)
    distance_km = db.Column(db.Numeric(5, 2), default=0, nullable=False)
    fare = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('requested', 'onboard', 'completed', 'cancelled'), default='requested')
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    payments = db.relationship('Payment', backref='ride_passenger', cascade="all, delete")
    discount_usages = db.relationship('DiscountUsage', backref='ride_passenger', cascade="all, delete")


class Payment(db.Model):
    __tablename__ = 'Payments'
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ride_passenger_id = db.Column(db.Integer, db.ForeignKey('Ride_Passengers.id', ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.Enum('cash', 'credit_card', 'wallet'), nullable=False)
    payment_status = db.Column(db.Enum('pending', 'completed', 'failed'), default='pending')
    paid_at = db.Column(db.DateTime, nullable=True)


class Rating(db.Model):
    __tablename__ = 'Ratings'
    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('Rides.ride_id', ondelete="CASCADE"), nullable=False)
    rater_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete="CASCADE"), nullable=False)
    ratee_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete="CASCADE"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('ride_id', 'rater_id', 'ratee_id', name='unique_rating'),)


class ChatMessage(db.Model):
    __tablename__ = 'Chat_Messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete="CASCADE"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete="CASCADE"), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey('Rides.ride_id', ondelete="CASCADE"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = 'Notifications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete="CASCADE"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Discount(db.Model):
    __tablename__ = 'Discounts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_percentage = db.Column(db.Numeric(5, 2), nullable=False)
    max_discount_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    valid_from = db.Column(db.Date, nullable=False)
    valid_to = db.Column(db.Date, nullable=False)
    max_usage = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    discount_usages = db.relationship('DiscountUsage', backref='discount', cascade="all, delete")


class DiscountUsage(db.Model):
    __tablename__ = 'Discount_Usage'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ride_passenger_id = db.Column(db.Integer, db.ForeignKey('Ride_Passengers.id', ondelete="CASCADE"), nullable=False)
    discount_id = db.Column(db.Integer, db.ForeignKey('Discounts.id', ondelete="CASCADE"), nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.utcnow)
