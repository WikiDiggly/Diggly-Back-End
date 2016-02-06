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

class TopicManager():
    def create_topic(self, data):
        topic = Topic(article_title = data['article_title'],
                        article_id = data['article_id'],
                        description = data['description'],
                        summary = data['summary'],
                        wiki_link = data['wiki_link'],
                        linked_topics = data['linked_topics']) 

        topic.save()
        return topic

    #def delete_topic(self, tid):
        #topic = Topic.objects.get(article_id=tid) 
        #Topic.objects.remove(topic)

        #return topic
    
class TopicLinkManager():
    def create_topiclink(self, data):
        topiclink = TopicLink(source_id = data['source_id'],
                        target_id = data['target_id'],
                        title = data['title'],
                        description = data['description'],
                        wiki_link = data['wiki_link'],
                        score = data['score']) 

        topiclink.save()
        return topiclink

    #def delete_topiclink(seld, tid):
