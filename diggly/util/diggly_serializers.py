from ..models import Topic, TopicLink
from rest_framework import serializers

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('article_title', 'article_id', 'summary', 'description', 'wiki_link')

class TopicLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicLink
        fields = ('source_id', 'target_id', 'description', 'score')

class TopicCreator():
    def create_topic(self, data):
        topic = Topic(article_title = data['article_title'],
                        article_id = data['article_id'],
                        description = data['description'],
                        summary = data['summary'],
                        wiki_link = data['wiki_link'],
                        linked_topics = data['linked_topics']) 

        return topic

class TopicLinkCreator():
    def create_topiclink(self, data):
        topiclink = TopicLink(source_id = data['source_id'],
                        target_id = data['target_id'],
                        title = data['title'],
                        description = data['description'],
                        wiki_link = data['wiki_link'],
                        score = data['score']) 

        return topiclink

