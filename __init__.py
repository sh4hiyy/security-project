from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from forms import *
from listing import Listing
from user import User
from sendemail import Email
from transaction import Transaction
from dbmanager import *
import plotly.express as px
from functools import wraps
import logging
import pandas as pd
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

app = Flask(__name__, static_folder='')
app.secret_key = 'helpmepls'

# Initialize logging
logger = logging.getLogger(__name__)


# ======================
# HELPER FUNCTIONS
# ======================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')


def verify_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=expiration
        )
    except:
        return False
    return email


# ======================
# CORE ROUTES
# ======================
@app.route('/')
def start():
    session.clear()
    session['loggedin'] = False
    session['admin'] = False
    return redirect(url_for('home'))


@app.route('/home')
def home():
    db = DBManager()
    listings = db.get_table('listings').to_dict(orient='records')
    if session.get('admin'):
        return render_template('admin_report.html')
    return render_template('home.html', listings=listings)


@app.route('/base')
def base():
    return render_template('base.html')


# ======================
# AUTHENTICATION ROUTES
# ======================
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        credential = form.username_or_email.data.strip()
        password = form.password.data.strip()
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')

        user = User()
        login_success, otp = user.login(credential, password)

        if login_success:
            DBManager().log_audit_event(user.user_id, 'login', ip_address, user_agent, "Successful login")
            session['user_email'] = user.email
            if otp:
                return redirect(url_for('otp_route'))
            else:
                DBManager().log_audit_event(None, 'login_failed', ip_address, user_agent, f"Failed login: {credential}")
                flash("Invalid username or password", "danger")
                session.update({
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'is_admin': user.is_admin,
                    'profile_pic': user.profile_pic,
                    'loggedin': True
                })
                return redirect(url_for('home'))
        flash("Invalid username or password", "danger")
    return render_template('login.html', form=form)


@app.route('/otp_route', methods=['GET', 'POST'])
def otp_route():
    form = OTPForm(request.form)
    user_email = session.get('user_email')

    if request.method == 'GET':
        session['otp'] = Email().send_otp(user_email)

    elif request.method == 'POST' and form.validate():
        user = User(email=user_email)
        if user.verify_otp(form.otp.data.strip(), session.get('otp')):
            session.update({
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'profile_pic': user.profile_pic,
                'loggedin': True
            })
            session.pop('user_email', None)
            flash("OTP verified successfully!", "success")
            DBManager().log_audit_event(user.user_id, '2fa_attempt', request.remote_addr,
                                        request.headers.get('User-Agent'), "2FA verified successfully")
            return redirect(url_for('home'))
        flash("Incorrect OTP", "danger")
    return render_template('otp.html', form=form)

