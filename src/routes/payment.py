from flask import Blueprint, render_template, request

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        amount = request.form['amount']
        # Add payment processing logic
        return render_template('payments/payment.html', message="Payment successful!")
    return render_template('payments/payment.html')