from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user
from flask_login.utils import login_required
from pymongo.common import validate

from ..forms import ReceiptForm, SearchForm
from ..models import Receipt, User
from ..utils import current_time
from werkzeug.utils import secure_filename
import random
from datetime import datetime
import plotly.express as px
import io
from pathlib import Path

from ..utils import get_b64_img

report = Blueprint('report', __name__)

@report.route("/", methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
            return redirect(url_for("report.summary"))

    return render_template("home.html")

@report.route('/summary', methods=['GET', 'POST'])
@login_required
def summary():
    date_form = SearchForm()
    if date_form.validate_on_submit():
        date = date_form.date.data
        receipt_date = list(Receipt.objects(date=date.strftime("%Y-%m-%d"), user=current_user._get_current_object()))
        receipt_month = list(Receipt.objects(date__startswith=date.strftime("%Y-%m"), user=current_user._get_current_object()))
        receipt_year = list(Receipt.objects(date__startswith=date.strftime("%Y"), user=current_user._get_current_object()))
        
        receipt_date = [obj.to_mongo().to_dict() for obj in receipt_date]
        receipt_month = [obj.to_mongo().to_dict() for obj in receipt_month]
        receipt_year = [obj.to_mongo().to_dict() for obj in receipt_year]

        if len(receipt_date) == 0:
            return render_template("summary.html", date=date_form, message="Go upload some receipts!")
        else:
            fig1 = px.pie(receipt_date, values='cost', names='category')
            f1 = io.StringIO()
            fig1.write_html(f1, full_html=False)
        if len(receipt_month) == 0:
            return render_template("summary.html", date=date_form, message="Go upload some receipts!")
        else:
            fig2 = px.pie(receipt_month, values='cost', names='category')
            f2 = io.StringIO()
            fig2.write_html(f2, full_html=False)
        if len(receipt_year) == 0:
            return render_template("summary.html", date=date_form, message="Go upload some receipts!")
        else:
            fig3 = px.pie(receipt_year, values='cost', names='category')
            f3 = io.StringIO()
            fig3.write_html(f3, full_html=False)


        return render_template("summary.html", date=date_form, 
                plot1=f1.getvalue(),
                plot2=f2.getvalue(),
                plot3=f3.getvalue())
        
    return render_template("summary.html", date=date_form)

@report.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    receipt_form = ReceiptForm()
    if receipt_form.validate_on_submit():
        s = receipt_form.date.data.strftime('%Y-%m-%d') + receipt_form.description.data + receipt_form.category.data + f'{random.random()*1000000}'
        img = receipt_form.receipt.data
        receipt = Receipt(
            user = current_user._get_current_object(),
            date = receipt_form.date.data.strftime('%Y-%m-%d'),
            cost = receipt_form.amount.data,
            category = receipt_form.category.data,
            hash =abs(hash(s)) % (10 ** 8),
            description = receipt_form.description.data,
        )

        if img is not None:
            filename = secure_filename(img.filename)
            content_type = f'images/{filename[-3:]}'
            receipt.receipt_img.put(img.stream, content_type=content_type)
        else:
            path = str(Path(__file__).parent)
            with open(path+"/.."+url_for("static", filename='img/default_receipt.jpg'), 'rb') as img:
                receipt.receipt_img.put(img, content_type='image/jpg')

        receipt.save()
        return redirect(url_for("report.receipts", date=receipt.date))

    return render_template("upload.html", form=receipt_form)

@report.route('/receipt', methods=['GET','POST'])
@login_required
def receipt():
    date = SearchForm()
    if date.validate_on_submit():
        return redirect(url_for("report.receipts", date=date.date.data.strftime('%Y-%m-%d')))
    
    return render_template("receipt.html", form=date)


@report.route('/receipts/<date>', methods=['GET', 'POST'])
@login_required
def receipts(date):
    receipts = Receipt.objects(date=date, user=current_user._get_current_object())
    return render_template("receipts.html", receipts=receipts, get_b64_img = get_b64_img)

@report.route('/delete/<date>/<hash>', methods=['GET', 'POST'])
@login_required
def delete(date, hash):
    receipt = Receipt.objects(date=date, hash=hash, user=current_user._get_current_object()).first()
    date = receipt.date
    receipt.delete()
    return redirect(url_for("report.receipts", date=date))

@report.route('/edit/<date>/<hash>', methods=['GET', 'POST'])
@login_required
def edit(date, hash):
    receipt = Receipt.objects(date=date, hash=hash, user=current_user._get_current_object()).first()
    update_form = ReceiptForm(
        amount= receipt.cost,
        description = receipt.description,
        category = receipt.category,
        date= datetime.strptime(receipt.date, "%Y-%m-%d"))
    
    if update_form.validate_on_submit():
        img = update_form.receipt.data
        receipt.date= update_form.date.data.strftime('%Y-%m-%d')
        receipt.description=update_form.description.data
        receipt.cost=update_form.amount.data
        receipt.category=update_form.category.data

        if img is not None:
            filename = secure_filename(img.filename)
            content_type = f'images/{filename[-3:]}'
            receipt.receipt_img.replace(img.stream, content_type=content_type)

        receipt.save()
        return redirect(url_for("report.edit", date=receipt.date, hash=receipt.hash))

    return render_template("update.html", form=update_form, receipt=receipt, get_b64_img = get_b64_img)









