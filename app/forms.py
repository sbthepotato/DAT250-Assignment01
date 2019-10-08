from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField, validators
from wtforms.fields.html5 import DateField
from flask_wtf.file import FileAllowed

# defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields

# https://wtforms.readthedocs.io/en/stable/validators.html
# https://flask.palletsprojects.com/en/1.1.x/patterns/wtforms/
# TODO: There was some important security feature that wtforms provides, but I don't remember what; implement it
# https://wtforms.readthedocs.io/en/stable/csrf.html


class LoginForm(FlaskForm):
    username = StringField('Username', [
            validators.InputRequired(message='Must input username'), 
            validators.Length(min=4, max=32, message='Username is between 4 and 32 characters')],
        render_kw={'placeholder': 'Username'}) 
    password = PasswordField('Password', [
            validators.InputRequired(message='Must input password'),
            validators.Length(min=6, max=32, message='Password is between 6 and 32 characters')],
        render_kw={'placeholder': 'Password'})
    remember_me = BooleanField('Remember me') 
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', [
        validators.InputRequired(message='Must input first name'),
        validators.Length(min=2, max=12, message='First name must be between 2 & 12 characters')], 
        render_kw={'placeholder': 'First Name'})
    last_name = StringField('Last Name', [
        validators.InputRequired(message='Must input last name'), 
        validators.Length(min=2, max=12, message='Last name must be between 2 & 12 characters')], 
        render_kw={'placeholder': 'Last Name'})
    username = StringField('Username', [
        validators.InputRequired(message='Must enter username'), 
        validators.Length(min=4, max=32, message='Username must be between 4 & 32 characters')], 
        render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', [
        validators.InputRequired(message='Must input password'), 
        validators.EqualTo('confirm_password', message='Passwords must match'), 
        validators.Length(min=6, max=32, message='Password must be between 6 & 32 characters')], 
        render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField('Confirm Password', [
        validators.InputRequired(message='Must input password again')], 
        render_kw={'placeholder': 'Confirm Password'})
    submit = SubmitField('Sign Up')


class IndexForm(FlaskForm):
    login = FormField(LoginForm)
    register = FormField(RegisterForm)


class PostForm(FlaskForm):
    content = TextAreaField('New Post', render_kw={'placeholder': 'What are you thinking about?'})
    image = FileField('Image',validators=[FileAllowed(['jpg','jpeg','gif','png'], message='Images only!')])
    submit = SubmitField('Post')


class CommentsForm(FlaskForm):
    comment = TextAreaField('New Comment', render_kw={'placeholder': 'What do you have to say?'})
    submit = SubmitField('Comment')


class FriendsForm(FlaskForm):
    username = StringField('Friend\'s username', render_kw={'placeholder': 'Username'})
    submit = SubmitField('Add Friend')


class ProfileForm(FlaskForm):
    education = StringField('Education', render_kw={'placeholder': 'Highest education'})
    employment = StringField('Employment', render_kw={'placeholder': 'Current employment'})
    music = StringField('Favorite song', render_kw={'placeholder': 'Favorite song'})
    movie = StringField('Favorite movie', render_kw={'placeholder': 'Favorite movie'})
    nationality = StringField('Nationality', render_kw={'placeholder': 'Your nationality'})
    birthday = DateField('Birthday')
    submit = SubmitField('Update Profile')
