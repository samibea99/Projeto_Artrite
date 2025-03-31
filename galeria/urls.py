from django.urls import path
from . import views
from galeria.views import index, cadastro_paciente, questionario_reducao

urlpatterns = [
    path('', index),
    path('cadastro_paciente/', views.cadastro_paciente, name ="cadastro_paciente"),
    path('questionario_reducao/<int:paciente_id>/', views.questionario_reducao, name="questionario_reducao"),

]