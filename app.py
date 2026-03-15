import os
from datetime import date
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, jsonify)
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from models import db, User, Category, MenuItem, Reservation, ContactMessage


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'time-caffe-secret-key-2026')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timecaffe.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False
    app.jinja_env.auto_reload = True

    @app.after_request
    def set_utf8(response):
        if 'text/html' in response.content_type:
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response

    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'admin_login'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ── Public Routes ────────────────────────────────────────────────

    @app.route('/')
    def index():
        highlights = MenuItem.query.filter_by(available=True).limit(3).all()
        return render_template('index.html', highlights=highlights)

    @app.route('/meni')
    def menu():
        categories = Category.query.order_by(Category.sort_order).all()
        return render_template('menu.html', categories=categories)

    @app.route('/rezervacija', methods=['GET', 'POST'])
    def reservation():
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            new_res = Reservation(
                guest_name=data.get('guest_name', ''),
                phone=data.get('phone', ''),
                email=data.get('email', ''),
                date=data.get('date', ''),
                time=data.get('time', ''),
                guests=int(data.get('guests', 1)),
                note=data.get('note', ''),
                status='nova'
            )
            db.session.add(new_res)
            db.session.commit()
            if request.is_json:
                return jsonify({'success': True, 'message': 'Rezervacija uspešno poslata!'})
            flash('Rezervacija uspešno poslata!', 'success')
            return redirect(url_for('reservation'))
        return render_template('reservation.html')

    @app.route('/kontakt', methods=['GET', 'POST'])
    def contact():
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            msg = ContactMessage(
                name=data.get('name', ''),
                email=data.get('email', ''),
                message=data.get('message', '')
            )
            db.session.add(msg)
            db.session.commit()
            if request.is_json:
                return jsonify({'success': True, 'message': 'Poruka uspešno poslata!'})
            flash('Poruka uspešno poslata!', 'success')
            return redirect(url_for('contact'))
        return render_template('contact.html')

    @app.route('/lokacija')
    def location():
        return render_template('location.html')

    @app.route('/o-nama')
    def about():
        return render_template('about.html')

    # ── Admin Auth ───────────────────────────────────────────────────

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if current_user.is_authenticated:
            return redirect(url_for('admin_dashboard'))
        if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('admin_dashboard'))
            flash('Pogrešno korisničko ime ili lozinka.', 'error')
        return render_template('admin/login.html')

    @app.route('/admin/logout')
    @login_required
    def admin_logout():
        logout_user()
        return redirect(url_for('admin_login'))

    # ── Admin Dashboard ──────────────────────────────────────────────

    @app.route('/admin/')
    @login_required
    def admin_dashboard():
        today = date.today().isoformat()
        total_reservations = Reservation.query.count()
        today_reservations = Reservation.query.filter_by(date=today).count()
        new_reservations = Reservation.query.filter_by(status='nova').count()
        menu_count = MenuItem.query.count()
        recent = Reservation.query.order_by(Reservation.created_at.desc()).limit(10).all()
        return render_template('admin/dashboard.html',
                               total_reservations=total_reservations,
                               today_reservations=today_reservations,
                               new_reservations=new_reservations,
                               menu_count=menu_count,
                               recent=recent)

    @app.route('/admin/meni')
    @login_required
    def admin_menu():
        categories = Category.query.order_by(Category.sort_order).all()
        return render_template('admin/menu.html', categories=categories)

    @app.route('/admin/rezervacije')
    @login_required
    def admin_reservations():
        status_filter = request.args.get('status', '')
        date_filter = request.args.get('date', '')
        query = Reservation.query
        if status_filter:
            query = query.filter_by(status=status_filter)
        if date_filter:
            query = query.filter_by(date=date_filter)
        reservations = query.order_by(Reservation.created_at.desc()).all()
        return render_template('admin/reservations.html',
                               reservations=reservations,
                               status_filter=status_filter,
                               date_filter=date_filter)

    # ── Admin API (JSON) ─────────────────────────────────────────────

    @app.route('/admin/api/menu', methods=['POST'])
    @login_required
    def api_create_menu_item():
        data = request.get_json()
        item = MenuItem(
            category_id=int(data['category_id']),
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            available=data.get('available', True),
            sort_order=int(data.get('sort_order', 0))
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({'success': True, 'id': item.id})

    @app.route('/admin/api/menu/<int:item_id>', methods=['PUT'])
    @login_required
    def api_update_menu_item(item_id):
        item = MenuItem.query.get_or_404(item_id)
        data = request.get_json()
        item.name = data.get('name', item.name)
        item.description = data.get('description', item.description)
        item.price = float(data.get('price', item.price))
        item.available = data.get('available', item.available)
        item.sort_order = int(data.get('sort_order', item.sort_order))
        if 'category_id' in data:
            item.category_id = int(data['category_id'])
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/admin/api/menu/<int:item_id>', methods=['DELETE'])
    @login_required
    def api_delete_menu_item(item_id):
        item = MenuItem.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/admin/api/category', methods=['POST'])
    @login_required
    def api_create_category():
        data = request.get_json()
        max_order = db.session.query(db.func.max(Category.sort_order)).scalar() or 0
        cat = Category(name=data['name'], sort_order=max_order + 1)
        db.session.add(cat)
        db.session.commit()
        return jsonify({'success': True, 'id': cat.id})

    @app.route('/admin/api/category/<int:cat_id>', methods=['DELETE'])
    @login_required
    def api_delete_category(cat_id):
        cat = Category.query.get_or_404(cat_id)
        MenuItem.query.filter_by(category_id=cat_id).delete()
        db.session.delete(cat)
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/admin/api/reservation/<int:res_id>', methods=['PUT'])
    @login_required
    def api_update_reservation(res_id):
        res = Reservation.query.get_or_404(res_id)
        data = request.get_json()
        res.status = data.get('status', res.status)
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/admin/api/reservation/<int:res_id>', methods=['DELETE'])
    @login_required
    def api_delete_reservation(res_id):
        res = Reservation.query.get_or_404(res_id)
        db.session.delete(res)
        db.session.commit()
        return jsonify({'success': True})

    return app


if __name__ == '__main__':
    application = create_app()
    with application.app_context():
        db.create_all()
    application.run(debug=True, port=5000)
