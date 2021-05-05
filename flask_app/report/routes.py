from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from ..forms import SearchForm
from ..models import User
from ..utils import current_time

report = Blueprint('report', __name__)

@report.route("/", methods=['GET', 'POST'])
def home():
    return render_template("home.html")