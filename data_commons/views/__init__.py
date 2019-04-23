from django.shortcuts import render, get_object_or_404
from django.db.transaction import atomic
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

from registration.backends.hmac.views import RegistrationView

from apps.profiles.forms import RegistrationForm


def styleguide(request):
    return render(request, 'styleguide.html')

def page_not_found(request):
    return render(request, '404.html', status=404)

def server_error(request):
    return render(request, '500.html', status=500)


#Add html messages
class CustomRegistrationView(RegistrationView):
    def send_activation_email(self, user):
        """
        Send the activation email. The activation key is the username,
        signed using TimestampSigner.
        """
        activation_key = self.get_activation_key(user)
        context = self.get_email_context(activation_key)
        context.update({
            'user': user,
        })
        subject = render_to_string(self.email_subject_template,
                                   context)
        # Force subject to a single line to avoid header-injection
        # issues.
        subject = ''.join(subject.splitlines())
        html_message = render_to_string(self.email_body_template,
                                   context)
        message = strip_tags(html_message.split('</head>', 1)[-1])
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL, html_message=html_message)


#rollback if registration fails
register = atomic(CustomRegistrationView.as_view(
    form_class = RegistrationForm,
))
