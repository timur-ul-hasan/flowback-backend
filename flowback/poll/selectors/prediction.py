import django_filters
from django.db import models
from django.db.models import Avg, When, F, Case, Count, Q, Exists, Subquery, OuterRef
from django.db.models.lookups import LessThan
from django.utils import timezone

from flowback.group.selectors import group_user_permissions
from flowback.poll.models import PollPredictionStatement, PollPrediction, PollPredictionStatementVote
from flowback.user.models import User


class BasePollPredictionStatementFilter(django_filters.FilterSet):
    proposals = django_filters.NumberFilter(field_name='pollpredictionstatementsegment__proposal', lookup_expr='in')
    description = django_filters.CharFilter(lookup_expr='icontains')
    created_by_id = django_filters.NumberFilter(field_name='created_by__user_id', lookup_expr='exact')
    user_prediction_exists = django_filters.BooleanFilter(lookup_expr='isnull', exclude=True)
    user_vote_exists = django_filters.BooleanFilter(lookup_expr='isnull', exclude=True)


    class Meta:
        model = PollPredictionStatement
        fields = dict(id=['exact'],
                      poll_id=['exact'])


def poll_prediction_statement_list(*, fetched_by: User, group_id: int, filters=None):
    filters = filters or {}
    group_user = group_user_permissions(group=group_id, user=fetched_by)

    # Annotations
    score = Case(When(LessThan(F('end_date'), timezone.now()),
                 then=Avg('pollprediction__score')),
                 default=None, output_field=models.FloatField)
    vote_yes = Count(F('pollpredictionstatementvote'), filter=Q(pollpredictionstatementvote__vote=True))
    vote_no = Count(F('pollpredictionstatementvote'), filter=Q(pollpredictionstatementvote__vote=False))
    user_prediction = Subquery(PollPrediction.objects.filter(prediction_statement=OuterRef('pk'),
                                                             created_by=fetched_by).first())
    user_vote = Subquery(PollPredictionStatementVote.objects.filter(prediction_statement=OuterRef('pk'),
                                                                    created_by=fetched_by).first())

    qs = PollPredictionStatement.objects.filter(poll__created_by__group_id=group_id
                                                ).annotate(score=score,
                                                           vote_yes=vote_yes,
                                                           vote_no=vote_no,
                                                           user_prediction=user_prediction,
                                                           user_vote=user_vote
                                                           ).all()

    return BasePollPredictionStatementFilter(filters, qs).qs


# poll_prediction_list
class BasePollPredictionFilter(django_filters.FilterSet):
    created_by_id = django_filters.NumberFilter(field_name='created_by__user_id')

    class Meta:
        model = PollPrediction
        fields = dict(id=['exact'],
                      prediction_statement_id=['exact'],
                      score=['exact', 'lt', 'gt'],
                      created_at=['lt', 'gt'])


def poll_prediction_list(*, fetched_by: User, group_id: int = None, filters=None):
    filters = filters or {}
    group_user_permissions(group=group_id, user=fetched_by)

    qs = PollPrediction.objects.filter(prediction_statement__created_by__group_id=group_id).all()
    return BasePollPredictionFilter(filters, qs).qs
