\getenv db_name POSTGRES_DB
\getenv admin_password POSTGRES_PASSWORD
\getenv app_user APP_DB_USER
\getenv app_password APP_DB_PASSWORD
\getenv metrics_user POSTGRES_EXPORTER_USER
\getenv metrics_password POSTGRES_EXPORTER_PASSWORD

SELECT length(:'admin_password') >= 24
   AND length(:'app_password') >= 24
   AND length(:'metrics_password') >= 24
   AND :'admin_password' NOT LIKE 'replace-with-%'
   AND :'app_password' NOT LIKE 'replace-with-%'
   AND :'metrics_password' NOT LIKE 'replace-with-%' AS strong_passwords
\gset

\if :strong_passwords
CREATE ROLE :"app_user" LOGIN PASSWORD :'app_password';
GRANT CONNECT ON DATABASE :"db_name" TO :"app_user";
GRANT USAGE, CREATE ON SCHEMA public TO :"app_user";

CREATE ROLE :"metrics_user" LOGIN PASSWORD :'metrics_password';
GRANT CONNECT ON DATABASE :"db_name" TO :"metrics_user";
GRANT pg_monitor TO :"metrics_user";
\else
\echo Database passwords must be unique, random, and at least 24 characters.
\quit 1
\endif
