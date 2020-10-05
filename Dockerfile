FROM python:slim
RUN apt update && apt dist-upgrade -y &&apt -y install git
WORKDIR /jmeter
RUN ls -atlrh
RUN git clone https://github.com/matiasgonzalocalvo/jmeterapi . 
RUN ls -atlrh
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
