from django.db.models import Q
from django.http import JsonResponse

from users.models import User


class MainLoader:

    def __init__(self, what_are_looking: str):
        self.what_are_looking = what_are_looking

    def _get_data(self)->list:
        pass

    def search(self) -> JsonResponse:
        return JsonResponse({
            'results': self._get_data(),
            'pagination': {
                'more': False
            }
        })


class SearchUsers(MainLoader):

    def _get_data(self) ->list:
        if self.what_are_looking == '':
            return []
        result = User.objects.filter(Q(first_name__icontains=self.what_are_looking) |
                                          Q(last_name__icontains=self.what_are_looking) |
                                          Q(surname__icontains=self.what_are_looking)).iterator()
        list_for_return = []
        for item in result:
            if len(list_for_return) < 10:
                list_for_return.append({'id': item.pk, 'text': item.__str__()})
            else:
                break
        return list_for_return