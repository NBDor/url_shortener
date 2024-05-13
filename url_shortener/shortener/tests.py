import json
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.test import TestCase, Client
from django.urls import reverse
from .models import AvailableShortURL, ShortURL
from .queue_manager import graceful_shutdown


class ShortURLTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.long_url = 'https://ravkavonline.co.il'
        self.short_url = ShortURL.objects.create(long_url=self.long_url, short_url='abcdef')
        self.available_short_url = AvailableShortURL.objects.create(short_url='abc123')


    def test_create_short_url(self):
        data = {'url': self.long_url}
        response = self.client.post(
            reverse('create_short_url'), 
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertIn('short_url', response.json())
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertIn('short_url', response.json())

    def test_redirect_short_url(self):
        response = self.client.get(reverse('redirect_url', args=[self.short_url.short_url]))
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
        self.assertEqual(response.url, self.long_url)

    def test_non_existing_short_url(self):
        response = self.client.get(reverse('redirect_url', args=['invalid']))
        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)
        self.assertIn('error', response.json())

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        graceful_shutdown()