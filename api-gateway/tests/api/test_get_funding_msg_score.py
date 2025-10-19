# from django.test import TestCase
# from rest_framework.test import APIClient
# from django.conf import settings
# from rest_framework import status

# settings.RUNNING_ENV = 'test'

# import io, time, os, glob, pprint, json, re, shutil, ntpath
# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# from base.management.commands.create_base_data import Command

# class GetFundingMsgScoreCase(TestCase):
# 	def setUp(self):
# 		command = Command()
# 		command.create_config_funding_msg()
# 		self.client = APIClient()


# 	def test_1(self):
# 		response = self.client.get('/api/funding-msg-score/', {
# 			'sise': '5000',
# 			'reserved': '3000',
# 			'return_period': '6'
# 		}, format='json')
# 		self.assertEqual(response.status_code, status.HTTP_200_OK)
# 		self.assertEqual(response.data['result']['score'], 60)
