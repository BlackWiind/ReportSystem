from django import template

register = template.Library()


@register.simple_tag()
def get_buttons(user):
    groups = user.groups.all()
    possible_actions = {}
    for group in groups:
        possible_actions = {action.verbose_name: action.new_status.pk for
                            action in group.customgroups.possible_actions.all()}
    return possible_actions
