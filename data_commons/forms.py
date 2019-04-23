from django import forms
from django_comments_xtd.forms import XtdCommentForm


class CommentForm(XtdCommentForm):
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(widget=forms.HiddenInput, required=False)
        self.fields['email'] = forms.EmailField(widget=forms.HiddenInput, required=False)
        self.fields['url'] = forms.URLField(widget=forms.HiddenInput, required=False)
