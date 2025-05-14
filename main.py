from flask import Flask, flash, render_template, request, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_bcrypt import Bcrypt
import time
from flask import Flask, request, session, jsonify
import subprocess
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import os


nfc_buffer = {"value": ""}
nfc_process = None


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ums.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = '65b0b774279de460f1cc5c92'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = 'filesystem'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
Session(app)

# Item Model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nfc_id = db.Column(db.String(255), nullable=False, unique=True)
    condition = db.Column(db.String(255), nullable=False)
    create_date = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'Item("{self.id}", "{self.nfc_id}", "{self.condition}", "{self.create_date}","{self.name}", "{self.status}", "{self.location}")'
    
class PendingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nfc_id = db.Column(db.String(255), nullable=False, unique=True)
    condition = db.Column(db.String(255), nullable=False)
    create_date = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<PendingItem {self.nfc_id}>"


# Admin Model
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'Admin("{self.username}", "{self.id}")'
    
class MovementLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nfc_id = db.Column(db.String(255), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.String(255), nullable=False)
    from_location = db.Column(db.String(255))

# Create tables and default admin
def create_tables():    
    with app.app_context():
        db.create_all()
        if not Admin.query.first():
            admin = Admin(username='Admin', password=bcrypt.generate_password_hash('admin123', 10))
            db.session.add(admin)
            db.session.commit()

create_tables()

# Main index
@app.route('/')
def index():
    return render_template('index.html', title="")

# Admin login
@app.route('/admin/', methods=["POST", "GET"])
def adminIndex():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "" or password == "":
            flash('Please fill all the fields', 'logindanger')
            return redirect('/admin/')
        else:
            admin = Admin.query.filter_by(username=username).first()
            if admin and bcrypt.check_password_hash(admin.password, password):
                session['admin_id'] = admin.id
                session['admin_name'] = admin.username
                flash('Login Successfully', 'loginsuccess')
                return redirect('/admin/dashboard')
            else:
                flash('Invalid Username or Password', 'logindanger')
                return redirect('/admin/')
    return render_template('admin/index.html', title="Admin Login")

# Admin Dashboard
# Route for dashboard and logs
@app.route('/admin/dashboard', methods=["GET"])
def admin_dashboard():
    if not session.get('admin_id'):
        return redirect('/admin/')

    # Get counts for total items, CTH101, CTh102, and pending items
    totalItems = Item.query.count()
    cth101Count = Item.query.filter_by(location="CTH101").count()
    cth102Count = Item.query.filter_by(location="CTH102").count()
    cth103Count = Item.query.filter_by(location="CTH103").count()
    cth104Count = Item.query.filter_by(location="CTH104").count()
    cth105Count = Item.query.filter_by(location="CTH105").count()
    cth106Count = Item.query.filter_by(location="CTH106").count()
    cth110Count = Item.query.filter_by(location="CTH110").count()
    cth111Count = Item.query.filter_by(location="CTH111").count()
    cth112Count = Item.query.filter_by(location="CTH112").count()
    cth113Count = Item.query.filter_by(location="CTH113").count()
    cth201Count = Item.query.filter_by(location="CTH201").count()
    cth202Count = Item.query.filter_by(location="CTH202").count()
    cth203Count = Item.query.filter_by(location="CTH203").count()
    cth204Count = Item.query.filter_by(location="CTH204").count()
    cth205Count = Item.query.filter_by(location="CTH205").count()
    cth206Count = Item.query.filter_by(location="CTH206").count()
    cth207Count = Item.query.filter_by(location="CTH207").count()
    cth208Count = Item.query.filter_by(location="CTH208").count()
    cth209Count = Item.query.filter_by(location="CTH209").count()
    cth210Count = Item.query.filter_by(location="CTH210").count()
    cth211Count = Item.query.filter_by(location="CTH211").count()
    cth212Count = Item.query.filter_by(location="CTH212").count()
    cth213Count = Item.query.filter_by(location="CTH213").count()
    cth214Count = Item.query.filter_by(location="CTH214").count()
    pendingCount = Item.query.filter_by(location="Pending").count()

    # Fetch recent movement logs

    logs = (
    db.session.query(MovementLog, Item.name)
    .outerjoin(Item, MovementLog.nfc_id == Item.nfc_id)
    .order_by(MovementLog.timestamp.desc())
    .limit(20)
    .all()
)

    return render_template(
        'admin/dashboard.html',
        title='Admin Dashboard',
        totalItems=totalItems,
        cth101Count=cth101Count,
        cth102Count=cth102Count,
        cth103Count=cth103Count,
        cth104Count=cth104Count,
        cth105Count=cth105Count,
        cth106Count=cth106Count,
        cth110Count=cth110Count,
        cth111Count=cth111Count,
        cth112Count=cth112Count,
        cth113Count=cth113Count,
        cth201Count=cth201Count,
        cth202Count=cth202Count,
        cth203Count=cth203Count,
        cth204Count=cth204Count,
        cth205Count=cth205Count,
        cth206Count=cth206Count,
        cth207Count=cth207Count,
        cth208Count=cth208Count,
        cth209Count=cth209Count,
        cth210Count=cth210Count,
        cth211Count=cth211Count,
        cth212Count=cth212Count,
        cth213Count=cth213Count,
        cth214Count=cth214Count,
        pendingCount=pendingCount,
        logs=logs
    )




