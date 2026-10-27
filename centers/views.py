"""Class-based views for center and lane CRUD workflows."""
from django.contrib import messages
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .forms import BowlingCenterForm, LaneForm
from .models import BowlingCenter, Lane


class SuccessMessageMixin:
    success_message = "Changes saved successfully."
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class CenterListView(ListView):
    model = BowlingCenter
    template_name = "centers/center_list.html"
    context_object_name = "centers"
    paginate_by = 9

    def get_queryset(self):
        return BowlingCenter.objects.annotate(lane_count=Count("lanes")).order_by("city", "name")


class CenterDetailView(DetailView):
    model = BowlingCenter
    template_name = "centers/center_detail.html"
    context_object_name = "center"

    def get_queryset(self):
        return BowlingCenter.objects.prefetch_related("lanes__games")


class CenterCreateView(SuccessMessageMixin, CreateView):
    model = BowlingCenter
    form_class = BowlingCenterForm
    template_name = "centers/center_form.html"
    success_message = "Bowling center created."
    def get_success_url(self): return reverse("centers:center_detail", kwargs={"pk": self.object.pk})


class CenterUpdateView(SuccessMessageMixin, UpdateView):
    model = BowlingCenter
    form_class = BowlingCenterForm
    template_name = "centers/center_form.html"
    success_message = "Bowling center updated."
    def get_success_url(self): return reverse("centers:center_detail", kwargs={"pk": self.object.pk})


class CenterDeleteView(DeleteView):
    model = BowlingCenter
    template_name = "centers/center_confirm_delete.html"
    success_url = reverse_lazy("centers:center_list")

    def post(self, request, *args, **kwargs):
        center = self.get_object()
        if center.lanes.exists():
            messages.error(request, "This center still has lanes. Remove its lanes first, then retry deletion.")
            return redirect("centers:center_detail", pk=center.pk)
        messages.success(request, "Bowling center deleted.")
        return super().post(request, *args, **kwargs)


class LaneListView(ListView):
    model = Lane
    template_name = "centers/lane_list.html"
    context_object_name = "lanes"
    paginate_by = 12

    def get_queryset(self):
        queryset = Lane.objects.select_related("center").annotate(game_count=Count("games")).order_by("center__name", "number")
        center_id = self.request.GET.get("center", "").strip()
        availability = self.request.GET.get("availability", "").strip()
        if center_id.isdigit(): queryset = queryset.filter(center_id=int(center_id))
        if availability == "available": queryset = queryset.filter(is_available=True)
        elif availability == "unavailable": queryset = queryset.filter(is_available=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["centers"] = BowlingCenter.objects.order_by("name")
        context["selected_center"] = self.request.GET.get("center", "")
        context["selected_availability"] = self.request.GET.get("availability", "")
        return context


class LaneDetailView(DetailView):
    model = Lane
    template_name = "centers/lane_detail.html"
    context_object_name = "lane"
    def get_queryset(self): return Lane.objects.select_related("center").prefetch_related("games")


class LaneCreateView(SuccessMessageMixin, CreateView):
    model = Lane
    form_class = LaneForm
    template_name = "centers/lane_form.html"
    success_message = "Lane created."

    def get_initial(self):
        initial = super().get_initial()
        center_id = self.request.GET.get("center", "").strip()
        if center_id.isdigit():
            initial["center"] = int(center_id)
        return initial

    def get_success_url(self): return reverse("games:lane_detail", kwargs={"pk": self.object.pk})


class LaneUpdateView(SuccessMessageMixin, UpdateView):
    model = Lane
    form_class = LaneForm
    template_name = "centers/lane_form.html"
    success_message = "Lane updated."
    def get_success_url(self): return reverse("games:lane_detail", kwargs={"pk": self.object.pk})


class LaneDeleteView(DeleteView):
    model = Lane
    template_name = "centers/lane_confirm_delete.html"
    success_url = reverse_lazy("games:lane_list")

    def post(self, request, *args, **kwargs):
        lane = self.get_object()
        if lane.games.exists():
            messages.error(request, "This lane is assigned to one or more games. Move or delete those games first.")
            return redirect("games:lane_detail", pk=lane.pk)
        messages.success(request, "Lane deleted.")
        return super().post(request, *args, **kwargs)
