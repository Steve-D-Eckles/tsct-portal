import pytest
from flask import g, session
from portal.db import get_db

def test_assignments(client, auth):
    auth.teacher_login()

    # Test data assignment should appear in assignment list
    response = client.get('/teacher/assignments')
    assert b'Bigger Software' in response.data

    # Test assignment should be deleted if checked box is submitted
    response = client.post(
        '/teacher/assignments',
        data={'id': 2}
    )
    assert b'Bigger Software' not in response.data

    # Teachers should not be able to delete other teachers' assignments
    response = client.post(
        '/teacher/assignments',
        data={'id': 5}
    )
    assert b'Something went wrong.' in response.data

def test_edit_assignments(client, auth):
    auth.teacher_login()

    # On GET request, user should be redirected
    response = client.get('/teacher/assignments/edit')
    assert 'http://localhost/teacher/assignments' == response.headers['Location']

    # On POST request, user should see an edit page with forms pre-filled with
    # current data from database
    response = client.post(
        '/teacher/assignments/edit',
        data={'edit': 2}
    )
    assert b'value="Bigger' in response.data

    # Teachers should not be able to edit other teachers' assignments
    response = client.post(
        '/teacher/assignments/edit',
         data={'edit': 5}
    )
    assert 'http://localhost/teacher/assignments' == response.headers['Location']

def test_submit_assignments(client, auth, app):
    auth.teacher_login()

    # On GET request, user should be redirected
    response = client.get('/teacher/assignments/edit/submit')
    assert 'http://localhost/teacher/assignments' == response.headers['Location']

    # Client should be able to post updates to change database entry
    client.post(
        '/teacher/assignments/edit/submit',
        data={'name': 'Biggerest', 'description': 'And besterest', 'points': 500, 'submit': 2, 'assignment_type': 'Handout'}
    )
    # Data for the second assignment should now be updated
    response = client.get('/teacher/assignments')
    assert b'Biggerest' in response.data

    # Teachers should not be able to submit their edits to other teachers' assignments
    client.post(
        '/teacher/assignments/edit/submit',
        data={'name': 'Mondoest', 'description': 'And besterest', 'points': 500, 'submit': 5, 'assignment_type': 'Upload'}
    )
    response = client.get('/teacher/assignments')
    assert b'Something went wrong.' in response.data

#Test the grading of the Assignments
def test_grade_submission(client, auth,app):
    #Log in as teacher
    auth.teacher_login()
    #Response posts to this URL
    response = client.get('/teacher/assignments/grade/submission')
    # Assert the quest is redirected
    assert response.status_code == 302
    #Open up app-context
    with app.app_context():
        #Assert that posting to the client makes you get redirected
        assert client.get('/teacher/assignments/grade/submission', data={'grade' : 100, 'submission': '2', 'assignment_id': '1'}).status_code == 302
        #Send data to the form with grade as 100, for a student with id '2' for the 1st assignment of this session.
        client.post('/teacher/assignments/grade/submission', data={'grade' : 100, 'submission': '2', 'assignment_id': '1'})
        # With database Select the first grade in the database, and check if the grade is 100
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("""
                SELECT * FROM assignment_grades
                """)
                res = cur.fetchone()
                assert res[2] == '100'
        #Post to the same student and assignment in the same session as before
        client.post('/teacher/assignments/grade/submission', data={'grade' : 200, 'submission': '2', 'assignment_id': '1'})
        with get_db() as con:
            #Grab the grade for that assignment to see if it has been updated, if successful the grade should now be 200 instead of 100
            with con.cursor() as cur:
                cur.execute("""
                SELECT * FROM assignment_grades
                """)
                res = cur.fetchone()
                assert res[2] == '200'

def test_view_assignments(client,auth):
    auth.teacher_login()
    #Post to assignment views with the session id of 1, make sure the post request is successful
    assert client.post('/teacher/assignments/view', data={'view-grade': 1}).status_code == 200
    #Make sure that you're redirected to 'view-assignments.html'
    assert b'List of assignments' in client.post('/teacher/assignments/view', data={'view-grade': 1}).data
    #Send get request to page
    response = client.get('/teacher/assignments/view')
    #Make sure that you're redirected
    assert response.status_code == 302

    # Teachers should not be able to view a list of assignments for a session that
    # they do not own
    client.post(
        '/teacher/assignments/view',
        data={'view-grade': 3}
    )
    response = client.get('/teacher/courses')
    assert b'Something went wrong.' in response.data