@app.route('/admin/get-all-item', methods=["POST", "GET"])
def adminGetAllItem():
    if not session.get('admin_id'):
        return redirect('/admin/')


    search = request.form.get('search', "") if request.method == "POST" else ""
    room_filter = request.form.get('room_filter', "all")

    def build_search_filter():
        return or_(
            Item.nfc_id.ilike(f"%{search}%"),
            Item.condition.ilike(f"%{search}%"),
            Item.create_date.ilike(f"%{search}%"),
            Item.name.ilike(f"%{search}%"),
            Item.status.ilike(f"%{search}%"),
            Item.location.ilike(f"%{search}%"),
        )

    search_filter = build_search_filter()

    if room_filter == "CTH101":
        items101 = Item.query.filter(and_(Item.location == "CTH101", search_filter)).all()
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH102":
        items101 = []
        items102 = Item.query.filter(and_(Item.location == "CTH102", search_filter)).all()
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH103":
        items101 = []
        items102 = []
        items103 = Item.query.filter(and_(Item.location == "CTH103", search_filter)).all()
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH104":
        items101 = []
        items102 = []
        items103 = []
        items104 = Item.query.filter(and_(Item.location == "CTH104", search_filter)).all()
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH105":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = Item.query.filter(and_(Item.location == "CTH105", search_filter)).all()
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH106":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = Item.query.filter(and_(Item.location == "CTH106", search_filter)).all()
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH110":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = Item.query.filter(and_(Item.location == "CTH110", search_filter)).all()
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH111":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = Item.query.filter(and_(Item.location == "CTH111", search_filter)).all()
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH112":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = Item.query.filter(and_(Item.location == "CTH112", search_filter)).all()
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH113":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = Item.query.filter(and_(Item.location == "CTH113", search_filter)).all()
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH201":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = Item.query.filter(and_(Item.location == "CTH201", search_filter)).all()
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH202":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = Item.query.filter(and_(Item.location == "CTH202", search_filter)).all()
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH203":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = Item.query.filter(and_(Item.location == "CTH203", search_filter)).all()
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH204":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = Item.query.filter(and_(Item.location == "CTH204", search_filter)).all()
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH205":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = Item.query.filter(and_(Item.location == "CTH205", search_filter)).all()
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH206":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = Item.query.filter(and_(Item.location == "CTH206", search_filter)).all()
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH207":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = Item.query.filter(and_(Item.location == "CTH207", search_filter)).all()
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH208":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = Item.query.filter(and_(Item.location == "CTH208", search_filter)).all()
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH209":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = Item.query.filter(and_(Item.location == "CTH209", search_filter)).all()
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH210":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = Item.query.filter(and_(Item.location == "CTH210", search_filter)).all()
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH211":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = Item.query.filter(and_(Item.location == "CTH211", search_filter)).all()
        items212 = []
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH212":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = Item.query.filter(and_(Item.location == "CTH212", search_filter)).all()
        items213 = []
        items214 = []
        pending_items = []
    elif room_filter == "CTH213":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = Item.query.filter(and_(Item.location == "CTH213", search_filter)).all()
        items214 = []
        pending_items = []
    elif room_filter == "CTH214":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = Item.query.filter(and_(Item.location == "CTH214", search_filter)).all()
        pending_items = []
    elif room_filter == "Pending":
        items101 = []
        items102 = []
        items103 = []
        items104 = []
        items105 = []
        items106 = []
        items110 = []
        items111 = []
        items112 = []
        items113 = []
        items201 = []
        items202 = []
        items203 = []
        items204 = []
        items205 = []
        items206 = []
        items207 = []
        items208 = []
        items209 = []
        items210 = []
        items211 = []
        items212 = []
        items213 = []
        items214 = []
        pending_items = Item.query.filter(and_(Item.status == "Pending", search_filter)).all()
    else:
        items101 = Item.query.filter(and_(Item.location == "CTH101", search_filter)).all()
        items102 = Item.query.filter(and_(Item.location == "CTH102", search_filter)).all()
        items103 = Item.query.filter(and_(Item.location == "CTH103", search_filter)).all()
        items104 = Item.query.filter(and_(Item.location == "CTH104", search_filter)).all()
        items105 = Item.query.filter(and_(Item.location == "CTH105", search_filter)).all()
        items106 = Item.query.filter(and_(Item.location == "CTH106", search_filter)).all()
        items110 = Item.query.filter(and_(Item.location == "CTH110", search_filter)).all()
        items111 = Item.query.filter(and_(Item.location == "CTH111", search_filter)).all()
        items112 = Item.query.filter(and_(Item.location == "CTH112", search_filter)).all()
        items113 = Item.query.filter(and_(Item.location == "CTH113", search_filter)).all()
        items201 = Item.query.filter(and_(Item.location == "CTH201", search_filter)).all()
        items202 = Item.query.filter(and_(Item.location == "CTH202", search_filter)).all()
        items203 = Item.query.filter(and_(Item.location == "CTH203", search_filter)).all()
        items204 = Item.query.filter(and_(Item.location == "CTH204", search_filter)).all()
        items205 = Item.query.filter(and_(Item.location == "CTH205", search_filter)).all()
        items206 = Item.query.filter(and_(Item.location == "CTH206", search_filter)).all()
        items207 = Item.query.filter(and_(Item.location == "CTH207", search_filter)).all()
        items208 = Item.query.filter(and_(Item.location == "CTH208", search_filter)).all()
        items209 = Item.query.filter(and_(Item.location == "CTH209", search_filter)).all()
        items210 = Item.query.filter(and_(Item.location == "CTH210", search_filter)).all()
        items211 = Item.query.filter(and_(Item.location == "CTH211", search_filter)).all()
        items212 = Item.query.filter(and_(Item.location == "CTH212", search_filter)).all()
        items213 = Item.query.filter(and_(Item.location == "CTH213", search_filter)).all()
        items214 = Item.query.filter(and_(Item.location == "CTH214", search_filter)).all()
        pending_items = Item.query.filter(and_(Item.status == "Pending", search_filter)).all()
        items101 = Item.query.filter_by(location="CTH101").all()
        items102 = Item.query.filter_by(location="CTH102").all()
        items103 = Item.query.filter_by(location="CTH103").all()
        items104 = Item.query.filter_by(location="CTH104").all()
        items105 = Item.query.filter_by(location="CTH105").all()
        items106 = Item.query.filter_by(location="CTH106").all()
        items110 = Item.query.filter_by(location="CTH110").all()
        items111 = Item.query.filter_by(location="CTH111").all()
        items112 = Item.query.filter_by(location="CTH112").all()
        items113 = Item.query.filter_by(location="CTH113").all()
        items201 = Item.query.filter_by(location="CTH201").all()
        items202 = Item.query.filter_by(location="CTH202").all()
        items203 = Item.query.filter_by(location="CTH203").all()
        items204 = Item.query.filter_by(location="CTH204").all()
        items205 = Item.query.filter_by(location="CTH205").all()
        items206 = Item.query.filter_by(location="CTH206").all()
        items207 = Item.query.filter_by(location="CTH207").all()
        items208 = Item.query.filter_by(location="CTH208").all()
        items209 = Item.query.filter_by(location="CTH209").all()
        items210 = Item.query.filter_by(location="CTH210").all()
        items211 = Item.query.filter_by(location="CTH211").all()
        items212 = Item.query.filter_by(location="CTH212").all()
        items213 = Item.query.filter_by(location="CTH213").all()
        items214 = Item.query.filter_by(location="CTH214").all()
        pending_items = Item.query.filter_by(location="Pending").all()

    # Check pending notification
    notifications = []
    now = datetime.now()
    for item in pending_items:
        try:
            created = datetime.strptime(item.create_date, "%Y-%m-%dT%H:%M")
        except ValueError:
            created = datetime.strptime(item.create_date, "%Y-%m-%d %H:%M:%S")
        if now - created > timedelta(minutes=1):
            notifications.append(f"{item.name} (NFC ID: {item.nfc_id}) has been in pending for over 1 minute.")

    return render_template(
        'admin/all-item.html',
        title='All Items',
        items101=items101,
        items102=items102,
        items103=items103,
        items104=items104,
        items105=items105,
        items106=items106,
        items110=items110,
        items111=items111,
        items112=items112,
        items113=items113,
        items201=items201,
        items202=items202,
        items203=items203,
        items204=items204,
        items205=items205,
        items206=items206,
        items207=items207,
        items208=items208,
        items209=items209,
        items210=items210,
        items211=items211,
        items212=items212,
        items213=items213,
        items214=items214,
        pending_items=pending_items,
        notifications=notifications
    )
