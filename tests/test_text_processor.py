import os
import sys
import mock
import pytest
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../diggly/util'))
from diggly.util.text_process import Text_Process
from util.django_util import Django_Helper
from django.http import Http404


django_mgt = Django_Helper()

#This class tests the public functions in the diggly/util/Text_Process class
class TestTextProcessorClass:
	def test_get_description(self):
		desc_len = 2
		summ_len = 1
		num_sentences = 5;
		sentence_list = self.__create_sentences(num_sentences)
		text_content = " ".join(sentence_list)

		print "TEST-CONTENT -->", text_content

		txt_mgt = Text_Process(desc_len, summ_len)
		description = txt_mgt.get_description(text_content)
		assert (description == " ".join(sentence_list[0:2]))


	#helper functions
	def __create_sentences(self, num_sentences):
		template = "This is sentence #{}."
		sentence_list = []

		for i in range(0, num_sentences):
			sentence_list.append(template.format(i))

		return sentence_list


