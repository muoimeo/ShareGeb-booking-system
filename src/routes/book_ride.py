from flask import Blueprint, render_template, request

book_ride_bp = Blueprint('book_ride', __name__)

@book_ride_bp.route('/book-ride')
def book_ride():
    return render_template('book_ride/book_ride.html')

@book_ride_bp.route('/book_ride', methods=['GET', 'POST'])
def book_ride_post():
    if request.method == 'POST':
        pickup = request.form['pickup']  # Get form data
        dropoff = request.form['dropoff']
        # Add logic to save to database here
        return render_template('book_ride/book_ride.html', message="Ride booked!")
    return render_template('book_ride/book_ride.html')