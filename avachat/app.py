import os
import csv
import subprocess
import generate_api
import pandas as pd
from functools import wraps
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from datetime import datetime, timedelta
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField
from flask import Flask, render_template, redirect, url_for, flash, jsonify, request, session
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required

# Database connection
CSV_FILE = 'avachat.csv'

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)

plans = {

    'trial': {
        'trial_plan': {'name': 'Free Trial', 'price': 01.00, 'features': 'Trial features', 'duration': 10},
    },

    'monthly': {
        'basic': {'name': 'Basic ', 'price': 10.00, 'features': 'Basic features', 'duration': 30},
        'standard': {'name': 'Standard ', 'price': 20.00, 'features': 'Standard features', 'duration': 30},
        'premium': {'name': 'Premium ', 'price': 30.00, 'features': 'Premium features', 'duration': 30},
    },

    'yearly': {
        'basic': {'name': 'Basic ', 'price': 40.00, 'features': 'Basic features', 'duration': 365},
        'standard': {'name': 'Standard ', 'price': 50.00, 'features': 'Standard features', 'duration': 365},
        'premium': {'name': 'Premium ', 'price': 60.00, 'features': 'Premium features', 'duration': 365},
    },

}


def read_users_from_csv():
    users = []
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            users.append(row)
    return users


def get_user_by_email(email):
    users = read_users_from_csv()
    for user in users:
        if user['email'] == email:
            return user
    return None


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, email, password):
        self.id = email
        self.email = email
        self.password = password
        self.username = email.split('@')[0]

    @staticmethod
    def get(email):
        user_data = get_user_by_email(email)
        if user_data:
            return User(user_data['email'], user_data['password'])
        return None


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# Function to get the CSV file path based on the user's email
def get_user_csv_path(email):
    return f"user_qa/{email}.csv"


