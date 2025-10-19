# from django.test import TestCase
# from rest_framework.test import APIClient
# from django.conf import settings
# from rest_framework import status

# settings.RUNNING_ENV = 'test'

# import io, time, os, glob, pprint, json, re, shutil, ntpath
# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# class PostReviewCase(TestCase):
# 	def setUp(self):
# 		self.client = APIClient()

# 	def test_1(self):
# 		result = self.client.post('/api/write-review-pre/', {}, format='json')
# 		self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

# 	def test_good(self):
# 		result = self.client.post('/api/write-review-pre/', {
# 			'user_email': 'email@email.com',
# 			'target_name_or_nickname': 'federer',
# 			'target_gender': 'female',
# 			'rating': 5,
# 			'review': 'The Emperor.'
# 		}, format='json')
# 		self.assertEqual(result.status_code, status.HTTP_201_CREATED)