#Export Daily Logs to PDF
@app.route('/admin/export-daily-logs', methods=["GET"])
def export_daily_logs():
    if not session.get('admin_id'):
        return redirect('/admin/')

    # Get today's date
    today_date = datetime.now().strftime("%Y-%m-%d")
    # Fetch movement logs for today (filter logs by today's date)
    start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    logs = (
    db.session.query(MovementLog, Item.name)
    .outerjoin(Item, MovementLog.nfc_id == Item.nfc_id)
    .filter(
        MovementLog.timestamp >= start_of_day.strftime("%Y-%m-%d %H:%M:%S"),
        MovementLog.timestamp <= end_of_day.strftime("%Y-%m-%d %H:%M:%S")
    )
    .all()
)

    # Create a PDF in memory using BytesIO
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 750, f"Movement Logs for {today_date}")

    # Adding log entries
    pdf.setFont("Helvetica", 10)
    y_position = 730  # starting position for the logs

    # Column Headers
    pdf.drawString(30, y_position, "NFC ID")
    pdf.drawString(150, y_position, "Asset")
    pdf.drawString(250, y_position, "From")
    pdf.drawString(350, y_position, "Action")
    pdf.drawString(450, y_position, "Timestamp")

    # Adjust y-position after header
    y_position -= 20

    # Log entries
    for log, asset_name in logs:
        pdf.drawString(30, y_position, log.nfc_id)
        pdf.drawString(150, y_position, asset_name or "Unknown")
        pdf.drawString(250, y_position, log.from_location or "N/A")
        pdf.drawString(350, y_position, log.action)
        pdf.drawString(450, y_position, log.timestamp)

        y_position -= 20
        if y_position < 50:  # If space runs out, create a new page
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y_position = 750
            pdf.drawString(30, y_position, "NFC ID")
            pdf.drawString(150, y_position, "Asset")
            pdf.drawString(250, y_position, "From")
            pdf.drawString(350, y_position, "Action")
            pdf.drawString(450, y_position, "Timestamp")
            y_position -= 20

    # Finalize PDF
    pdf.save()

    # Go back to the beginning of the BytesIO buffer
    buffer.seek(0)

    # Return the PDF as a response
    return send_file(buffer, as_attachment=True, download_name=f"movement_logs_{today_date}.pdf", mimetype="application/pdf")

