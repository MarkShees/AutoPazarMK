from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app,abort
from flask_login import login_required, current_user
from extensions import db 
from models import CarListing, CarImage, Favorite
from forms import CarListingForm
from utils.helpers import save_car_images, delete_listing_images, build_car_query
from utils.decorators import owner_or_admin_required

cars_bp = Blueprint('cars', __name__, url_prefix='/cars')

@cars_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CarListingForm()
    if form.validate_on_submit():
        listing = CarListing(
            user_id = current_user.id,
            title = form.title.data,
            brand=form.brand.data,
            model = form.model.data,
            year=form.year.data,
            price = form.price.data,
            currency=form.currency.data,
            mileage=form.mileage.data,
            fuel_type=form.fuel_type.data,
            transmission=form.transmission.data,
            body_type=form.body_type.data,
            power_kw=form.power_kw.data,
            engine_size=form.engine_size.data,
            doors=form.doors.data,
            color=form.color.data,
            registration=form.registration.data,
            city=form.city.data,
            description=form.description.data,
            contact_phone=form.contact_phone.data,
            status='active',
        )
        db.session.add(listing)
        db.session.flush()

        files = request.files.getlist('images')
        if len(files) > 10:
            flash('Максимум 10 слики по оглас.', 'danger')
            return render_template('cars/form.html', form=form)
        
        for img_data in save_car_images(files, listing.id):
            db.session.add(CarImage(car_listing_id=listing.id, **img_data))

        db.session.commit()
        flash('Огласот е успешно додаден', 'success')
        return redirect(url_for('cars.detail', id=listing.id))
    return render_template('cars/form.html', form=form, title='Додади оглас')

@cars_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@owner_or_admin_required
def edit(id):
    listing = CarListing.query.get_or_404(id)
    form = CarListingForm(obj = listing)
    if form.validate_on_submit():
        form.populate_obj(listing)
        files = request.files.getlist('images')
        existing_count = listing.images.count()
        if existing_count + len([f for f in files if f.filename]) > 10:
            flash('Максимум 10 слики по оглас.', 'danger')
            return render_template('cars/form.html', form=form, listing=listing)
        
        for img_data in save_car_images(files, listing.id):
            db.session.add(CarImage(car_listing_id=listing.id, **img_data))

        db.session.commit()
        flash('Огласот е успешно изменет', 'success')
        return redirect(url_for('cars.detail', id=listing.id))
    return render_template('cars/form.html', form=form, listing=listing, title='Измени оглас')

@cars_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@owner_or_admin_required
def delete(id):
    listing = CarListing.query.get_or_404(id)
    delete_listing_images(listing.id)
    db.session.delete(listing)
    db.session.commit()
    flash('Огласот е избришан', 'success')
    return redirect(url_for('cars.my_cars'))

@cars_bp.route('/<int:id>/image/<int:image_id>/delete', methods=['POST'])
@login_required
@owner_or_admin_required
def delete_image(id, image_id):
    listing = CarListing.query.get_or_404(id)
    image = CarImage.query.filter_by(id=image_id, car_listing_id = id).first_or_404()

    import os
    from flask import current_app
    full_path = os.path.join(current_app.root_path, 'static', image.path)
    if os.path.exists(full_path):
        os.remove(full_path)
    db.session.delete(image)
    db.session.commit()
    flash('Сликата е избришана.', 'info')
    return redirect(url_for('cars.edit', id=id))

@cars_bp.route('/')
def list_cars():
    page = request.args.get('page', 1, type=int)
    query = build_car_query(request.args)
    pagination = query.paginate(page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    return render_template('cars/list.html', pagination=pagination, args=request.args)

@cars_bp.route('/<int:id>')
def detail(id):
    listing = CarListing.query.get_or_404(id)
    if listing.status == 'expired':
        abort(404)
    listing.views_count +=1
    db.session.commit()

    similar = CarListing.query.filter(
        CarListing.brand == listing.brand,
        CarListing.model == listing.model,
        CarListing.id != listing.id,
        CarListing.status == 'active'
    ).limit(4).all()

    is_favorited = False 
    if current_user.is_authenticated:
        is_favorited = Favorite.query.filter_by(
            user_id = current_user.id, car_listing_id = listing.id
        ).first() is not None 

    return render_template('cars/detail.html', listing=listing,
                           similar=similar, is_favorited=is_favorited)

@cars_bp.route('/<int:id>/show-phone', methods=['POST'])
def show_phone(id):
    listing = CarListing.query.get_or_404(id)
    listing.phone_views_count += 1
    db.session.commit()
    return jsonify({'phone': listing.contact_phone})

@cars_bp.route('/my-cars')
@login_required
def my_cars():
    listings = current_user.listings.order_by(CarListing.created_at.desc()).all()
    return render_template('cars/my_cars.html', listings=listings)

@cars_bp.route('/<int:id>/sold', methods=['POST'])
@login_required
@owner_or_admin_required
def mark_sold(id):
    listing = CarListing.query.get_or_404(id)
    listing.status = 'sold'
    db.session.commit()
    flash('Огласот е означен како продаден.', 'success')
    return redirect(url_for('cars.my_cars'))

@cars_bp.route('/<int:id>/renew', methods=['POST'])
@login_required
@owner_or_admin_required
def renew(id):
    listing = CarListing.query.get_or_404(id)
    listing.status = 'active'
    db.session.commit()
    flash('Огласот е обновен.', 'success')
    return redirect(url_for('cars.my_cars'))