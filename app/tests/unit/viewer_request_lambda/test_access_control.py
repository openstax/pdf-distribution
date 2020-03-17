import json
import pytest
import pdb

from src import viewer_request_lambda_function

##
## These tests assume the following configuration
## is stored in the DynamoDb table used by the
## AWS Lambda function:
##   {
##     "access_map": {
##       "/some-ugly-path/another-ugly-path/biology/biology_book_1.txt": "teacher student anonymous -",
##       "/some-ugly-path/another-ugly-path/biology/biology_book_2.txt": "teacher student -",
##       "/some-ugly-path/another-ugly-path/biology/biology_book_3.txt": "teacher -",
##       "/some-ugly-path/another-ugly-path/biology/biology_book_4.txt": "-"
##     },
##     "config_id": "ver_1",
##     "uri_map": {
##       "/biology/vers/1": "/some-ugly-path/another-ugly-path/biology/biology_book_1.txt",
##       "/biology/vers/2": "/some-ugly-path/another-ugly-path/biology/biology_book_2.txt",
##       "/biology/vers/3": "/some-ugly-path/another-ugly-path/biology/biology_book_3.txt",
##       "/biology/vers/4": "/some-ugly-path/another-ugly-path/biology/biology_book_4.txt",
##       "/biology/vers/5": "/some-ugly-path/another-ugly-path/biology/biology_book_5.txt",
##       "/biology/vers/latest": "/biology/vers/2",
##       "/some-ugly-path/another-ugly-path/biology/biology_book_1.txt": "/some-ugly-path/another-ugly-path/biology/biology_book_1.txt"
##     }
##   }
##

def load_event(event_name, **data):
    from mako.template import Template

    with open('./events/{}.json'.format(event_name)) as fd:
        template_text = fd.read()

    data['cookies'] = ';'.join(data.get('cookies',[]) + ['random=junk;diversion=no'])

    event_text = Template(template_text).render(**data)
    event = json.loads(event_text)
    return event

def test_access_denied_teacher_missing_acl():
    event = load_event('access_tests_template',
        uri='/biology/vers/5',
        cookies=['user=teacher'],
    )
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['status'] == 403

def test_access_denied_student_missing_acl():
    event = load_event('access_tests_template',
        uri='/biology/vers/5',
        cookies=['user=student'],
    )
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['status'] == 403

def test_access_denied_anonymous_missing_acl():
    event = load_event('access_tests_template',
        uri='/biology/vers/5',
        cookies=[],
    )
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['status'] == 403

def test_access_denied_teacher_not_in_acl():
    event = load_event('access_tests_template',
        uri='/biology/vers/4',
        cookies=['user=teacher'],
    )
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['status'] == 403

def test_access_denied_student_not_in_acl():
    event = load_event('access_tests_template',
        uri='/biology/vers/3',
        cookies=['user=student'],
    )
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['status'] == 403

def test_access_denied_anonymous_not_in_acl():
    event = load_event('access_tests_template',
        uri='/biology/vers/2',
        cookies=[],
    )
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['status'] == 403

def test_access_granted_teacher():
    event = load_event('access_tests_template',
        uri='/biology/vers/3',
        cookies=['user=teacher'],
    )
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['uri'] == '/some-ugly-path/another-ugly-path/biology/biology_book_3.txt'

def test_access_granted_student():
    event = load_event('access_tests_template',
        uri='/biology/vers/2',
        cookies=['user=student'],
    )
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['uri'] == '/some-ugly-path/another-ugly-path/biology/biology_book_2.txt'

def test_access_granted_anonymous():
    event = load_event('access_tests_template',
        uri='/biology/vers/1',
        cookies=[],
    )
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['uri'] == '/some-ugly-path/another-ugly-path/biology/biology_book_1.txt'

