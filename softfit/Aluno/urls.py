from django.urls import path

from . import views

app_name = 'aluno'

urlpatterns = [
    path('inicial/<int:id>', views.inicial, name='inicial'),
    path('objetivo/<int:id>', views.objetivo, name='objetivo')
]
