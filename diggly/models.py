from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ModelMultipleChoiceField
from django.forms.models import model_to_dict
from djangotoolbox.fields import ListField, EmbeddedModelField
#from .fields import LinkedTopicsMMCField

class LinkedTopicMMCFormField(ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = TopicLink.objects.all()
        super().__init__(*args, **kwargs)

#to allow use of ListField in django admin
class LinkedTopicsField(ListField):
    def formfield(self, **kwargs):
        return ModelMultipleChoiceField(queryset=TopicLink.objects.all(), required=False, **kwargs)

#diggly application models
class Topic(models.Model):
    article_title = models.CharField(max_length = 256, null=False)
    article_id = models.BigIntegerField(primary_key=True, null=False)
    summary = models.CharField(max_length = 1028, null=False)
    description = models.TextField(null=False)
    wiki_link = models.URLField(null=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True) 
    linked_topics = LinkedTopicsField(EmbeddedModelField('TopicLink'), blank=True, null=True)

    def to_json(self):
        return dict(
            article_id=self.article_id, 
            article_title=self.article_title,
            summary=self.summary, 
            description=self.description,
            wiki_link=self.wiki_link,
            linked_topics=self.convert_linked_topics())

    def convert_linked_topics(self):
        res = []
        if self.linked_topics == None:        
            return res

        for tl in self.linked_topics:
            #convert topiclink object to dictionary, exclude AutoField 
            res.append(model_to_dict(tl, exclude=tl._meta.fields[0].name))
    
        res_sorted = sorted(res, key=lambda instance: instance.score, reverse=True)    
        return res_sorted

    def clean(self):
        #validate all linked_topics source_id
        if self.linked_topics != None:
            for tl in self.linked_topics:
                if self.article_id != tl.source_id:
                    raise ValidationError('Linked topic source_id is different from main topic article_id') 

class TopicLink(models.Model):
    source_id = models.ForeignKey('Topic', related_name='topiclink_source', to_field='article_id')
    target_id = models.ForeignKey('Topic', related_name='topiclink_target', to_field='article_id')
    title = models.CharField(max_length = 256)
    description = models.TextField()
    wiki_link = models.URLField()
    score = models.FloatField()

    def to_json(self):
         return dict(
             source=self.source.article_id,
             target=self.target.article_id,
             description=self.description,
             score=self.score)

