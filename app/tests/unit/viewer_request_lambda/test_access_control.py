from src import viewer_request_lambda_function

import json
from mako.template import Template
from unittest import mock

def load_event(event_name, **data):
    with open('./events/{}.json'.format(event_name)) as fd:
        template_text = fd.read()

    data['cookies'] = ';'.join(data.get('cookies',[]) + ['random=junk;diversion=no'])

    event_text = Template(template_text).render(**data)
    event = json.loads(event_text)
    return event

def test_missing_ugly_uri_gives_response_with_status_404():
    with mock.patch('src.viewer_request_lambda_function.Config') as MockConfig:
        MockConfig.return_value.get_ugly_uri.return_value = None
        MockConfig.return_value.access_is_allowed.return_value = True
        event = load_event('access_tests_template',
            uri='/some/pretty/uri',
            cookies=['user=some_user'],
        )
        context = ''
        response = viewer_request_lambda_function.lambda_handler(event, context)
        assert response['status'] == 404

def test_access_denied_gives_response_with_status_403():
    with mock.patch('src.viewer_request_lambda_function.Config') as MockConfig:
        MockConfig.return_value.get_ugly_uri.return_value = '/some/ugly/uri'
        MockConfig.return_value.access_is_allowed.return_value = False
        event = load_event('access_tests_template',
            uri='/some/pretty/uri',
            cookies=['user=some_user'],
        )
        context = ''
        response = viewer_request_lambda_function.lambda_handler(event, context)
        assert response['status'] == 403

def test_access_allowed_gives_request_with_ugly_uri():
    with mock.patch('src.viewer_request_lambda_function.Config') as MockConfig:
        MockConfig.return_value.get_ugly_uri.return_value = '/some/ugly/uri'
        MockConfig.return_value.access_is_allowed.return_value = True
        event = load_event('access_tests_template',
            uri='/some/pretty/uri',
            cookies=['user=some_user'],
        )
        context = ''
        request = viewer_request_lambda_function.lambda_handler(event, context)
        assert request['uri'] == '/some/ugly/uri'
