from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import DetailView
from django.views.generic.list import BaseListView
from movies.models import Filmwork, RoleType


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def _aggregate_person(role):
        return ArrayAgg(
            'personfilmwork__person__full_name',
            filter=Q(personfilmwork__role=role),
            distinct=True
        )

    @classmethod
    def get_queryset(cls):
        return Filmwork.objects.values().annotate(
            genres=ArrayAgg('genres__name', distinct=True),
            writers=cls._aggregate_person(role=RoleType.WRITER),
            actors=cls._aggregate_person(role=RoleType.ACTOR),
            directors=cls._aggregate_person(role=RoleType.DIRECTOR)
        )

    @staticmethod
    def render_to_response(context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        data = self.get_queryset()

        paginator, page, object_list, is_paginated = self.paginate_queryset(data, self.paginate_by)
        total_pages = paginator.num_pages
        prev_page = page.previous_page_number() if page.has_previous() else None
        next_page = page.next_page_number() if page.has_next() else None

        context = {
            'count': paginator.count,
            'total_pages': total_pages,
            'prev': prev_page,
            'next': next_page,
            'results': list(object_list)
        }
        return context


class MovieDetailsApi(MoviesApiMixin, DetailView):
    pk_url_kwarg = 'id'

    def get_context_data(self, *, object_list=None, **kwargs):
        return kwargs['object']
