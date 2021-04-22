#FROM debian AS clone 

#WORKDIR /app/

#RUN apt update && apt dist-upgrade -y &&apt -y install git wget
#RUN git clone https://github.com/matiasgonzalocalvo/jmeterapi

FROM python:slim

#ENV JEMETER_VERSION 5.3
ENV WORKDIR jmeter

WORKDIR /${WORKDIR}

#COPY --from=clone /app/jmeterapi .
COPY . .
RUN apt update ; apt install vim curl tcpdump -y
COPY certs/santander-root-ca-1.pem /etc/ssl/certs/
COPY certs/santander-root-ca-2.pem /etc/ssl/certs/
RUN update-ca-certificates  -f

RUN pip install -r requirements.txt
RUN cat certs/santander-root-ca-1.pem >> /usr/local/lib/python3.9/site-packages/certifi/cacert.pem
RUN cat certs/santander-root-ca-2.pem >> /usr/local/lib/python3.9/site-packages/certifi/cacert.pem

CMD ["python", "app.py"]
