import json
import matplotlib.pyplot as plt
import io
import plotly.express as px
import plotly.io as pio
import pandas as pd
from datetime import datetime
from PIL import Image as PILImage
from reportlab.platypus import Image
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from textwrap import wrap
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from .models import Paciente, Pergunta, Resposta
from django.http import HttpResponse 

def index(request):
    return render(request, 'galeria/index.html')

def cadastro_paciente(request):
    if request.method == "POST":
        numero_paciente = request.POST.get("numero_paciente")
        numero_centro = request.POST.get("numero_centro")
        numero_pesquisador = request.POST.get("numero_pesquisador")
        data_observacao = request.POST.get("data_observacao")
        fase_tratamento = request.POST.get("fase_tratamento")

        # Criar o paciente no banco de dados
        paciente = Paciente.objects.create(
            numero_paciente=numero_paciente,
            numero_centro=numero_centro,
            numero_pesquisador=numero_pesquisador,
            data_observacao=data_observacao,
            fase_tratamento=fase_tratamento
        )
        
        # Redirecionar para o questionário com base na fase do tratamento
        if fase_tratamento == "fase1":
            return redirect("questionario_fase1", paciente_id=paciente.id)
        elif fase_tratamento == "fase1b":
            return redirect("questionario_fase1b", paciente_id=paciente.id)
        elif fase_tratamento == "fase2":
            return redirect("questionario_fase2", paciente_id=paciente.id)
        elif fase_tratamento == "fase3":
            return redirect("questionario_fase3", paciente_id=paciente.id)
        elif fase_tratamento == "reducao":
            return redirect("questionario_reducao", paciente_id=paciente.id)

    return render(request, "galeria/cadastro_paciente.html")

