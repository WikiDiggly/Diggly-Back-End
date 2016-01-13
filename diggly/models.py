from django.db import models
from django.http import Http404
from djangotoolbox.fields import ListField, EmbeddedModelField

class Topic(models.Model):
    article_title = models.CharField(max_length = 256, null=False)
    article_id = models.BigIntegerField(primary_key=True, null=False)
    summary = models.CharField(max_length = 1028, null=False)
    description = models.TextField(null=False)
    wiki_link = models.URLField(null=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True) 
   
class TopicLink(models.Model):
    source_id = models.ForeignKey('Topic', related_name='topiclink_source', to_field='article_id')
    target_id = models.ForeignKey('Topic', related_name='topiclink_target', to_field='article_id')
    title = models.CharField(max_length = 256)
    description = models.TextField()
    wiki_link = models.URLField()
    score = models.DecimalField(max_digits=6, decimal_places=5)

#class SectionLink(models.Model):
#    section_id = models.AutoField(primary_key=True) 
#    section_title = models.CharField(max_length = 256)
#    source_id = models.ForeignKey('Topic', related_name='sectionlink_source', to_field='article_id')
#    redirect_article_id = models.ForeignKey('Topic', related_name='sectionlink_article', to_field='article_id', null=True)
#    section_wiki_link = models.URLField()
#    score = models.DecimalField(max_digits=6, decimal_places=5)
    #outlinks = ListField(EmbeddedModelField('Topic'))

#class TopicExplorer(models.Model):
#    main_topic = models.ForeignKey('Topic', related_name='topicexplorer_main', to_field='article_id')
#    linked_topics = models.ForeignKey('TopicLink', related_name='topicexplored_rel', to_field='target_id')

