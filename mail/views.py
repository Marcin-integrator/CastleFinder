# sendemail/views.py
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from validate_email import validate_email
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMessage
import threading
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import generate_token

from .forms import ContactForm
from profiles.models import Profile


def contactView(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, from_email, ['janou@interia.pl'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('contact')
    messages.success(request, 'Success! Thank you for your message.')
    return render(request, "contact_form.html", {'form': form})


def successView(request):
    messages.success(request, 'Success! Thank you for your message.')


class EmailThread(threading.Thread):

    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'small_change_password_form.html')

    def post(self, request):

        email = request.POST.get('email')
        context = {
            'values': request.POST
        }

        if not validate_email(email):
            messages.error(request, 'Please supply a valid email')
            return render(request, 'small_change_password_form.html', context)

        current_site = get_current_site(request)
        profile_user = Profile.objects.filter(email=email)
        # user = User.objects.filter(username=str(Profile.objects.filter(email=email)[0].user))
        user = User.objects.filter(email=email)
        if user.exists():
            email_subject = '[Reset your Password]'
            message = render_to_string('mail/reset_mail.html',
                                       {
                                           'domain': current_site.domain,
                                           'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                                           'token': PasswordResetTokenGenerator().make_token(user[0])
                                       }
                                       )
            MAIL_FROM = 'janouinteria@gmail.com'

            email_message = EmailMessage(
                email_subject,
                message,
                MAIL_FROM,
                [email]
            )

            # send_mail(email_subject, message, 'janouinteria@gmail.com', [email])
            EmailThread(email_message).start()

            # email_contents = {
            #     'user': user[0],
            #     "domain": current_site.domain,
            #     "uid": urlsafe_base64_encode(force_bytes(user[0].pk)),
            #     "token": PasswordResetTokenGenerator().make_token(user[0])
            # }
            #
            # link = reverse('reset_password', kwargs={
            #     'uidb64': email_contents['uid'], 'token': email_contents['token']})
            #
            # email_subject = "Password reset instructions"
            #
            # reset_url = 'http://'+current_site.domain+link
            #
            # email = EmailMessage(
            #     email_subject, "Hi there, please click link below to reset your password \n" + reset_url,
            #     "noreply@castles.com",
            #     [email]
            # )
            #
            # email.send(fail_silently=False)

            messages.success(request, 'We have sent you an email to reset your password')

        return render(request, 'small_change_password_form.html')


class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        return render(request, 'reset_password.html')

    def post(self, request, token):
        return render(request, 'reset_password.html')


class SetNewPasswordView(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(
                    request, 'Password reset link, is invalid, please request a new one')
                return render(request, 'small_change_password_form.html')

        except DjangoUnicodeDecodeError as identifier:
            messages.success(
                request, 'Invalid link')
            return render(request, 'small_change_password_form.html')

        return render(request, 'mail/reset_pass.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
            'has_error': False
        }

        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if len(password) < 6:
            messages.add_message(request, messages.ERROR,
                                 'passwords should be at least 6 characters long')
            context['has_error'] = True
        if password != password2:
            messages.add_message(request, messages.ERROR,
                                 'passwords don`t match')
            context['has_error'] = True

        if context['has_error']:
            return render(request, 'mail/reset_pass.html', context)

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()

            messages.success(
                request, 'Password reset success, you can login with new password')

            return redirect('login')

        except DjangoUnicodeDecodeError as identifier:
            messages.error(request, 'Something went wrong')
            return render(request, 'mail/reset_pass.html', context)

        # return render(request, 'auth/set-new-password.html', context)
