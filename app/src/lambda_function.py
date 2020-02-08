# https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-examples.html#lambda-examples-redirect-based-on-country

def lambda_handler(event, context):

     request = event['Records'][0]['cf']['request']
     headers = request['headers']

     url = 'https://openstax.org/'

     viewerCountry = headers.get('cloudfront-viewer-country')
     if viewerCountry:
         countryCode = viewerCountry[0]['value']
         if countryCode == 'US':
             url = 'https://amazon.com/'
         else:
             url = 'https://hp.com/'

     response = {
         'status': '302',
         'statusDescription': 'Found',
         'headers': {
             'location': [{
                 'key': 'Location',
                 'value': url
             }]
         }
     }

     return response
