import json

def lambda_handler(event, context):
    request  = event['Records'][0]['cf']['request']
    response = event['Records'][0]['cf']['response']

    ## Super hacky way to avoid colliding with any existing
    ## Set-Cookie headers: vary the case.  See:
    ##     https://forums.aws.amazon.com/thread.jspa?messageID=701434
    if request['headers'].get('openstax-add-diversion', None):
        response['headers']['SeT-CoOkIe'] = [
            {
                'key': 'SeT-CoOkIe',
                'value': 'diversion=no; Path=/'
            }
        ]
    return response
