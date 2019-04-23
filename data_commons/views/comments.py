from data_commons.serializers.comments import CommentSerializer
from django_comments_xtd.models import XtdComment
from rest_framework import viewsets

from django_comments_xtd.api.views import CommentCreate

CommentCreate.queryset = XtdComment.objects.none()


class CommentViewSet(viewsets.ModelViewSet):
    queryset = XtdComment.objects.all()
    serializer_class = CommentSerializer
