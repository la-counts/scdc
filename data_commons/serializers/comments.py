from django_comments_xtd.models import XtdComment
from rest_framework import serializers


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = XtdComment
        fields = (
            'user', 'user_name', 'user_email',
            'comment', 'submit_date',
            'thread_id', 'parent_id', 'level', 'order', 'followup'
        )
