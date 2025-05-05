from django.urls import path
from . import views
from galeria.views import index, cadastro_paciente, responder_pergunta,exportar_relatorio_excel

urlpatterns = [
    path('', index, name='index'),
    path('cadastro_paciente/', views.cadastro_paciente, name ="cadastro_paciente"),
    path("responder_pergunta/<int:paciente_id>/<int:pergunta_id>/", views.responder_pergunta, name="responder_pergunta"),
    path('exportar-relatorio-excel/', exportar_relatorio_excel, name='exportar_relatorio_excel'),


]