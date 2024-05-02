FROM python:3.12
LABEL authors="Me"

WORKDIR /src

RUN apt-get update && \
    apt-get -y install \
      apt-utils \
      apt-transport-https && \
    apt -y upgrade && \
    apt -y autoremove && \
    pip install --upgrade pip && \
    pip install poetry

COPY pyproject.toml ./
RUN poetry install --no-root

COPY . .

CMD ["poetry", "run", "pytest"]