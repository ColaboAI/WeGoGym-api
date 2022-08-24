FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY . /home
WORKDIR /home

ENV PYTHONPATH "${PYTHONPATH}:/"
ENV PORT=8000
ENV DEV=dev

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz


RUN chmod +x /home/docker/api/startup.sh
ENTRYPOINT /home/docker/api/startup.sh
EXPOSE 8000  
