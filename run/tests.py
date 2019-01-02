from django.test import TestCase


class CheckRunScanningPage(TestCase):
    fixtures = ['fixtures/users.json', 'fixtures/tasks.json',
                'benchmark_cis_microsoft_office_2016.json']

    def auth_user(self, user, next=None):
        if next:
            data = {"next": next, "username": user, "password": "123Qwe!23"}
            response = self.client.post("/login", data, follow=True)
            self.assertEqual(response.redirect_chain[-1], (next, 302))
        else:
            data = {"username": user, "password": "123Qwe!23"}
            response = self.client.post("/login", data, follow=True)
            self.assertEqual(response.redirect_chain[-1], ("/run", 302))
        return response

    def test_empty_parametr(self):
        self.auth_user("testuser1")
        data_list = [
            {"name": "", "conf": "19"},
            {"conf": "19"},
            {"name": "test scan", "conf": ""},
            {"name": "test scan"}
        ]
        for data in data_list:
            response = self.client.post("/run", data)
            self.assertIn("Some data is empty", response.content.decode("utf-8"), str(data))

    def test_nonexistent_conf(self):
        self.auth_user("testuser1")
        data = {"name": "test scan", "conf": "1001"}
        response = self.client.post("/run", data)
        self.assertIn("Configuration not found", response.content.decode("utf-8"))

    def test_scan_with_foreign_conf(self):
        self.auth_user("testuser2")
        data = {"name": "test scan", "conf": "19"}
        response = self.client.post("/run", data)
        self.assertIn("Configuration not found", response.content.decode("utf-8"))

    def test_start_scanning_by_anonim(self):
        data = {"name": "test scan", "conf": "19"}
        response = self.client.post("/run", data, follow=True)
        redirect_page, status_code = response.redirect_chain[-1]
        self.assertIn("/login", redirect_page, "No redirecting to /login page")
