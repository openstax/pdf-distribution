import json
import pytest
import pdb

from src import lambda_function

def event(country_code):
    return {
        "Records": [
            {
                "cf": {
                    "request": {
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
    assert_redirects(response, "https://amazon.com/")

def test_non_us_requests_redirect_to_hp(mocker):
    response = lambda_function.lambda_handler(event("JP"), "")
    assert_redirects(response, "https://hp.com/")