def questionario_reducao(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    pergunta_atual = int(request.POST.get("pergunta_atual", 1))  # Pergunta inicial = 1 se não houver POST

    # 🔹 Mapeamento das perguntas com base na resposta
    transicoes = {
        1: {'sim': 2, 'nao': 3},
        2: {'sim': 4, 'nao': 9},
        3: {'sim': 6, 'nao': 4},
        4: {'sim': 5, 'nao': 9},
        5: {'sim': 9, 'nao': 9},
        6: {'sim': 9, 'nao': 7},
        7: {'sim': 9, 'nao': 8},
        8: {'sim': 9, 'nao': 9},
        9: {'sim': 10, 'nao': 10},
        10: {'sim': 11, 'nao': 11},
        11: {'sim': 12, 'nao': 12},
        12: {'sim': 13, 'nao': 13},
        13: {'sim': 14, 'nao': 14},
        14: {'sim': 15, 'nao': 15},
        15: {'sim': 16, 'nao': 16},
        16: {'sim': 'fim', 'nao': 'fim'}  # Conclui o questionário
    }

    pergunta = Pergunta.objects.filter(numero_pergunta=pergunta_atual, fase_tratamento="reducao").first()
    if not pergunta:
        return HttpResponse("Pergunta não encontrada.", status=404)

    if request.method == "POST":
        resposta_raw = request.POST.get("resposta")

        # 🔹 Log do que está sendo recebido no POST
        print(f"DEBUG: Resposta recebida no POST -> {resposta_raw}")

        # 🔹 Converte "sim"/"nao" para True/False corretamente
        resposta = resposta_raw.strip().lower() == "sim"

        # 🔹 Log do valor convertido
        print(f"DEBUG: Resposta convertida para booleano -> {resposta}")

        # 🔹 Salva a resposta corretamente
        resposta_obj, created = Resposta.objects.update_or_create(
            paciente=paciente,
            pergunta=pergunta,
            defaults={"resposta": resposta}  # Salva "True" ou "False"
        )

        print(f"DEBUG: Resposta salva -> {resposta_obj.resposta} (Criado: {created})")

        # 🔹 Define a próxima pergunta
        proxima_pergunta = transicoes.get(pergunta_atual, {}).get(resposta_raw)

        if proxima_pergunta == 'fim':
            return render(request, "galeria/confirmacao_conclusao.html", {"paciente": paciente})

        pergunta_atual = proxima_pergunta
        pergunta = Pergunta.objects.filter(numero_pergunta=pergunta_atual, fase_tratamento="reducao").first()

        if not pergunta:
            return HttpResponse("Pergunta seguinte não encontrada.", status=404)

    return render(request, "galeria/questionario_reducao.html", {
        "paciente": paciente,
        "pergunta": pergunta
    })

def dashboard_view(request):
    # Contagem de pacientes por fase
    pacientes_por_fase = Paciente.objects.values('fase_tratamento').annotate(total=Count('id'))
    df_pacientes = pd.DataFrame(list(pacientes_por_fase))
    
    # Criando o gráfico de pizza com Plotly
    if not df_pacientes.empty:
        fig = px.pie(df_pacientes, 
                     names='fase_tratamento', 
                     values='total', 
                     title='Distribuição de Pacientes por Fase',
                     color_discrete_sequence=px.colors.qualitative.Set2)  # Cores suaves
        grafico_pacientes = pio.to_html(fig, full_html=False)
    else:
        grafico_pacientes = "<p>Nenhum dado disponível</p>"

    return render(request, "galeria/dashboard.html", {"grafico_pacientes": grafico_pacientes})

def estatisticas_respostas(request):
    # Obtendo as respostas agrupadas por fase, pergunta e resposta (Sim/Não)
    respostas_por_fase = Resposta.objects.values(
            'pergunta__fase_tratamento',  
            'pergunta__texto', 
            'resposta'
        ).annotate(total=Count('id'))

    # Estruturando os dados para o gráfico
    estatisticas = {}
    perguntas_registradas = {}

    for item in respostas_por_fase:
        fase = item['pergunta__fase_tratamento']
        pergunta = item['pergunta__texto']
        resposta = "Sim" if item['resposta'] else "Não"
        total = item['total']

        if fase not in estatisticas:
            estatisticas[fase] = {}

        if pergunta not in estatisticas[fase]:
            estatisticas[fase][pergunta] = {"Sim": 0, "Não": 0}
            perguntas_registradas[pergunta] = {"Sim": 0, "Não": 0}

        estatisticas[fase][pergunta][resposta] += total
        perguntas_registradas[pergunta][resposta] += total

    # Garantir que "Sim" e "Não" existam para todas as perguntas
    for fase, perguntas in estatisticas.items():
        for pergunta, respostas in perguntas.items():
            if "Sim" not in respostas:
                respostas["Sim"] = 0
            if "Não" not in respostas:
                respostas["Não"] = 0

    # Convertendo os dados para JSON para passar ao template
    estatisticas_json = json.dumps(estatisticas)

    return render(request, 'galeria/estatisticas_respostas.html', {'estatisticas_json': estatisticas_json})

def exportar_relatorio_pdf(request):
    # Criar a resposta HTTP para o PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_estatisticas.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(letter))  # 🟢 Modo paisagem para mais espaço
    elements = []

    # Obtendo os dados agrupados por fase, pergunta e resposta
    respostas_por_fase = Resposta.objects.values(
        'pergunta__fase_tratamento',  
        'pergunta__texto', 
        'resposta'
    ).annotate(total=Count('id'))

    # Contar o número de pacientes distintos que responderam cada pergunta
    pacientes_por_pergunta = Resposta.objects.values(
        'pergunta__texto'
    ).annotate(total_pacientes=Count('paciente', distinct=True))

    pacientes_dict = {p['pergunta__texto']: p['total_pacientes'] for p in pacientes_por_pergunta}

    # Estruturando os dados para o relatório
    estatisticas = {}

    for item in respostas_por_fase:
        fase = item['pergunta__fase_tratamento']
        pergunta = item['pergunta__texto']
        resposta = "Sim" if item['resposta'] else "Não"
        total = item['total']
        total_pacientes = pacientes_dict.get(pergunta, 0)

        if fase not in estatisticas:
            estatisticas[fase] = {}

        if pergunta not in estatisticas[fase]:
            estatisticas[fase][pergunta] = {
                "Sim": 0, "Não": 0, "Total": 0, "Respondentes": total_pacientes
            }

        estatisticas[fase][pergunta][resposta] = total
        estatisticas[fase][pergunta]["Total"] += total

    for fase, perguntas in estatisticas.items():
        for pergunta, respostas in perguntas.items():
            total_respostas = respostas["Total"]
            if total_respostas > 0:
                respostas["% Sim"] = round((respostas["Sim"] / total_respostas) * 100, 2)
                respostas["% Não"] = 100 - respostas["% Sim"]
            else:
                respostas["% Sim"] = respostas["% Não"] = 0

    # Criando a tabela para o PDF
    dados_tabela = [["Fase", "Pergunta", "Sim", "Não", "% Sim", "% Não", "Respondentes"]]

    for fase, perguntas in estatisticas.items():
        for pergunta, respostas in perguntas.items():
            # 🔹 Quebra de linha automática para perguntas longas
            pergunta_formatada = "\n".join(wrap(pergunta, width=40))  

            dados_tabela.append([
                fase, pergunta_formatada,
                respostas["Sim"], respostas["Não"],
                f"{respostas['% Sim']:.2f}%", f"{respostas['% Não']:.2f}%",
                respostas["Respondentes"]
            ])

    # Criando a tabela no ReportLab com ajuste de largura
    colWidths = [1.5 * inch, 3 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 1 * inch]
    tabela = Table(dados_tabela, colWidths=colWidths)  

    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),  # 🔹 Diminui a fonte para caber melhor
    ]))

    elements.append(tabela)

    # Criando gráfico do número de pacientes por fase
    pacientes_por_fase = Paciente.objects.values('fase_tratamento').annotate(total=Count('id'))
    df_pacientes = pd.DataFrame(list(pacientes_por_fase))

    if not df_pacientes.empty:
        plt.figure(figsize=(6, 4))
        plt.bar(df_pacientes['fase_tratamento'], df_pacientes['total'], color='skyblue')
        plt.xlabel('Fase de Tratamento')
        plt.ylabel('Número de Pacientes')
        plt.title('Número de Pacientes por Fase')
        plt.xticks(rotation=45)

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close()

        img_buffer.seek(0)
        pil_img = PILImage.open(img_buffer)
        pil_img.save("grafico.png", format="PNG")

        img = Image("grafico.png", width=400, height=300)
        elements.append(img)

    # Construir o documento PDF
    doc.build(elements)

    return response