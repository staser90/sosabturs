# Dilan Tours SaaS - Django

SaaS profissional para gestão de tours na Ilha do Sal com integração completa do Stripe, construído com Django e Django REST Framework.

## 🚀 Funcionalidades

- ✅ Sistema de autenticação (registro/login) com JWT
- ✅ Checkout Stripe para reservas únicas
- ✅ Planos de assinatura recorrentes
- ✅ Dashboard do usuário
- ✅ Gestão de assinaturas (cancelar/reativar)
- ✅ Portal do cliente Stripe
- ✅ Webhooks do Stripe para sincronização
- ✅ Banco de dados SQLite (fácil migração para PostgreSQL)

## 📋 Pré-requisitos

- Python 3.9+
- pip
- Conta Stripe (teste ou produção)

## 🔧 Instalação

1. **Criar ambiente virtual (recomendado):**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

3. **Configurar variáveis de ambiente:**

Edite o arquivo `.env` na raiz do projeto:

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Django Configuration
DEBUG=True
DJANGO_SECRET_KEY=django-insecure-change-this-in-production

# Frontend URL
FRONTEND_URL=http://localhost:8000
```

4. **Executar migrações:**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Criar superusuário (opcional):**
```bash
python manage.py createsuperuser
```

6. **Coletar arquivos estáticos:**
```bash
python manage.py collectstatic --noinput
```

7. **Iniciar servidor:**
```bash
python manage.py runserver
```

O servidor estará rodando em: http://localhost:8000

## 📝 Configuração do Stripe

### Criar Produtos e Preços

1. Acesse [Stripe Dashboard](https://dashboard.stripe.com)
2. Vá em Products > Add product
3. Crie produtos para seus planos (ex: "Plano Básico", "Plano Premium")
4. Configure preços recorrentes (mensal/anual)
5. Copie os Price IDs (começam com `price_`)

### Configurar Webhook

1. Vá em Developers > Webhooks
2. Clique em "Add endpoint"
3. URL: `http://localhost:8000/api/stripe/webhook/` (ou sua URL de produção)
4. Selecione os eventos:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
5. Copie o "Signing secret" e adicione ao `.env` como `STRIPE_WEBHOOK_SECRET`

## 🗂️ Estrutura do Projeto

```
tours-saas/
├── accounts/              # App de autenticação
│   ├── models.py          # Modelo User customizado
│   ├── views.py           # Views de autenticação
│   └── serializers.py      # Serializers
├── stripe_app/            # App do Stripe
│   ├── views.py           # Checkout e webhooks
│   └── urls.py
├── subscriptions/         # App de assinaturas
│   ├── models.py          # Modelo Subscription
│   └── views.py           # Gestão de assinaturas
├── bookings/             # App de reservas
│   ├── models.py          # Modelo Booking
│   └── views.py           # Listagem de reservas
├── tours_saas/           # Configurações do projeto
│   ├── settings.py        # Configurações Django
│   └── urls.py            # URLs principais
├── templates/            # Templates HTML
├── static/               # Arquivos estáticos (CSS, JS, imagens)
├── manage.py
└── requirements.txt
```

## 🔐 Autenticação

O sistema usa JWT (JSON Web Tokens) através do Django REST Framework Simple JWT.

**Endpoints:**
- `POST /api/auth/register/` - Criar conta
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/me/` - Obter usuário atual

## 💳 Pagamentos

### Reservas Únicas
- `POST /api/stripe/create-booking-checkout/` - Criar checkout para reserva
- Checkout Stripe para pagamentos únicos
- Suporte a extras (fato de mergulho, GoPro, etc.)

### Assinaturas
- `POST /api/stripe/create-checkout-session/` - Criar checkout para assinatura
- `GET /api/stripe/prices/` - Listar preços disponíveis
- `GET /api/subscriptions/current/` - Assinatura atual
- `POST /api/subscriptions/cancel/` - Cancelar assinatura
- `POST /api/subscriptions/reactivate/` - Reativar assinatura
- `POST /api/subscriptions/portal/` - Portal do cliente

## 🧪 Testes

Use os cartões de teste do Stripe:

- **Sucesso:** `4242 4242 4242 4242`
- **Requer autenticação:** `4000 0025 0000 3155`
- **Recusado:** `4000 0000 0000 0002`

Data de expiração: qualquer data futura  
CVC: qualquer 3 dígitos

## 🚢 Deploy

### Opções de Deploy

1. **Heroku**
2. **Railway**
3. **Render**
4. **DigitalOcean App Platform**
5. **AWS/GCP/Azure**

### Checklist de Deploy

- [ ] Configurar `DEBUG=False` em produção
- [ ] Usar `DJANGO_SECRET_KEY` forte e único
- [ ] Configurar chaves Stripe de produção
- [ ] Configurar webhook com URL de produção
- [ ] Configurar banco de dados PostgreSQL (recomendado)
- [ ] Configurar domínio personalizado
- [ ] Habilitar HTTPS
- [ ] Configurar `ALLOWED_HOSTS`
- [ ] Executar `collectstatic`

## 📚 Comandos Úteis

```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic

# Acessar shell Django
python manage.py shell

# Rodar testes
python manage.py test
```

## 🔧 Migração de Node.js para Django

Este projeto foi migrado de Node.js/Express para Django. As principais mudanças:

- ✅ Backend agora em Python/Django
- ✅ Autenticação com Django REST Framework Simple JWT
- ✅ Models Django ao invés de SQLite direto
- ✅ Templates Django ao invés de HTML estático
- ✅ Admin Django para gestão de dados
- ✅ API REST completa

## 📄 Licença

ISC

## 🤝 Suporte

Para questões ou problemas, abra uma issue no repositório.

---

Desenvolvido com ❤️ para Dilan Tours usando Django
