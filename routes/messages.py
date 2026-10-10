from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from extensions import db
from models import Message, CarListing
from forms import MessageForm

messages_bp = Blueprint('messages', __name__)
@messages_bp.route('/messages')
@login_required
def inbox():
    messages = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.created_at.desc()).all()
    return render_template('messages/inbox.html', messages=messages)

@messages_bp.route('/messages/sent')
@login_required
def sent():
    messages = Message.query.filter_by(sender_id=current_user.id).order_by(Message.created_at.desc()).all()
    return render_template('messages/sent.html', messages=messages)


@messages_bp.route('/messages/<int:id>')
@login_required
def detail(id):
    message = Message.query.get_or_404(id)
    if message.sender_id != current_user.id and message.receiver_id != current_user.id:
        abort(403)
    if message.receiver_id == current_user.id and not message.read_at:
        from datetime import datetime
        message.read_at = datetime.utcnow()
        db.session.commit()
    return render_template('messages/detail.html', message=message)


@messages_bp.route('/messages/send/<int:car_id>', methods=['GET', 'POST'])
@login_required
def send(car_id):
    listing = CarListing.query.get_or_404(car_id)
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(sender_id=current_user.id, receiver_id=listing.user_id, car_listing_id=car_id, body=form.body.data)
        db.session.add(msg)
        db.session.commit()
        flash('Пораката е успешно испратена', 'success')
        return redirect(url_for('messages.inbox'))
    return render_template('messages/compose.html', form=form, listing=listing)
