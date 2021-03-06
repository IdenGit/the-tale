# coding: utf-8

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _


from the_tale.accounts.models import Account, ChangeCredentialsTask, Award, ResetPasswordTask, RandomPremiumRequest


class AccountChangeForm(forms.ModelForm):
    nick = forms.RegexField( label=_("Username"), max_length=30, regex=r"^[\w.@+-]+$",
                             help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
                             error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    password = ReadOnlyPasswordHashField(label=_("Password"),
                                         help_text=_("Raw passwords are not stored, so there is no way to see "
                                                     "this user's password, but you can change the password "
                                                     "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = Account
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        super(AccountChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial['password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        return Account.objects.normalize_email(email) if email else None


class AccountAdmin(DjangoUserAdmin):
    form = AccountChangeForm

    list_display = ('id', 'email', 'nick', 'action_id', 'referral_of', 'referer_domain', 'last_login', 'created_at')
    ordering = ('-created_at',)

    search_fields = ('nick', 'email')
    fieldsets = ( (None, {'fields': ('nick', 'password')}),
                  (_('Personal info'), {'fields': ('email',
                                                   'referer_domain',
                                                   'referer',
                                                   'action_id')}),
                  (_('Permissions'), {'fields': ('is_fast',
                                                 'is_bot',
                                                 'is_active',
                                                 'is_staff',
                                                 'is_superuser',
                                                 'groups',
                                                 'user_permissions')}),
                  (_('Settings'), {'fields': ('personal_messages_subscription', 'news_subscription')}),
                  (_('Data'), {'fields': ('permanent_purchases',)}),
                  (_('Important dates'), {'fields': ('last_login',
                                                    'active_end_at', 'premium_end_at',
                                                    'ban_game_end_at', 'ban_forum_end_at')}),
                  (_('Additional info'), {'fields': ('might',
                                                     'actual_bills')}),)

    readonly_fields = list(DjangoUserAdmin.readonly_fields) + ['referer', 'referer_domain', 'referral_of', 'referrals_number']


class ChangeCredentialsTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'account', 'old_email', 'new_email')
    list_filter = ('state',)


class AwardAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'type', 'created_at')
    list_filter = ('type',)

class ResetPasswordTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'is_processed', 'uuid', 'created_at')


class RandomPremiumRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'initiator', 'receiver', 'state', 'created_at')


admin.site.register(Account, AccountAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(ChangeCredentialsTask, ChangeCredentialsTaskAdmin)
admin.site.register(ResetPasswordTask, ResetPasswordTaskAdmin)
admin.site.register(RandomPremiumRequest, RandomPremiumRequestAdmin)
