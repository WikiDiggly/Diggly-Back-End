import pytest
from util.django_util import Django_Helper

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