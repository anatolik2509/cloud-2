FROM python:3.11.1

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY FaceCut.py .

CMD [ "python", "./FaceCut.py" ]
