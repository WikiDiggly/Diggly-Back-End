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

    def to_json(self):
        return dict(
            article_id=self.article_id, 
            article_title=self.article_title,
            summary=self.summary, 
            description=self.description,
            wiki_link=self.wiki_link)
   
class TopicLink(models.Model):
    source_id = models.ForeignKey('Topic', related_name='topiclink_source', to_field='article_id')
    target_id = models.ForeignKey('Topic', related_name='topiclink_target', to_field='article_id')
    description = models.TextField()
    score = models.DecimalField(max_digits=6, decimal_places=5)

    def to_json(self):
        return dict(
            source=self.source.article_id,
            target=self.target.article_id,
            description=self.description,
            score=self.score)

class SectionLink(models.Model):
    section_id = models.AutoField(primary_key=True) 
    section_title = models.CharField(max_length = 256)
    source_id = models.ForeignKey('Topic', related_name='sectionlink_source', to_field='article_id')
    redirect_article_id = models.ForeignKey('Topic', related_name='sectionlink_article', to_field='article_id', null=True)
    section_wiki_link = models.URLField()
    score = models.DecimalField(max_digits=6, decimal_places=5)
    #outlinks = ListField(EmbeddedModelField('Topic'))

    def to_json(self):
        return dict(
            section_id=self.section_id,
            section_title=self.section_title,
            source_article_id=self.source_article_id,
            main_article=self.main_article_id,
            section_wiki_link=self.section_wiki_link,
            score=self.score)
