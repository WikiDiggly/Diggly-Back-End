from diggly.models import Topic, TopicLink, TopicRedirect
from rest_framework import serializers


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('article_title', 'article_id', 'summary', 'description', 'wiki_link')


class TopicLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicLink
        fields = ('source_id', 'target_id', 'description', 'base_score', 'user_score', 'score')


class TopicManager():
    def create_topic(self, data):
        topic = Topic(article_title=data['article_title'],
                      article_id=data['article_id'],
                      description=data['description'],
                      summary=data['summary'],
                      wiki_link=data['wiki_link'],
                      linked_topics=data['linked_topics'])

        topic.save()
        return topic

    def update_topic(self, data):
        # detect which topic is being updated (article_id?)
        # detect what fields are bieng updated (ignore empty/null fields)... take non-null/non-empty fields and update those only, leaving others untouched.
        topic = Topic.objects.get(article_id=data['article_id'])  # get the topic being edited/updated by id

        if (data['article_title'] and data['article_title'] != ""):
            topic.article_title = data['article_title']

        if (data['description'] and data['description'] != ""):
            topic.description = data['description']

        if (data['summary'] and data['summary'] != ""):
            topic.summary = data['summary']

        if (data['wiki_link'] and data['wiki_link'] != ""):
            topic.wiki_link = data['wiki_link']

        if (data['linked_topics'] and data['linked_topics']):
            topic.linked_topics = data['linked_topics']

        topic.save()
        return topic

    # delete topic and all associated linked topics
    def delete_topic(self, tid):
        topic = Topic.objects.get(article_id=tid)
        topiclinks = topic.topiclink_source.all()

        tlm = TopicLinkManager()
        tlm.delete_mul_topiclink(topiclinks)
        Topic.objects.remove(topic)

        return True


class TopicLinkManager():
    def create_topiclink(self, data):
        if data['source_id'] == data['target_id']:
            print "[LOG] Prevented creation of topiclink with source_id == target_id"
            return None

        topiclink = TopicLink(source_id = data['source_id'],
                        target_id = data['target_id'],
                        title = data['title'],
                        description = data['description'],
                        wiki_link = data['wiki_link'],
                        base_score = data['base_score'],
                        user_score = data['user_score'],
                        score = data['score'])  

        topiclink.save()
        return topiclink

    def delete_topiclink(self, tid):
        topiclink = TopicLink.objects.get(source_id=tid)
        TopicLink.objects.remove(TopicLink)

        return True

    def delete_mul_topiclinks(self, listtl):
        for topiclink in listtl:
            delete_topiclink(topiclink.article_id)

        return True

        # def delete_mul_topiclinks(self, listtl):


class TopicRedirectManager():
    def create_topic_redirect(self, data):
        topic_redirect = TopicRedirect(source_id=data['source_id'],
                                       redirect_topic=data['redirect_topic'])

        topic_redirect.save()
        return topic_redirect
