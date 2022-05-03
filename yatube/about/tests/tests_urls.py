from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.unauthorised_client = Client()

    def test_author(self):
        response = self.unauthorised_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech(self):
        response = self.unauthorised_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
