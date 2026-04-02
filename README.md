# Dilan Tours - Sistema de Reservas

Sistema profissional de reservas de tours na Ilha do Sal com integração Stripe para pagamentos.

## 🚀 Funcionalidades

- ✅ Sistema de autenticação (registro/login) com JWT
- ✅ Checkout Stripe para pagamentos únicos
- ✅ Dashboard do usuário para visualizar reservas
- ✅ Gestão de reservas
- ✅ Webhooks do Stripe para sincronização automática
- ✅ Interface moderna e responsiva

## 📋 Pré-requisitos

- Python 3.9+
- pip
- Conta Stripe (teste ou produção)

## 🔧 Instalação

1. **Criar ambiente virtual:**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou no Windows: venv\Scripts\activate
```

2. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

3. **Configurar variáveis de ambiente:**

Edite o arquivo `.env`:

```env
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
DEBUG=True
DJANGO_SECRET_KEY=django-insecure-change-this-in-production
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

Acesse: http://localhost:8000

## 📝 Configuração do Stripe

### Obter Chaves da API

1. Acesse [Stripe Dashboard](https://dashboard.stripe.com)
2. Vá em Developers > API keys
3. Copie a chave secreta (Secret key) e chave pública (Publishable key)

### Configurar Webhook

1. Vá em Developers > Webhooks
2. Clique em "Add endpoint"
3. URL: `http://localhost:8000/api/stripe/webhook/` (ou sua URL de produção)
4. Selecione o evento: `checkout.session.completed`
5. Copie o "Signing secret" e adicione ao `.env`

## 🗂️ Estrutura do Projeto

```
tours-saas/
├── accounts/              # App de autenticação
│   ├── models.py          # Modelo User customizado
│   ├── views.py           # Views de autenticação
│   └── serializers.py     # Serializers
├── stripe_app/            # App do Stripe
│   ├── views.py           # Checkout e webhooks
│   └── urls.py
├── bookings/              # App de reservas
│   ├── models.py          # Modelo Booking
│   └── views.py          # Listagem de reservas
├── tours_saas/           # Configurações do projeto
│   ├── settings.py        # Configurações Django
│   └── urls.py            # URLs principais
├── templates/            # Templates HTML
├── static/               # Arquivos estáticos
├── manage.py
└── requirements.txt
```

## 🔐 API Endpoints

### Autenticação
- `POST /api/auth/register/` - Criar conta
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/me/` - Obter usuário atual

### Stripe
- `POST /api/stripe/create-booking-checkout/` - Criar checkout para reserva
- `POST /api/stripe/webhook/` - Webhook do Stripe

### Reservas
- `GET /api/bookings/` - Listar reservas do usuário
- `GET /api/bookings/:id/` - Obter reserva específica

## 🧪 Testes com Stripe

Use os cartões de teste do Stripe:

- **Sucesso:** `4242 4242 4242 4242`
- **Requer autenticação:** `4000 0025 0000 3155`
- **Recusado:** `4000 0000 0000 0002`

Data de expiração: qualquer data futura  
CVC: qualquer 3 dígitos

## 🚢 Deploy

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
```

## 📄 Licença

ISC

---

Desenvolvido com ❤️ para Dilan Tours
