from src import viewer_request_lambda_function

import json
from mako.template import Template
from unittest import mock

def load_event(event_name, **data):
    with open('./events/{}.json'.format(event_name)) as fd:
        template_text = fd.read()

    data['cookies'] = ';'.join(data.get('cookies',[]) + ['random=junk'])

    event_text = Template(template_text).render(**data)
    event = json.loads(event_text)
    return event

def test_no_diversion_cookie_sets_diversion_uri():
    with mock.patch('src.viewer_request_lambda_function.Config') as MockConfig:
        MockConfig.return_value.get_ugly_uri.return_value      = None
        MockConfig.return_value.access_is_allowed.return_value = False
        event = load_event('diversion_tests_template',
            uri='/some/pretty/uri',
            cookies=['user=some_user'],
        )
        context = ''
        request = viewer_request_lambda_function.lambda_handler(event, context)
        assert request['uri'] == '/diversion/diversion_page.html'

def test_no_diversion_cookie_sets_add_diversion_header():
    with mock.patch('src.viewer_request_lambda_function.Config') as MockConfig:
        MockConfig.return_value.get_ugly_uri.return_value      = None
        MockConfig.return_value.access_is_allowed.return_value = False
        event = load_event('diversion_tests_template',
            uri='/some/pretty/uri',
            cookies=['user=some_user'],
        )
        context = ''
        request = viewer_request_lambda_function.lambda_handler(event, context)
        assert 'openstax-add-diversion' in request['headers']

def test_diversion_cookie_continues_to_requested_uri():
    with mock.patch('src.viewer_request_lambda_function.Config') as MockConfig:
        MockConfig.return_value.get_ugly_uri.return_value      = '/ugly-path/ugly-file'
        MockConfig.return_value.access_is_allowed.return_value = True
        event = load_event('diversion_tests_template',
            uri='/some/pretty/uri',
            cookies=['user=some_user;diversion=no'],
        )
        context = ''
        request = viewer_request_lambda_function.lambda_handler(event, context)
        assert request['uri'] == '/ugly-path/ugly-file'

def test_diversion_cookie_does_not_set_add_diversion_header():
    with mock.patch('src.viewer_request_lambda_function.Config') as MockConfig:
        MockConfig.return_value.get_ugly_uri.return_value      = '/ugly-path/ugly-file'
        MockConfig.return_value.access_is_allowed.return_value = True
        event = load_event('diversion_tests_template',
            uri='/some/pretty/uri',
            cookies=['user=some_user;diversion=no'],
        )
        context = ''
        request = viewer_request_lambda_function.lambda_handler(event, context)
        assert 'openstax-add-diversion' not in request['headers']

