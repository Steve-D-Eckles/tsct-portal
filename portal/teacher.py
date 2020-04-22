from flask import Flask, render_template, Blueprint, request, redirect, url_for, g, flash, session

from . import db

from portal.auth import login_required, admin

bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@bp.route('/home')
@login_required
@admin
def home():
    return render_template("teacher-home.html")

@bp.route('/courses', methods=('GET', 'POST'))
@login_required
@admin
def courses():
    if request.method == 'POST':
        with db.get_db() as con:
            with con.cursor() as cur:
                for item in request.form:
                    cur.execute("""
                        DELETE FROM roster
                        WHERE session_id in (SELECT id FROM sessions
                                             WHERE course_id = %s)
                    """, (request.form[item],))
                    cur.execute("""
                        DELETE FROM session_assignments
                        WHERE session_id in (SELECT id from sessions
                                             WHERE course_id = %s)
                    """, (request.form[item],))
                    cur.execute("""
                        DELETE FROM sessions
                        WHERE course_id = %s
                    """, (request.form[item],))
                    cur.execute("""
                        DELETE FROM assignments
                        WHERE course_id = %s
                    """, (request.form[item],))
                    cur.execute("""
                        DELETE FROM courses
                        WHERE id = %s
                    """, (request.form[item],))

    with db.get_db() as con:
        with con.cursor() as cur:
            cur.execute("""
                SELECT * FROM courses
                WHERE teacher_id = %s
            """, (g.user['id'],))
            courses = cur.fetchall()
    return render_template('class.html', courses=courses)

@bp.route('/courses/create', methods=('GET', 'POST'))
#Checks if the user is log in and if they are an admin role
@login_required
@admin
#Creates class
def create():
    if request.method == "POST":
        #Requests tags with 'code', 'name', 'major', and 'description' in form
        class_code = request.form['code']
        class_name = request.form['name']
        class_subject = request.form['major']
        class_description = request.form['description']
        #Inserts data into database
        with db.get_db() as con:
            with con.cursor() as cur:
                cur.execute("INSERT INTO courses(course_code, course_name, major, description, teacher_id ) VALUES(%s, %s, %s, %s, %s)",
                (class_code, class_name, class_subject, class_description, g.user['id'], )
                )
        #Selects all the data from courses and returns it to 'class.html'
        return redirect(url_for('teacher.courses'))
    return render_template('course-creation.html')

@bp.route('/sessions', methods=('GET', 'POST'))
@login_required
@admin
def sessions():
    if request.method == 'POST':
        with db.get_db() as con:
            with con.cursor() as cur:
                for item in request.form.getlist('id'):
                    cur.execute("""
                        DELETE FROM roster
                        WHERE session_id = %s
                    """, (item,))
                    cur.execute("""
                        DELETE FROM session_assignments
                        WHERE session_id = %s
                    """, (item,))
                    cur.execute("""
                        DELETE FROM sessions
                        WHERE id = %s
                    """, (item,))

    with db.get_db() as con:
        with con.cursor() as cur:
            cur.execute("""
                SELECT s.id, s.session_name, c.course_code, c.course_name, c.major
                FROM sessions s JOIN courses c
                ON s.course_id = c.id
                WHERE c.teacher_id = %s
            """, (g.user['id'],))
            sessions = cur.fetchall()
    return render_template('sessions.html', sessions=sessions)


@bp.route('/sessions/create', methods=('GET', 'POST'))
@login_required
@admin
def make_session():
    if request.method == "POST":
        course_id = request.form['session']
        session['course_id'] = course_id
        with db.get_db() as con:
            with con.cursor() as cur:
                cur.execute("""
                    INSERT INTO sessions (course_id)
                    VALUES (%s);
                    SELECT * FROM sessions
                    WHERE course_id = %s
                    ORDER BY id DESC
                """, (course_id, course_id))

                session_id = cur.fetchone().get('id')
                session['class_session'] = session_id

    if session.get('class_session'):
        with db.get_db() as con:
            with con.cursor() as cur:
                cur.execute("""
                    SELECT * FROM courses
                    WHERE id = %s
                """, (session['course_id'],))
                course = cur.fetchone()

                cur.execute("""
                    SELECT * FROM users
                    WHERE major = %s AND role = 'student' AND id NOT IN (SELECT student_id FROM roster WHERE session_id = %s)
                """, (course['major'], session['class_session']))

                students = cur.fetchall()

                cur.execute("""
                    SELECT u.last_name, u.first_name, u.id FROM roster r JOIN users u
                    ON r.student_id = u.id
                    WHERE r.session_id = %s
                """, (session['class_session'],))

                roster = cur.fetchall()

        return render_template('create-sessions.html', students=students, roster=roster)
    else:
        return redirect(url_for('teacher.home'))


