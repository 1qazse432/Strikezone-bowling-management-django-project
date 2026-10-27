"""Views for games, score entry, and ranking-oriented listings."""
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from centers.models import BowlingCenter
from .forms import BowlingGameForm, GameScoreForm
from .models import BowlingGame, GameScore

class GameListView(ListView):
    model = BowlingGame
    template_name = "games/game_list.html"
    context_object_name = "games"
    paginate_by = 12

    def get_queryset(self):
        queryset = BowlingGame.objects.annotate(participant_total=Count("scores__bowler", distinct=True)).select_related("lane__center").prefetch_related("scores__bowler")
        status = self.request.GET.get("status", "").strip()
        center = self.request.GET.get("center", "").strip()
        sort = self.request.GET.get("sort", "newest")
        query = self.request.GET.get("q", "").strip()
        if status in BowlingGame.Status.values: queryset = queryset.filter(status=status)
        if center.isdigit(): queryset = queryset.filter(lane__center_id=int(center))
        if query:
            text_filter = Q(title__icontains=query) | Q(lane__center__name__icontains=query)
            if query.isdigit():
                text_filter |= Q(lane__number=int(query))
            queryset = queryset.filter(text_filter)
        sort_fields = {"newest": ("-scheduled_at", "title"), "oldest": ("scheduled_at", "title"), "title": ("title", "-scheduled_at")}
        return queryset.order_by(*sort_fields.get(sort, sort_fields["newest"]))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "centers": BowlingCenter.objects.order_by("name"),
            "selected_status": self.request.GET.get("status", ""),
            "selected_center": self.request.GET.get("center", ""),
            "selected_sort": self.request.GET.get("sort", "newest"),
            "search_query": self.request.GET.get("q", ""),
            "statuses": BowlingGame.Status.choices,
        })
        return context

class GameDetailView(DetailView):
    model = BowlingGame
    template_name = "games/game_detail.html"
    context_object_name = "game"
    def get_queryset(self): return BowlingGame.objects.select_related("lane__center").prefetch_related("scores__bowler")

class GameCreateView(CreateView):
    model = BowlingGame
    form_class = BowlingGameForm
    template_name = "games/game_form.html"
    def form_valid(self, form):
        messages.success(self.request, "Game scheduled. Add participant scores from the game page.")
        return super().form_valid(form)
    def get_success_url(self): return reverse("games:game_detail", kwargs={"pk": self.object.pk})

class GameUpdateView(UpdateView):
    model = BowlingGame
    form_class = BowlingGameForm
    template_name = "games/game_form.html"
    def form_valid(self, form):
        messages.success(self.request, "Game details updated.")
        return super().form_valid(form)
    def get_success_url(self): return reverse("games:game_detail", kwargs={"pk": self.object.pk})

class GameDeleteView(DeleteView):
    model = BowlingGame
    template_name = "games/game_confirm_delete.html"
    success_url = reverse_lazy("games:game_list")
    def post(self, request, *args, **kwargs):
        messages.success(request, "Game deleted along with its score records.")
        return super().post(request, *args, **kwargs)

class GameScoreListView(ListView):
    model = GameScore
    template_name = "games/score_list.html"
    context_object_name = "scores"
    paginate_by = 15
    def get_queryset(self):
        queryset = GameScore.objects.select_related("game__lane__center", "bowler")
        query = self.request.GET.get("q", "").strip()
        sort = self.request.GET.get("sort", "top")
        if query:
            queryset = queryset.filter(Q(bowler__first_name__icontains=query) | Q(bowler__last_name__icontains=query) | Q(game__title__icontains=query))
        sort_fields = {"top": ("-score", "bowler__last_name"), "recent": ("-created_at",), "player": ("bowler__last_name", "bowler__first_name")}
        return queryset.order_by(*sort_fields.get(sort, sort_fields["top"]))
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_sort"] = self.request.GET.get("sort", "top")
        return context

class GameScoreCreateView(CreateView):
    model = GameScore
    form_class = GameScoreForm
    template_name = "games/score_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        game_pk = self.kwargs.get("game_pk")
        if game_pk is not None:
            kwargs["game"] = get_object_or_404(BowlingGame, pk=game_pk)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_pk = self.kwargs.get("game_pk")
        context["fixed_game"] = get_object_or_404(BowlingGame, pk=game_pk) if game_pk is not None else None
        return context

    def form_valid(self, form):
        try:
            with transaction.atomic():
                response = super().form_valid(form)
        except IntegrityError:
            form.add_error(
                "bowler",
                "A score for this bowler and game already exists. Edit the existing record instead.",
            )
            return self.form_invalid(form)
        messages.success(self.request, "Score recorded.")
        return response

    def get_success_url(self): return reverse("games:game_detail", kwargs={"pk": self.object.game_id})

class GameScoreUpdateView(UpdateView):
    model = GameScore
    form_class = GameScoreForm
    template_name = "games/score_form.html"
    def get_queryset(self): return GameScore.objects.select_related("game", "bowler")
    def form_valid(self, form):
        try:
            with transaction.atomic():
                response = super().form_valid(form)
        except IntegrityError:
            form.add_error(
                "bowler",
                "A score for this bowler and game already exists. Edit the existing record instead.",
            )
            return self.form_invalid(form)
        messages.success(self.request, "Score updated.")
        return response

    def get_success_url(self): return reverse("games:game_detail", kwargs={"pk": self.object.game_id})

class GameScoreDeleteView(DeleteView):
    model = GameScore
    template_name = "games/score_confirm_delete.html"
    def get_queryset(self): return GameScore.objects.select_related("game", "bowler")
    def get_success_url(self): return reverse("games:game_detail", kwargs={"pk": self.object.game_id})
    def post(self, request, *args, **kwargs):
        messages.success(request, "Score record deleted.")
        return super().post(request, *args, **kwargs)
