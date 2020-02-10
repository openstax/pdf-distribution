import json
import pytest
import pdb

from src import lambda_function

def event(country_code, slug="/psychology"):
    return {
        "Records": [
            {
                "cf": {
                    "request": {
                        "uri": slug,
                        "headers": {
                            "cloudfront-viewer-country": [
                                {
                                    "key": "CloudFront-Viewer-Country",
                                    "value": country_code
                                }
                            ],
                        }
                    }
                }
            }
        ]
    }

def assert_redirects(response, url):
    assert response['status'] == '302'
    assert response['headers']['location'] == [{'key': 'Location', 'value': url}]

def test_us_requests_redirect_to_amazon(mocker):
    response = lambda_function.lambda_handler(event("US"), "")
    assert_redirects(response, "https://www.amazon.com/dp/1938168356")

def test_non_us_requests_redirect_to_hp(mocker):
    response = lambda_function.lambda_handler(event("JP"), "")
    assert_redirects(response, "https://hp.com")

def test_unknown_us_requests_redirect_to_amazon_all_books_page(mocker):
    response = lambda_function.lambda_handler(event("US", "howdy"), "")
    assert_redirects(response, "https://www.amazon.com/s?me=A1540JPBBI3F06&qid=1517336719")