@bp.route('/sessions/add', methods=('GET', 'POST'))
@login_required
@admin
def session_add():
    if request.method == 'POST':
        if session.get('class_session'):
            with db.get_db() as con:
                with con.cursor() as cur:
                    for id in request.form:
                        cur.execute("""
                            INSERT INTO roster (student_id, session_id)
                            VALUES (%s, %s)
                        """, (id, session['class_session']))
    if not session.get('edit'):
        return redirect(url_for('teacher.make_session'))
    else:
        return redirect(url_for('teacher.session_edit'))

@bp.route('/sessions/remove', methods=('GET', 'POST'))
@login_required
@admin
def session_remove():
    if request.method == 'POST':
        if session.get('class_session'):
            with db.get_db() as con:
                with con.cursor() as cur:
                    for item in request.form:
                        cur.execute("""
                            DELETE FROM roster
                            WHERE student_id = %s and session_id = %s
                        """, (request.form[item], session['class_session']))
    if not session.get('edit'):
        return redirect(url_for('teacher.make_session'))
    else:
        return redirect(url_for('teacher.session_edit'))

@bp.route('/sessions/submit', methods=('GET', 'POST'))
@login_required
@admin
def session_submit():
    if request.method == 'POST':
        if session.get('class_session'):
            session_name = request.form['session_name']
            meeting_days = request.form['meeting_days']
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("""
                        UPDATE sessions
                        SET session_name = %s, meeting_days = %s
                        WHERE id = %s
                    """, (session_name, meeting_days, session['class_session']))
            session.pop('class_session', None)
            session.pop('course_id', None)
            session.pop('edit', None)
            return redirect(url_for('teacher.sessions'))
    if not session.get('edit'):
        return redirect(url_for('teacher.make_session'))
    else:
        return redirect(url_for('teacher.session_edit'))

@bp.route('/sessions/cancel')
@login_required
@admin
def session_cancel():
    if session.get('class_session'):
        if not session.get('edit'):
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("""
                        DELETE FROM roster
                        WHERE session_id = %s
                    """, (session['class_session'],))
                    cur.execute("""
                        DELETE FROM sessions
                        WHERE id = %s
                    """, (session['class_session'],))
            session.pop('class_session', None)
            session.pop('course_id', None)
            error = "Session creation canceled"
        else:
            session.pop('class_session', None)
            session.pop('course_id', None)
            session.pop('edit', None)
            error = "Session edit canceled"
    else:
        error = "Not able to cancel session"

    flash(error)

    return redirect(url_for('teacher.home'))

@bp.route('/sessions/edit', methods=('GET', 'POST'))
@login_required
@admin
def session_edit():
    if request.method == "POST":
        session['class_session'] = request.form['edit']
        session['edit'] = True

    if session.get('edit'):
        with db.get_db() as con:
            with con.cursor() as cur:
                cur.execute("""
                    SELECT * FROM sessions
                    WHERE id = %s
                """, (session['class_session'],))
                session_info = cur.fetchone()

                cur.execute("""
                    SELECT last_name, first_name, id FROM users
                    WHERE role = 'student' AND major IN (SELECT major from courses
                        WHERE id IN (SELECT course_id FROM sessions where id = %s))
                    AND id NOT IN (SELECT student_id FROM roster WHERE session_id = %s)
                """, (session['class_session'], session['class_session']))
                students = cur.fetchall()

                cur.execute("""
                    SELECT u.last_name, u.first_name, u.id FROM roster r JOIN users u
                    ON r.student_id = u.id
                    WHERE r.session_id = %s
                """, (session['class_session'],))

                roster = cur.fetchall()

        return render_template('edit-sessions.html', session_info=session_info, students=students, roster=roster)

    return redirect(url_for('teacher.home'))
