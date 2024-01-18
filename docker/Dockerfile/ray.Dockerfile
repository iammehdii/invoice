# Base Image
FROM python:3.10.12-slim-buster


# Set default environment variables
ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Setting Locale Settings
RUN apt-get update -qy && \
    apt-get upgrade -qy && \
    apt-get autoremove -y && \
     rm -rf /var/lib/apt/lists/*

# Set required environment variables
#ARG PROJECT_ROOT
#ARG PROJECT_NAME
#ARG RAY_SERVICE_NAME
#
#ENV PROJECT_ROOT ${PROJECT_ROOT}
#ENV PROJECT_NAME ${PROJECT_NAME}
#ENV RAY_SERVICE_NAME ${RAY_SERVICE_NAME}

# Create a user by the name of "user".
RUN adduser --disabled-login --disabled-password user

# Create and set a working directory in the container
WORKDIR /srv/invoice-ray/

RUN pip3 install --upgrade pip
RUN pip3 install poetry
RUN pip3 install ray && pip3 install -U "ray[serve]"
RUN poetry config virtualenvs.create false

#COPY app/poetry.lock .
COPY app/pyproject.toml .

# Install the required packages for our project
RUN poetry install --only main

# Copy project files to the working directory
COPY app .

# Change permission of media folder
RUN chown -R user:user /srv/
RUN chmod -R 755 /srv/

# Switch to the non-root user.
USER user

ENTRYPOINT ["/bin/bash", "-c", "/srv/invoice-ray/entrypoint.sh"]

EXPOSE 8003