# Change admin register item
@app.route('/admin/admin-register-item', methods=["POST", "GET"])
def adminRegisterItem():
    if not session.get('admin_id'):
        return redirect('/admin/')

    # ✅ Clear scanned NFC ID when reloading the form page (fresh start)
    if request.method == 'GET':
        session['scanned_nfc'] = ""

    if request.method == 'POST':
        nfc_id = request.form.get('nfc_id')
        condition = request.form.get('condition')
        create_date = request.form.get('create_date')
        name = request.form.get('name')
        status = request.form.get('status')
        location = request.form.get('location')

        if not nfc_id or not condition or not create_date or not location:
            flash('Please fill all the fields', 'cleardanger')
            return redirect('/admin/admin-register-item')

        existing_item = Item.query.filter_by(nfc_id=nfc_id).first()
        if existing_item:
            flash('Item with this NFC ID already exists', 'clearwarning')
            session['scanned_nfc'] = ""
            nfc_buffer["nfc_id"] = ""
            return redirect('/admin/admin-register-item')

        item = Item(nfc_id=nfc_id, condition=condition, create_date=create_date, name=name, status=status, location=location)
        db.session.add(item)
        db.session.commit()

        # ✅ Clear after storing to prevent re-fill
        session['scanned_nfc'] = ""
        nfc_buffer["nfc_id"] = ""

        flash('Item registered successfully!', 'clearsuccess')
        session['scanned_nfc'] = ""
        return redirect('/admin/admin-register-item')

    return render_template('admin/admin-register-item.html', title='Register New Item')

