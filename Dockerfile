# Usa imagem oficial Python
FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho no container
WORKDIR /app

# Copia tudo para o container
COPY . /app/

# Instala dependências Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expõe porta
EXPOSE 8000

# Comando padrão para rodar o Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
