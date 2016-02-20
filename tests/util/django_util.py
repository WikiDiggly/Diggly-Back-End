import django
from django.core.urlresolvers import reverse, resolve

#settings.configure(default_settings=diggly_defaults, DEBUG=True)
#django.setup()

class Django_Helper:
	def test_paths(self, routes_to_test):
		for route in routes_to_test:
			path    = route["url_path"]
			pattern = route["pattern_name"]
			kwparams = route.get("kwargs")

			if kwparams:
				yield reverse(pattern, kwargs=kwparams), path
			else:
				yield reverse(pattern), path

			yield resolve(path).url_name, pattern

