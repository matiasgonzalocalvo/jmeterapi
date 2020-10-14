FROM debian AS clone 
WORKDIR /app/
RUN apt update && apt dist-upgrade -y &&apt -y install git wget
RUN git clone https://github.com/matiasgonzalocalvo/jmeterapi

FROM python:slim
ENV JEMETER_VERSION 5.3
ENV WORKDIR jmeter
#RUN mkdir -p /usr/share/man/man1
#RUN apt update && apt dist-upgrade -y &&apt -y install git default-jdk wget  
#RUN apt update && apt dist-upgrade -y &&apt -y install git wget 
WORKDIR /${WORKDIR}
#RUN git clone https://github.com/matiasgonzalocalvo/jmeterapi .
#RUN wget https://downloads.apache.org/jmeter/binaries/apache-jmeter-${JEMETER_VERSION}.tgz
#RUN tar -xf apache-jmeter-${JEMETER_VERSION}.tgz
#ENV JMETER_HOME=/${WORKDIR}/apache-jmeter-${JEMETER_VERSION}
#ENV PATH=$JMETER_HOME/bin:$PATH
#RUN cd /${WORKDIR}/apache-jmeter-${JEMETER_VERSION}/lib/ext && wget https://github.com/NovatecConsulting/JMeter-InfluxDB-Writer/releases/download/v-1.2/JMeter-InfluxDB-Writer-plugin-1.2.jar 
#RUN chmod 755 /${WORKDIR}/apache-jmeter-5.3 -R 
COPY --from=clone /app/jmeterapi .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
