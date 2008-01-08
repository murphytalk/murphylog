
def free_comment_context_processor(request):
    """
    return a context processor which looks for a dict in request object's META dict by using key murphylog_context
    this processor is implemented to pass extra context to contrib.comments.view.comments.post_free_comment
    """
    if request.META.has_key("murphylog_context"):
        context_extras = request.META["murphylog_context"]
    else:
        context_extras = {}

    return context_extras
