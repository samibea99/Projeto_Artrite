from django.db import models


FASES_PRINCIPAIS = [
    ('fase1', 'Fase 1 - Início do tratamento'),
    ('fase1b', 'Fase 1B - Menos de 3 meses de tratamento'),
    ('fase2', 'Fase 2 - 3 a 6 meses de tratamento'),
    ('fase3', 'Fase 3 - Mais de 6 meses de tratamento'),
    ('reducao', 'Redução'),
]

DESVIOS = [
    ('mtx', 'MTX'),
    ('ssz', 'SSZ'),
    ('lef', 'LEF'),
    ('hcq', 'HCQ'),
    ('aine', 'AINE'),
    ('gcs', 'GCS'),
    ('bmmcd', 'bMMCD'),
    ('aemmcd', 'aeMMCD'),
]

FASES_TRATAMENTO = FASES_PRINCIPAIS + DESVIOS

TIPO_PERGUNTA_CHOICES = [
    ('sim_nao', 'Sim/Não'),
    ('multipla_escolha', 'Múltipla Escolha'),
]

class Paciente(models.Model):
    numero_paciente = models.CharField(max_length=50)
    numero_centro = models.CharField(max_length=50)
    numero_pesquisador = models.CharField(max_length=50)
    data_observacao = models.DateField()
    fase_tratamento = models.CharField(max_length=20, choices=FASES_TRATAMENTO)

    def __str__(self):
        return f"Paciente {self.numero_paciente} - {self.fase_tratamento}"

class Pergunta(models.Model):
    numero_pergunta = models.IntegerField()
    texto = models.CharField(max_length=255)
    fase_tratamento = models.CharField(max_length=20, choices=FASES_TRATAMENTO)
    tipo = models.CharField(max_length=20, choices=TIPO_PERGUNTA_CHOICES, default='sim_nao')

    proxima_se_sim = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='proxima_sim')
    proxima_se_nao = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='proxima_nao')
    desvio_para = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='desvio')
    retornar_para = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='retorno')

    critica_sim = models.TextField(blank=True, null=True)
    critica_nao = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('numero_pergunta', 'fase_tratamento')

    def __str__(self):
        return f"{self.fase_tratamento.upper()} - P{self.numero_pergunta}: {self.texto[:40]}"

class Alternativa(models.Model):
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE, related_name='alternativas')
    texto = models.CharField(max_length=255)

    def __str__(self):
        return self.texto

class Resposta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)
    resposta = models.CharField(max_length=255)  # Suporta sim/não ou múltiplas

    class Meta:
        unique_together = ('paciente', 'pergunta')

    def __str__(self):
        return f"Paciente {self.paciente.numero_paciente} - Pergunta {self.pergunta.numero_pergunta} - Resposta {self.resposta}"
