from django.contrib.auth.models import User
from django.db import models
from django.utils.text import gettext_lazy as _


class BaseModel(models.Model):

    class Meta:
        abstract = True

    created_by = models.ForeignKey(
        User, related_name="%(app_label)s_%(class)s_created_by", verbose_name=_("Criado por"), null=True,
        blank=True, on_delete=models.DO_NOTHING
    )

    updated_by = models.ForeignKey(
        User, related_name="%(app_label)s_%(class)s_updated_by", verbose_name=_("Atualizado por"), null=True,
        blank=True, on_delete=models.DO_NOTHING
    )

    creation_date = models.DateTimeField(_('Data de criação'), null=True, auto_now_add=True)
    last_update = models.DateTimeField(_('Última atualização'), null=True, auto_now=True)
    is_active = models.BooleanField(_('Ativo'), null=False, default=True)
