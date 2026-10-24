


from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path(
        "feedback/",
        views.submit_feedback,
        name="submit_feedback",
    ),

    path(
        "feedback/import/",
        views.import_feedback,
        name="import_feedback",
    ),

    path(
        "feedback/history/",
        views.import_history,
        name="import_history",
    ),

    path(
        "feedback/history/<int:import_id>/",
        views.import_detail,
        name="import_detail",
    ),
    path(
      "marketing/import/",
       views.import_marketing,
       name="import_marketing",
    ),

    path(
       "marketing/",
        views.marketing_dashboard,
        name="marketing_dashboard",
    ),

]
