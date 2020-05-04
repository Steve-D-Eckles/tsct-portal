import pytest
from portal.db import get_db
from flask import g, session
from io import BytesIO

def test_file_upload(client, auth):
    """Upload a file"""
    # Attempt to visit page without logging in
    response = client.get('/student/assignments/upload')
    # Non-authorized users should be redirected to login
    assert 'http://localhost/' == response.headers['Location']
    # Log in as a student
    auth.student_login()

    # Attempt to submit a get request
    response = client.get('/student/assignments/upload')
    # Student should be redirected to assignments
    assert 'http://localhost/student/assignments'

    response = client.post(
        '/student/assignments/upload',
        # Use StringIO to simulate file object
        data={'file': (BytesIO(b'my file contents'), 'test_file.txt'), 'assignment_id': 1}
        )
    assert 'http://localhost/student/assignments' == response.headers['Location']
    response = client.get('/student/home')
    assert b'File Uploaded Succesfully!' in response.data
    
    # Try to upload the same file again
    response = client.post(
        '/student/assignments/upload',
        # Use StringIO to simulate file object
        data={'file': (BytesIO(b'my file contents'), 'test_file.txt'), 'assignment_id': 1}
        )

    assert 'http://localhost/student/assignments' == response.headers['Location']
    response = client.get('/student/home')
    # Assert that the file has already been turned in
    assert b'File already turned in.' in response.data
    
    # Try to upload a file without a name/no file was selected
    response = client.post(
        '/student/assignments/upload',
        # Use StringIO to simulate file object
        data={'file': (BytesIO(b'my file contents'), ''), 'assignment_id': 1}
        )

    assert 'http://localhost/student/assignments' == response.headers['Location']
    response = client.get('/student/home')
    # Assert that the file wasn't being uploaded
    assert b'No file was selected' in response.data

    # Try to upload a file that isn't an allowed type
    response = client.post(
        '/student/assignments/upload',
        # Use StringIO to simulate file object
        data={'file': (BytesIO(b'my file contents'), 'test_file.css'), 'assignment_id': 1}
        )
    # Should be redirected without anything being uploaded
    assert 'http://localhost/student/assignments' == response.headers['Location']
    response = client.get('/student/home')
    # The file would get this error message if it was an invalid type
    assert b'Not a file that can be turned in.' in response.data

def test_uploaded_file(client, auth):
    """View an uploaded assignment from a student"""
    # First log a student in and make an upload
    auth.student_login()
    response = client.post(
        '/student/assignments/upload',
        # Use StringIO to simulate file object
        data={'file': (BytesIO(b'my file contents'), 'test_file.txt'), 'assignment_id': 1}
        )
    auth.logout()

    # Log a teacher in and view the uploaded file
    auth.teacher_login()

    response = client.get('/teacher/assignments/uploads/9bd0ef51-2f7b-4c8d-b376-772bb138b3e0.txt')
    assert b'my file contents' in response.data
