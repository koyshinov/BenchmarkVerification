from django.test import TestCase


class CheckConfigurations(TestCase):
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

    def test_configuration_table(self):
        response = self.auth_user("testuser1", "/task/table")
        self.assertIn("test configuration 1", response.content.decode("utf-8"))
        self.assertIn("test configuration 2", response.content.decode("utf-8"))

    def test_empty_parametr(self):
        self.auth_user("testuser1")
        data = {
            "name": "test configuration",
            "benchmarks": ["3"],
            "hosts": "192.168.88.88",
            "wmi_login": "admin",
            "wmi_passw": "1234567",
            "wmi_passw2": "1234567"
        }
        empty_params = (
            ("name", ),
            ("hosts", ),
            ("wmi_login", ),
            ("wmi_passw", "wmi_passw2"),
        )
        for params in empty_params:
            new_data = data
            for param in params:
                new_data[param] = ""
            response = self.client.post("/task/create", new_data)
            self.assertIn("Some data is empty", response.content.decode("utf-8"))

    def test_empty_benchmark(self):
        self.auth_user("testuser1")
        data = {
            "name": "test configuration",
            "hosts": "192.168.88.88",
            "wmi_login": "admin",
            "wmi_passw": "1234567",
            "wmi_passw2": "1234567"
        }
        response = self.client.post("/task/create", data)
        self.assertIn("Choose benchmarks", response.content.decode("utf-8"))

    def test_nonexistent_benchmark(self):
        self.auth_user("testuser1")
        data = {
            "name": "test configuration",
            "benchmarks": ["3", "1000"],
            "hosts": "192.168.88.88",
            "wmi_login": "admin",
            "wmi_passw": "1234567",
            "wmi_passw2": "1234567"
        }
        response = self.client.post("/task/create", data)
        self.assertIn("Some benchmarks not found", response.content.decode("utf-8"))

    def test_not_equal_passwords(self):
        self.auth_user("testuser1")
        data = {
            "name": "test configuration",
            "benchmarks": ["3"],
            "hosts": "192.168.88.88",
            "wmi_login": "admin",
            "wmi_passw": " 1234567",
            "wmi_passw2": "1234567"
        }
        response = self.client.post("/task/create", data)
        self.assertIn("Passwords do not match", response.content.decode("utf-8"))

    def test_normal_adding_configuration(self):
        self.auth_user("testuser1")
        data = {
            "name": "test configuration 3",
            "benchmarks": ["3"],
            "hosts": "192.168.88.88",
            "wmi_login": "admin",
            "wmi_passw": "1234567",
            "wmi_passw2": "1234567"
        }
        response = self.client.post("/task/create", data, follow=True)
        self.assertEqual(response.redirect_chain, [('/task/table', 302)])
        self.assertIn("test configuration 3", response.content.decode("utf-8"))

    def test_delete_my_configuration(self):
        self.auth_user("testuser1")
        response = self.client.get("/task/delete/19", follow=True)
        self.assertIn("test configuration 2", response.content.decode("utf-8"))
        self.assertNotIn("test configuration 1", response.content.decode("utf-8"))

    def test_delete_configuration_by_anonim(self):
        response = self.client.get("/task/delete/19", follow=True)
        redirect_page, status_code = response.redirect_chain[-1]
        self.assertIn("/login", redirect_page, "No redirecting to /login page")

    def test_delete_foreign_configuration(self):
        self.auth_user("testuser2")
        self.client.get("/task/delete/19", follow=True)
        self.client.get("/logout")
        response = self.auth_user("testuser1", "/task/table")
        self.assertIn("test configuration 1", response.content.decode("utf-8"))
