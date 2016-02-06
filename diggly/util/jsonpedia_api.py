import os
import requests
import random

from text_process import Text_Process
from .diggly_serializers import TopicCreator, TopicLinkCreator, TopicLinkSerializer
from ..models import Topic, TopicLink
