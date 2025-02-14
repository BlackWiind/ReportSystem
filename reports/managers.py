from django.db import models

# class DraftQuerySet(models.QuerySet):
#     def not_closed(self):
#         return self.filter(closed=False)
#
#     def closed(self):
#         return self.filter(closed=True)
#
# class DraftManager(models.Manager):
#     def get_queryset(self):
#         return DraftQuerySet(self.model)
#
#     def not_closed(self, user):
#         if user.custom_permissions.name == 'head_of_department':
#             return self.get_queryset().not_closed().filter(creator__department=user.department)
#         return self.get_queryset().not_closed().filter(creator=user)
#
#     def closed(self):
#         return self.get_queryset().closed()


class ReportQuerySet(models.QuerySet):
    def get_drafts(self):
        return self.filter(draft=True)

    def get_reports(self):
        return self.filter(draft=False)

    def closed(self):
        return self.filter(closed=True)

    def not_closed(self):
        return self.filter(closed=False)

class ReportManager(models.Manager):
    def get_queryset(self):
        return ReportQuerySet(self.model)

    def not_closed_reports(self, user):
        my_set = self.get_queryset().get_reports().not_closed()
        if user.custom_permissions.name == 'head_of_department':
            return my_set.filter(creator__department=user.department)
        return my_set.filter(creator=user)

    def not_closed_draft(self, user):
        my_set = self.get_queryset().get_drafts().not_closed()
        if user.custom_permissions.name == 'head_of_department':
            return my_set.filter(creator__department=user.department)
        return my_set.filter(creator=user)

    def closed_reports(self, user):
        my_set = self.get_queryset().get_reports().closed()
        if user.custom_permissions.name == 'head_of_department':
            return my_set.filter(creator__department=user.department)
        return my_set.filter(creator=user)

    def closed_drafts(self, user):
        my_set = self.get_queryset().get_drafts().closed()
        if user.custom_permissions.name == 'head_of_department':
            return my_set.filter(creator__department=user.department)
        return my_set.filter(creator=user)
