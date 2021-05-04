FROM python:3.7
RUN pip install git+https://github.com/samstudio8/ocarina.git
COPY .ocarina /root/


