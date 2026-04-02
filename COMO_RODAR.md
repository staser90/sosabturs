# 🚀 Como Rodar o Projeto Django

## Passo 1: Criar Ambiente Virtual (Recomendado)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou no Windows: venv\Scripts\activate
```

## Passo 2: Instalar Dependências

```bash
pip install -r requirements.txt
```

## Passo 3: Configurar Variáveis de Ambiente

O arquivo `.env` já foi criado. Edite e configure as chaves do Stripe:

1. **Criar conta no Stripe** (se ainda não tiver):
   - Acesse: https://stripe.com
   - Crie uma conta gratuita

2. **Obter chaves da API**:
   - Acesse: https://dashboard.stripe.com/test/apikeys
   - Copie a **Secret key** (começa com `sk_test_`)
   - Copie a **Publishable key** (começa com `pk_test_`)

3. **Editar o arquivo `.env`**:
   - Abra o arquivo `.env` na raiz do projeto
   - Substitua as chaves do Stripe pelas suas

## Passo 4: Executar Migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

## Passo 5: Criar Superusuário (Opcional)

```bash
python manage.py createsuperuser
```

## Passo 6: Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --noinput
```

## Passo 7: Rodar o Servidor Django

```bash
python manage.py runserver
```

## Passo 8: Acessar o Site

Após iniciar o servidor, acesse:
- **URL:** http://127.0.0.1:8000 ou http://localhost:8000
- O servidor estará rodando na porta 8000

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
- ❌ Fazer checkout (precisa do Stripe)

## 📝 Próximos Passos

1. Configure o Stripe seguindo o arquivo `COMO_RODAR_DJANGO.md`
2. Configure o webhook: `http://127.0.0.1:8000/api/stripe/webhook/`
3. Teste o checkout com cartão de teste: `4242 4242 4242 4242`

## 🆘 Problemas?

- **Erro ao iniciar:** Verifique se a porta 8000 está livre
- **Erro de módulo:** Execute `pip install -r requirements.txt` novamente
- **Erro do Stripe:** Configure as chaves no arquivo `.env`
- **Erro de migração:** Execute `python manage.py makemigrations` e depois `python manage.py migrate`
