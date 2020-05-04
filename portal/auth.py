import functools
import re

from flask import (
    Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from portal.db import get_db
from psycopg2 import sql

bp = Blueprint('auth', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        cur = db.cursor()
        error = None
        cur.execute(
            'SELECT * FROM users WHERE email = %s', (email,)
        )
        user = cur.fetchone()
        cur.close()

        if user is None:
            error = 'Incorrect username or password.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect username or password.'

        #If no error occurs then a user has logged in
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            #Return different views for a teacher vs student
            if user['role'] == 'teacher':
                return redirect(url_for('teacher.home'))
            else:
                return redirect(url_for('student.home'))

        flash(error)

    return render_template('layouts/index.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        cur = db.cursor()
        cur.execute(
            'SELECT * FROM users WHERE id = %s', (user_id,)
        )
        g.user = cur.fetchone()
        cur.close()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))

#add this to a bp to make login required before going to a view
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.index'))

        return view(**kwargs)

    return wrapped_view

#Add to bp to check admin role
def admin(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user['role'] != 'teacher':
            return redirect(url_for('auth.index'))

        return view(**kwargs)

    return wrapped_view

def validate(id, table):
    """Check that a user's attempted action is on a database item they have access to"""
    if table in ['sessions', 'assignments']:
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute(sql.SQL("""
                    SELECT * FROM courses
                    WHERE id IN (SELECT course_id FROM {} WHERE id = %s)
                    AND teacher_id = %s
                """).format(sql.Identifier(table)), (id, g.user['id']))
                result = cur.fetchone()
    elif table == 'courses':
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("""
                    SELECT * FROM courses
                    WHERE id = %s AND teacher_id = %s
                """, (id, g.user['id']))
                result = cur.fetchone()
    elif table == 'users':
        # This is used to confirm that users being added to the roster are students
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("""
                    SELECT * FROM users
                    WHERE id = %s AND role = 'student'
                """, (id,))
                result = cur.fetchone()
    else:
        result = None

    if not result:
        return False
    else:
        return True

def validate_text(input, max, min=1):
    """Check that text input is within reasonable length limits"""
    length = len(input)
    if length <= max and length >= min:
        return True
    else:
        return False

def validate_date(date):
    """Check that date input is in the expected format"""
    pattern = re.compile('([12]\\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01]))')
    if pattern.match(date):
        return True
    else:
        return False

def validate_number(num, max, min=1):
    """Check that numbers are within reasonable ranges"""
    try:
        num = int(num)
        if num <= max and num >= min:
            return True
        else:
            return False
    except ValueError:
        return False

def validate_student():
    """Return a list of valid session IDs for the logged in user"""
    with get_db() as con:
        with con.cursor() as cur:
            cur.execute("""
                SELECT s.id FROM sessions s JOIN roster r
                ON s.id = r.session_id
                WHERE r.student_id = %s
            """, (g.user['id'],))
            result = cur.fetchall()
            valid_sessions = []
            for row in result:
                valid_sessions.append(str(row['id']))

    return valid_sessions

def validate_roster():
    """Confirm a student is in roster"""
    with get_db() as con:
        with con.cursor() as cur:
            cur.execute("""
                SELECT student_id
                FROM roster
                WHERE student_id = %s
            """, (g.user['id'],))

            result = cur.fetchone()
    
    if not result:
        return False
    else:
        return True
