from rest_framework.response import Response
from rest_framework import status

from flowback.common.pagination import get_paginated_response
from flowback.group.selectors import group_kanban_entry_list
from flowback.group.services import group_kanban_entry_create, group_kanban_entry_update, group_kanban_entry_delete

from flowback.kanban.views import KanbanEntryListApi, KanbanEntryCreateAPI, KanbanEntryUpdateAPI, KanbanEntryDeleteAPI


class GroupKanbanEntryListAPI(KanbanEntryListApi):
    def get(self, request, group_id: int):
        serializer = self.FilterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        entries = group_kanban_entry_list(fetched_by=request.user, group_id=group_id, **serializer.validated_data)
        return get_paginated_response(pagination_class=self.Pagination,
                                      serializer_class=self.OutputSerializer,
                                      queryset=entries,
                                      request=request,
                                      view=self)


class GroupKanbanEntryCreateAPI(KanbanEntryCreateAPI):
    def get(self, request, group_id: int):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_kanban_entry_create(group_id=group_id, fetched_by_id=request.user.id, **serializer.validated_data)
        return Response(status=status.HTTP_200_OK)


class GroupKanbanEntryUpdateAPI(KanbanEntryUpdateAPI):
    def post(self, request, group_id: int):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_kanban_entry_update(group_id=group_id,
                                  fetched_by_id=request.user.id,
                                  entry_id=serializer.validated_data.pop('entry_id'),
                                  data=serializer.validated_data)
        return Response(status=status.HTTP_200_OK)


class GroupKanbanEntryDeleteAPI(KanbanEntryDeleteAPI):
    def post(self, request, group_id: int):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_kanban_entry_delete(group_id=group_id, fetched_by_id=request.user.id, **serializer.validated_data)
        return Response(status=status.HTTP_200_OK)
