import pytest
from portal.db import get_db
from flask import g, session
from io import BytesIO

def test_file_upload(client, auth):
    # Attempt to visit page without logging in
    response = client.get('/student/assignments/upload')
    # Non-authorized users should be redirected to login
    assert 'http://localhost/' == response.headers['Location']
    # Log in as a student
    auth.student_login()

    response = client.post(
        '/student/assignments/upload',
        # Use StringIO to simulate file object
        data={'file': (BytesIO(b'my file contents'), 'test_file.txt'), 'assignment_id': 1}
        )
    #assert response.status_code == 200
    assert 'http://localhost/student/assignments' == response.headers['Location']
    assert b'File' in response.data

    

