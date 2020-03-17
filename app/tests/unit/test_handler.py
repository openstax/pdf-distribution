import json
import pytest
import pdb

from src import viewer_request_lambda_function

def load_event(event_name):
    with open('./events/{}.json'.format(event_name)) as fd:
        text = fd.read()
    event = json.loads(text)
    return event

def assert_redirects(response, url):
    assert response['status'] == '302'
    assert response['headers']['location'] == [{'key': 'Location', 'value': url}]

def test_missing_books_return_response_status_404(mocker):
    event = load_event('missing_book_teacher')
    context = ''
    response = viewer_request_lambda_function.lambda_handler(event, context)
    assert response['status'] == 404

# def test_non_us_requests_redirect_to_other(mocker):
#     response = lambda_function.lambda_handler(event("JP"), "")
#     # assert_redirects(response, "https://google.com") # temporarily set to Amazon
#     assert_redirects(response, "https://www.amazon.com/dp/1938168356")

# def test_unknown_us_requests_redirect_to_amazon_all_books_page(mocker):
#     response = lambda_function.lambda_handler(event("US", "howdy"), "")
#     assert_redirects(response, "https://www.amazon.com/s?me=A1540JPBBI3F06&qid=1517336719")

# def test_diagnostic(mocker):
#     response = lambda_function.lambda_handler(event("US", "/diagnostic"), "")
#     assert response['status'] == '200'
