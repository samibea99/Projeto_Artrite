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
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment
from openpyxl import load_workbook

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

        # Obter a primeira pergunta da fase selecionada
        primeira_pergunta = Pergunta.objects.filter(
            numero_pergunta=1,
            fase_tratamento=paciente.fase_tratamento
        ).first()

        if primeira_pergunta:
            return redirect("responder_pergunta", paciente_id=paciente.id, pergunta_id=primeira_pergunta.id)
        else:
            return HttpResponse("Nenhuma pergunta encontrada para a fase selecionada.", status=404)

    return render(request, "galeria/cadastro_paciente.html")



def responder_pergunta(request, paciente_id, pergunta_id=None):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    if pergunta_id:
        pergunta = get_object_or_404(Pergunta, id=pergunta_id)
    else:
        pergunta = Pergunta.objects.filter(numero_pergunta=1, fase_tratamento=paciente.fase_tratamento).first()

    if not pergunta:
        return HttpResponse("Pergunta não encontrada.", status=404)

    if request.method == "POST":
        resposta_raw = request.POST.get("resposta", "").strip().lower()

        # Trata tipo booleano somente se sim/não
        if pergunta.tipo == "sim_nao":
            resposta_convertida = resposta_raw == "sim"
        else:
            resposta_convertida = resposta_raw  # salva como string mesmo

        # Salva resposta
        Resposta.objects.update_or_create(
            paciente=paciente,
            pergunta=pergunta,
            defaults={"resposta": resposta_convertida}
        )

        # Inicializa a pilha se necessário
        if "retornar_para_pilha" not in request.session:
            request.session["retornar_para_pilha"] = []

        # Se for desvio, empilha o retorno correto
        if resposta_raw == "sim" and pergunta.desvio_para:
            # se houver retornar_para, ele é mais confiável do que proxima_se_sim
            if pergunta.retornar_para:
                request.session["retornar_para_pilha"].append(pergunta.retornar_para.id)
            elif pergunta.proxima_se_sim:
                request.session["retornar_para_pilha"].append(pergunta.proxima_se_sim.id)
            request.session.modified = True
            return redirect("responder_pergunta", paciente_id=paciente.id, pergunta_id=pergunta.desvio_para.id)

        # Se chegou ao fim do desvio (sem próxima pergunta)
        if not pergunta.proxima_se_sim and not pergunta.proxima_se_nao:
            if request.session.get("retornar_para_pilha"):
                proxima_id = request.session["retornar_para_pilha"].pop()
                request.session.modified = True
                return redirect("responder_pergunta", paciente_id=paciente.id, pergunta_id=proxima_id)
            else:
                return render(request, "galeria/confirmacao_conclusao.html", {"paciente": paciente})

        # Continua normalmente
        proxima = pergunta.proxima_se_sim if resposta_raw == "sim" else pergunta.proxima_se_nao
        if proxima:
            return redirect("responder_pergunta", paciente_id=paciente.id, pergunta_id=proxima.id)

        return render(request, "galeria/confirmacao_conclusao.html", {"paciente": paciente})

    return render(request, "galeria/questionario.html", {
        "paciente": paciente,
        "pergunta": pergunta
    })



def exportar_relatorio_excel(request):
    # Obtendo os dados agrupados por fase, pergunta e resposta
    respostas_por_fase = Resposta.objects.values(
        'pergunta__fase_tratamento',  
        'pergunta__texto', 
        'resposta'
    ).annotate(total=Count('id'))

    # Contar o número de pacientes distintos por pergunta
    pacientes_por_pergunta = Resposta.objects.values(
        'pergunta__texto'
    ).annotate(total_pacientes=Count('paciente', distinct=True))

    pacientes_dict = {p['pergunta__texto']: p['total_pacientes'] for p in pacientes_por_pergunta}

    # Estruturando os dados
    dados_exportacao = []

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
            estatisticas[fase][pergunta] = {"Sim": 0, "Não": 0, "Respondentes": total_pacientes}

        estatisticas[fase][pergunta][resposta] += total

    # Preenchendo os dados na lista
    for fase, perguntas in estatisticas.items():
        for pergunta, respostas in perguntas.items():
            total = respostas["Sim"] + respostas["Não"]
            percentual_sim = round((respostas["Sim"] / total) * 100, 2) if total > 0 else 0
            percentual_nao = 100 - percentual_sim if total > 0 else 0

            dados_exportacao.append({
                "Fase": fase,
                "Pergunta": pergunta,
                "Sim": respostas["Sim"],
                "Não": respostas["Não"],
                "% Sim": percentual_sim,
                "% Não": percentual_nao,
                "Respondentes": respostas["Respondentes"]
            })

    # Criando o DataFrame
    df = pd.DataFrame(dados_exportacao)

    # Criar a resposta HTTP com o Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="relatorio_estatisticas.xlsx"'

    # Escrever para Excel usando pandas
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Estatísticas')

        # Ajuste de largura automática
        worksheet = writer.sheets['Estatísticas']
        for col in worksheet.columns:
            max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            col_letter = get_column_letter(col[0].column)
            worksheet.column_dimensions[col_letter].width = max_length + 2

        # Alinhar colunas
        for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical='top')

    return response

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