def test_grade(client,auth,app):
    auth.teacher_login()
    #Open up app-context
    with app.app_context():
        #Send post request, requesting to see the assignment with id 1 assert the request is successful
        assert client.post('/teacher/assignments/grade', data={'assignment_id': 1}).status_code == 200
        #Assert that you're redirected to 'teacher-assignments.html'
        assert b'Kevstice--Lueklee' in client.post('/teacher/assignments/grade', data={'assignment_id': 1}).data
        #Send a get request to the page
        response = client.get('/teacher/assignments/grade')
        #Make sure you're redirected else where
        assert response.status_code == 302

        # Teachers should not be able to grade assignments that they don't own
        client.post(
            '/teacher/assignments/grade',
            data={'assignment_id': 5}
        )
        response = client.get('/teacher/courses')
        assert b'Something went wrong.' in response.data

def test_create_assignments(client, auth, app):
    auth.teacher_login()
    # On a GET request, user should see a form for creating new assignments
    response = client.get('/teacher/assignments/create')
    assert b'Assignment Creation' in response.data

    # On POST, user should be able to insert new assignments into the database
    client.post(
        '/teacher/assignments/create',
        data={'name': 'Wumbo Software', 'description': 'I wumbo, you wumbo, he, she, it... wumbo.',
              'points': 900, 'course': 1, 'assignment_type': 'Handout'}
    )
    with app.app_context():
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("SELECT * FROM assignments WHERE name ILIKE 'Wumbo%'")
                assert cur.fetchone()['name'] == 'Wumbo Software'

    # POST request data is validated and should not allow invalid data
    response = client.post(
        '/teacher/assignments/create',
        data={'name': 'Wumbo Software', 'description': 'I wumbo, you wumbo, he, she, it... wumbo.',
              'points': 900, 'course': 4, 'assignment_type': 'Handout'}
    )
    assert b'Something went wrong.' in response.data

def test_assign_work(client, auth):
    auth.teacher_login()

    # GET requests are redirected
    response = client.get('/teacher/assignments/assign')
    assert 'http://localhost/teacher/sessions' == response.headers['Location']

    # On POST, user should be able to see assignments that belong to posted course
    # id but only ones that have not been assigned already
    response = client.post(
        '/teacher/assignments/assign',
        data={'session_id': 1}
    )
    assert b'Mondo Software' in response.data
    assert b'Bigger Software' not in response.data

    # Teachers should not be able to try to assign work to sessions that aren't theirs
    response = client.post(
        '/teacher/assignments/assign',
        data={'session_id': 3}
    )
    assert 'http://localhost/teacher/sessions' == response.headers['Location']

def test_assign_submit(client, auth, app):
    auth.teacher_login()

    # GET requests are redirected
    response = client.get('/teacher/assignments/assign/submit')
    assert 'http://localhost/teacher/sessions' == response.headers['Location']

    # On POST, user should be able to insert assignments into the session_assignments
    # junction table with a due date
    response = client.post(
        '/teacher/assignments/assign/submit',
        data={'date': '2020-05-08', 'session_id': 1, 'assign_id': 4}
    )
    with app.app_context():
         with get_db() as con:
            with con.cursor() as cur:
                cur.execute("""
                    SELECT * FROM session_assignments where assignment_id = 4 AND session_id = 1   """)
                assert cur.fetchone() is not None

    # Teachers should not be able to submit assignments to sessions that they do not own
    # or assign assignments that they do not own to any session
    client.post(
        '/teacher/assignments/assign/submit',
        # The teacher does not own this session
        data={'date': '2020-05-08', 'session_id': 3, 'assign_id': 4}
    )
    response = client.get('/teacher/sessions')
    assert b'Something went wrong' in response.data

    client.post(
        '/teacher/assignments/assign/submit',
        # The teacher does not own this assignment
        data={'date': '2020-05-08', 'session_id': 1, 'assign_id': 5}
    )
    response = client.get('/teacher/sessions')
    assert b'Something went wrong' in response.data


def test_assignments_gradebook(client, auth):
    auth.teacher_login()
    response = client.get('/teacher/assignments/gradebook')
    assert 'http://localhost/teacher/home' == response.headers['Location']
    response = client.post('/teacher/assignments/gradebook', data={'assignment_id': 1})
    assert b'Big Software' in response.data
    assert b'<td>Lueklee, Kevstice</td>' in response.data

def test_grade_book(auth, client,app):
    auth.teacher_login()
    response = client.post('/teacher/assignments/grades/view-grades', data={'gradebook': 1})
    assert response.status_code == 200
    assert b'Kevstice, Lueklee' in response.data
    get = client.get('/teacher/assignments/grades/view-grades')
    assert get.status_code == 302
def test_personal_view(auth, client,app):
    auth.teacher_login()
    with app.app_context():
        response = client.post('/teacher/assignments/grades/all-grades', data={'student_id' : 2, 'session_id': 1})
        assert b'Kevstice, Lueklee' in response.data
        get = client.get('/teacher/assignments/grades/all-grades')
        assert get.status_code == 302
