import os 
import uuid
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename
from models import CarListing, CarImage
from sqlalchemy import or_
from extensions import db

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_car_images(files, listing_id):
    saved = []
    upload_dir = current_app.config['UPLOAD_FOLDER']
    listing_dir = os.path.join(upload_dir, str(listing_id))
    os.makedirs(listing_dir, exist_ok=True)

    for i, file in enumerate(files):
        if not file or not file.filename or not allowed_file(file.filename):
            continue
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(listing_dir, filename)
        file.save(filepath)

        try:
            img = Image.open(filepath)
            img.thumbnail((1200, 900))
            img.save(filepath, quality = 85)
        
        except Exception:
            pass

        rel_path = f"uploads/cars/{listing_id}/{filename}"
        saved.append({'path': rel_path, 'is_main': i == 0, 'sort_order': i})
    return saved 

def delete_listing_images(listing_id):
    import shutil
    listing_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(listing_id))
    if os.path.exists(listing_dir):
        shutil.rmtree(listing_dir)

def build_car_query(args):
    q = CarListing.query.filter(CarListing.status.in_(['active', 'sold']))

    if args.get('keyword'):
        kw = f"%{args['keyword']}%"
        q = q.filter(or_(
            CarListing.title.ilike(kw),
            CarListing.brand.ilike(kw),
            CarListing.model.ilike(kw),
            CarListing.description.ilike(kw),
        ))
    
    if args.get('brand'):
        q = q.filter(CarListing.brand == args['brand'])
    if args.get('model'):
        q = q.filter(CarListing.model.ilike(f"%{args['model']}%"))
    if args.get('price_from'):
        q = q.filter(CarListing.price >= float(args['price_from']))
    if args.get('price_to'):
        q = q.filter(CarListing.price <= float(args['price_to']))
    if args.get('year_from'):
        q = q.filter(CarListing.year >= int(args['year_from']))
    if args.get('year_to'):
        q = q.filter(CarListing.year <= int(args['year_to']))
    if args.get('mileage_to'):
        q = q.filter(CarListing.mileage <= int(args['mileage_to']))
    if args.get('fuel'):
        q = q.filter(CarListing.fuel_type == args['fuel'])
    if args.get('transmission'):
        q = q.filter(CarListing.transmission == args['transmission'])
    if args.get('body_type'):
        q = q.filter(CarListing.body_type == args['body_type'])
    if args.get('city'):
        q = q.filter(CarListing.city == args['city'])
    if args.get('with_image') == '1':
        q = q.filter(CarListing.images.any())
    if args.get('featured') == '1':
        q = q.filter(CarListing.listing_type == 'featured')
    if args.get('registered') == '1':
        q = q.filter(CarListing.registration == 'Регистрирано')
    

    sort = args.get('sort', 'newest')
    type_order = db.case(
        (CarListing.listing_type == 'premium', 0),
        (CarListing.listing_type == 'featured', 1),
        else_=2
    )
    q = q.order_by(type_order)

    sort_map = {
        'newest': CarListing.created_at.desc(),
        'cheapest': CarListing.price.asc(),
        'expensive': CarListing.price.desc(),
        'mileage': CarListing.mileage.asc(),
        'year': CarListing.year.desc(),
    }

    q = q.order_by(sort_map.get(sort, CarListing.created_at.desc()))
    return q
