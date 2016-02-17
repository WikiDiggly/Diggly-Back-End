import os
import sys
import mock
import pytest


sys.path.append(os.path.join(os.path.dirname(__file__), '../diggly'))
#import diggly.views as Diggly_Views
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

	def test_list_topic(self):
		with mock.patch('diggly.models.Topic') as Topic_mock:
			from diggly.views import get_topic_by_id
			Topic.objects = mock.Mock()
			#Topic_mock.objects = mock.Mock()
			#Topic_mock.objects.configure_mock(**conf)
			request_context = mock.MagicMock()

			conf = {'get.side_effect': Topic.DoesNotExist}
			Topic.objects.configure_mock(**conf)
			
			with pytest.raises(Http404):
				get_topic_by_id(request_context, 1)



	#helper functions
	def __create_mock_Topic(self):
		mock_instance = mock.Mock(spec=Topic)
		mock_instance.article_id = 123
		mock_instance.article_title = "TestTopic1"

		return mock_instance