# 🚀 Como Rodar o Projeto Django

## Passo 1: Criar Ambiente Virtual (Recomendado)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou no Windows:
# venv\Scripts\activate
```

## Passo 2: Instalar Dependências

```bash
pip install -r requirements.txt
```

## Passo 3: Configurar Variáveis de Ambiente

O arquivo `.env` já foi criado. Edite e configure as chaves do Stripe:

```env
STRIPE_SECRET_KEY=sk_test_sua_chave_aqui
STRIPE_PUBLISHABLE_KEY=pk_test_sua_chave_aqui
STRIPE_WEBHOOK_SECRET=whsec_seu_secret_aqui
DEBUG=True
DJANGO_SECRET_KEY=django-insecure-change-this-in-production
FRONTEND_URL=http://localhost:8000
```

## Passo 4: Executar Migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

## Passo 5: Criar Superusuário (Opcional)

```bash
python manage.py createsuperuser
```

Isso permite acessar o admin Django em `/admin/`

## Passo 6: Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --noinput
```

## Passo 7: Rodar o Servidor

```bash
python manage.py runserver
```

O servidor estará rodando em: **http://localhost:8000**

## 📝 URLs Importantes

- **Home:** http://localhost:8000/
- **Admin Django:** http://localhost:8000/admin/
- **API Auth:** http://localhost:8000/api/auth/
- **API Stripe:** http://localhost:8000/api/stripe/
- **API Subscriptions:** http://localhost:8000/api/subscriptions/
- **API Bookings:** http://localhost:8000/api/bookings/

## ⚠️ Nota Importante

**O servidor vai iniciar mesmo sem as chaves do Stripe configuradas**, mas:
- O checkout não funcionará até configurar o Stripe
- Você verá erros ao tentar fazer pagamentos
- Configure o Stripe para usar todas as funcionalidades

## 🧪 Testar Sem Stripe Configurado

Você pode:
- ✅ Navegar pelo site
- ✅ Criar conta e fazer login
- ✅ Ver o dashboard
- ✅ Ver o catálogo de tours
- ✅ Acessar o admin Django
- ❌ Fazer checkout (precisa do Stripe)

## 🆘 Problemas Comuns

### Erro: "No module named 'django'"
- Execute `pip install -r requirements.txt`

### Erro: "ModuleNotFoundError"
- Verifique se o ambiente virtual está ativado
- Reinstale as dependências

### Erro: "django.db.utils.OperationalError"
- Execute `python manage.py migrate`

### Erro: "Static files not found"
- Execute `python manage.py collectstatic`

### Porta 8000 já em uso
- Use outra porta: `python manage.py runserver 8001`

## 📚 Próximos Passos

1. Configure o Stripe seguindo o arquivo `README_DJANGO.md`
2. Crie produtos e preços no Stripe Dashboard
3. Configure o webhook para sincronização automática
4. Personalize os templates conforme necessário
