import datetime
import json
import urllib
import re

from oxlate import Event, Request, Response

from .config import Config

def lambda_handler(event, context):
    ##
    ## Extract the request and pretty URI
    ## from the event.
    ##

    request = Event(event).request()
    pretty_uri = request.get_uri()

    ##
    ## If this is an echo request, just return
    ## the given request (for debugging).
    ##

    if pretty_uri == '/echo':
        response = {
            'status': 200,
            'body': json.dumps(request.to_dict()),
        }
        return response

    ##
    ## If this is a login request, set the appropriate user cookie.
    ##

    match = re.search(r'^/login/(\w+)$', pretty_uri)
    if match:
        user_cookie = match.group(1)

        response = Response(
            status = 200,
            body   = json.dumps('logged in as {}'.format(user_cookie))
        )
        response.get_headers() \
                .set_response_cookie(name='user', value=user_cookie)

        return response.to_dict()

    ##
    ## If this is a logout request, clear the user cookie.
    ##

    if pretty_uri == '/logout':
        response = Response(
            status = 200,
            body   = json.dumps('logged out'),
        )

        expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=-1)
        response.get_headers() \
                .set_response_cookie(
                    name  = 'user',
                    value = 'deleted',
                    path  = '/',
                    expires_at = expires_at,
                )

        return response.to_dict()

    ##
    ## Extract the relevant cookies from the request.
    ##

    user_cookie      = request.get_headers() \
                              .get_request_cookie('user', default='anonymous')
    diversion_cookie = request.get_headers() \
                              .get_request_cookie('diversion', default=None)

    ##
    ## If the user does NOT have a diversion cookie,
    ## send them to the diversion page.  Also add
    ## a custom header to indicate to the viewer
    ## response lambda function that a diversion
    ## cookie should be added.
    ##

    if diversion_cookie is None:
        request.set_uri('/diversion/diversion_page.html')
        request.get_headers().set(
            name  = 'openstax-add-diversion',
            value = 'do-it-NOW!',
        )
        return request.to_dict()

    ##
    ## Connect to DynamoDb and look up the
    ## current configuration.
    ##

    config = Config(
        region_name='us-east-1',
        table_name='kevin-pdfdistro-configs',
    )

    ##
    ## Keep mapping uris until we reach a final,
    ## ugly behind-the-scenes one.
    ##
    ## If we couldn't find an explicit ugly uri,
    ## return File Not Found (404)
    ##

    ugly_uri = config.get_ugly_uri(pretty_uri)
    if ugly_uri is None:
        response = Response(
            status = 404,
            body   = json.dumps("Ain't no Thang!"),
        )
        return response.to_dict()

    ##
    ## Check the permissions on the ugly uri,
    ## and return a Permission Denied (403)
    ## if appropriate.
    ##

    if not config.access_is_allowed(user=user_cookie, ugly_uri=ugly_uri):
        response = Response(
            status = 403,
            body   = json.dumps("Oh no you didn't!"),
        )
        return response.to_dict()

    ##
    ## Adjust the uri and forward the request.
    ##

    request.set_uri(ugly_uri)
    return request.to_dict()
