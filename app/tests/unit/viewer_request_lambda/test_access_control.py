import json
import pytest
import pdb

from src import viewer_request_lambda_function

def load_event(event_name):
    with open('./events/{}.json'.format(event_name)) as fd:
        text = fd.read()
    event = json.loads(text)
    return event

def test_access_denied_teacher_missing_acl():
    event = load_event('access_denied_teacher_missing_acl')
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['status'] == 403

def test_access_denied_student_missing_acl():
    event = load_event('access_denied_student_missing_acl')
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['status'] == 403

def test_access_denied_anonymous_missing_acl():
    event = load_event('access_denied_anonymous_missing_acl')
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['status'] == 403

def test_access_denied_teacher_not_in_acl():
    event = load_event('access_denied_teacher_not_in_acl')
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['status'] == 403

def test_access_denied_student_not_in_acl():
    event = load_event('access_denied_student_not_in_acl')
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['status'] == 403

def test_access_denied_anonymous_not_in_acl():
    event = load_event('access_denied_anonymous_not_in_acl')
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['status'] == 403

def test_access_granted_teacher():
    event = load_event('access_granted_teacher')
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['uri'] == '/some-ugly-path/another-ugly-path/biology/biology_book_3.txt'

def test_access_granted_student():
    event = load_event('access_granted_student')
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['uri'] == '/some-ugly-path/another-ugly-path/biology/biology_book_2.txt'

def test_access_granted_anonymous():
    event = load_event('access_granted_anonymous')
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['uri'] == '/some-ugly-path/another-ugly-path/biology/biology_book_1.txt'

