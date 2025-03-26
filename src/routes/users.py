import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, session
from werkzeug.utils import secure_filename
from models import db, User
import secrets
import datetime
import time

users_bp = Blueprint('users', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Store user info in session
            session['user_id'] = user.user_id
            session['full_name'] = user.full_name
            session['email'] = user.email
            session['phone'] = user.phone
            session['bio'] = user.bio
            session['interests'] = user.interests

            # Make sure avatar is set correctly, defaulting to basic_avatar.png if None
            if user.avatar is None or user.avatar == '':
                # If avatar is None or empty, update it in the database
                user.avatar = 'basic_avatar.png'
                db.session.commit()
                print(f"Updated null avatar to basic_avatar.png in database")
            
            # Set avatar in session
            session['avatar'] = user.avatar
            print(f"Set avatar in session to: {session['avatar']}")

            session['rating'] = user.rating
            session['ride_count'] = user.ride_count
            session['member_rank'] = user.member_rank
            
            # Redirect to dashboard
            return redirect(url_for('home.home'))
        else:
            # Invalid credentials
            return render_template('users/log_in.html', error="Invalid email or password")
            
    return render_template('users/log_in.html')

@users_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('users/register.html', error="Email already registered")
        
        # Create new user
        new_user = User(
            full_name=full_name,
            email=email,
            phone=phone
        )
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return render_template('users/log_in.html', message="Registration successful! Please login.")
        except Exception as e:
            db.session.rollback()
            return render_template('users/register.html', error=str(e))
    
    return render_template('users/register.html')

@users_bp.route('/forget_password', methods=['GET', 'POST'], endpoint='forget_password')
def forget_password():
    if request.method == 'POST':
        email = request.form['email']
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return render_template('users/forget_password.html', error="Email not found")
        
        # Generate reset token
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
        
        try:
            db.session.commit()
            # In a real app, you would send an email with the reset link
            # For now, we'll just redirect to the reset page with the token
            return redirect(url_for('users.reset_password', token=token))
        except Exception as e:
            db.session.rollback()
            return render_template('users/forget_password.html', error=str(e))
            
    return render_template('users/forget_password.html')

@users_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Find user by token
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or user.reset_token_expiry < datetime.datetime.now():
        return render_template('users/forget_password.html', error="Invalid or expired reset link")
    
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return render_template('users/reset_password.html', error="Passwords do not match", token=token)
        
        # Update password
        user.set_password(password)
        user.reset_token = None
        user.reset_token_expiry = None
        
        try:
            db.session.commit()
            return render_template('users/log_in.html', message="Password reset successful! Please login.")
        except Exception as e:
            db.session.rollback()
            return render_template('users/reset_password.html', error=str(e), token=token)
    
    return render_template('users/reset_password.html', token=token)

@users_bp.route('/logout')
def logout():
    # Clear session
    session.clear()
    return redirect(url_for('users.login'))

@users_bp.route('/profile')
def profile():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('users.login'))
    
    # Get user from database
    user = User.query.get(session['user_id'])
    
    if not user:
        session.clear()
        return redirect(url_for('users.login'))
    
    # Convert interests from comma-separated string to list
    interests_list = []
    if user.interests:
        interests_list = [interest.strip() for interest in user.interests.split(',')]
    
    # Create a user profile dictionary with all the required fields
    user_profile = {
        'name': user.full_name,
        'phone': user.phone,
        'email': user.email,
        'bio': user.bio or '',
        'interests': interests_list,
        'avatar': user.avatar or 'basic_avatar.png',
        'rating': user.rating or 0,
        'member_rank': user.member_rank
    }
    
    return render_template('users/profile.html', user=user_profile)

@users_bp.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Chưa đăng nhập'})
        
    try:
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'message': 'Không có file được tải lên'})
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Không có file được chọn'})
        
        if file and allowed_file(file.filename):
            # Save file to avatars folder
            filename = secure_filename(file.filename)
            # Generate unique filename to avoid conflicts
            unique_filename = f"{session['user_id']}_{int(time.time())}_{filename}"
            
            # Directly use the Flask app's static folder
            avatar_dir = os.path.join(current_app.root_path, 'static', 'image', 'avatars')
            print(f"Avatar directory: {avatar_dir}")
            
            # Ensure directory exists
            os.makedirs(avatar_dir, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(avatar_dir, unique_filename)
            print(f"Saving file to: {file_path}")
            file.save(file_path)
            print(f"File saved successfully")
            
            # Update user in database
            user = User.query.get(session['user_id'])
            if user:
                # Store the old avatar filename to delete it later if needed
                old_avatar = user.avatar
                print(f"Old avatar: {old_avatar}")
                
                try:
                    # Update user in database with explicit commit
                    user.avatar = unique_filename
                    db.session.commit()
                    print(f"User avatar updated in database to: {unique_filename}")
                    
                    # Force a refresh of the user object from the database to verify the update
                    db.session.refresh(user)
                    print(f"After refresh, user avatar is: {user.avatar}")
                    
                    # Update session data explicitly
                    session['avatar'] = unique_filename
                    print(f"Session avatar updated to: {unique_filename}")
                    
                    # Force session to be saved
                    session.modified = True
                    
                    return jsonify({'success': True, 'filename': unique_filename})
                except Exception as e:
                    db.session.rollback()
                    print(f"Database error: {str(e)}")
                    return jsonify({'success': False, 'message': f"Lỗi cơ sở dữ liệu: {str(e)}"})
            else:
                return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'})
        else:
            return jsonify({'success': False, 'message': 'Loại file không hợp lệ'})
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error uploading avatar: {str(e)}")
        print(f"Traceback: {error_traceback}")
        return jsonify({'success': False, 'message': f"Lỗi: {str(e)}"})

@users_bp.route('/update-profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
        
    if request.method == 'POST':
        # Get data from form
        fullname = request.form.get('fullname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        bio = request.form.get('bio')
        interests = request.form.getlist('interests')
        
        # Join interests into comma-separated string
        interests_str = ','.join(interests) if interests else ''
        
        # Update user in database
        user = User.query.get(session['user_id'])
        if user:
            user.full_name = fullname
            user.phone = phone
            user.email = email
            user.bio = bio
            user.interests = interests_str
            
            try:
                db.session.commit()
                
                # Update session data
                session['full_name'] = fullname
                session['phone'] = phone
                session['email'] = email
                session['bio'] = bio
                session['interests'] = interests_str
                
                return jsonify({'success': True})
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': str(e)})
    
    return jsonify({'success': False, 'message': 'Invalid request'})

@users_bp.route('/recent-rides')
def recent_rides():
    # Mock data for recent rides
    rides = [
        {
            'from': 'Hồ Hoàn Kiếm',
            'to': 'Văn Miếu',
            'date': '15/03/2024',
            'time': '14:30',
            'status': 'Hoàn thành',
            'rating': None
        },
        {
            'from': 'Hồ Tây',
            'to': 'Lotte Center',
            'date': '10/03/2024',
            'time': '09:15',
            'status': 'Hoàn thành',
            'rating': 5
        }
    ]
    return render_template('users/recent_rides.html', rides=rides)

@users_bp.route('/settings')
def settings():
    return render_template('users/settings.html')