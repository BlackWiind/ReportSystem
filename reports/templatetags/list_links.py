from django import template

register = template.Library()


@register.simple_tag()
def get_links(user):
    # groups = user.groups.all()
    # available_statuses = {}
    # for group in groups:
    #     available_statuses = {link.name: link.link for link in group.customgroups.links.all()}
    # return available_statuses
    m = user.custom_permissions.links.all()
    available_statuses = {link.name: link.link for link in m}
    print(m)
    return available_statuses