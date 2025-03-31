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

    # 🔹 Dicionário de transições de perguntas com base nas respostas
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

    # 🔹 Busca a pergunta atual
    pergunta = Pergunta.objects.filter(numero_pergunta=pergunta_atual, fase_tratamento="reducao").first()
    if not pergunta:
        return HttpResponse("Pergunta não encontrada.", status=404)

    if request.method == "POST":
        resposta_raw = request.POST.get("resposta")

        # 🔹 Converte "sim"/"nao" para True/False
        if resposta_raw == "sim":
            resposta = True
        elif resposta_raw == "nao":
            resposta = False
        else:
            return HttpResponse("Resposta inválida.", status=400)  # Caso venha um valor inesperado

        # 🔹 Salva a resposta
        Resposta.objects.create(
            paciente=paciente,
            pergunta=pergunta,
            resposta=resposta  # Agora sempre será True ou False
        )

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

