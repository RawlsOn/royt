from django.test import TestCase
from django.conf import settings
from rest_framework import status

settings.RUNNING_ENV = 'test'

import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from common.util.finance_util import get_score_from

class FinanceUtilCase(TestCase):
	# def setUp(self):
		# self.client = APIClient()

	def test_get_score_from_1(self):
		result = get_score_from(ltv= 70, return_period_month= 3)
		self.assertEqual(result, 60)