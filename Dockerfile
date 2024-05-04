FROM python:3.12

WORKDIR /planning

COPY requirements.txt /planning/requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python3.12",  "src/main.py"]