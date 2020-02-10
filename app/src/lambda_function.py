# https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-examples.html#lambda-examples-redirect-based-on-country

from event import Event
from book_redirects import BookRedirects
import re

BookRedirects.set("psychology", amazon_id="1938168356", hp_id="")
BookRedirects.set("prealgebra", amazon_id="1938168992", hp_id="")
BookRedirects.set("elementary-algebra", amazon_id="099862571X", hp_id="")
BookRedirects.set("intermediate-algebra", amazon_id="0998625728", hp_id="")

def lambda_handler(event, context):
    event = Event(event)
    request = event.request()

    if re.match(".?diagnostic.*",request.path()):
        return render_diagnostic(request)
    else:
        return redirect(request)

def redirect(request):
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

def render_diagnostic(request):
    content = f"""
        <html>
            <head>
                <meta name="robots" content="noindex">
                <title>Buy Print diagnostics</title>
            </head>
            <body>
                {BookRedirects.to_html()}
            </body>
        </html>
        """

    response = {
        'status': '200',
        'headers': {
            'x-robots-tag': [{
                'key': 'X-Robots-Tag',
                'value': 'noindex'
            }]
        },
        'body': content
    }

    return response
