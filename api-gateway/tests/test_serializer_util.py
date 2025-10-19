from django.test import TestCase

import io, time, os, glob, pprint, json, re, shutil, ntpath

import common.util.serializer_util as util

pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

class SerializerUtilCase(TestCase):
    def setUp(self):
        self.results = [
    {
      "content": "1  여기서는 전체 모집단에 대하여 정의된 것이다. 베타원이 로xy의 상수배라는 사실은 실험자료가 없는 경우 단순회기가 갖는 중요한 한계를 드러낸다.",
    },
    {
      "content": "2  여기서는 전체 모집단에 대하여 정의된 것이다. 베타원이 로xy의 상수배라는 사실은 실험자료가 없는 경우 단순회기가 갖는 중요한 한계를 드러낸다.",
    }]

    def test_add_search_keyword_em_1(self):
        """검색어가 두 단어 이상인 경우"""
        results = util.add_search_keyword_em('실험자료 중요 한계', self.results)
        self.assertEqual(results[0]['content_html'], '1  여기서는 전체 모집단에 대하여 정의된 것이다. 베타원이 로xy의 상수배라는 사실은 <em>실험자료</em>가 없는 경우 단순회기가 갖는 <em>중요</em>한 <em>한계</em>를 드러낸다.')

    def test_add_search_keyword_em_2(self):
        """검색어가 한 단어인 경우"""
        results = util.add_search_keyword_em('한계', self.results)
        self.assertEqual(results[0]['content_html'], '1  여기서는 전체 모집단에 대하여 정의된 것이다. 베타원이 로xy의 상수배라는 사실은 실험자료가 없는 경우 단순회기가 갖는 중요한 <em>한계</em>를 드러낸다.')
