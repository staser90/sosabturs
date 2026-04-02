# Deploy no Render (Django)

## O que foi preparado

- **Gunicorn** + **WhiteNoise** para servir estáticos em produção.
- **PostgreSQL** quando `DATABASE_URL` está definida (Render injeta ao ligar a base de dados).
- **ALLOWED_HOSTS**, **CSRF_TRUSTED_ORIGINS**, **CORS_ALLOWED_ORIGINS** e **FRONTEND_URL** via variáveis de ambiente.
- **HTTPS** atrás do proxy do Render (`SECURE_PROXY_SSL_HEADER`, cookies seguros).
- **Rotas HTML** (catálogo, login, checkout, etc.) ativas com `DEBUG=False` (antes só existiam em modo debug).
- Ficheiros: `build.sh`, `Procfile`, `render.yaml` (opcional), `.env.example`.

## Passos no Render

1. Criar um **PostgreSQL** (free ou pago) e copiar a URL interna se precisares.
2. Criar um **Web Service** a partir do repositório Git (Python 3.10).
3. **Build command:** `chmod +x build.sh && ./build.sh`  
   **Start command:** `gunicorn tours_saas.wsgi:application --bind 0.0.0.0:$PORT`
4. Em **Environment**, ligar a base de dados ao serviço (o Render define `DATABASE_URL`).
5. Definir manualmente (ver `.env.example`):

   | Variável | Notas |
   |----------|--------|
   | `DJANGO_SECRET_KEY` | Obrigatório; não usar o default de desenvolvimento. |
   | `DEBUG` | `False` |
   | `FRONTEND_URL` | URL pública HTTPS, ex. `https://nome-do-servico.onrender.com` |
   | `ALLOWED_HOSTS` | Ex. `nome-do-servico.onrender.com,.onrender.com` |
   | `CSRF_TRUSTED_ORIGINS` | Ex. `https://nome-do-servico.onrender.com` |
   | `CORS_ALLOWED_ORIGINS` | Normalmente o mesmo URL HTTPS |
   | `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET` | Chaves de teste ou live |
   | Email (opcional) | `EMAIL_*` se quiseres envio real |

6. No **Stripe Dashboard**, atualizar URLs de sucesso/cancelamento e webhook para o domínio de produção (`FRONTEND_URL`).
7. Fazer **deploy**. O `build.sh` corre `migrate` e `collectstatic`.

## Notas

- **Ficheiros em `media/`**: no plano free o disco é efémero; uploads podem perder-se ao reiniciar. Para produção séria, usar S3 ou similar.
- **Primeiro deploy**: criar superutilizador com `python manage.py createsuperuser` (shell do Render ou job one-off).
- **Blueprint**: podes usar `render.yaml` e ajustar o nome do serviço e variáveis sensíveis no painel.
