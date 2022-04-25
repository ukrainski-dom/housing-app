FROM node:17-bullseye as build

COPY . /app
WORKDIR /app

RUN npm i --prefix house_of_refuge/frontend && \
    npm run build --prefix house_of_refuge/frontend

FROM python:3.9-bullseye

COPY --from=build /app /app
WORKDIR /app

RUN apt update && \
    apt install -y gettext && \
    pip install -U pip && \
    pip install -r requirements/production.txt && \
    python manage.py collectstatic --no-input && \
    django-admin compilemessages
