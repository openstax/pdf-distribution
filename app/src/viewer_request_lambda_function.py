import json
import boto3
import urllib
import re
import datetime

## from: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-examples.html#lambda-examples-redirect-to-signin-page
def parseCookies(headers):
    parsedCookie = {}
    if headers.get('cookie'):
        for cookie in headers['cookie'][0]['value'].split(';'):
            if cookie:
                parts = cookie.split('=')
                parsedCookie[parts[0].strip()] = parts[1].strip()
    return parsedCookie

def lambda_handler(event, context):
    ##
    ## Extract the request and pretty URI
    ## from the event.
    ##

    request = event['Records'][0]['cf']['request']
    pretty_uri = request['uri']

    ##
    ## If this is an echo request, just return
    ## the given request (for debugging).
    ##

    if pretty_uri == '/echo':
        response = {
            'status': 200,
            'body': json.dumps(request),
        }
        return response

    ##
    ## If this is a login request, set the appropriate user cookie.
    ##

    match = re.search('^/login/(\w+)$', pretty_uri)
    if match:
        user_cookie = match.group(1)
        response = {
            'status': 200,
            'headers': {
                'Set-COOKIE': [
                    {
                        'key': 'Set-COOKIE',
                        'value': 'user={}; Path=/'.format(user_cookie)
                    }
                ]
            },
            'body': json.dumps('logged in as {}'.format(user_cookie))
        }
        return response

    ##
    ## If this is a logout request, clear the user cookie.
    ##

    if pretty_uri == '/logout':
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=-1)
        expires_str = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
        response = {
            'status': 200,
            'headers': {
                'Set-COOKIE': [
                    {
                        'key': 'Set-COOKIE',
                        'value': 'user=deleted; Path=/; Expires={}'.format(expires_str)
                    }
                ]
            },
            'body': json.dumps('logged out')
        }
        return response

    ##
    ## Extract the relevant cookies from the request.
    ##

    cookies = parseCookies(request['headers'])
    user_cookie      = cookies.get('user', 'anonymous')
    diversion_cookie = cookies.get('diversion', None)

    ##
    ## If the user does NOT have a diversion cookie,
    ## send them to the diversion page.  Also add
    ## a custom header to indicate to the viewer
    ## response lambda function that a diversion
    ## cookie should be added.
    ##

    if diversion_cookie is None:
        request['uri'] = '/diversion/diversion_page.html'
        request['headers']['openstax-add-diversion'] = [
            { 'key': 'Openstax-Add-Diversion',
              'value': 'do-it-NOW!' }
        ]
        return request

    ##
    ## Connect to DynamoDb and look up the
    ## current configuration.
    ##

    session = boto3.session.Session(region_name='us-east-1')
    ddb_client = session.client('dynamodb')

    ## Get the current config id.
    ddb_response = ddb_client.get_item(
        TableName='kevin-pdfdistro-configs',
        Key={'config_id': {'S': 'current'}},
    )
    cur_config_id = ddb_response['Item']['data']['S']

    ## Get the current config data.
    config = ddb_client.get_item(
        TableName='kevin-pdfdistro-configs',
        Key={'config_id': {'S': cur_config_id}},
    )

    ##
    ## Keep mapping uris until we reach a final,
    ## ugly behind-the-scenes one.
    ##

    ugly_uri = None
    new_uri = pretty_uri
    while True:
        new_uri = config['Item']['uri_map']['M'].get(new_uri,{}).get('S', None)
        if new_uri is None:
            break
        elif new_uri == ugly_uri:
            break
        else:
            ugly_uri = new_uri

    ##
    ## If we couldn't find an explicit ugly uri,
    ## return File Not Found (404)
    ##

    if ugly_uri is None:
        response = {
            'status': 404,
            'body': json.dumps("Ain't no Thang!")
        }
        return response

    ##
    ## Check the permissions on the ugly uri,
    ## and return a Permission Denied (403)
    ## if appropriate.
    ##

    allowed = config['Item']['access_map']['M'].get(ugly_uri,{}).get('S', '-').strip().split()
    if user_cookie not in allowed:
        response = {
            'status': 403,
            'body': json.dumps("Oh no you didn't!")
        }
        return response

    ##
    ## Adjust the uri and forward the request.
    ##

    request['uri'] = ugly_uri
    return request
