FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=10001:2000 . .
RUN mkdir -p /var/log/contracts /staticfiles \
    && chown -R 10001:2000 /var/log/contracts /staticfiles /app \
    && chmod 2770 /var/log/contracts \
    && DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')" python manage.py collectstatic --noinput \
    && chown -R 10001:2000 /var/log/contracts /staticfiles /app

USER 10001:2000

EXPOSE 8000

CMD ["gunicorn", "contract_portal.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-", "--error-logfile", "-"]
