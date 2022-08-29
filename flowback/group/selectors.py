# TODO groups, groupusers, groupinvites, groupuserinvites,
#  groupdefaultpermission, grouppermissions, grouptags, groupuserdelegates
import django_filters
from typing import Union
from django.db.models import Q
from flowback.common.services import get_object
from flowback.user.models import User
from flowback.group.models import Group, GroupUser, GroupUserInvite, GroupPermissions, GroupTags, GroupUserDelegate
from rest_framework.exceptions import ValidationError


def group_user_permissions(*,
                           group: id,
                           user: Union[User, int],
                           permissions: list[str] = None,
                           raise_exception=True) -> Union[GroupUser, bool]:
    if type(user) == int:
        user = get_object(User, user_id=user)
    permissions = permissions or []
    user = get_object(GroupUser, 'User is not in group', group=group, user=user)
    user_permissions = user.permission.values()

    # Check if admin permission is present
    if 'admin' in permissions or user.user.is_superuser:
        if user.is_admin or user.group.created_by == user.user or user.is_superuser:
            return user

        permissions.remove('admin')

    # Check if creator permission is present
    if 'creator' in permissions:
        if user.group.created_by == user.user or user.user.is_superuser:
            return user

        permissions.remove('creator')

    failed_permissions = [key for key in permissions if user_permissions[key] is False]
    if failed_permissions:
        if raise_exception:
            raise ValidationError('Permission denied')
        else:
            return False

    return user


class BaseGroupFilter(django_filters.FilterSet):
    joined = django_filters.NumberFilter(field_name='group_user__user', lookup_expr='exact')

    class Meta:
        model = Group
        fields = dict(id=['exact'],
                      name=['exact', 'icontains'],
                      direct_join=['exact'])


class BaseGroupUserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='user__username')

    class Meta:
        model = GroupUser
        fields = dict(user_id=['exact'],
                      username=['exact', 'icontains'],
                      is_delegate=['exact'],
                      is_admin=['exact'],
                      permission=['in'])


class BaseGroupUserInviteFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='user__username')
    username__icontains = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')

    class Meta:
        model = GroupUser
        fields = ['user']


class BaseGroupPermissionsFilter(django_filters.FilterSet):
    class Meta:
        model = GroupPermissions
        fields = ['role_name']


class BaseGroupTagsFilter(django_filters.FilterSet):
    class Meta:
        model = GroupTags
        fields = dict(tag_name=['exact', 'icontains'],
                      active=['exact'])


class BaseGroupUserDelegateFilter(django_filters.FilterSet):
    delegate_name__icontains = django_filters.CharFilter(field_name='delegate__username__icontains')
    tag_name = django_filters.CharFilter(field_name='tags__tag_name')
    tag_name__icontains = django_filters.CharFilter(field_name='tags__tag_name', lookup_expr='icontains')

    class Meta:
        model = GroupUserDelegate
        fields = ['delegate', 'tag']


def group_get_visible_for(user: User):
    query = Q(public=True) | Q(Q(public=False) | Q(group_user__user=user))
    return Group.objects.filter(query)


def group_list(*, fetched_by: User, filters=None):
    filters = filters or {}
    qs = group_get_visible_for(user=fetched_by).all()

    if filters.get('joined') is True:
        filters['joined'] = fetched_by.id

    return BaseGroupFilter(filters, qs).qs


def group_user_list(*, group: int, fetched_by: User, filters=None):
    group_user_permissions(group=group, user=fetched_by)
    filters = filters or {}
    qs = GroupUser.objects.filter(group_id=group).all()
    return BaseGroupUserFilter(filters, qs).qs


def group_user_invite_list(*, group: int, fetched_by: User, filters=None):
    group_user_permissions(group=group, user=fetched_by, permissions=['invite_user'])
    filters = filters or {}
    qs = GroupUserInvite.objects.filter(group_id=group).all()
    return BaseGroupUserFilter(filters, qs).qs


def group_permissions_list(*, group: int, fetched_by: User, filters=None):
    group_user_permissions(group=group, user=fetched_by)
    filters = filters or {}
    qs = GroupPermissions.objects.filter(group_id=group).all()
    return BaseGroupPermissionsFilter(qs, filters).qs


def group_tags_list(*, group: int, fetched_by: User, filters=None):
    filters = filters or {}
    group_user_permissions(group=group, user=fetched_by)
    query = Q(group_id=group, active=False)
    if group_user_permissions(group=group, user=fetched_by, permissions=['admin'], raise_exception=False):
        query = Q(group_id=group)

    qs = GroupTags.objects.filter(query).all()
    return BaseGroupTagsFilter(qs, filters).qs


def group_user_delegate_list(* group: int, fetched_by: User, filters=None):
    filters = filters or {}
    group_user_permissions(group=group, user=fetched_by)
    query = Q(group_id=group, delegator_id=fetched_by)

    qs = GroupUserDelegate.objects.filter(query).all()
    return BaseGroupUserDelegateFilter(qs, filters).qs
