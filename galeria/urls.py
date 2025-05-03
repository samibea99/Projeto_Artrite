from django.urls import path
from . import views
from galeria.views import index, cadastro_paciente, responder_pergunta, dashboard_view, estatisticas_respostas, exportar_relatorio_pdf, exportar_relatorio_excel

urlpatterns = [
    path('', index),
    path('cadastro_paciente/', views.cadastro_paciente, name ="cadastro_paciente"),
    path("responder_pergunta/<int:paciente_id>/<int:pergunta_id>/", views.responder_pergunta, name="responder_pergunta"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path('estatisticas/', estatisticas_respostas, name='estatisticas'),
    path("exportar_relatorio_pdf/", views.exportar_relatorio_pdf, name="exportar_relatorio_pdf"),
    path('exportar-relatorio-excel/', exportar_relatorio_excel, name='exportar_relatorio_excel'),


]