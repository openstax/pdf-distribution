import re

class BookRedirects:
    redirects = {}
    fallback_url = "https://www.amazon.com/s?me=A1540JPBBI3F06&qid=1517336719"

    @classmethod
    def normalize_slug(self, slug):
        return re.sub("^/|/$","",slug.lower().strip())

    @classmethod
    def set(self, book_slug, amazon_id, other_id):
        self.redirects[self.normalize_slug(book_slug)] = {
            'US': "https://www.amazon.com/dp/" + amazon_id,
            '**': "https://www.amazon.com/dp/" + amazon_id
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

    @classmethod
    def to_html(self):
        result = "<ul>"

        for slug, hsh in self.redirects.items():
            result += "<li>" + slug + "<ul>"

            for code, url in hsh.items():
                result += f"<li>{code}: <a href='{url}'>{url}</a></li>"

            result += "</ul></li>"

        result += "</ul>"

        return result

