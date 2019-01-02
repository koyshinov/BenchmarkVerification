from django.test import TestCase


class CheckAccessPages(TestCase):
    fixtures = ['fixtures/users.json']

    def test_access_signin_page(self):
        html_sub_string = '<p class="text-muted">Sign In to your account</p>'
        response = self.client.get("/login")
        self.assertInHTML(html_sub_string, response.content.decode("utf-8"))

    def test_good_login_testuser(self):
        data = {"next": "/run", "username": "testuser1", "password": "123Qwe!23"}
        response = self.client.post("/login", data, follow=True)
        self.assertEqual(response.redirect_chain, [('/run', 302)])

    def test_bad_login_testuser(self):
        html_sub_string = '<div class="invalid-feedback">Username or password is invalid!</div>'
        data = {"next": "/run", "username": "testuser1", "password": "123Qwe!23123123"}
        response = self.client.post("/login", data)
        self.assertInHTML(html_sub_string, response.content.decode("utf-8"))

    def test_access_pages_wo_auth(self):
        urls = ["/", "/run", "/task/table", "/scan/results"]
        for url in urls:
            response = self.client.get(url, follow=True)
            redirect_page, status_code = response.redirect_chain[-1]
            self.assertIn("/login", redirect_page, "No redirecting to /login page")

    def test_access_pages_with_auth(self):
        data = {"next": "/run", "username": "testuser1", "password": "123Qwe!23"}
        self.client.post("/login", data, follow=True)

        response = self.client.get("/", follow=True)
        self.assertEqual(response.redirect_chain, [('/run', 302)])

        urls = ["/run", "/task/table", "/scan/results"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