# Custom decorator to redirect logged-in users
def login_required_for_signup(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# Function to read chatbot responses from the CSV file
def get_chatbot_response(email, question):
    csv_path = get_user_csv_path(email)
    #print(csv_path)
    with open(csv_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Question'].lower() == question.lower():
                return row['Answer']
    return "Sorry, I don't understand that question."


# User registration form
class RegistrationForm(FlaskForm):
    f_name = StringField('First Name', validators=[DataRequired()])
    l_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    mobile = StringField('Mobile No.', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                         validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def search_email_by_column(self, email, csv_file, column_name):
        with open(csv_file, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if email == row[column_name]:
                    return True
        return False

    def append_row_to_csv(self, csv_file, row_values):
        fieldnames = ['f_name', 'l_name', 'email', 'dob', 'password', 'mobile', 'gender']
        # Assuming these are your column headers

        with open(csv_file, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Check if the file is empty, if so, write the header
            file.seek(0, 2)  # Go to the end of the file
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(row_values)

# User login form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

    def check_credentials(self, csv_file, email, password):
        with open(csv_file, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['email'] == email and bcrypt.check_password_hash(row['password'], password):
                    return True
        return False

class QuestionAnswer(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    answer = StringField('Answer', validators=[DataRequired()])
    submit = SubmitField('Add')


# Routes
@app.route('/')
def index():
    return render_template('base.html')


@app.route('/signup', methods=['GET', 'POST'])
@login_required_for_signup
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():

        f_name = form.f_name.data
        l_name = form.l_name.data
        email = form.email.data
        dob = form.dob.data
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        mobile = form.mobile.data
        gender = form.gender.data

        target_column = "email"
        found = form.search_email_by_column(email, CSV_FILE, target_column)

        if found:
            flash('An account with same E-mail already exists', 'Existing')
        else:
            new_row = {'f_name': f_name,
                       'l_name': l_name,
                       'email': email,
                       'dob': dob,
                       'password': hashed_password,
                       'mobile': mobile,
                       'gender': gender}

            # Append the new row to the CSV file
            form.append_row_to_csv(CSV_FILE, new_row)
            flash('Your account has been created! You are now able to log in.', 'success')

        return redirect(url_for('dashboard'))
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        login_email = form.email.data
        login_password = form.password.data
        valid = form.check_credentials(CSV_FILE, login_email, login_password)
        user_data = get_user_by_email(login_email)

        if valid and user_data:
            user = User(user_data['email'], user_data['password'])
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    email = current_user.email
    password = current_user.password
    return render_template('dashboard.html', password=password, email=email)


@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')


@app.route('/chat', methods=['POST', 'GET'])
@login_required
def chat():
    question = request.json.get('question')
    #print("question")
    if not question:
        return jsonify({'error': 'No question provided.'}), 400

    email = current_user.email
    response = get_chatbot_response(email, question)

    return jsonify({'response': response})


@app.route('/add_questions', methods=['GET', 'POST'])
@login_required
def add_questions():
    form = QuestionAnswer()
    email = current_user.email
    if form.validate_on_submit():
        question = form.question.data
        answer = form.answer.data

        data = [
            {"Question": question,
             "Answer": answer}
        ]

        # Create a CSV writer
        foldername = "user_qa"
        filename = foldername + "/" + email + '.csv'

        # Check if the folder already exists
        if not os.path.exists(foldername):
            os.makedirs(foldername)  # If not make one
            # Check if the file already exists
            if not os.path.exists(filename):
                # If the file doesn't exist, create a new one with the header row
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=["Question", "Answer"])
                    writer.writeheader()

                # Now append the data rows
                with open(filename, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=["Question", "Answer"])
                    writer.writerows(data)
                return redirect(url_for('add_questions'))
            else:
                # If the folder and file already exists, append the data rows
                with open(filename, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=["Question", "Answer"])
                    writer.writerows(data)
                return redirect(url_for('add_questions'))
        else:
            if not os.path.exists(filename):
                # If the file doesn't exist, create a new one with the header row
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=["Question", "Answer"])
                    writer.writeheader()

                # Now append the data rows
                with open(filename, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=["Question", "Answer"])
                    writer.writerows(data)
                return redirect(url_for('add_questions'))
            else:
                # If the file already exists, append the data rows
                with open(filename, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=["Question", "Answer"])
                    writer.writerows(data)
                return redirect(url_for('add_questions'))

    return render_template('question_answers.html', form=form)


@app.route('/payment_page', methods=['GET', 'POST'])
@login_required
def payment_page():
    #print("Inside payment")
    return render_template('payment_page.html', plans=plans)


@app.route('/subscribe', methods=['GET', 'POST'])
@login_required
def subscribe():
    print("Inside Subscribe")
    selected_plan = request.form.get('plan')
    if selected_plan == 'trial':
        session['subscription'] = {
            'start_date': datetime.now(),
            'duration': int(request.form.get('duration')),
        }
        # Print the subscription information for debugging purposes
        app.logger.info(f"Subscribed to {plans['trial']['trial_plan']['name']} - Plan: {selected_plan}")

        return jsonify({'success': True, 'message': f'Subscribed to {plans["trial"]["trial_plan"]["name"]}!'})

    elif selected_plan in [plan_key for period_plans in plans.values() for plan_key in period_plans]:
        session['subscription'] = {
            'start_date': datetime.now(),
            'duration': plans[selected_plan]['duration'],
        }
        # Print the subscription information for debugging purposes
        app.logger.info(f"Subscribed to {plans[selected_plan]['basic']['name']} - Plan: {selected_plan}")

        return jsonify({'success': True, 'message': f'Subscribed to {plans[selected_plan]["basic"]["name"]}!'})
    else:
        return jsonify({'success': False, 'message': 'Invalid plan selected!'})


@app.route('/protected_resource', methods=['GET', 'POST'])
@login_required
def protected_resource():
    #print("Inside Protected")
    if 'subscription' in session:
        start_date = session['subscription']['start_date']
        duration = timedelta(days=session['subscription']['duration'])
        expiration_date = start_date + duration

        if datetime.now() <= expiration_date:
            return render_template('protected_resource.html')
        else:
            # Redirect to a page indicating the subscription has expired
            return render_template('subscription_expired.html')
    else:
        # Redirect to a page indicating the user needs to subscribe
        return redirect(url_for('payment_page'))


@app.route('/execute_python_script', methods=['GET', 'POST'])
@login_required
def execute_python_script():
    #print("Inside execute_python_script")
    # Get the payer's name from the request data
    payer_email = current_user.email
    #print(payer_email)

    payer_plan = request.json.get('payer_plan')
    print(payer_plan)

    #update_date = subprocess.run(['python', 'update_sql_database.py', payer_email, payer_plan], capture_output=True, text=False)
    df = pd.read_csv(CSV_FILE)
    # Check if the email exists in the DataFrame

    if payer_email in df['email'].values:
        today = datetime.today().date()

        # Update the 'plan' column to 'Free' for the given email
        df.loc[df['email'] == payer_email, 'plan'] = payer_plan

        # Update the 'start_date' column to the purchase date
        df.loc[df['email'] == payer_email, 'start_date'] = today

        # Update the 'end_date' column as per the purchased plan
        if 'trial_trial_plan' == payer_plan:
            after_10_days = today + timedelta(days=10)
            df.loc[df['email'] == payer_email, 'end_date'] = after_10_days
        elif 'monthly_basic' == payer_plan or 'monthly_standard' == payer_plan or 'monthly_premium' == payer_plan:
            after_30_days = today + timedelta(days=30)
            df.loc[df['email'] == payer_email, 'end_date'] = after_30_days
        elif 'yearly_basic' == payer_plan or 'yearly_standard' == payer_plan or 'yearly_premium' == payer_plan:
            after_365_days = today + timedelta(days=365)
            df.loc[df['email'] == payer_email, 'end_date'] = after_365_days
        else:
            print("None matching case for: ",payer_plan)

        # Save the updated DataFrame back to the CSV file
        df.to_csv(CSV_FILE, index=False)

    #generate_api.call_api(payer_email)

    result = subprocess.run(['python', 'generate_file_user.py', payer_email], capture_output=True, text=True)
    # print(result)

    # Return the output of the Python script as a JSON response
    response = {'output': result.stdout, 'error': result.stderr}
    # print(response)

    # return render_template('success_link.html', user_name=response['output'])
    return jsonify(response)


@app.route('/success_link', methods=['GET', 'POST'])
@login_required
def success_link():

    def get_plan_length(csv_file, email):
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row
            for row in reader:
                if row[2] == email:
                    return len(row[7])
        return None  # Return None if email not found

    current_user_email = current_user.email
    #print(current_user_email)
    has_a_plan = get_plan_length(CSV_FILE, current_user_email)
    #print(has_a_plan)
    if has_a_plan:
        return render_template('success_link2.html')
    else:
        return redirect(url_for('payment_page'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
