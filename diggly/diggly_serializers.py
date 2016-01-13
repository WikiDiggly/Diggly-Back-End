from models import *
from rest_framework import serializers

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('article_title', 'article_id', 'summary', 'description', 'wiki_link')

class TopicLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicLink
        fields = ('source_id', 'target_id', 'description', 'score')

#class SectionLinkSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = SectionLink
#        fields = ('source_id', 'section_title', 'redirect_article_id', 'section_wiki_link', 'score')
                                                                                         
#converts topic and topiclink or sectionlink to json object
class TopicExploreSerializer(serializers.Serializer):
    #article_title = serializers.CharField(required=True, allow_blank=False, max_length=256)
    #article_id = serializers.IntegerField(read_only=True)
    #description = serializers.CharField(required=True, allow_blank=False)
    #summary = serializers.CharField(required=True, allow_blank=False, max_length=1028)
    #wiki_link = serializers.URLField(required=True)
    #links = serializers.ListField() #TODO: validate child arguments?

    m_topic = Topic
    l_topics = TopicLink

    def create(self, topicObj, linkedObj):
        tExplorer = TopicExplorer(main_topic = m_topic, linked_topics = l_topics )     
        return tExplorer

