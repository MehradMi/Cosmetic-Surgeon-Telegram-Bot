from flask import (Flask, render_template, request, 
                   redirect, url_for, flash, jsonify, session)
import sqlite3
import os
from datetime import datetime
from functools import wraps
import hashlib
import logging
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PICTURES_DIR = os.path.join(BASE_DIR, "static/pictures")

app = Flask(__name__)

# Use environment variable for secret key
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24).hex())

# Admin credentials from environment variables
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

# Production configuration
class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or os.urandom(24).hex()
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))

def setup_logging():
    """Setup logging for production environment"""
    if not app.debug:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Setup file handler with rotation
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Flask application startup')

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_admin_credentials():
    """Verify that admin credentials are properly configured"""
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        app.logger.error("Admin credentials not configured!")
        print("=" * 60)
        print("⚠️  CRITICAL: Admin credentials not configured!")
        print("Please set the following environment variables:")
        print("  ADMIN_USERNAME=your_admin_username")
        print("  ADMIN_PASSWORD=your_secure_password")
        print("  FLASK_SECRET_KEY=your_secret_key (optional)")
        print("  FLASK_DEBUG=false (for production)")
        print("  FLASK_HOST=0.0.0.0 (to accept external connections)")
        print("  FLASK_PORT=5000 (default port)")
        print("")
        print("Example (Linux/Mac):")
        print("  export ADMIN_USERNAME=admin")
        print("  export ADMIN_PASSWORD=your_secure_password123")
        print("  export FLASK_SECRET_KEY=your_very_secure_random_key")
        print("  export FLASK_DEBUG=false")
        print("")
        print("Example (Windows):")
        print("  set ADMIN_USERNAME=admin")
        print("  set ADMIN_PASSWORD=your_secure_password123")
        print("  set FLASK_SECRET_KEY=your_very_secure_random_key")
        print("  set FLASK_DEBUG=false")
        print("")
        print("Or create a .env file with:")
        print("  ADMIN_USERNAME=admin")
        print("  ADMIN_PASSWORD=your_secure_password123")
        print("  FLASK_SECRET_KEY=your_very_secure_random_key")
        print("  FLASK_DEBUG=false")
        print("  FLASK_HOST=0.0.0.0")
        print("  FLASK_PORT=5000")
        print("=" * 60)
        return False
    return True

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('لطفاً ابتدا وارد شوید.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Function for making a connection to our users.db database (returns the initiated connection)
def get_db_connection():
    try:
        conn = sqlite3.connect('users.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        app.logger.error(f"Database connection error: {e}")
        raise

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error: {error}")
    return render_template('500.html'), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if admin credentials are configured
    if not verify_admin_credentials():
        flash('خطا: اطلاعات مدیر پیکربندی نشده است. لطفاً با مدیر سیستم تماس بگیرید.', 'error')
        return render_template('login_persian.html')
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check credentials against environment variables
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            app.logger.info(f"Successful login for user: {username}")
            flash('با موفقیت وارد شدید!', 'success')
            return redirect(url_for('dashboard'))
        else:
            app.logger.warning(f"Failed login attempt for user: {username}")
            flash('نام کاربری یا رمز عبور اشتباه است.', 'error')
    
    return render_template('login_persian.html')

@app.route('/logout')
def logout():
    username = session.get('username', 'Unknown')
    session.clear()
    app.logger.info(f"User logged out: {username}")
    flash('با موفقیت خارج شدید.', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    try:
        conn = get_db_connection()
        
        # Get total users count
        total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        
        # Get recent users (last 10)
        recent_users = conn.execute('''
            SELECT rowid, * FROM users 
            ORDER BY rowid DESC 
            LIMIT 10
        ''').fetchall()
        
        conn.close()
        
        return render_template('dashboard_persian_with_logout.html', 
                             total_users=total_users, 
                             recent_users=recent_users)
    except Exception as e:
        app.logger.error(f"Dashboard error: {e}")
        flash('خطا در نمایش داشبورد', 'error')
        return redirect(url_for('login'))

@app.route('/users')
@login_required
def users_list():
    try:
        search = request.args.get('search', '')
        filter_city = request.args.get('city', '')
        filter_celeb = request.args.get('celeb', '')
        filter_phone = request.args.get('phone', '')
        filter_gender = request.args.get('gender', '')
        
        conn = get_db_connection()
        
        # Build the query based on filters
        query = 'SELECT rowid, * FROM users WHERE 1=1'
        params = []
        
        if search:
            query += ' AND (first_name LIKE ? OR last_name LIKE ? OR phone LIKE ?)'
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param])
        
        if filter_city:
            query += ' AND city LIKE ?'
            params.append(f'%{filter_city}%')
        
        if filter_celeb:
            query += ' AND celeb_name LIKE ?'
            params.append(f'%{filter_celeb}%')
        
        if filter_phone:
            query += ' AND phone LIKE ?'
            params.append(f'%{filter_phone}%')
        
        if filter_gender:
            query += ' AND gender LIKE ?'
            params.append(f'%{filter_gender}%')
        
        query += ' ORDER BY rowid DESC'
        
        users = conn.execute(query, params).fetchall()
        
        # Get unique cities and celebrities for filter dropdowns
        cities = conn.execute('SELECT DISTINCT city FROM users WHERE city IS NOT NULL ORDER BY city').fetchall()
        celebs = conn.execute('SELECT DISTINCT celeb_name FROM users WHERE celeb_name IS NOT NULL ORDER BY celeb_name').fetchall()
        phones = conn.execute('SELECT DISTINCT phone FROM users WHERE phone IS NOT NULL ORDER BY phone').fetchall()
        genders = conn.execute('SELECT DISTINCT gender FROM users WHERE gender IS NOT NULL ORDER BY gender').fetchall()
        
        conn.close()
        
        return render_template('users_persian_with_logout.html', 
                             users=users, 
                             cities=cities,
                             celebs=celebs,
                             phones=phones,
                             search=search,
                             genders=genders,
                             filter_city=filter_city,
                             filter_celeb=filter_celeb,
                             filter_phone=filter_phone,
                             filter_gender=filter_gender)
    except Exception as e:
        app.logger.error(f"Users list error: {e}")
        flash('خطا در نمایش لیست کاربران', 'error')
        return redirect(url_for('dashboard'))

@app.route('/user/<int:user_id>/bot/<string:bot_id>')
@login_required
def user_detail(user_id, bot_id):
    try:
        conn = get_db_connection()
        user = conn.execute('SELECT telegram_id, * FROM users WHERE telegram_id = ? AND bot_id = ?', (user_id, bot_id)).fetchone()
        conn.close()
         
        if user is None:
            flash('کاربر یافت نشد', 'error')
            return redirect(url_for('users_list'))
        
        return render_template('user_detail_persian_with_logout.html', user=user)
    except Exception as e:
        app.logger.error(f"User detail error: {e}")
        flash('خطا در نمایش جزئیات کاربر', 'error')
        return redirect(url_for('users_list'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    try:
        conn = get_db_connection()

        row_photo = conn.execute('SELECT user_photo FROM users WHERE rowid = ?', (user_id,)).fetchone()
        row_bot_id = conn.execute('SELECT bot_id FROM users WHERE rowid = ?', (user_id,)).fetchone()
        
        if row_photo and row_bot_id:
            user_photo_id = row_photo[0]
            bot_id = row_bot_id[0]
            user_photo_file_path = os.path.join(PICTURES_DIR, f"{user_photo_id}_{bot_id}.jpg")

            if os.path.exists(user_photo_file_path):
                os.remove(user_photo_file_path)
                app.logger.info(f"Deleted file: {user_photo_file_path}")
            else:
                app.logger.warning(f"File not found: {user_photo_file_path}")

        conn.execute('DELETE FROM users WHERE rowid = ?', (user_id,))
        conn.commit()
        conn.close()

        app.logger.info(f"User deleted: {user_id}")
        flash('کاربر با موفقیت حذف شد.', 'success')
        return redirect(url_for('users_list'))
    except Exception as e:
        app.logger.error(f"Delete user error: {e}")
        flash('خطا در حذف کاربر', 'error')
        return redirect(url_for('users_list'))

@app.route('/export')
@login_required
def export_users():
    try:
        import csv
        from io import StringIO
        from flask import Response
        
        conn = get_db_connection()
        users = conn.execute('SELECT * FROM users').fetchall()
        conn.close()
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['First Name', 'Last Name', 'Phone', 'City', 'Celebrity', 'Surgery Suggestions'])
        
        # Write data
        for user in users:
            writer.writerow([user['first_name'], user['last_name'], user['phone'], 
                            user['city'], user['celeb_name'], user['surgery_suggestions']])
        
        output.seek(0)
        
        app.logger.info("Users exported to CSV")
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=users_export.csv'}
        )
    except Exception as e:
        app.logger.error(f"Export error: {e}")
        flash('خطا در صادرات اطلاعات', 'error')
        return redirect(url_for('users_list'))

@app.route('/api/stats')
@login_required
def api_stats():
    try:
        conn = get_db_connection()
        
        # Get stats
        total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        
        # Users by city
        city_stats = conn.execute('''
            SELECT city, COUNT(*) as count 
            FROM users 
            WHERE city IS NOT NULL 
            GROUP BY city 
            ORDER BY count DESC
        ''').fetchall()
        
        # Users by celebrity
        celeb_stats = conn.execute('''
            SELECT celeb_name, COUNT(*) as count 
            FROM users 
            WHERE celeb_name IS NOT NULL 
            GROUP BY celeb_name 
            ORDER BY count DESC
        ''').fetchall()
        
        conn.close()
        
        return jsonify({
            'total_users': total_users,
            'city_stats': [dict(row) for row in city_stats],
            'celeb_stats': [dict(row) for row in celeb_stats]
        })
    except Exception as e:
        app.logger.error(f"API stats error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def create_directories():
    """Create necessary directories"""
    directories = ['templates', 'static', 'static/pictures', 'logs']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

if __name__ == '__main__':
    # Create necessary directories
    create_directories()
    
    # Setup logging
    setup_logging()
    
    # Load configuration
    config = Config()
    
    # Verify admin credentials are configured
    if verify_admin_credentials():
        print("=" * 50)
        print("✅ Admin credentials configured successfully!")
        print(f"Username: {ADMIN_USERNAME}")
        print("Password: [PROTECTED]")
        print(f"Debug Mode: {config.DEBUG}")
        print(f"Host: {config.HOST}")
        print(f"Port: {config.PORT}")
        print("=" * 50)
        
        if config.DEBUG:
            print("⚠️  WARNING: Running in DEBUG mode!")
            print("Set FLASK_DEBUG=false for production")
        else:
            print("✅ Running in PRODUCTION mode")
        
        print("🚀 Starting Flask application...")
        print("=" * 50)
        
        app.run(
            debug=config.DEBUG,
            host=config.HOST,
            port=config.PORT
        )
    else:
        print("❌ Cannot start application without proper admin credentials.")
        print("Please configure the required environment variables and try again.")