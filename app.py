from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from utils import generate_doc_number
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    unit = db.Column(db.String(20))
    min_qty = db.Column(db.Integer)
    stock_qty = db.Column(db.Integer, default=0)

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc_number = db.Column(db.String(50), unique=True)
    date = db.Column(db.Date, default=datetime.date.today)
    note = db.Column(db.String(200))

class IssueItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    issue = db.relationship('Issue', backref=db.backref('items', lazy=True))
    product = db.relationship('Product')

class AddStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc_number = db.Column(db.String(50), unique=True)
    date = db.Column(db.Date, default=datetime.date.today)
    note = db.Column(db.String(200))

class AddItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    add_id = db.Column(db.Integer, db.ForeignKey('add_stock.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    add = db.relationship('AddStock', backref=db.backref('items', lazy=True))
    product = db.relationship('Product')

with app.app_context():
    db.create_all()

@app.route('/')
def index(): return redirect(url_for('product'))

@app.route('/product', methods=['GET','POST'])
def product():
    if request.method=='POST':
        code=request.form['code']
        name=request.form['name']
        unit=request.form['unit']
        min_qty=int(request.form['min_qty'])
        new_product=Product(code=code,name=name,unit=unit,min_qty=min_qty)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('product'))
    products=Product.query.all()
    return render_template('product.html', products=products, active_page='product')

@app.route('/issue', methods=['GET','POST'])
def issue():
    products=Product.query.all()
    if request.method=='POST':
        product_id=int(request.form['product_id'])
        quantity=int(request.form['quantity'])
        note=request.form['note']
        
        product_to_update = Product.query.get(product_id)
        if product_to_update and product_to_update.stock_qty >= quantity:
            doc=generate_doc_number('ISS', Issue.query.count())
            new_issue=Issue(doc_number=doc,note=note)
            db.session.add(new_issue)
            db.session.commit()
            
            new_item=IssueItem(issue_id=new_issue.id,product_id=product_id,quantity=quantity)
            db.session.add(new_item)
            
            product_to_update.stock_qty -= quantity
            db.session.commit()
        else:
            # อาจจะเพิ่มการแจ้งเตือน (flash message) ว่าสินค้าไม่พอ
            pass
        return redirect(url_for('issue'))
    
    issue_items=IssueItem.query.order_by(IssueItem.id.desc()).limit(20).all()
    return render_template('issue.html', products=products, issue_items=issue_items, active_page='issue')

@app.route('/add_stock', methods=['GET','POST'])
def add_stock():
    products=Product.query.all()
    if request.method=='POST':
        product_id=int(request.form['product_id'])
        quantity=int(request.form['quantity'])
        note=request.form['note']
        doc=generate_doc_number('ADD', AddStock.query.count())
        new_add=AddStock(doc_number=doc,note=note)
        db.session.add(new_add)
        db.session.commit()
        new_item=AddItem(add_id=new_add.id,product_id=product_id,quantity=quantity)
        db.session.add(new_item)
        product=Product.query.get(product_id)
        product.stock_qty+=quantity
        db.session.commit()
        return redirect(url_for('add_stock'))
    
    add_items=AddItem.query.order_by(AddItem.id.desc()).limit(20).all()
    return render_template('add_stock.html', products=products, add_items=add_items, active_page='add_stock')

@app.route('/report_stock')
def report_stock():
    products=Product.query.order_by(Product.name).all()
    return render_template('report_stock.html', products=products, active_page='report_stock')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

