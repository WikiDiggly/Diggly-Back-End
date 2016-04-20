from diggly.models import TopicVisit
from datetime import datetime, timedelta

def log_visit(topic):
	topicvisit = TopicVisit()
	topicvisit.source_id = topic
	print "Logging Visit for Topic ID", topicvisit.source_id.article_id, "\n"

	topicvisit.save()
	purge_visits()
	return None

def purge_visits():
	ttl_in_days = 365
	TopicVisit.objects.filter(visit_timestamp=datetime.now()-timedelta(days=ttl_in_days)).delete()
	print "Purging visits older than 1 year..."

