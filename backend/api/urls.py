from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookListView, ProcessView, ChatView, InsightView

router = DefaultRouter()
router.register(r'books', BookListView, basename='book')

urlpatterns = [
    path('', include(router.urls)),
    path('process/', ProcessView.as_view(), name='process'),
    path('chat/', ChatView.as_view(), name='chat'),
    path('insights/', InsightView.as_view(), name='insights'),
]