@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    DBManager().log_audit_event(user_id, 'logout', request.remote_addr, request.headers.get('User-Agent'), "User logged out")
    session.clear()
    return redirect(url_for('start'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = signupForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip(),
            password=form.password.data.strip()
        )

        msg = user.create_user()

        if msg is None:
            flash('Registration successful! Please log in.', 'success')
            Email().send_email(user.email, "Registration", "Thank you for signing up")
            return redirect(url_for('login'))
        flash(msg, 'danger')

    return render_template('signup.html', form=form)


# ======================
# PASSWORD MANAGEMENT
# ======================

@app.route('/change_password_with_email', methods=['GET', 'POST'])
def change_password_with_email():
    form = RequestResetForm()
    if form.validate_on_submit():
        # Add your password reset logic here
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Send reset email
            pass
        flash('If an account exists with that email, a reset link has been sent', 'info')
        return redirect(url_for('login'))
    return render_template('change_password.html', form=form)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(user_id=session['user_id'])
        if user.verify_password(form.current_password.data):
            if user.change_password(form.new_password.data):
                flash("Password changed successfully", "success")
                return redirect(url_for('profile', user_id=session['user_id']))
            flash("Failed to change password", "danger")
        else:
            flash("Current password is incorrect", "danger")
    return render_template('change_password.html', form=form)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(email=form.email.data.strip())
        if user.get_user_by_email():
            token = generate_token(user.email)
            reset_url = url_for('reset_password', token=token, _external=True)
            Email().send_email(user.email, "Password Reset", f"Reset link: {reset_url}")
        flash("If this email exists, a reset link has been sent", "info")
        return redirect(url_for('login'))
    return render_template('forgot_password.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_token(token)
    if not email:
        flash("Invalid or expired reset link", "danger")
        return redirect(url_for('forgot_password'))

    form = ResetPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(email=email)
        if user.get_user_by_email():
            if user.change_password(form.new_password.data):
                flash("Password reset successfully", "success")
                return redirect(url_for('login'))
    return render_template('reset_password.html', form=form, token=token)


# ======================
# USER PROFILE ROUTES
# ======================
@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    form = ProfileForm(request.form)
    user = User(user_id=user_id)
    user.get_user_by_id()

    if request.method == 'POST' and form.validate():
        user.profile_pic = form.profile_pic_url.data
        user.username = form.username.data.strip()
        user.email = form.email.data.strip()
        user.name = form.name.data
        user.phone_number = int(form.phone_number.data) if form.phone_number.data else None
        user.twofa = form.twofa.data
        user.edit_user()

        session['user_image'] = user.profile_pic
        if session['user_id'] == user_id:
            session['profile_pic'] = user.profile_pic
            session['username'] = user.username

        flash("Profile updated successfully", "success")
        return redirect(url_for('profile', user_id=user_id))

    if request.method == 'GET':
        form.profile_pic_url.data = user.profile_pic
        form.username.data = user.username
        form.email.data = user.email
        form.name.data = user.name
        form.phone_number.data = user.phone_number
        form.twofa.data = user.twofa

    return render_template('profile.html', form=form, user_id=user_id)


@app.route('/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    form = PasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(user_id=session['user_id'])
        if user.verify_password(form.password.data):
            return redirect(url_for('confirm_delete_user', user_id=session['user_id']))
        flash("Incorrect password", "danger")
    return render_template('delete_user.html', form=form)


@app.route('/confirm_delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def confirm_delete_user(user_id):
    form = ProfileForm(request.form)
    user = User(user_id=user_id)
    user.get_user_by_id()

    if request.method == 'POST':
        user.delete_user()
        if session['admin']:
            return redirect(url_for('manage_user'))
        return redirect(url_for('start'))

    if request.method == 'GET':
        form.profile_pic_url.data = user.profile_pic
        form.username.data = user.username
        form.email.data = user.email
        form.name.data = user.name
        form.phone_number.data = user.phone_number

    return render_template('confirm_delete_user.html', form=form, user_id=user_id)


# ======================
# LISTING ROUTES
# ======================
@app.route('/products')
def get_products():
    db = DBManager()
    listings = db.get_table('listings').to_dict(orient='records')
    return render_template('home.html', listings=listings)


@app.route('/create_listing', methods=['GET', 'POST'])
@login_required
def create_listing():
    form = CreateListingForm(request.form)
    if request.method == 'POST' and form.validate():
        listing = Listing(
            user_id=session['user_id'],
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            category=form.category.data.strip(),
            price=form.price.data,
            image_path=form.image_path.data.strip()
        )
        if listing.create_listing():
            flash("Listing created successfully", "success")
            return redirect(url_for('home'))
    return render_template('create_listing.html', form=form)


@app.route('/edit_listing/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def edit_listing(listing_id):
    form = CreateListingForm(request.form)
    listing = Listing(listing_id=listing_id)
    listing.get_listing_by_id()

    if request.method == 'POST' and form.validate():
        listing.title = form.title.data.strip()
        listing.description = form.description.data.strip()
        listing.category = form.category.data
        listing.price = float(form.price.data)
        listing.image_path = str(form.image_path.data)
        listing.edit_listing()
        session['listing_image'] = listing.image_path
        flash("Listing updated successfully", "success")
        return redirect(url_for('edit_listing', listing_id=listing_id))

    if request.method == 'GET':
        form.title.data = listing.title
        form.description.data = listing.description
        form.category.data = listing.category
        form.price.data = listing.price
        form.image_path.data = listing.image_path
        session['listing_image'] = listing.image_path

    return render_template('edit_listing.html', form=form, listing_id=listing_id)


@app.route('/delete_listing/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def delete_listing(listing_id):
    form = CreateListingForm(request.form)
    listing = Listing(listing_id=listing_id)
    listing.get_listing_by_id()

    if request.method == 'POST':
        listing.delete_listing()
        if session['admin']:
            return redirect(url_for('admin_report'))
        return redirect(url_for('listing_report'))

    if request.method == 'GET':
        form.title.data = listing.title
        form.description.data = listing.description
        form.category.data = listing.category
        form.price.data = listing.price
        form.image_path.data = listing.image_path
        session['listing_image'] = listing.image_path

    return render_template('delete_listing.html', form=form, listing_id=listing_id)


# ======================
# TRANSACTION ROUTES
# ======================
@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.json.get('user_id')
    db = DBManager()
    cursor = db.conn.cursor()
    cursor.execute("SELECT listing_id, title, price FROM listings WHERE listing_id = %s", (product_id,))
    row = cursor.fetchone()
    if row:
        return jsonify(product=dict(listing_id=row[0], title=row[1], price=row[2]))
    return jsonify({"error": "Product not found"}), 404


@app.route('/cart')
@login_required
def cart():
    return render_template('cart.html')


@app.route('/checkout')
@login_required
def checkout():
    return render_template('checkout.html')


@app.route('/process_checkout', methods=['POST'])
@login_required
def process_checkout():
    return redirect(url_for('confirm_checkout'))


@app.route('/confirm_checkout')
@login_required
def confirm_checkout():
    return render_template('confirm_checkout.html')


@app.route('/add_transactions', methods=['GET', 'POST'])
@login_required
def add_transactions():
    data = request.json
    listing_ids = data.get('product_id')
    if not listing_ids:
        return jsonify({'error': 'Missing listing ID'}), 400

    for listing_id in listing_ids:
        Transaction(buyer_id=session['user_id'], listing_id=listing_id).create_transaction()

    return render_template('/Transaction_Table.html')


@app.route('/transaction_table')
@login_required
def transaction_table():
    trans_df = DBManager().get_table('transactions')
    list_df = DBManager().get_table('listings')
    merged_df = pd.merge(trans_df, list_df)
    return render_template('/Transaction_Table.html', merged_df=merged_df.to_dict(orient='records'))


@app.route('/transaction_update', methods=['POST'])
@login_required
def transaction_update():
    transaction = Transaction()
    success = transaction.update_transaction(
        request.form.get('transaction_id'),
        {
            'listing_id': request.form.get('listing_id'),
            'buyer_id': request.form.get('buyer_id')
        }
    )
    trans_df = DBManager().get_table('transactions')
    list_df = DBManager().get_table('listings')
    merged_df = pd.merge(trans_df, list_df)
    return render_template('Transaction_Table.html', success=success, merged_df=merged_df.to_dict(orient='records'))


@app.route('/delete_transaction', methods=['POST'])
@login_required
def delete_transaction():
    transaction = Transaction(transaction_id=request.form.get('transaction_id'))
    transaction.delete_transaction()
    trans_df = DBManager().get_table('transactions')
    list_df = DBManager().get_table('listings')
    merged_df = pd.merge(trans_df, list_df)
    return render_template('Transaction_Table.html', merged_df=merged_df.to_dict(orient='records'))


# ======================
# REPORT ROUTES
# ======================
@app.route('/user_listing_report')
@login_required
def listing_report():
    df_listings = DBManager().get_table('listings')
    user_listings = df_listings[df_listings['user_id'] == session['user_id']]
    total_value = user_listings['price'].sum()

    fig_price = px.bar(user_listings, x='category', y='price', title='Category by Price')
    fig_html = fig_price.to_html(full_html=False)

    return render_template('/user_listing_report.html',
                           user_listings=user_listings.to_dict(orient='records'),
                           fig_html=fig_html,
                           table_type='listings',
                           total_value=round(total_value, 2))


@app.route('/admin_report')
@admin_required
def admin_report():
    df_listings = DBManager().get_table('listings')
    df_users = DBManager().get_table('users')
    merged = pd.merge(df_listings, df_users)

    fig = px.bar(merged.groupby('category').size().reset_index(name='count'),
                 x='category', y='count', title='Category by Count', color='count')

    return render_template('/admin_report.html',
                           user_listings=merged.to_dict(orient='records'),
                           fig_html=fig.to_html(full_html=False),
                           table_type='listings',
                           total_value=round(merged['price'].sum(), 2))


# ======================
# ADMIN ROUTES
# ======================
@app.route('/admin/users')
@admin_required
def admin_users():
    users = DBManager().get_table('users').to_dict(orient='records')
    return render_template('admin/users.html', users=users)


@app.route('/admin/user/<int:user_id>/lock', methods=['POST'])
@admin_required
def admin_lock_user(user_id):
    DBManager().execute_query(
        "UPDATE users SET account_locked = TRUE WHERE user_id = %s",
        (user_id,)
    )
    flash("User account locked", "success")
    return redirect(url_for('admin_users'))


@app.route('/admin/user/<int:user_id>/unlock', methods=['POST'])
@admin_required
def admin_unlock_user(user_id):
    DBManager().execute_query(
        "UPDATE users SET account_locked = FALSE, failed_login_attempts = 0 WHERE user_id = %s",
        (user_id,)
    )
    flash("User account unlocked", "success")
    return redirect(url_for('admin_users'))


# ======================
# ERROR HANDLERS
# ======================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# ======================
# SECURITY MIDDLEWARE
# ======================
# ======================
# SECURITY MIDDLEWARE
# ======================
@app.before_request
def before_request():
    # Force HTTPS in production
    if not request.is_secure and not app.debug:
        return redirect(request.url.replace('http://', 'https://'), code=301)

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return response

if __name__ == '__main__':
    app.run(debug=True)

# from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
# from forms import *
# from listing import Listing
# from user import User
# from sendemail import Email
# from transaction import Transaction
# from dbmanager import *
# import plotly.express as px
# from flask import request, session
# from functools import wraps
# import logging
#
# logger = logging.getLogger(__name__)
#
#
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             return redirect(url_for('login', next=request.url))
#         return f(*args, **kwargs)
#
#     return decorated_function
#
#
# def admin_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session or not session.get('is_admin'):
#             return redirect(url_for('login', next=request.url))
#         return f(*args, **kwargs)
#
#     return decorated_function
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm(request.form)
#     if request.method == 'POST' and form.validate():
#         credential = form.username_or_email.data.strip()
#         password = form.password.data.strip()
#
#         # Get IP and user agent for logging
#         ip_address = request.remote_addr
#         user_agent = request.headers.get('User-Agent')
#
#         user = User()
#         success, message = user.login(credential, password, ip_address, user_agent)
#
#         if success:
#             session['user_id'] = user.user_id
#             session['username'] = user.username
#             session['email'] = user.email
#             session['is_admin'] = user.is_admin
#
#             # Check if 2FA is required
#             if user.twofa_enabled:
#                 return redirect(url_for('otp_route'))
#
#             return redirect(url_for('home'))
#         else:
#             flash(message, 'danger')
#             return redirect(url_for('login'))
#
#     return render_template('login.html', form=form)
#
#
# @app.route('/change_password', methods=['GET', 'POST'])
# @login_required
# def change_password():
#     form = ChangePasswordForm(request.form)
#     if request.method == 'POST' and form.validate():
#         current_password = form.current_password.data
#         new_password = form.new_password.data
#
#         user = User(user_id=session['user_id'])
#         if not user.verify_password(current_password):
#             flash("Current password is incorrect", "danger")
#             return redirect(url_for('change_password'))
#
#         # Check password complexity
#         is_valid, msg = user.validate_password_complexity(new_password)
#         if not is_valid:
#             flash(msg, "danger")
#             return redirect(url_for('change_password'))
#
#         # Check against password history (implement this in User class)
#         if user.is_password_in_history(new_password):
#             flash("You cannot reuse a previous password", "danger")
#             return redirect(url_for('change_password'))
#
#         # Change password
#         if user.change_password(new_password):
#             flash("Password changed successfully", "success")
#             return redirect(url_for('profile'))
#         else:
#             flash("Failed to change password", "danger")
#
#     return render_template('change_password.html', form=form)
#
#
# # Implement similar enhanced routes for:
# # - Registration
# # - Password reset
# # - Account recovery
# # - Admin functions
#
#
# from itsdangerous import URLSafeTimedSerializer
# from flask import current_app
#
#
# def generate_token(email):
#     serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
#     return serializer.dumps(email, salt='password-reset-salt')
#
#
# def verify_token(token, expiration=3600):
#     serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
#     try:
#         email = serializer.loads(
#             token,
#             salt='password-reset-salt',
#             max_age=expiration
#         )
#     except:
#         return False
#     return email
#
#
# @app.route('/forgot_password', methods=['GET', 'POST'])
# def forgot_password():
#     form = ForgotPasswordForm(request.form)
#     if request.method == 'POST' and form.validate():
#         email = form.email.data.strip()
#         user = User(email=email)
#         if user.get_user_by_email():
#             token = generate_token(email)
#             reset_url = url_for('reset_password', token=token, _external=True)
#
#             # Send email with reset link
#             email_body = f"Click this link to reset your password: {reset_url}"
#             Email().send_email(email, "Password Reset Request", email_body)
#
#             flash("Password reset link sent to your email", "success")
#             return redirect(url_for('login'))
#
#         flash("If this email exists, a reset link has been sent", "info")
#
#     return render_template('forgot_password.html', form=form)
#
#
# @app.route('/reset_password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     email = verify_token(token)
#     if not email:
#         flash("The reset link is invalid or has expired", "danger")
#         return redirect(url_for('forgot_password'))
#
#     form = ResetPasswordForm(request.form)
#     if request.method == 'POST' and form.validate():
#         new_password = form.new_password.data
#         confirm_password = form.confirm_password.data
#
#         if new_password != confirm_password:
#             flash("Passwords do not match", "danger")
#             return redirect(url_for('reset_password', token=token))
#
#         user = User(email=email)
#         if user.get_user_by_email():
#             # Check password complexity
#             is_valid, msg = user.validate_password_complexity(new_password)
#             if not is_valid:
#                 flash(msg, "danger")
#                 return redirect(url_for('reset_password', token=token))
#
#             if user.change_password(new_password):
#                 flash("Password reset successfully", "success")
#                 return redirect(url_for('login'))
#
#     return render_template('reset_password.html', form=form, token=token)
#
# # admin featuressss
# @app.route('/admin/users')
# @admin_required
# def admin_users():
#     db = DBManager()
#     users = db.get_table('users')
#     return render_template('admin/users.html', users=users.to_dict(orient='records'))
#
# @app.route('/admin/user/<int:user_id>/lock', methods=['POST'])
# @admin_required
# def admin_lock_user(user_id):
#     db = DBManager()
#     db.execute_query(
#         "UPDATE users SET account_locked = TRUE WHERE user_id = %s",
#         (user_id,)
#     )
#     flash("User account locked", "success")
#     return redirect(url_for('admin_users'))
#
# @app.route('/admin/user/<int:user_id>/unlock', methods=['POST'])
# @admin_required
# def admin_unlock_user(user_id):
#     db = DBManager()
#     db.execute_query(
#         "UPDATE users SET account_locked = FALSE, failed_login_attempts = 0 WHERE user_id = %s",
#         (user_id,)
#     )
#     flash("User account unlocked", "success")
#     return redirect(url_for('admin_users'))
#
# @app.route('/admin/audit_logs')
# @admin_required
# def admin_audit_logs():
#     db = DBManager()
#     logs = db.fetch_all("""
#     SELECT l.*, u.username
#     FROM audit_log l
#     LEFT JOIN users u ON l.user_id = u.user_id
#     ORDER BY created_at DESC
#     LIMIT 100
#     """)
#     return render_template('admin/audit_logs.html', logs=logs)
#
# # security middleware
#
# @app.before_request
# def before_request():
#     # Force HTTPS in production
#     if not request.is_secure and current_app.env == 'production':
#         url = request.url.replace('http://', 'https://', 1)
#         code = 301
#         return redirect(url, code=code)
#
#     # Add security headers
#     @app.after_request
#     def add_security_headers(response):
#         response.headers['X-Content-Type-Options'] = 'nosniff'
#         response.headers['X-Frame-Options'] = 'SAMEORIGIN'
#         response.headers['X-XSS-Protection'] = '1; mode=block'
#         if 'Cache-Control' not in response.headers:
#             response.headers[
#                 'Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
#         return response
#
# # end
#
# app = Flask(__name__,static_folder='')
# app.secret_key = 'helpmepls'
#
# @app.route('/')
# def start():
#     for x in list(session.keys()):
#         session.pop(x, None)
#     session['loggedin'] = False
#     session['admin'] = False
#     return redirect(url_for('home'))
#
# @app.route('/home')
# def home():
#     db_manager = DBManager()
#     listings = db_manager.get_table('listings')
#     if session['admin'] == True:
#         return render_template('admin_report.html')
#     else:
#         return render_template('home.html', listings=listings.to_dict(orient='records'))
#
# @app.route('/base')
# def base():
#     return render_template('base.html')
#
# @app.route('/products', methods=['GET'])
# def get_products():
#     db_manager = DBManager()
#     listings = db_manager.get_table('listings')
#     listings = listings.to_dict(orient='records')  # Convert dataframe to list of dictionaries
#     return render_template('home.html', listings=listings)
#
# @app.route('/add_to_cart', methods=['POST'])
# def add_to_cart():
#     product_id = request.json.get('user_id')
#     db = DBManager()
#     cursor = db.conn.cursor()
#     cursor.execute("SELECT listing_id, title, price FROM listings WHERE listing_id = 1", (product_id,))
#     row = cursor.fetchone()
#     if row:
#         product = dict(listing_id=row[0], title=row[1], price=row[2])
#         return jsonify(product=product)
#     else:
#         return jsonify({"error": "Product not found"}), 404
#
# @app.route('/cart')
# def cart():
#     return render_template('cart.html')
#
# @app.route('/checkout')
# def checkout():
#     return render_template('checkout.html')
#
# @app.route('/checkout_details')
# def checkout_details():
#     return render_template('checkout_details.html')
#
# @app.route('/process_checkout', methods=['POST'])
# def process_checkout():
#     # Process form data here (e.g., save transaction details)
#     return redirect(url_for('confirm_checkout'))
#
# @app.route('/confirm_checkout')
# def confirm_checkout():
#     return render_template('confirm_checkout.html')
#
#
# @app.route('/add_transactions', methods=['GET','POST'])
# def add_transactions():
#     data = request.json
#     listing_ids = data.get('product_id')
#     if not listing_ids:
#         return jsonify({'error': 'Missing listing ID'}), 400
#
#     for listing_id in listing_ids:
#         transaction = Transaction(buyer_id=session['user_id'], listing_id=listing_id)
#         transaction.create_transaction()
#
#     return render_template('/Transaction_Table.html')
#
# @app.route('/transaction_table')
# def transaction_table():
#     trans_df = DBManager().get_table('transactions')
#     list_df = DBManager().get_table('listings')
#     merged_df= pd.merge(trans_df, list_df)
#     return render_template('/Transaction_Table.html', merged_df=merged_df.to_dict(orient='records') )
#
# @app.route('/transaction_updating')
# def transaction_updating():
#     transaction_id = request.args.get('transaction_id')
#     listing_id = request.args.get('listing_id')
#     buyer_id = request.args.get('buyer_id')
#
#     trans_df = DBManager().get_table('transactions')
#     list_df = DBManager().get_table('listings')
#     user_df = DBManager().get_table('users')
#
#
#     merged_df = pd.merge(trans_df, list_df)
#     merged_df = pd.merge(merged_df, user_df)
#
#     if transaction_id and listing_id and buyer_id:
#         transaction_id = int(transaction_id)
#         listing_id = int(listing_id)
#         buyer_id = int(buyer_id)
#
#         filtered_df = merged_df[
#                 (merged_df['transaction_id'] == transaction_id) &
#                 (merged_df['listing_id'] == listing_id) &
#                 (merged_df['buyer_id'] == buyer_id)
#
#                 ]
#     else:
#         filtered_df = merged_df
#     data = filtered_df.to_dict(orient='records')
#     return render_template('Transaction_update.html',data=data,  transaction_id=transaction_id, listing_id=listing_id, buyer_id=buyer_id )
#
#
# @app.route('/transaction_update', methods=['POST'])
# def transaction_update():
#     transaction_id = request.form.get('transaction_id')
#     listing_id = request.form.get('listing_id')
#     buyer_id = request.form.get('buyer_id')
#     new_data = {
#         'listing_id': listing_id,
#         'buyer_id': buyer_id
#
#     }
#     transaction = Transaction()
#     success = transaction.update_transaction(transaction_id, new_data)
#     trans_df = DBManager().get_table('transactions')
#     list_df = DBManager().get_table('listings')
#     merged_df = pd.merge(trans_df, list_df)
#
#     return render_template('Transaction_Table.html', success=success, merged_df=merged_df.to_dict(orient='records'))
#
# @app.route('/delete_transaction' , methods=['POST'])
# def delete_transaction():
#     transaction_id = request.form.get('transaction_id')
#     transaction = Transaction(transaction_id).delete_transaction()
#     trans_df = DBManager().get_table('transactions')
#     list_df = DBManager().get_table('listings')
#     merged_df = pd.merge(trans_df, list_df)
#
#     return render_template('Transaction_Table.html', transaction=transaction, merged_df=merged_df.to_dict(orient='records') )
#
# @app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
# def profile(user_id):
#     form = ProfileForm(request.form)
#     user1 = User(user_id=user_id)
#     user1.get_user_by_id()
#     session['user_image'] = user1.profile_pic
#     if request.method == 'GET':
#         user = User(user_id=user_id)
#         user.get_user_by_id()
#         form.profile_pic_url.data = user.profile_pic
#         form.username.data = user.username
#         form.email.data = user.email
#         form.name.data = user.name
#         form.phone_number.data = user.phone_number
#         form.twofa.data = user.twofa
#     if request.method == 'POST':
#         print('sent')
#         updated_user = User(user_id=user_id)
#         updated_user.profile_pic = form.profile_pic_url.data
#         updated_user.username = form.username.data.strip()
#         updated_user.email = form.email.data.strip()
#         if form.name.data:
#             updated_user.name = form.name.data
#         if form.phone_number.data:
#             updated_user.phone_number = int(form.phone_number.data)
#         updated_user.twofa = form.twofa.data
#         updated_user.edit_user()
#         session['user_image'] = updated_user.profile_pic
#         if session['user_id'] == user_id:
#             session['profile_pic'] = updated_user.profile_pic
#             session['username'] = updated_user.username
#
#         return redirect(url_for('profile', user_id=user_id))
#     return render_template('profile.html', form=form, user_id=user_id)
#
# @app.route('/manage_user')
# def manage_user():
#     db = DBManager()
#     users_df = db.get_table('users')
#     data = users_df.to_dict(orient='records')
#     return render_template('manage_user.html',data=data)
#
# @app.route('/delete_user', methods=['GET', 'POST'])
# def delete_user():
#     form = PasswordForm(request.form)
#     if request.method == 'POST':
#         password = form.password.data
#         id = session['user_id']
#         user = User(id)
#         user.get_user_by_id()
#         if user.verify_password(password):
#             return redirect(url_for('confirm_delete_user', user_id=session['user_id']))
#     return render_template('delete_user.html', form=form)
#
# @app.route('/confirm_delete_user/<int:user_id>', methods=['GET', 'POST'])
# def confirm_delete_user(user_id):
#     form = ProfileForm(request.form)
#     user1 = User(user_id=user_id)
#     user1.get_user_by_id()
#     session['user_image'] = user1.profile_pic
#     if request.method == 'GET':
#         user = User(user_id=user_id)
#         user.get_user_by_id()
#         form.profile_pic_url.data = user.profile_pic
#         form.username.data = user.username
#         form.email.data = user.email
#         form.name.data = user.name
#         form.phone_number.data = user.phone_number
#     if request.method == 'POST':
#         delete_user = User(user_id=user_id)
#         delete_user.delete_user()
#         if session['admin'] == True:
#             return redirect(url_for('manage_user'))
#         else:
#             return redirect(url_for('start'))
#     return render_template('confirm_delete_user.html', form=form, user_id=user_id)
#
#
# @app.route('/create_user_listing', methods=['GET', 'POST'])
# def create_user_listing():
#     form = CreateListingForm(request.form)
#     if request.method == 'POST' and form.validate():
#         user_id = session['user_id']
#         title = form.title.data.strip()
#         description = form.description.data.strip()
#         category = form.category.data.strip()
#         price = str(form.price.data)
#         image_path = form.image_path.data.strip()
#         listing = Listing(user_id=user_id, title=title, description=description, category=category, price=price, image_path=image_path)
#         listing.create_listing()
#         return redirect(url_for('home'))
#     return render_template('create_user_listing.html', form=form)
#
# @app.route('/edit_listing/<int:listing_id>', methods=['GET', 'POST'])
# def edit_listing(listing_id):
#     form = CreateListingForm(request.form)
#     listing1 = Listing(listing_id=listing_id)
#     listing1.get_listing_by_id()
#     session['listing_image'] = listing1.image_path
#     if request.method == 'GET':
#         listing = Listing(listing_id=listing_id)
#         listing.get_listing_by_id()
#         form.title.data = listing.title
#         form.description.data = listing.description
#         form.category.data = listing.category
#         form.price.data = listing.price
#         form.image_path.data = listing.image_path
#     if request.method == 'POST':
#         print('sent')
#         updated_listing = Listing(listing_id=listing_id)
#         updated_listing.title = form.title.data.strip()
#         if form.description.data:
#             updated_listing.description = form.description.data.strip()
#         updated_listing.category = form.category.data
#         updated_listing.price = float(form.price.data)
#         updated_listing.image_path = str(form.image_path.data)
#         updated_listing.edit_listing()
#         session['listing_image'] = updated_listing.image_path
#         return redirect(url_for('edit_listing', listing_id=listing_id))
#     return render_template('edit_listing.html', form=form, listing_id=listing_id)
#
# @app.route('/delete_listing/<int:listing_id>', methods=['GET', 'POST'])
# def delete_listing(listing_id):
#     form = CreateListingForm(request.form)
#     listing1 = Listing(listing_id=listing_id)
#     listing1.get_listing_by_id()
#     session['listing_image'] = listing1.image_path
#     if request.method == 'GET':
#         listing = Listing(listing_id=listing_id)
#         listing.get_listing_by_id()
#         form.title.data = listing.title
#         form.description.data = listing.description
#         form.category.data = listing.category
#         form.price.data = listing.price
#         form.image_path.data = listing.image_path
#     if request.method == 'POST':
#         delete_listing = Listing(listing_id=listing_id)
#         delete_listing.delete_listing()
#         if session['admin'] == True:
#             return redirect(url_for('admin_report'))
#         else:
#             return redirect(url_for('listing_report'))
#     return render_template('delete_listing.html', form=form,listing_id=listing_id)
#
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     form = signupForm(request.form)
#     if request.method == 'POST' and form.validate():
#         username = form.username.data.strip()
#         email = form.email.data.strip()
#         password = form.password.data.strip()
#         user = User(username=username, email=email, password=password)
#         msg = user.create_user()
#         if msg is None:
#             flash('Registration successful! Please log in.', 'success')
#             Email().send_email(email, "EcoThrift Registration", "Thank You for signing up at EcoThrift")
#             return redirect(url_for('login'))
#         else:
#             flash(msg)
#             return render_template('signup.html', form=form)
#
#     return render_template('signup.html', form=form)
#
# from flask import flash
#
# @app.route('/otp_route', methods=['GET', 'POST'])
# def otp_route():
#     form = OTPForm(request.form)
#     user_email = session.get('user_email')
#
#     if request.method == 'GET':
#         session['otp'] = Email().send_otp(user_email)
#         print(session['otp'])  # Debugging, remove in production
#
#     elif request.method == 'POST' and form.validate():
#         otp = form.otp.data.strip()
#         sent_otp = session.get('otp')
#         user = User(email=user_email)
#         verified = user.verify_otp(otp, sent_otp)
#         print(verified)  # Debugging
#
#         if verified:
#             flash("OTP verified successfully!", "success")
#             session.pop('user_email', None)
#             session['loggedin'] = True
#             session['user_id'] = user.user_id
#             session['admin'] = user.is_admin
#             session['username'] = user.username
#             session['profile_pic'] = user.profile_pic
#             return redirect(url_for('home'))
#         else:
#             flash("Incorrect OTP. Please try again.", "danger")
#             return redirect(url_for('otp_route'))
#
#     return render_template('otp.html', form=form)
#
# from flask import flash
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm(request.form)
#     if request.method == 'POST' and form.validate():
#         # Retrieve form data
#         credential = form.username_or_email.data.strip()
#         password = form.password.data.strip()
#         print(credential)
#         print(password)
#         user = User()
#         login_success, otp = user.login(credential, password)
#
#         if login_success:
#             session['user_email'] = user.email
#             if otp:
#                 return redirect(url_for('otp_route'))
#             else:  # No 2FA required
#                 user.get_user_by_email()
#                 session.pop('user_email', None)
#                 session['loggedin'] = True
#                 session['user_id'] = user.user_id
#                 session['admin'] = user.is_admin
#                 session['username'] = user.username
#                 session['profile_pic'] = user.profile_pic
#                 return redirect(url_for('home'))
#         else:
#             flash("Invalid username or password. Please try again.", "danger")
#             return redirect(url_for('login'))
#
#     return render_template('login.html', form=form)
#
#
# @app.route('/change_password', methods=['GET', 'POST'])
# def change_password():
#     form = PasswordForm(request.form)
#     if request.method == 'POST' and form.validate():
#         password = form.password.data
#         new_password = form.new_password.data
#         id = session['user_id']
#         user = User(id)
#         user.get_user_by_id()
#         if user.verify_password(password):
#             msg = User(user_id=id, password=new_password).edit_password()
#             print(msg)
#             Email().send_email(user.email, "Password Changed", "Your Password has been changed")
#             return redirect(url_for('change_password_with_email'))
#
#     return render_template('change_password.html', form=form)
#
# @app.route('/change_password_with_email', methods=['GET', 'POST'])
# def change_password_with_email():
#     form = RequestResetForm(request.form)
#     if request.method == "POST" and form.validate():
#         user = User(email=form.email_reset.data)
#         try:
#             user.get_user_by_email()
#             session['email'] = user.email
#             session['user_id'] = user.user_id
#             return redirect(url_for('password_reset_otp'))
#         except:
#             return redirect(url_for('change_password_with_email'))
#     return render_template("change_password_with_email.html", form=form)
#
# @app.route('/password_reset_otp', methods=['GET', 'POST'])
# def password_reset_otp():
#     form = OTPForm(request.form)
#     user_email = session['email']
#
#     if request.method == 'GET':
#         session['otp'] = Email().send_otp(user_email)
#         print(session['otp'])
#
#     elif request.method == 'POST' and form.validate():
#         otp = form.otp.data.strip()
#         sent_otp = session['otp']
#         user = User(email=user_email)
#         verified = user.verify_otp(otp, sent_otp)
#         print(verified)
#         if verified:
#             flash("OTP verified successfully!", "success")
#
#             return redirect(url_for('change_forgot_password'))
#         else:
#             return redirect(url_for('password_reset_otp'))
#
#     return render_template('password_reset_otp.html', form=form)
#
# @app.route('/change_forgot_password', methods=['GET', 'POST'])
# def change_forgot_password():
#     form = PasswordForm(request.form)
#     if request.method == 'POST':
#         new_password = form.new_password.data
#         id = session['user_id']
#         user = User(id)
#         user.get_user_by_id()
#
#         msg = User(user_id=id, password=new_password).edit_password()
#         print(msg)
#         return redirect(url_for('start'))
#
#     return render_template('change_forgot_password.html', form=form)
#
#
# @app.route('/user_listing_report')
# def listing_report():
#     df_listings = DBManager().get_table('listings')
#     user_id = session['user_id']
#
#     user_listings = df_listings[df_listings['user_id'] == user_id]
#     print(df_listings)
#     print(user_listings)
#     total_value = user_listings['price'].sum()
#
#     fig_price  = px.bar(user_listings, x='category', y='price', title='Category by Price')
#
#     category_count = user_listings['category'].value_counts().reset_index()
#     category_count.columns = ['category', 'count']
#     fig_count = px.bar(category_count, x='category', y='count', title='Category by Count')
#
#     fig_html = fig_price.to_html(full_html=False)
#
#     return render_template('/user_listing_report.html', user_listings=user_listings.to_dict(orient='records'), fig_html=fig_html, table_type = 'listings', total_value=round(total_value,2))
#
# @app.route('/user_listing_report/count')
# def listing_report_count():
#     df_listings = DBManager().get_table('listings')
#     user_id = session['user_id']
#
#     user_listings = df_listings[df_listings['user_id'] == user_id]
#     print(df_listings)
#     print(user_listings)
#     total_value = user_listings['price'].sum()
#
#     fig_price  = px.bar(user_listings, x='category', y='price', title='Category by Price')
#
#     category_count = user_listings['category'].value_counts().reset_index()
#     category_count.columns = ['category', 'count']
#     fig_count = px.bar(category_count, x='category', y='count', title='Category by Count')
#
#     fig_html = fig_price.to_html(full_html=False)
#     fig_html = fig_count.to_html(full_html=False)
#
#     return render_template('/user_listing_report.html', user_listings=user_listings.to_dict(orient='records'), fig_html=fig_html, table_type = 'listings', total_value=round(total_value,2))
#
#
# @app.route('/user_listing_report/categoryportion')
# def category_report():
#     df_listings = DBManager().get_table('listings')
#     user_id = session['user_id']
#     user_listings = df_listings[df_listings['user_id'] == user_id]
#     category_count = user_listings.groupby('category').size().reset_index(name='count')
#     total_value = user_listings['price'].sum()
#     fig = px.pie(category_count, names='category', values='count', title='Category by Count', color='category')
#     fig_html = fig.to_html(full_html=False)
#     return render_template('/user_listing_report.html', user_listings=user_listings.to_dict(orient='records'), fig_html=fig_html, table_type = 'categories',total_value=round(total_value,2))
#
#
# @app.route('/user_listing_report/salesperformance')
# def sales_report():
#     df_transactions = DBManager().get_table("transactions")
#     df_listings = DBManager().get_table("listings")
#     user_id = session['user_id']
#
#     df_transactions['transaction_date'] = pd.to_datetime(df_transactions['transaction_date'], errors='coerce')
#
#     df_transactions['year_month'] = df_transactions['transaction_date'].dt.strftime('%Y-%m')
#     print(df_transactions['year_month'].to_dict())
#
#     df_transactions_listings = df_transactions.merge(df_listings[['listing_id', 'user_id', 'title', 'category', 'price', 'is_sold']], on='listing_id', how='left')
#     print(df_transactions_listings)
#     df_transactions_listings = df_transactions_listings[df_transactions_listings['user_id'] == user_id]
#     df_transactions_listings['year_month'] = df_transactions_listings['transaction_date'].dt.strftime('%Y_%m')
#     df_transactions_listings['year_month'] = pd.to_datetime(df_transactions_listings['year_month'], format='%Y_%m')
#     monthly_sales = df_transactions_listings.groupby(df_transactions_listings['year_month'].dt.strftime('%Y_%m')).agg({'price': 'sum'}).reset_index()
#     monthly_sales['year_month'] = pd.to_datetime(monthly_sales['year_month'], format='%Y_%m')
#     full_months = pd.date_range(start='2024-01-01', end='2024-12-31', freq='MS').strftime("%Y_%m")
#     all_months_df = pd.DataFrame(full_months, columns=['year_month'])
#     all_months_df['year_month'] = pd.to_datetime(all_months_df['year_month'], format='%Y_%m')
#     all_months_df['month_name'] = all_months_df['year_month'].dt.strftime('%b')
#     df_merged = pd.merge(all_months_df, monthly_sales, on='year_month', how='left')
#     print(monthly_sales)
#     print(all_months_df)
#     print(df_merged)
#     print(df_transactions_listings)
#     print(user_id)
#     total_sales = df_merged['price'].sum()
#     print(total_sales)
#     fig = px.bar(df_merged , x='month_name', y='price', title='Sales Performance Over Time', text='price')
#     fig.update_traces(texttemplate='%{text:.2f}', textposition='inside')
#     fig.update_layout(xaxis_title='Month', yaxis_title='Total Sales')
#     fig_html = fig.to_html(full_html=False)
#
#     return render_template('/user_listing_report.html', transactions_listings=df_transactions_listings.to_dict(orient='records'), fig_html=fig_html, table_type = 'sales', total_sales=round(total_sales,2))       # user_listings=user_listings.to_dict(orient='records')
#
# @app.route('/admin_report')
# def admin_report():
#     df_listings = DBManager().get_table('listings')
#     df_users = DBManager().get_table('users')
#     df_listings = pd.merge(df_listings, df_users)
#     df_listings_categories = df_listings.groupby('category').size().reset_index(name='count')
#     print(df_listings.to_string())
#     total_value = round(df_listings['price'].sum(),2)
#     print(total_value.round(2))
#     fig = px.bar(df_listings_categories, x='category', y='count', title='Category by Count', color='count')
#     fig_html = fig.to_html(full_html=False)
#     return render_template('/admin_report.html', user_listings=df_listings.to_dict(orient='records'), fig_html=fig_html, table_type = 'listings', total_value=round(total_value,2))
#
#
# @app.route('/admin_report/category_portion')
# def admin_category_report():
#     df_listings = DBManager().get_table('listings')
#
#     category_price_sum = df_listings.groupby('category')['price'].sum().reset_index()
#     category_price_sum.columns = ['category', 'total_price']
#     total_price_all_categories = category_price_sum['total_price'].sum()
#     category_price_sum['percentage'] = ((category_price_sum['total_price'] / total_price_all_categories) * 100).round(2)
#     category_count = df_listings.groupby('category').size().reset_index(name='count')
#     category_price_sum = category_price_sum.merge(category_count, on='category')
#     print(df_listings)
#     total_value = round(df_listings['price'].sum(),2)
#     fig = px.pie(df_listings, names='category', values='price', title='Category by Count', color='category')
#     fig_html = fig.to_html(full_html=False)
#     return render_template('/admin_report.html', user_listings=category_price_sum.to_dict(orient='records'), fig_html=fig_html, table_type = 'category', total_value=round(total_value,2))
#
# @app.route('/admin_report/salesperformance')
# def admin_sales_report():
#     df_transactions = DBManager().get_table("transactions")
#     df_listings = DBManager().get_table("listings")
#
#     df_transactions['transaction_date'] = pd.to_datetime(df_transactions['transaction_date'], errors='coerce')
#     df_transactions['year_month'] = df_transactions['transaction_date'].dt.strftime('%Y-%m')
#     print(df_transactions['year_month'].to_dict())
#     df_transactions_listings = df_transactions.merge(df_listings[['listing_id', 'user_id', 'title', 'category', 'price', 'is_sold']], on='listing_id', how='left')
#     print(df_transactions_listings)
#     df_transactions_listings['year_month'] = df_transactions_listings['transaction_date'].dt.strftime('%Y_%m')
#     df_transactions_listings['year_month'] = pd.to_datetime(df_transactions_listings['year_month'], format='%Y_%m')
#     monthly_sales = df_transactions_listings.groupby(df_transactions_listings['year_month'].dt.strftime('%Y_%m')).agg({'price': 'sum'}).reset_index()
#     monthly_sales['year_month'] = pd.to_datetime(monthly_sales['year_month'], format='%Y_%m')
#     full_months = pd.date_range(start='2024-01-01', end='2024-12-31', freq='MS').strftime("%Y_%m")
#     all_months_df = pd.DataFrame(full_months, columns=['year_month'])
#     all_months_df['year_month'] = pd.to_datetime(all_months_df['year_month'], format='%Y_%m')
#     all_months_df['month_name'] = all_months_df['year_month'].dt.strftime('%b')
#     df_merged = pd.merge(all_months_df, monthly_sales, on='year_month', how='left')
#     print(monthly_sales)
#     print(all_months_df)
#     print(df_merged)
#     print(df_transactions_listings)
#     total_sales = round(df_transactions_listings['price'].sum(),2)
#     fig = px.bar(df_merged , x='month_name', y='price', title='Sales Performance Over Time', text='price')
#     fig.update_traces(texttemplate='%{text:.2f}', textposition='inside')
#     fig.update_layout(xaxis_title='Month', yaxis_title='Total Sales')
#     fig_html = fig.to_html(full_html=False)
#
#     return render_template('/admin_report.html', transactions_listings=df_transactions_listings.to_dict(orient='records'), fig_html=fig_html, table_type = 'sales', total_sales=round(total_sales,2))       # user_listings=user_listings.to_dict(orient='records')
#
#
# if __name__ == '__main__':
#     app.run(debug=True)