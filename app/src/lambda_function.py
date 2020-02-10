# https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-examples.html#lambda-examples-redirect-based-on-country

from event import Event
from book_redirects import BookRedirects

BookRedirects.set("psychology", amazon_id="1938168356", hp_id="")

def lambda_handler(event, context):
    event = Event(event)
    request = event.request()

    redirect_url = BookRedirects.get(book_slug=request.path(),
                                     country_code=request.country_code())

    response = {
        'status': '302',
        'statusDescription': 'Found',
        'headers': {
            'location': [{
                'key': 'Location',
                'value': redirect_url
            }]
        }
    }

    return response