@app.route('/admin/reset-nfc', methods=["POST"])
def reset_nfc():
    session['scanned_nfc'] = ""
    return jsonify({"status": "cleared"})




#update item
@app.route('/admin/update-item/<int:id>', methods=["GET", "POST"])
def updateItem(id):
    if not session.get('admin_id'):
        return redirect('/admin/')
    
    item = Item.query.get_or_404(id)

    if request.method == "POST":
        item.nfc_id = request.form.get("nfc_id")
        item.condition = request.form.get("condition")
        item.create_date = request.form.get("create_date")
        item.name = request.form.get("name")
        item.status = request.form.get("status")
        item.location = request.form.get("location")

        if not item.nfc_id or not item.condition or not item.create_date or not item.name or not item.status or not item.location:
            flash("Please  all fields", "updatedanger")
            return redirect(f"/admin/update-item/{id}")

        db.session.commit()
        flash("Item updated successfully!", "updatesuccess")
        return redirect("/admin/get-all-item")

    return render_template("admin/update-item.html", item=item, title="Update Item")

#delete item
@app.route('/admin/delete-item/<int:id>', methods=["GET"])
def deleteItem(id):
    if not session.get('admin_id'):
        return redirect('/admin/')
    
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash("Item deleted successfully!", "deletesuccess")
    return redirect("/admin/get-all-item")

# NFC stream endpoint for frontend

@app.route('/admin/start-nfc-reader', methods=['POST'])
def start_nfc_reader():
    try:
        session['scanned_nfc'] = ""  # ✅ Reset before scan
        subprocess.Popen(["python", "nfc/send_nfc_to_flask.py"])
        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/admin/nfc-stream')
