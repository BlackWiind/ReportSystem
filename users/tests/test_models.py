from django.test import TestCase

from users.models import Department, User


class DepartmentModelCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Department.objects.create(name='Отдел информации')

    def test_name_label(self):
        department = Department.objects.get(id=1)
        field_label = department._meta.get_field('name').verbose_name
        self.assertEqual('Название отдела', field_label)

    def test_name_max_length(self):
        department = Department.objects.get(id=1)
        field_max_length = department._meta.get_field('name').max_length
        self.assertEqual(255, field_max_length)

    def test_name_str_method(self):
        department = Department.objects.get(id=1)
        expected_name = '%s' % (department.name)
        self.assertEqual(expected_name, str(department))

    def test_verbose_name(self):
        department = Department.objects.get(id=1)
        verbose_name = department._meta.verbose_name
        self.assertEqual('Название отдела', verbose_name)

    def test_verbose_name_plural(self):
        department = Department.objects.get(id=1)
        verbose_name_plural = department._meta.verbose_name_plural
        self.assertEqual('Названия отделов', verbose_name_plural)


class UserModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        department = Department.objects.create(name='Отдел информации')
        User.objects.create(username='user1', first_name='Иван', last_name='Иванов',
                            surname='Иванович', department=department)

    def test_surname_name_max_length(self):
        user = User.objects.get(id=1)
        field_max_length = user._meta.get_field('surname').max_length
        self.assertEqual(255, field_max_length)

    def test_department(self):
        user = User.objects.get(id=1)
        users_department = user.department.name
        self.assertEqual('Отдел информации', users_department)

    def test_speciality_verbose_name(self):
        user = User.objects.get(id=1)
        users_department = user._meta.get_field('department').verbose_name
        self.assertEqual('Отдел', users_department)

    def test_user_str_method(self):
        user = User.objects.get(id=1)
        expected_name = '%s %s %s' % (user.last_name, user.first_name, user.surname)
        self.assertEqual(expected_name, str(user))

    def test_verbose_name(self):
        user = User.objects.get(id=1)
        name = user._meta.verbose_name
        self.assertEqual('Пользователь', name)

    def test_verbose_name_plural(self):
        user = User.objects.get(id=1)
        name = user._meta.verbose_name_plural
        self.assertEqual('Пользователи', name)