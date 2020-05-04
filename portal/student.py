from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from portal.db import get_db

from portal.auth import login_required, validate_student

bp = Blueprint('student', __name__, url_prefix='/student')

@bp.route('/home')
@login_required
def home():
    with get_db() as con:
        with con.cursor() as cur:
            cur.execute("""
                SELECT c.course_name, c.course_code, s.session_name, s.meeting_days,
                s.meeting_time, s.meeting_place, s.id, r.student_id
                FROM courses c JOIN sessions s
                ON c.id = s.course_id
                JOIN roster r
                ON s.id = r.session_id
                WHERE r.student_id = %s
                """, (g.user['id'],))
            courses = cur.fetchall()
    return render_template('layouts/student/student-page.html', courses=courses)

@bp.route('/assignments', methods=('GET', 'POST'))
@login_required
def assignments():
    if request.method == 'POST':
        session_id = request.form['session_id']
        if session_id in validate_student():
            with get_db() as con:
                with con.cursor() as cur:
                    cur.execute("""
                        SELECT a.name, a.description, a.points, s.due_date, a.id, a.assignment_type, s.session_id FROM assignments a JOIN session_assignments s
                        ON a.id = s.assignment_id
                        WHERE session_id = %s
                    """, (session_id,))
                    assignments = cur.fetchall()
            return render_template('layouts/student/assignments/student-assignments.html', assignments=assignments)
        else:
            flash('Something went wrong.')

    return redirect(url_for('student.home'))

@bp.route('/grades', methods=('GET', 'POST'))
@login_required
def grades():
    if request.method == 'POST':
        session_id = request.form['session_id']
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("""
                    SELECT a.name, a.points, g.grades, g.owner_id FROM assignments a JOIN assignment_grades g
                    ON a.id = g.assigned_id
                    JOIN session_assignments s
                    ON s.assignment_id = a.id
                    WHERE session_id = %s
                """, (session_id,))
                assignments = cur.fetchall()

                cur.execute("""
                    SELECT s.session_name, c.course_name, c.course_code, c.major FROM sessions s JOIN courses c
                    ON s.course_id = c.id
                    WHERE s.id = %s
                """, (session_id,))
                session_info = cur.fetchone()

        return render_template('layouts/student/assignments/student-grade.html', assignments=assignments, session_info=session_info)
    return redirect(url_for('student.home'))
