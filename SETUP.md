# 🚀 Guia Rápido de Configuração - Django

## Passo 1: Instalar Dependências Python

```bash
pip install -r requirements.txt
```

## Passo 2: Configurar Stripe

1. **Criar conta no Stripe:**
   - Acesse https://stripe.com
   - Crie uma conta (modo teste é gratuito)

2. **Obter chaves da API:**
   - Acesse https://dashboard.stripe.com/test/apikeys
   - Copie a **Secret key** (começa com `sk_test_`)
   - Copie a **Publishable key** (começa com `pk_test_`)

3. **Configurar Webhook:**
   - Vá em Developers > Webhooks
   - Clique em "Add endpoint"
   - URL: `http://127.0.0.1:8000/api/stripe/webhook/` (ou sua URL de produção)
   - Selecione evento: `checkout.session.completed`
   - Copie o **Signing secret** (começa com `whsec_`)

## Passo 3: Criar Arquivo .env

O arquivo `.env` já existe. Edite e configure:

```env
STRIPE_SECRET_KEY=sk_test_SUA_CHAVE_SECRETA_AQUI
STRIPE_PUBLISHABLE_KEY=pk_test_SUA_CHAVE_PUBLICA_AQUI
STRIPE_WEBHOOK_SECRET=whsec_SEU_WEBHOOK_SECRET_AQUI

DEBUG=True
DJANGO_SECRET_KEY=django-insecure-change-this-in-production

FRONTEND_URL=http://localhost:8000
```

## Passo 4: Executar Migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

## Passo 5: Iniciar o Servidor Django

```bash
python manage.py runserver
```

## Passo 6: Testar

1. Acesse http://127.0.0.1:8000
2. Crie uma conta em `/register.html`
3. Faça login em `/login.html`
4. Veja o catálogo em `/catalogo.html`
5. Teste o checkout com cartão de teste: `4242 4242 4242 4242`

## 🧪 Cartões de Teste Stripe

- **Sucesso:** `4242 4242 4242 4242`
- **Requer autenticação:** `4000 0025 0000 3155`
- **Recusado:** `4000 0000 0000 0002`

Data: qualquer data futura (ex: 12/25)  
CVC: qualquer 3 dígitos (ex: 123)

## ⚠️ Problemas Comuns

### Erro: "No module named 'django'"
- Execute `pip install -r requirements.txt`

### Erro: "Stripe API key not found"
- Verifique se o arquivo `.env` existe e tem as chaves corretas

### Webhook não funciona
- Use o Stripe CLI para testar webhooks localmente:
  ```bash
  stripe listen --forward-to localhost:8000/api/stripe/webhook/
  ```

### Banco de dados não cria
- Execute `python manage.py makemigrations` e depois `python manage.py migrate`

## 📚 Próximos Passos

1. Configure produtos no Stripe Dashboard (não precisa de preços recorrentes)
2. Personalize os templates conforme necessário
3. Adicione suas próprias imagens na pasta `static/images`
4. Configure para produção quando estiver pronto
