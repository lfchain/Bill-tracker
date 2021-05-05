from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user

from .. import bcrypt
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm, UpdateProfilePicForm
from ..models import User
from werkzeug.utils import secure_filename
import io, base64

users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("report.summary"))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        user.save()

        return redirect(url_for("users.login"))
    
    return render_template("register.html", title="Register", form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("report.summary"))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user)
            return redirect(url_for("users.account"))
        else:
            flash("Login failed. Check your username and/or password")
            return redirect(url_for("users.login"))
    
    return render_template("login.html", title="Login", form=form)

@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("report.home"))

@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    usernameForm = UpdateUsernameForm()
    profileForm = UpdateProfilePicForm()
    if usernameForm.validate_on_submit():
        try:
            usernameForm.validate_username(usernameForm.username)
            current_user.modify(username=usernameForm.username.data)
            current_user.save()
        except ValueError as e:
            return render_template("account.html", error_msg = str(e), username=current_user.username, 
            image=get_b64_img(current_user.profile_pic.read()), usernameForm=usernameForm, profileForm=profileForm)
    if profileForm.validate_on_submit():
        img = profileForm.picture.data
        filename = secure_filename(img.filename)
        content_type = f'images/{filename[-3:]}'

        if current_user.profile_pic.get() is None:
            current_user.profile_pic.put(img.stream, content_type=content_type)
        else:
            current_user.profile_pic.replace(img.stream, content_type=content_type)
        current_user.save()

    return render_template("account.html", 
                username=current_user.username, image=get_b64_img(current_user.profile_pic.read()),
                usernameForm=usernameForm, profileForm=profileForm)

def get_b64_img(image):       
    bytes_im = io.BytesIO(image)    
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image
