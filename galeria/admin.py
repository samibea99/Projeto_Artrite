from django.contrib import admin

from galeria.models import Paciente, Resposta, Pergunta, Alternativa  

# Inline para cadastrar alternativas diretamente na pergunta
class AlternativaInline(admin.TabularInline):
    model = Alternativa
    extra = 1

# Customização do admin para Pergunta
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ("numero_pergunta", "texto", "fase_tratamento", "tipo")
    list_filter = ("fase_tratamento", "tipo")
    inlines = [AlternativaInline]

admin.site.register(Paciente)
admin.site.register(Resposta)
admin.site.register(Pergunta, PerguntaAdmin)


