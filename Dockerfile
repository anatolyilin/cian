FROM python:3.9

WORKDIR /usr/src/app
RUN adduser myuser && chown -R myuser /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY helpers/ .
COPY misc/ .

COPY dummy.py .

COPY app.py .
COPY config.yaml .

USER myuser
CMD [ "python", "./dummy.py" ]