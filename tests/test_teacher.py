import pytest
from flask import g, session, url_for, request
from portal.db import get_db
def test_home(client, auth):
    # Attempt to visit page without logging in
    response = client.get('/teacher/home')
    # Non-authorized users should be redirected to login
    assert 'http://localhost/' == response.headers['Location']
    # Log in as a teacher
    auth.teacher_login()
    response = client.get('/teacher/home')
    # Logged-in teachers should not be redirected
    assert b'Manage Courses' in response.data

#def test_courses(client, auth):
 #auth.teacher_login()
 #response = client.get('/teacher/courses')
 # Check that mock course exists
 #assert b'Big Software Energy' in response.data
  # Attempt to delete mock course
 #response = client.post(
    #'/teacher/courses',
    #data={1:1}
 #)
 # Check that mock course no longer exists
#assert b'Big Software Energy' not in response.data

def test_creation(client, auth):
    auth.teacher_login()
    #Makes sure that you can go to Class Creation
    assert client.get('/teacher/courses/create').status_code == 200
    #Fills out the form in Class Creation
    response = client.post(
        '/teacher/courses/create',
        data={'code': 180, 'name': 'Software Project II', 'major': 'CSET',
        'description': 'A basic computer course'}
    )
    #Asserts that it's switched over to the Course Selection
    assert 'http://localhost/teacher/courses' == response.headers['Location']

def test_course_edit(client,auth,app):
    auth.teacher_login()
    #Get the elements of the edit page
    response = client.get('teacher/courses/1/edit')
    #Make sure the title 'Course-Edit' is inside.
    assert b'Course-Edit' in response.data
    #Using App context to execute commands, so that the database has a context to work off of.
    with app.app_context():
        #Post data to edit
        res = client.post(
            '/teacher/courses/1/edit',
            data={'code': 500, 'name': 'Ice-Cream', 'major': 'CSET',
            'description': 'A basic introduction to Ice-Cream'}
        )
        #Select data from DB
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("""
                SELECT * FROM courses
                WHERE id = %s
                """,
                (1,)
                )
                #Store all of it in results
                result = cur.fetchone()
                #Assert that the course name is the same as the course-name that was updated.
                assert result['course_name'] == 'Ice-Cream'
                #Assert that it returned to the courses page.
                assert res.headers['Location'] == 'http://localhost/teacher/courses'
#def test_sessions(client, auth):
#    auth.teacher_login()
#
#    # Teachers should see session from mock data on session page
#    response = client.get('/teacher/sessions')
#    assert b'180 A' in response.data
#
#    # Teachers should be able to delete sessions using a POST request
#    client.post(
#        '/teacher/sessions',
#        data={'id': 1}
#    )
#    response = client.get('/teacher/sessions')
#    # Session 1 should now be deleted and no longer shown
#    assert b'180 A' not in response.data


def test_make_session(client, auth):
    auth.teacher_login()
    response = client.get('teacher/sessions/create')
    assert 'http://localhost/teacher/home' == response.headers['Location']
    response = client.post(
        '/teacher/sessions/create',
        data={'session': 1}
    )
    assert b'Lueklee, Kevstice' in response.data

def test_session_add(client, auth):
    auth.teacher_login()

    # Get requests should be redirected away
    response = client.get('/teacher/sessions/add')
    assert 'http://localhost/teacher/sessions/create' == response.headers['Location']

    # Session creation must be underway to add students to the roster for that session
    # otherwise the user will simply be redirected away
    response = client.post(
        '/teacher/sessions/add',
        data={1:1}
    )
    assert 'http://localhost/teacher/sessions/create' == response.headers['Location']

    # Now we begin creating a session
    client.post(
        '/teacher/sessions/create',
        data={'session':1}
    )
    # Students may then be added with checkbox interface
    response = client.post(
        '/teacher/sessions/add',
        data={1:1}
    )
    # Confirm that session_add redirects to session page after running
    assert 'http://localhost/teacher/sessions/create' == response.headers['Location']
    response = client.get('/teacher/sessions/create')
    # Confirm that the roster is not empty
    assert b'Remove from Session' in response.data

