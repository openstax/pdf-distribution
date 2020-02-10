# https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-examples.html#lambda-examples-redirect-based-on-country

from event import Event
from book_redirects import BookRedirects
import re

BookRedirects.set("prealgebra", amazon_id="1938168992", other_id="")
BookRedirects.set("elementary-algebra", amazon_id="099862571X", other_id="")
BookRedirects.set("intermediate-algebra", amazon_id="0998625728", other_id="")
BookRedirects.set("college-algebra", amazon_id="1938168380", other_id="")
BookRedirects.set("algebra-and-trigonometry", amazon_id="1938168372", other_id="")
BookRedirects.set("precalculus", amazon_id="1938168348", other_id="")
BookRedirects.set("calculus-volume-1", amazon_id="193816802X", other_id="")
BookRedirects.set("calculus-volume-2", amazon_id="1938168062", other_id="")
BookRedirects.set("calculus-volume-3", amazon_id="1938168070", other_id="")
BookRedirects.set("introductory-statistics", amazon_id="1938168208", other_id="")
BookRedirects.set("anatomy-and-physiology", amazon_id="1938168135", other_id="")
BookRedirects.set("astronomy", amazon_id="1938168283", other_id="")
BookRedirects.set("biology-2e", amazon_id="1947172514", other_id="")
BookRedirects.set("concepts-biology", amazon_id="1938168119", other_id="")
BookRedirects.set("microbiology", amazon_id="1938168143", other_id="")
BookRedirects.set("chemistry-2e", amazon_id="194717262X", other_id="")
BookRedirects.set("chemistry-atoms-first-2e", amazon_id="1947172646", other_id="")
BookRedirects.set("college-physics", amazon_id="1938168003", other_id="")
BookRedirects.set("university-physics-volume-1", amazon_id="1938168275", other_id="")
BookRedirects.set("university-physics-volume-2", amazon_id="193816816X", other_id="")
BookRedirects.set("university-physics-volume-3", amazon_id="1938168186", other_id="")
BookRedirects.set("biology-ap-courses", amazon_id="1947172409", other_id="")
BookRedirects.set("college-physics-ap-courses", amazon_id="1938168933", other_id="")
BookRedirects.set("american-government-2e", amazon_id="1947172654", other_id="")
BookRedirects.set("principles-economics-2e", amazon_id="1947172360", other_id="")
BookRedirects.set("principles-macroeconomics-2e", amazon_id="1947172387", other_id="")
BookRedirects.set("principles-microeconomics-2e", amazon_id="1947172344", other_id="")
BookRedirects.set("psychology", amazon_id="1938168356", other_id="")
BookRedirects.set("introduction-sociology-2e", amazon_id="1938168410", other_id="")
BookRedirects.set("us-history", amazon_id="1938168364", other_id="")
BookRedirects.set("introduction-business", amazon_id="1947172549", other_id="")
BookRedirects.set("business-ethics", amazon_id="1593995776", other_id="")
BookRedirects.set("principles-financial-accounting", amazon_id="1947172689", other_id="")
BookRedirects.set("principles-managerial-accounting", amazon_id="1947172603", other_id="")
BookRedirects.set("introductory-business-statistics", amazon_id="1947172468", other_id="")
BookRedirects.set("principles-management", amazon_id="0998625760", other_id="")
BookRedirects.set("organizational-behavior", amazon_id="1593998775", other_id="")

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
