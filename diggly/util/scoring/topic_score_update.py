from diggly.models import Topic, TopicLink


# 2015 wiki_diggly
# prototype v1

def update_score(tid_src, tid_dst):
    try:
        topic_src = Topic.objects.get(article_id=tid_src)  # source topic
        topic_dst = Topic.objects.get(article_id=tid_dst)  # dest topic
        CURVE_FACTOR = 1
        POSITIVE_WEIGHT = 0.1
        NEGATIVE_WEIGHT = 0.05
        topiclinks = topic_src.linked_topics  # list
        linked_topics = []

        for tl in topiclinks:
            tlink = TopicLink.objects.get(source_id=topic_src.article_id, target_id=tl.target_id)
            new_score = tl.user_score - (NEGATIVE_WEIGHT/(tl.score_keeper * CURVE_FACTOR))

            if tlink.target_id.article_id == topic_dst.article_id:
                new_score = tl.user_score + (POSITIVE_WEIGHT/(tl.score_keeper * CURVE_FACTOR))
                tlink.score_keeper+=1

            tlink.user_score = new_score
            tlink.save()
            linked_topics.append(tlink)

        topic_src.linked_topics = linked_topics
        topic_src.save()

    except Exception as E:
        print str(E)


    # var total = 1000;
    # var t = [1000];

    # var inc = 1000;
    # var cf = 1;


    # for (var n = 1; n <= 1000; n++) {
    #     var temp = ( (inc) / (n * cf) ); #"n" can be a field added to TopicLink "score_number"
    #     var oldTotal = total;
    #     total = total + temp;

    #     console.log('\n\nTotal: ' + total);
    #     console.log('Increase: ' + (total - oldTotal));