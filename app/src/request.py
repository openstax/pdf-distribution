class Request:
    def __init__(self, data):
        self.data = data
        self.headers = data['headers']

    def country_code(self):
        viewer_country_header = self.headers.get('cloudfront-viewer-country')
        if viewer_country_header:
            return viewer_country_header[0]['value']
        else:
            return None

    def path(self):
        return self.data.get('uri')
