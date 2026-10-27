"""Views for bowler discovery, profiles, and lifecycle management."""
from django.contrib import messages
from django.db.models import Avg, Count, F, Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .forms import BowlerForm
from .models import Bowler

class BowlerListView(ListView):
    model = Bowler
    template_name = "players/bowler_list.html"
    context_object_name = "bowlers"
    paginate_by = 12

    def get_queryset(self):
        queryset = Bowler.objects.annotate(
            game_count=Count("games", distinct=True),
            calculated_average=Avg("scores__score"),
        )
        query = self.request.GET.get("q", "").strip()
        sort = self.request.GET.get("sort", "name")
        if query:
            queryset = queryset.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))
        if sort == "average":
            # Players without recorded scores are always listed after scored players.
            return queryset.order_by(F("calculated_average").desc(nulls_last=True), "last_name", "first_name")
        sort_fields = {"name": ("last_name", "first_name"), "joined": ("-joined_on", "last_name")}
        return queryset.order_by(*sort_fields.get(sort, sort_fields["name"]))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_sort"] = self.request.GET.get("sort", "name")
        return context

class BowlerDetailView(DetailView):
    model = Bowler
    template_name = "players/bowler_detail.html"
    context_object_name = "bowler"
    def get_queryset(self): return Bowler.objects.prefetch_related("scores__game__lane__center")

class BowlerCreateView(CreateView):
    model = Bowler
    form_class = BowlerForm
    template_name = "players/bowler_form.html"
    def form_valid(self, form):
        messages.success(self.request, "Bowler profile created.")
        return super().form_valid(form)
    def get_success_url(self): return reverse("players:bowler_detail", kwargs={"pk": self.object.pk})

class BowlerUpdateView(UpdateView):
    model = Bowler
    form_class = BowlerForm
    template_name = "players/bowler_form.html"
    def form_valid(self, form):
        messages.success(self.request, "Bowler profile updated.")
        return super().form_valid(form)
    def get_success_url(self): return reverse("players:bowler_detail", kwargs={"pk": self.object.pk})

class BowlerDeleteView(DeleteView):
    model = Bowler
    template_name = "players/bowler_confirm_delete.html"
    success_url = reverse_lazy("players:bowler_list")
    def post(self, request, *args, **kwargs):
        bowler = self.get_object()
        if bowler.scores.exists():
            messages.error(request, "This bowler has recorded scores and cannot be deleted. Edit the score records first.")
            return redirect("players:bowler_detail", pk=bowler.pk)
        messages.success(request, "Bowler profile deleted.")
        return super().post(request, *args, **kwargs)
