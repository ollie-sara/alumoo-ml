FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR ./suggestion-api
COPY fill_db.py .
COPY /schemafiller/ ./schemafiller/
COPY /db_model.py .

COPY /main.py .

CMD ["python", "main.py"]