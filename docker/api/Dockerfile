FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
# Define build arguments
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USER_NAME=api_default_user
ARG ostype=Linux

# Define environment variables
ENV USER_ID=${USER_ID}
ENV GROUP_ID=${GROUP_ID}
ENV WORK_DIR=/home

ENV PYTHONPATH "${PYTHONPATH}:/"
ENV ENV=dev
ENV PORT=8000

COPY . ${WORK_DIR}
WORKDIR ${WORK_DIR}


RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz


# Add group and user based on build arguments
# RUN addgroup --gid ${GROUP_ID} ${USER_NAME}
# RUN adduser --disabled-password --gecos '' --uid ${USER_ID} --gid ${GROUP_ID} ${USER_NAME}

# RUN bash -c 'if [ ${ostype} == Linux ]; then groupadd -r --gid ${GROUP_ID} ${USER_NAME}; fi && \
#     useradd -r --create-home --shell /bin/bash --uid ${USER_ID} --gid ${GROUP_ID} ${USER_NAME}' && \
#     mkdir -p ${WORK_DIR} && chown ${USER_NAME} ${WORK_DIR}
# USER ${USER_NAME}


# RUN chown ${USER_NAME} ${WORK_DIR}

# Set user and group of working directory
RUN chmod +x ${WORK_DIR}/docker/api/startup.sh
ENTRYPOINT ${WORK_DIR}/docker/api/startup.sh
# EXPOSE 8000  
