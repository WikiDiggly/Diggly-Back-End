import os
import sys
import mock
import pytest
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../diggly'))
from diggly.models import Topic, TopicLink
from util.django_util import Django_Helper
from django.http import Http404


django_mgt = Django_Helper()

class TestAPIClass:
	def test_diggly_routes(self):
		test_routes = [
			dict(url_path = "/diggly/topics/", pattern_name='list_topics'),
			dict(url_path="/diggly/topics/related/all/26903/", pattern_name='get_all_topiclinks', kwargs={"tid": 26903}),
			dict(url_path="/diggly/topics/related/top/26903/", pattern_name='get_top_topiclinks', kwargs={"tid": 26903}),
			dict(url_path="/diggly/topics/explore/26903/", pattern_name='explore_topic', kwargs={"tid": 26903})
			]

		routes = django_mgt.test_paths(test_routes)

		for stringOne, stringTwo in routes:
			assert (stringOne == stringTwo)

	def test_get_topic_by_id(self):
		from diggly.views import get_topic_by_id
		tid = 123
		Topic.objects = mock.Mock()
		request_context = mock.MagicMock()

		conf_1 = {'get.side_effect': Topic.DoesNotExist}
		Topic.objects.configure_mock(**conf_1)

		with pytest.raises(Http404):
			get_topic_by_id(request_context, tid)

		mock_instance = mock.MagicMock()
		conf_2 = {'get': mock_instance}
		Topic.objects.configure_mock(**conf_2)

		result = get_topic_by_id(request_context, tid)
		result_json = json.loads(result.content)
		assert (result_json['article_id'] != None)

	#helper functions
	def __create_mock_Topic(self):
		mock_instance = mock.Mock(spec=Topic)
		mock_instance.article_id = 123
		mock_instance.article_title = "TestTopic1"

		return mock_instance
