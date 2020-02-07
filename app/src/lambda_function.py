# https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-examples.html#lambda-examples-redirect-based-on-country
import logging
def lambda_handler(event, context):

     logger = logging.getLogger('tcpserver')
     logger.warning(event)
     request = event['Records'][0]['cf']['request']
     headers = request['headers']

     '''
      Based on the value of the CloudFront-Viewer-Country header, generate an
      HTTP status code 302 (Redirect) response, and return a country-specific
      URL in the Location header.
      NOTE: 1. You must configure your distribution to cache based on the
               CloudFront-Viewer-Country header. For more information, see
               http://docs.aws.amazon.com/console/cloudfront/cache-on-selected-headers
            2. CloudFront adds the CloudFront-Viewer-Country header after the viewer
               request event. To use this example, you must create a trigger for the
               origin request event.
     '''

     url = 'https://example.com/'
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
