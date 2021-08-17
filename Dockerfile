FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
# Python Env Vars
ENV PYTHONPATH "${PYTHONPATH}:/"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Port our app will run on
ENV PORT=8000
# Make new dir and cd
WORKDIR /app/
# Pip should be preinstalled, let's upgrade it
RUN pip install --upgrade pip
# Copy our reqs to our working dir
COPY ./requirements.txt /app/
# Install our reqs
RUN pip install -r requirements.txt
# Copy source into container
COPY ./app /app
# Open port on container
EXPOSE 8000