def nfc_stream():
    def stream():
        last_sent = ""
        while True:
            if nfc_buffer["value"] != last_sent:
                last_sent = nfc_buffer["value"]
                yield f"data: {last_sent}\n\n"
            time.sleep(1)
    return Response(stream(), mimetype="text/event-stream")

@app.route('/admin/nfc-update', methods=["POST"])
def update_nfc_id():
    data = request.get_json()
    nfc_id = data.get("nfc_id")
    print("Received NFC ID in Flask:", nfc_id)

    nfc_buffer["nfc_id"] = nfc_id  # store in global buffer
    return jsonify({"status": "success", "nfc_id": nfc_id})
    
    # Save it to session or just use it for display
    session['scanned_nfc'] = nfc_id
    return jsonify({"status": "success", "nfc_id": nfc_id})

@app.route('/admin/stop-nfc-reader', methods=["POST"])
def stop_nfc_reader():
    session['stop_polling'] = True
    return jsonify({"status": "stopped"})


@app.route('/admin/get-latest-nfc')
def get_latest_nfc():
    return jsonify({"nfc_id": nfc_buffer.get("nfc_id", "")})



#register-nfc
@app.route('/admin/register-nfc/<int:id>', methods=["GET", "POST"])
def register_nfc(id):
    if not session.get('admin_id'):
        return redirect('/admin/')
    
    item = Item.query.get_or_404(id)

    if request.method == 'POST':
        scanned_nfc_id = request.form.get('nfc_id')
        item.nfc_id = scanned_nfc_id
        db.session.commit()
        flash('NFC ID registered successfully!', 'registersuccess')
        return redirect('/admin/get-all-item')

    return render_template("admin/nfc-register.html", item=item, title="Register NFC")

# IN Page - Move item to another room
@app.route('/admin/in', methods=["GET", "POST"])
def move_in():
    if not session.get('admin_id'):
        return redirect('/admin/')

    if request.method == "POST":
        scanned_nfc = request.form.get("nfc_id")
        new_location = request.form.get("new_location")
        item = Item.query.filter_by(nfc_id=scanned_nfc).first()

        if item:
            from_location = item.location
            item.location = new_location
            item.create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.session.commit()

            # Log movement
            log = MovementLog(
                nfc_id=scanned_nfc,
                action=f"Moved to {new_location}",
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                from_location=from_location
            )
            db.session.add(log)
            db.session.commit()

            flash(f"Item moved to {new_location} successfully!", "INsuccess")
        else:
            flash("NFC Tag not found in system!", "INdanger")

    return render_template("admin/in.html", title="Move Item (IN)")

# OUT Page - Move item to Pending
@app.route('/admin/out', methods=["GET", "POST"])
def out_item():
    if not session.get('admin_id'):
        return redirect('/admin/')
    
    if request.method == "POST":
        nfc_id = request.form.get("nfc_id")
        if not nfc_id:
            flash("Please scan an NFC tag.", "OUTdanger")
            return redirect("/admin/out")

        # Find item by NFC
        item = Item.query.filter_by(nfc_id=nfc_id).first()
        if not item:
            flash("Item not found with this NFC ID.", "OUTwarning")
            return redirect("/admin/out")
        
        from_location = item.location 
        
        # Move to Pending
        item.location = "Pending"
        item.create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.commit()

        # Log the movement
        log = MovementLog(
            nfc_id=nfc_id,
            action="Marked as Pending",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            from_location=from_location
        )
        db.session.add(log)
        db.session.commit()

        flash("Item moved to pending successfully!", "pendingsuccess")
        return redirect("/admin/get-all-item")

    return render_template("admin/out.html", title="OUT - Mark Pending")

@app.route('/admin/logs')
def view_logs():
    if not session.get('admin_id'):
        return redirect('/admin/')
    
    logs = MovementLog.query.order_by(MovementLog.timestamp.desc()).all()
    return render_template("admin/logs.html", title="Movement Logs", logs=logs)




# Admin logout
@app.route('/admin/logout')
def adminLogout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    return redirect('/')

if __name__ == "__main__":
app.run(debug=False, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
