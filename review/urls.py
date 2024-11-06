from django.urls import path
from . import views

urlpatterns = [
    path("reviews/", views.ReviewListView.as_view(), name="review-list"),
    path("reviews/<int:pk>/", views.ReviewDetailView.as_view(), name="review-detail"),
    path(
        "reviews/<int:pk>/transition/<str:action>/",
        views.ReviewTransitionView.as_view(),
        name="review-transition",
    ),
    path("reviews/create/", views.ReviewCreateView.as_view(), name="review-create"),
]
