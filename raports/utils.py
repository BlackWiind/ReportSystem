from raports.models import Raport


def get_queryset_dependent_group(user):
    groups = list(user.groups.values_list('name', flat=True))
    if 'user_creator' in groups:
        return Raport.objects.filter(creator=user)
