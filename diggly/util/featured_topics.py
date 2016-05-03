from datetime import datetime, timedelta
from diggly.util.diggly_threads import FuncThread
from django.db.models import Max, Q
from diggly.models import Topic, FeaturedTopics

def update_featured_object(topic):
    #Get featured topics instance
    featured_topics = None
    now = datetime.now()
    earlier = timedelta(minutes=1)

    topic.visit_counter += 1
    topic.save()

    try:
        featured_topics = FeaturedTopics.objects.all()[0]
        recent_topics = featured_topics.recent_topics
        #Update recent topics object once an hour, ensuring all objects are unique
        if topic not in recent_topics and featured_topics.recent_topic_timestamp < (now-earlier):
            while len(recent_topics) >= 3:
                recent_topics.pop(0)
            recent_topics.append(topic)
            featured_topics.recent_topics = recent_topics
            featured_topics.recent_topic_timestamp = now

        max_visit_counter = Topic.objects.aggregate(Max('visit_counter'))['visit_counter__max']
        new_popular_topic = Topic.objects.filter(visit_counter=max_visit_counter)[0]

        if featured_topics.popular_topic.article_id != new_popular_topic.article_id:
            featured_topics.popular_topic = new_popular_topic
    
    except IndexError:
        featured_topics = FeaturedTopics()
        random_topics = Topic.objects.filter(~Q(article_id=topic.article_id))[:2]
        featured_topics.recent_topics = [random_topics[0], random_topics[1], topic]
        featured_topics.recent_topic_timestamp = now

        max_visit_counter = Topic.objects.aggregate(Max('visit_counter'))['visit_counter__max']
        new_popular_topic = Topic.objects.filter(visit_counter=max_visit_counter)[0]
        featured_topics.popular_topic = new_popular_topic
        featured_topics.trending_topic = new_popular_topic

    featured_topics.save()