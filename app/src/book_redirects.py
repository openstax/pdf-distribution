import re

class BookRedirects:
    redirects = {}
    fallback_url = "https://www.amazon.com/s?me=A1540JPBBI3F06&qid=1517336719"

    @classmethod
    def normalize_slug(self, slug):
        return re.sub("^/|/$","",slug.lower().strip())

    @classmethod
    def set(self, book_slug, amazon_id, hp_id):
        self.redirects[self.normalize_slug(book_slug)] = {
            'US': "https://www.amazon.com/dp/" + amazon_id,
            '**': "https://hp.com"
        }

    @classmethod
    def get(self, book_slug, country_code):
        book_redirects = self.redirects.get(self.normalize_slug(book_slug))
        if book_redirects == None:
            return self.fallback_url
        else:
            url = book_redirects.get(country_code)
            if url == None:
                return book_redirects.get("**") or self.fallback_url
            else:
                return url
