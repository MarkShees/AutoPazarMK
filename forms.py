from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FloatField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
from models import User

class RegisterForm(FlaskForm):
    name = StringField('Име', validators=[DataRequired(message='Ова поле e задолжително.')])
    email = StringField('Email', validators=[DataRequired(), Email(message='Внесете валиден email.')])
    password = PasswordField('Лозинка', validators=[
         DataRequired(), Length(min=6, message='Лозинката мора да има најмалку 6 карактери.')
    ])
    confirm_password = PasswordField('Потврди лозинка', validators=[
         DataRequired(), EqualTo('password', message='Лозинките не ce совпаѓаат.')
    ])
    phone = StringField('Телефон')
    city = StringField('Град')
    submit = SubmitField('Регистрирај ce')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email адресата веќе e регистрирана.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Лозинка', validators=[DataRequired()])
    submit = SubmitField('Најави ce')

class ProfileForm(FlaskForm):
    name=StringField('Име', validators=[DataRequired(message='Ова поле e задолжително.')])
    phone = StringField('Телефон')
    city = StringField('Град')
    submit = SubmitField('Зачувај')


FUEL_CHOICES = [('Бензин','Бензин'),('Дизел','Дизел'),('Хибрид','Хибрид'),
                ('Електричен','Електричен'),('Плин','Плин')]
TRANS_CHOICES = [('Рачен','Рачен'),('Автоматски','Автоматски')]

BODY_CHOICES = [('Лимузина','Лимузина'),('Хечбек','Хечбек'),('Караван','Караван'),
                ('SUV','SUV'),('Купе','Купе'),('Кабриолет','Кабриолет'),('Комбе','Комбе')]
CITY_CHOICES = [('Скопје','Скопје'),('Битола','Битола'),('Охрид','Охрид'),
                ('Тетово','Тетово'),('Куманово','Куманово'),('Прилеп','Прилеп'),
                ('Струмица','Струмица'),('Велес','Велес'),('Штип','Штип'),
                ('Гостивар','Гостивар'),('Кичево','Кичево'),('Кавадарци','Кавадарци'),
                ('Струга','Струга'),('Кочани','Кочани'),
                ('Неготино','Неготино'),('Крива Паланка','Крива Паланка'),('Радовиш','Радовиш'),
                ('Пробиштип','Пробиштип'), ('Свети Николе','Свети Николе'), ('Виница','Виница'), ('Друго','Друго')]
CURRENCY_CHOICES = [('EUR','EUR'),('MKD','MKD')]

class CarListingForm(FlaskForm):
    title = StringField('Наслов на оглас',validators=[DataRequired(message='Ова поле е задолжително.')])
    brand = StringField('Марка', validators=[DataRequired(message='Ова поле е задолжително.')])
    model = StringField('Модел', validators=[DataRequired(message='Ова поле е задолжително.')])
    year = IntegerField('Година', validators=[
        DataRequired(), NumberRange(min=1980, max=2026, message='Внесете реална година.')
    ])
    price = FloatField('Цена', validators=[DataRequired(message='Внесете валидна цена.')])
    currency = SelectField('Валута', choices=CURRENCY_CHOICES, default='EUR')
    mileage = IntegerField('Километража', validators=[DataRequired()])
    fuel_type = SelectField('Гориво', choices=FUEL_CHOICES)
    transmission = SelectField('Менувач', choices=TRANS_CHOICES)
    body_type = SelectField('Каросерија', choices=BODY_CHOICES)
    power_kw = IntegerField('Моќност кW', validators=[DataRequired()])
    engine_size = IntegerField('Кубикажа', validators=[DataRequired()])
    doors = IntegerField('Број на врати', validators=[Optional()])
    color = StringField('Боја')
    registration = SelectField('Регистрација', choices=[('Регистрирано','Регистрирано'),('Нерегистрирано','Нерегистрирано')])
    city = SelectField('Град', choices=CITY_CHOICES)
    description = TextAreaField('Опис')
    contact_phone = StringField('Контакт Телефон', validators=[DataRequired()])
    images = MultipleFileField('Слики')
    submit = SubmitField('Зачувај')

class MessageForm(FlaskForm):
    body = TextAreaField('Порака', validators=[
        DataRequired(message='Ова поле е задолжително.')
    ])
    submit = SubmitField('Испрати')

class ReviewForm(FlaskForm):
    type = SelectField('Тип', choices=[
        ('seller_review', 'Оцени го продавачот'),
        ('buyer_review', 'Оцени го купувачот'),
    ])
    rating = SelectField('Оцена', choices=[
        (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')
    ], coerce=int, validators=[
        DataRequired(message='Ова поле е задолжително.')
    ])
    comment = TextAreaField('Коментар', validators=[
        DataRequired(message='Ова поле е задолжително.')
    ])
    submit = SubmitField('Остави рецензија')

class ReportForm(FlaskForm):
    reason = SelectField('Причина', choices=[
        ('Лажен оглас', 'Лажен оглас'),
        ('Погрешна цена', 'Погрешна цена'),
        ('Неправилни податоци', 'Неправилни податоци'),
        ('Недозволена содржина', 'Недозволена содржина'),
        ('Друго', 'Друго'),
    ], validators=[DataRequired(message='Ова поле е задолжително.')])
    comment = TextAreaField('Коментар')
    submit = SubmitField('Пријави оглас')
