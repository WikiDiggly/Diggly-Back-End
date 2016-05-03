from diggly.util.serializers.forms import StringListField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ModelMultipleChoiceField
from django.forms.models import model_to_dict
from djangotoolbox.fields import ListField, EmbeddedModelField
from flufl.enum import Enum


#topic link enums
class TopicLinkType(Enum):
    article = 1
    section = 2 #TODO: implement section vs. article tagging in Topic objects

class OutlinkListField(ListField):
    def formfield(self, **kwargs):
        return models.Field.formfield(self, StringListField, **kwargs)

class LinkedTopicsField(ListField):
    def formfield(self, **kwargs):
        return ModelMultipleChoiceField(queryset=TopicLink.objects.all(), to_field_name="target_id", required=False, **kwargs)

class RecentTopicsField(ListField):
    def formfield(self, **kwargs):
        return ModelMultipleChoiceField(queryset=Topic.objects.all(), to_field_name="article_id", required=False, **kwargs)

#diggly application models
class Topic(models.Model):
    article_title = models.CharField(max_length = 256, null=False)
    article_id = models.BigIntegerField(primary_key=True, null=False)
    summary = models.CharField(max_length = 1028, null=False)
    description = models.TextField(null=False)
    wiki_link = models.URLField(null=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True) 
    visit_counter = models.BigIntegerField(null=False, default=0)
    linked_topics = LinkedTopicsField(EmbeddedModelField('TopicLink'), blank=True, null=True)
    outlinks = OutlinkListField(models.CharField)

    class Meta:
        ordering = ['article_title']

    def to_json(self):
        return dict(
            article_id=self.article_id, 
            article_title=self.article_title,
            summary=self.summary, 
            description=self.description,
            wiki_link=self.wiki_link,
            visit_counter=self.visit_counter,
            linked_topics=self.convert_linked_topics())

    def convert_linked_topics(self):
        res = []
        if self.linked_topics == None:        
            return res

        for tl in self.linked_topics:
            #convert topiclink object to dictionary, exclude AutoField 
            res.append(model_to_dict(tl, exclude=tl._meta.fields[0].name))
    
        res_sorted = sorted(res, key=lambda instance: instance['score'], reverse=True)    
        return res_sorted

    def get_linked_topics(self):
        topic_links = TopicLink.objects.filter(source_id=self.article_id)
        sorted_tl = sorted(topic_links, key=lambda instance: instance.score, reverse=True)
        self.linked_topics = sorted_tl[0:7]
        self.save()

        return self.linked_topics

    def clean(self):
        #validate all linked_topics source_id
        if self.linked_topics != None:
            for tl in self.linked_topics:
                if self.article_id != tl.source_id.article_id:
                    raise ValidationError('Linked topic source_id is different from main topic article_id')

    def __unicode__(self):
        return self.article_title

class TopicLink(models.Model):
    source_id = models.ForeignKey('Topic', related_name='topiclink_source', to_field='article_id')
    target_id = models.ForeignKey('Topic', related_name='topiclink_target', to_field='article_id')
    title = models.CharField(max_length = 256)
    description = models.TextField()
    wiki_link = models.URLField()
    base_score = models.FloatField(validators = [MinValueValidator(-1.0), MaxValueValidator(1.0)])
    user_score = models.FloatField(validators = [MinValueValidator(-1.0), MaxValueValidator(1.0)])
    score = models.FloatField(validators = [MinValueValidator(-1.0), MaxValueValidator(1.0)])
    score_keeper = models.BigIntegerField(default = 1) #number of scores recorded (1 by default) #need not be returned in JSON (to_json)

    class Meta:
        ordering = ['description']

    def to_json(self):
         return dict(
             source=self.source_id.article_id,
             target=self.target_id.article_id,
             description=self.description,
             base_score=self.base_score,
             user_score=self.user_score,
             score=self.score,
             score_keeper=self.score_keeper)

    def __unicode__(self):
        return self.description

class TopicRedirect(models.Model):
    source_id = models.BigIntegerField(primary_key=True, null=False)
    redirect_topic = models.ForeignKey('Topic', related_name='redirect_to', to_field='article_id')

    class Meta:
        ordering = ['source_id']

    def __unicode__(self):
        return str(self.source_id)

class FeaturedTopics(models.Model):
    recent_topics = RecentTopicsField(EmbeddedModelField('Topic'), blank=True, null=False)
    trending_topic = models.ForeignKey('Topic', related_name='trending_source', to_field='article_id', null=False)
    popular_topic = models.ForeignKey('Topic', related_name='popular_source', to_field='article_id', null=False)
    recent_topic_timestamp = models.DateTimeField(auto_now_add=True) #no modification
