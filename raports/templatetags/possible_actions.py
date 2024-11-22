from django import template

register = template.Library()


@register.simple_tag()
def get_buttons(user, status):
    groups = user.groups.all()
    possible_actions = {}
    for group in groups:
        for action in group.customgroups.possible_actions.all():
            if action.required_status:
                if action.required_status == status:
                    possible_actions[action.verbose_name] = action.new_status.pk
            else:
                possible_actions[action.verbose_name] = action.new_status.pk
    return possible_actions
