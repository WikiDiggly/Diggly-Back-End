from diggly.models import Topic, TopicLink


# 2015 wiki_diggly
# prototype v1

def update_score(tid_src, tid_dst):
    try:
        topic_src = Topic.objects.get(article_id=tid_src)  # source topic
        topic_dst = Topic.objects.get(article_id=tid_dst)  # dest topic
        POSITIVE_WEIGHT = 0.1
        NEGATIVE_WEIGHT = 0.05
        topiclinks = topic_src.linked_topics  # list
        linked_topics = []

        for tl in topiclinks:
            tlink = TopicLink.objects.get(source_id=topic_src.article_id, target_id=tl.target_id)
            new_score = tl.user_score - NEGATIVE_WEIGHT

            if tlink.target_id.article_id == topic_dst.article_id:
                new_score = tl.user_score + POSITIVE_WEIGHT

            tlink.user_score = new_score
            tlink.save()
            linked_topics.append(tlink)

        topic_src.linked_topics = linked_topics
        topic_src.save()

    except Exception as E:
        print str(E)
