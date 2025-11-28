# products/urls.py
from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    # Product list (optionally by category)
    path("", views.product_list, name="product_list"),
    path("category/<slug:category_slug>/", views.product_list, name="product_list_by_category"),
    
    # Product search
    path("search/", views.product_search, name="product_search"),


    # Product detail
    path("<slug:slug>/", views.product_detail, name="product_detail"),

    
    # Reviews
    path("reviews/", views.reviews_view, name="reviews"),
]
