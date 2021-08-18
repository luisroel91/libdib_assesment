FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
# Python Env Vars
ENV PYTHONPATH "${PYTHONPATH}:/"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Port our app will run on
ENV PORT=8000
# Pip should be preinstalled, let's upgrade it
RUN pip install --upgrade pip
# Copy our reqs to our working dir
COPY ./requirements.txt /app/
# Copy our DF pickle
# Install our reqs
RUN pip install -r requirements.txt
# Copy source into container
COPY ./app /app
# Copy our pickle
COPY ./data_processing /data_processing
# Run our app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Open port on container
EXPOSE 8000