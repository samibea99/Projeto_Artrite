from django.db import models

FASES_TRATAMENTO = [
    ('fase1', 'Fase 1 - Início do tratamento'),
    ('fase1b', 'Fase 1B - Menos de 3 meses de tratamento'),
    ('fase2', 'Fase 2 - 3 a 6 meses de tratamento'),
    ('fase3', 'Fase 3 - Mais de 6 meses de tratamento'),
    ('reducao', 'Redução'),
]

class Paciente(models.Model):
    numero_paciente = models.CharField(max_length=50, unique=True)
    numero_centro = models.CharField(max_length=50)
    numero_pesquisador = models.CharField(max_length=50)
    data_observacao = models.DateField()
    fase_tratamento = models.CharField(max_length=10, choices=FASES_TRATAMENTO)

    def __str__(self):
        return f"Paciente {self.numero_paciente} - {self.fase_tratamento}"

class Pergunta(models.Model):
    numero_pergunta = models.IntegerField(default=1)
    texto = models.CharField(max_length=255)
    fase_tratamento = models.CharField(max_length=10, choices=FASES_TRATAMENTO)
    pergunta_anterior = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    
    class Meta:
        unique_together = ('numero_pergunta', 'fase_tratamento')  # Garante que cada fase tenha sua numeração própria

    def __str__(self):
        return f"{self.fase_tratamento} - Pergunta {self.numero_pergunta}: {self.texto}"      

class Resposta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)  # Relaciona diretamente com a tabela Pergunta
    resposta = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('paciente', 'pergunta')  # Garante que não haja respostas duplicadas para a mesma pergunta e paciente

    def __str__(self):
        return f"Paciente {self.paciente.numero_paciente} - Pergunta {self.pergunta.numero_pergunta} - Resposta {self.resposta}"