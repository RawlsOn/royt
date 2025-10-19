# from django.test import TestCase

# import main.services as services
# import io, time, os, glob, pprint, json, re, shutil, ntpath
# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# class ServiceTestCase(TestCase):
#     def setUp(self):
#         with open('./tests/resources/multi_AEA_diff_priority.xml', 'r') as f:
#             self.multi_diff = f.read()
#         with open('./tests/resources/multi_AEA_same_priority.xml', 'r') as f:
#             self.multi_same = f.read()

#         self.serv = services.Service()

#     def test_1(self):
#         """복수의 AEA 텍스트, 다른 priority"""
#         extracted = self.serv.extract_data(self.multi_diff)
#         self.assertEqual(extracted['priority'], '4')

#     def test_2(self):
#         """복수의 AEA 텍스트, 같은 priority"""
#         extracted = self.serv.extract_data(self.multi_same)
#         self.assertEqual(extracted['EventDesc'][0]['text'], '호우 경보 발표')