def test_session_remove(client, auth):
    auth.teacher_login()

    # Get requests should be redirected away
    response = client.get('/teacher/sessions/remove')
    assert 'http://localhost/teacher/sessions/create' == response.headers['Location']

    # Session creation must be underway to remove students from the roster
    # otherwise the user will simply be redirected away
    response = client.post(
        '/teacher/sessions/remove',
        data={1:1}
    )
    assert 'http://localhost/teacher/sessions/create' == response.headers['Location']

    # Now we begin creating a session
    client.post(
        '/teacher/sessions/create',
        data={'session':1}
    )
    # Students need to be added before they can be removed
    client.post(
        '/teacher/sessions/add',
        data={1:1}
    )
    # The added student can be removed
    client.post(
        'teacher/sessions/remove',
        data={1:1}
    )

    response = client.get('/teacher/sessions/create')
    # In the test case, the roster for this session should now be empty
    assert b'Remove from Session' not in response.data

def test_session_submit(client, auth):
    auth.teacher_login()

    # If a user tries to use the GET method at the submit URL, they should be
    # redirected to the session creation interface
    response = client.get('/teacher/sessions/submit')
    assert 'http://localhost/teacher/sessions/create' == response.headers['Location']

    # Session creation must be underway to add students to the roster for it
    # otherwise the user will simply be redirected away
    response = client.post(
        '/teacher/sessions/submit',
        data={'session_name': 'A', 'meeting_days': 'MTWThF'}
    )
    assert 'http://localhost/teacher/sessions/create' == response.headers['Location']

    client.post(
        '/teacher/sessions/create',
        data={'session':1}
    )

    # If the user successfully submits the post request, they should be redirected
    # to the appropriate page
    response = client.post(
        '/teacher/sessions/submit',
        data={'session_name': 'A', 'meeting_days': 'MTWThF', 'meeting_place': 'Greenfield', 'meeting_time': '12:00-16:30'}
    )
    assert 'http://localhost/teacher/sessions' == response.headers['Location']

def test_session_cancel(client, auth):
    auth.teacher_login()

    # If the user tries to cancel a session when one does not exist, they will be
    # redirected away
    response = client.get('/teacher/sessions/cancel')
    assert 'http://localhost/teacher/home' == response.headers['Location']


    # The user begins creation of a session
    client.post(
        '/teacher/sessions/create',
        data={'session':1}
    )
    # The user cancels creation of a session
    response = client.get('/teacher/sessions/cancel')
    assert 'http://localhost/teacher/home' == response.headers['Location']
    # If the user now tries to view the session creation window, they will be
    # redirected to the teacher home
    response = client.get('/teacher/sessions/create')
    assert 'http://localhost/teacher/home' == response.headers['Location']

def test_session_edit(client, auth, app):
    auth.teacher_login()

    # If the user tries to visit the edit page without an edit in progress,
    # They should be redirected to the teacher home view
    response = client.get('/teacher/sessions/edit')
    assert 'http://localhost/teacher/home' == response.headers['Location']

    # The user should be able to begin a new editing session by posting a session code
    response = client.post(
        '/teacher/sessions/edit',
        data={'edit':1}
    )
    # They should then see the editing page
    assert b'Edit a Session' in response.data

def test_edit_mode(client, auth):
    auth.teacher_login()

    # A user begins editing a post
    client.post(
        '/teacher/sessions/edit',
        data={'edit':1}
    )

    # Adding and removing from the roster, canceling, and submitting
    # should behave differently when an edit is in progress

    response = client.get('/teacher/sessions/add')
    assert 'http://localhost/teacher/sessions/edit' == response.headers['Location']

    response = client.get('/teacher/sessions/remove')
    assert 'http://localhost/teacher/sessions/edit' == response.headers['Location']

    response = client.get('/teacher/sessions/submit')
    assert 'http://localhost/teacher/sessions/edit' == response.headers['Location']

    client.get('/teacher/sessions/cancel')
    response = client.get('/teacher/home')
    assert b'Session edit canceled' in response.data
