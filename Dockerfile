FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY ./requirements.txt /app/requirements.txt
COPY . /app

ENV STATIC_URL /static
ENV STATIC_PATH /app/app/static
ENV TEMPLATE_URL /template
ENV TEMPLATE_PATH /app/app/templates
ENV CLIENT_SECRET=CHANGEMEPLEASE

RUN pip install -r requirements.txt