#!/bin/sh
set -eu

if [ "${#POSTGRES_PASSWORD}" -lt 24 ] || [ "${#APP_DB_PASSWORD}" -lt 24 ] || [ "${#POSTGRES_EXPORTER_PASSWORD}" -lt 24 ]; then
  echo "Database passwords must each be at least 24 characters." >&2
  exit 1
fi
case "$POSTGRES_PASSWORD$APP_DB_PASSWORD$POSTGRES_EXPORTER_PASSWORD" in
  *replace-with-*) echo "Replace all sample database passwords before starting PostgreSQL." >&2; exit 1 ;;
esac

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set=db_name="$POSTGRES_DB" \
  --set=app_user="$APP_DB_USER" \
  --set=app_password="$APP_DB_PASSWORD" \
  --set=metrics_user="$POSTGRES_EXPORTER_USER" \
  --set=metrics_password="$POSTGRES_EXPORTER_PASSWORD" <<'SQL'
CREATE ROLE :"app_user" LOGIN PASSWORD :'app_password';
GRANT CONNECT ON DATABASE :"db_name" TO :"app_user";
GRANT USAGE, CREATE ON SCHEMA public TO :"app_user";

CREATE ROLE :"metrics_user" LOGIN PASSWORD :'metrics_password';
GRANT CONNECT ON DATABASE :"db_name" TO :"metrics_user";
GRANT pg_monitor TO :"metrics_user";
SQL
