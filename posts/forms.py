from django import forms
from django.db.models import Q
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _


class PostFilterForm(forms.Form):
    """Collects and applies the post-list filters (tag, year, month, order, search)."""

    tag = forms.CharField(required=False, widget=forms.Select(choices=[]))
    year = forms.CharField(required=False, widget=forms.Select(choices=[]))
    month = forms.CharField(required=False, widget=forms.Select(choices=[]))
    order = forms.ChoiceField(
        required=False,
        initial='newest',
        choices=[
            ('newest', _('Más recientes')),
            ('oldest', _('Más antiguos')),
            ('az', 'A → Z'),
            ('za', 'Z → A'),
        ],
    )
    q = forms.CharField(required=False)

    def __init__(self, data=None, lang='es', all_tags=None, all_years=None, all_months=None, **kwargs):
        super().__init__(data, **kwargs)
        self.lang = lang

        tag_choices = [('', _('Todos los temas'))]
        if all_tags is not None:
            tag_choices += [(tag.slug, tag.name) for tag in all_tags]
        self.fields['tag'].widget.choices = tag_choices

        year_choices = [('', _('Todos'))]
        if all_years is not None:
            year_choices += [(str(d.year), str(d.year)) for d in all_years]
        self.fields['year'].widget.choices = year_choices

        month_choices = [('', _('Todos'))]
        if all_months is not None:
            month_choices += [
                (str(d.month), date_format(d, 'F').capitalize())
                for d in all_months
            ]
        self.fields['month'].widget.choices = month_choices

    def filter_queryset(self, posts):
        """Apply filters and ordering to the provided queryset."""
        if not self.is_valid():
            return posts.ordered(self.lang, 'newest')

        data = self.cleaned_data
        order = data.get('order') or 'newest'
        posts = posts.ordered(self.lang, order)

        if data.get('tag'):
            posts = posts.filter(tags__slug=data['tag'])

        year = data.get('year')
        if year and year.isdigit():
            posts = posts.filter(created_at__year=int(year))

        month = data.get('month')
        if month and month.isdigit():
            posts = posts.filter(created_at__month=int(month))

        if data.get('q'):
            title_field = f'title_{self.lang}'
            posts = posts.filter(
                Q(**{f'{title_field}__icontains': data['q']})
                | Q(slug__icontains=data['q'])
            )

        return posts
