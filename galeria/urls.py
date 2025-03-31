from django.urls import path
from . import views
from galeria.views import index, cadastro_paciente, questionario_reducao, dashboard_view, estatisticas_respostas, exportar_relatorio_pdf

urlpatterns = [
    path('', index),
    path('cadastro_paciente/', views.cadastro_paciente, name ="cadastro_paciente"),
    path('questionario_reducao/<int:paciente_id>/', views.questionario_reducao, name="questionario_reducao"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path('estatisticas/', estatisticas_respostas, name='estatisticas'),
    path("exportar_relatorio_pdf/", views.exportar_relatorio_pdf, name="exportar_relatorio_pdf"),


]