from reports.models import Report
from users.models import User
from users.tasks import notification_api_connect



def create_new_notification(model_id:int):
    report = Report.objects.get(pk=model_id)
    current_status = report.status
    list_of_users = [report.creator, report.responsible]
    match current_status.name:
        case 'report_created':
            list_of_users.extend(User.objects.filter(custom_permissions__name='curator',
                                                     curators_group=report.curators_group).all())
        # case 'chief_medical_1':
        #     list_of_users.extend(User.objects.filter(custom_permissions__name='chief_doctor').all())
        # case 'purchasing_chief':
        #     list_of_users.extend(User.objects.filter(custom_permissions__name='head_of_purchasing_department').all())
        case 'purchasing_department_1':
            list_of_users.append(report.assigned_purchasing_specialist)
        # case 'economist_1':
        #     list_of_users.extend(User.objects.filter(custom_permissions__name='economist_1').all())
        # case 'deputy_for_economics':
        #     list_of_users.extend(User.objects.filter(custom_permissions__name='deputy_for_economics').all())
        # case 'economist_2':
        #     list_of_users.extend(User.objects.filter(custom_permissions__name='economist_2').all())
        # case 'chief_accountant':
        #     list_of_users.extend(User.objects.filter(custom_permissions__name='chief_accountant').all())
        case 'purchasing_department_2':
            list_of_users.append(report.assigned_purchasing_specialist)
        case _:
            list_of_users.extend(User.objects.filter(custom_permissions__statuses=current_status).distinct())
    message_text = (f'Изменение в рапорте №{report.pk}.\n'
                    f' Текщий статус {report.status.visible_name}') if not report.closed else 'Рапорт закрыт.'
    for user in set(list_of_users):
        if user:
            notification_api_connect.delay(user.pk, report.pk, message_text)