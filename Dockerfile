FROM python:3.10

WORKDIR /app/

COPY ./requirements.txt /app/

RUN mkdir /app/config && \
    pip install --no-cache-dir -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 80

ENV DOBO_ENV_PATH=config/.env
ENV DOBO_CONFIG_PATH=config/config.toml

COPY ./app /app/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
