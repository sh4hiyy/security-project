from wtforms import Form, StringField, PasswordField, DecimalField, IntegerField, SelectField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp
from wtforms.validators import InputRequired, Length, Email, EqualTo

from wtforms.widgets import TextArea

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from flask_wtf.recaptcha import RecaptchaField

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    SelectField,
    DecimalField,
    TextAreaField
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
    NumberRange
)

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message="Current password is required"),
        Length(min=8, message="Password must be at least 8 characters")
    ])

    new_password = PasswordField('New Password', validators=[
        DataRequired(message="New password is required"),
        Length(min=8, message="Password must be at least 8 characters")
    ])

    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message="Please confirm your new password"),
        EqualTo('new_password', message="Passwords must match")
    ])

    submit = SubmitField('Change Password')

    def validate_new_password(self, field):
        """Custom validation for password complexity"""
        password = field.data
        # Check for at least one uppercase letter
        if not any(char.isupper() for char in password):
            raise ValidationError("Password must contain at least one uppercase letter")
        # Check for at least one lowercase letter
        if not any(char.islower() for char in password):
            raise ValidationError("Password must contain at least one lowercase letter")
        # Check for at least one digit
        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one number")
        # Check for at least one special character
        special_chars = "!@#$%^&*(),.?\":{}|<>"
        if not any(char in special_chars for char in password):
            raise ValidationError("Password must contain at least one special character")
class PasswordForm(Form):
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'Current Password'})
    new_password = PasswordField('New Password', validators=[DataRequired()], render_kw={'placeholder': 'New Password'})
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')], render_kw={'placeholder': 'Confirm New Password'})

class CreateListingForm(Form):
    title = StringField('Title', validators=[DataRequired()], render_kw={'placeholder': 'Title'})
    description = StringField('Description', validators=[DataRequired()], render_kw={'placeholder': 'Description'})

    # From your forms.py
    category = SelectField('Category', choices=[('blouse', 'Blouse'), ('jeans', 'Jeans'),
                                                ('outerwear', 'Outerwear'), ('dresses', 'Dresses'),
                                                ('sweaters', 'Sweaters'), ('others', 'Others')])
    
    price = DecimalField('Price', validators=[DataRequired()], render_kw={'placeholder': 'Price'})
    image_path = StringField('Image URL', validators=[DataRequired()], render_kw={'placeholder': 'Image URL'})  # Replace with appropriate field type if needed

class ProfileForm(Form):
    twofa = BooleanField('Enable 2-Factor Authentication')
    email = EmailField('Email', validators=[DataRequired()], render_kw={'placeholder': 'Email'})
    username = StringField('Username', validators=[DataRequired(),
                                                   Regexp(r'^[a-zA-Z0-9._]+$',message='Username must contain only letters, numbers, underscores, and dots')],
                           render_kw={'placeholder': 'Username'})
    name = StringField('Name', render_kw={'placeholder': 'Name'})
    phone_number = StringField('Phone Number', render_kw={'placeholder': 'Phone Number'})
    profile_pic_url = StringField('Profile Pic URL', validators=[Regexp(r'.*\.(jpg|png|jpeg)$', message='Invalid image URL')], render_kw={'placeholder': 'Profile Picture URL'})


class LoginForm(Form):
    username_or_email = StringField('Username or Email', validators=[DataRequired()], render_kw={'placeholder': 'Username or Email'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'Password'})

class OTPForm(Form):
    otp = StringField('OTP', render_kw={'placeholder': '6 Digit OTP'})

class RequestResetForm(Form):
    email_reset = EmailField('Email', validators=[DataRequired()], render_kw={'placeholder': 'Email'})

# class signupForm(Form):
#     email = EmailField('Email', validators=[DataRequired()], render_kw={'placeholder': 'Email'})
#     username = StringField('Username', validators=[DataRequired(),
#                                                    Regexp(r'^[a-zA-Z0-9._]+$', message='Username must contain only letters, numbers, underscores, and dots')],
#                            render_kw={'placeholder': 'Username'})
#     password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'Password'})
#     confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], render_kw={'placeholder': 'Confirm Password'})

class signupForm(FlaskForm):  # ✅ was probably "Form" before
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    submit = SubmitField('Sign Up')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email Address', validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address"),
        Length(max=100, message="Email cannot exceed 100 characters")
    ])

    # Optional: CAPTCHA field if you're implementing bot protection
    # captcha = RecaptchaField()

    submit = SubmitField('Send Reset Link')

    def validate_email(self, field):
        """Optional: Add custom validation to check if email exists in system"""
        from user import User  # Import here to avoid circular imports
        user = User(email=field.data)
        if not user.get_user_by_email():
            raise ValidationError("If this email exists in our system, a reset link will be sent")


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[
        DataRequired(message="New password is required"),
        Length(min=8, max=50, message="Password must be between 8-50 characters")
    ])

    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message="Please confirm your new password"),
        EqualTo('new_password', message="Passwords must match")
    ])

    submit = SubmitField('Reset Password')

    def validate_new_password(self, field):
        """Password complexity validation"""
        password = field.data
        errors = []

        # Check for at least one uppercase letter
        if not any(char.isupper() for char in password):
            errors.append("at least one uppercase letter")

        # Check for at least one lowercase letter
        if not any(char.islower() for char in password):
            errors.append("at least one lowercase letter")

        # Check for at least one digit
        if not any(char.isdigit() for char in password):
            errors.append("at least one number")

        # Check for at least one special character
        special_chars = "!@#$%^&*(),.?\":{}|<>"
        if not any(char in special_chars for char in password):
            errors.append("at least one special character")

        if errors:
            raise ValidationError(f"Password must contain: {', '.join(errors)}")