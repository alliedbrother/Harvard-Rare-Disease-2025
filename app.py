# app.py
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import json

# -------------------------------------------------------------------
# 1. Local imports from your other modules
# -------------------------------------------------------------------
from models import db, User, Diagnosis  # from models.py
from orphanet_parser import load_orphanet_data  # from orphanet_parser.py
from phrank_pipeline import PhrankPipeline     # from phrank_pipeline.py
from custom_hpo_extractor import run_custom_extractor  # from custom_hpo_extractor.py

# -------------------------------------------------------------------
# 2. Flask Application Configuration
# -------------------------------------------------------------------
app = Flask(__name__)

# For production, replace with a secure/random key
app.config['SECRET_KEY'] = 'REPLACE_ME_WITH_A_SECURE_RANDOM_KEY'

# Example using SQLite (in-file), adapt if you prefer Postgres/MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///genomic_diagnostics.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# -------------------------------------------------------------------
# 3. Logging Setup
# -------------------------------------------------------------------
if not os.path.exists('logs'):
    os.mkdir('logs')

log_file = 'logs/app.log'
handler = RotatingFileHandler(log_file, maxBytes=1_024*1_024, backupCount=3)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# -------------------------------------------------------------------
# 4. Initialize DB and Phrank at first request
# -------------------------------------------------------------------
@app.before_request
def create_tables_and_init():
    db.create_all()  # Creates tables if they don't exist
    app.logger.info("Database tables ensured.")

    # Load or parse Orphanet data
    disease_json = os.path.join("data", "disease_data.json")
    xml_file = os.path.join("data", "en_product6.xml")
    disease_data = load_orphanet_data(disease_json, xml_file)

    # Initialize Phrank pipeline
    hpo_file = os.path.join("data", "hp.obo")
    global phrank_pipeline
    phrank_pipeline = PhrankPipeline(hpo_file=hpo_file, disease_data=disease_data)
    app.logger.info("Phrank pipeline initialized with Orphanet data.")

# -------------------------------------------------------------------
# 5. Decorator for routes that require login
# -------------------------------------------------------------------
def login_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

# -------------------------------------------------------------------
# 6. Auth Routes (Register, Login, Logout)
# -------------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for('register'))

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken. Please choose another.", "warning")
            return redirect(url_for('register'))

        # Create new user with hashed password
        pw_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=pw_hash)
        db.session.add(new_user)
        db.session.commit()

        app.logger.info(f"New user registered: {username}")
        flash("Registration successful! You can log in now.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Logged in successfully!", "success")
            app.logger.info(f"User logged in: {username}")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "danger")
            app.logger.warning(f"Failed login attempt for {username}")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# -------------------------------------------------------------------
# 7. Main Page & Diagnosis
# -------------------------------------------------------------------
@app.route('/')
@login_required
def index():
    """Show a form to enter symptoms."""
    return render_template('index.html', username=session.get('username'))


@app.route('/diagnose', methods=['POST'])
@login_required
def diagnose():
    user_id = session.get('user_id')
    user_input = request.form.get('symptoms', '').strip()

    if not user_input:
        flash("Please enter your symptoms.", "warning")
        return redirect(url_for('index'))

    app.logger.info(f"User {user_id} diagnosing. Input: {user_input}")

    # 1. Extract HPO terms using your custom code
    try:
        patient_hpo_terms = run_custom_extractor(user_input)
    except Exception as e:
        app.logger.exception("Error in custom HPO extraction.")
        flash("Error extracting HPO terms. Please try again later.", "danger")
        return redirect(url_for('index'))

    if not patient_hpo_terms:
        flash("No HPO terms recognized. Try more detailed symptoms.", "warning")
        return redirect(url_for('index'))

    # 2. Rank diseases with Phrank
    try:
        results, is_rare = phrank_pipeline.rank_diseases(patient_hpo_terms, threshold=0.2)
    except Exception as e:
        app.logger.exception("Error in Phrank pipeline.")
        flash("Error performing phenotype matching. Please try again.", "danger")
        return redirect(url_for('index'))

    top_results = results[:10]  # show top 10
    results_json = json.dumps(top_results)

    # 3. Store in DB for user history
    diagnosis_entry = Diagnosis(
        user_id=user_id,
        input_text=user_input,
        hpo_terms=json.dumps(patient_hpo_terms),
        results=results_json,
        is_rare=is_rare
    )
    db.session.add(diagnosis_entry)
    db.session.commit()

    # 4. Render results page
    return render_template(
        'results.html',
        input_text=user_input,
        patient_hpo_terms=patient_hpo_terms,
        top_results=top_results,
        is_rare=is_rare
    )

# -------------------------------------------------------------------
# 8. History Route
# -------------------------------------------------------------------
@app.route('/history')
@login_required
def history():
    """Display all previous diagnoses for the logged-in user."""
    user_id = session.get('user_id')
    user_diagnoses = Diagnosis.query.filter_by(user_id=user_id).order_by(Diagnosis.created_at.desc()).all()
    return render_template('history.html', diagnoses=user_diagnoses)

# -------------------------------------------------------------------
# 9. Error Handlers
# -------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning(f"404 Error: {e}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    app.logger.exception(f"500 Error: {e}")
    return render_template('500.html'), 500

# -------------------------------------------------------------------
# 10. Main Entry Point
# -------------------------------------------------------------------
if __name__ == '__main__':
    # For production, use gunicorn or another WSGI server
    app.run(debug=False, host='0.0.0.0', port=8001)
