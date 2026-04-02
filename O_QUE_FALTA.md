# O que falta para terminar o projeto SO SAB / Tours SaaS

Resumo do que está feito e do que falta para fechar o projeto.

---

## ✅ Já implementado

- **Autenticação:** Registo, login (email/username + senha), login com Google (opcional), logout, perfil, alterar senha
- **Packs (motas):** Catálogo, carrinho, checkout Stripe, sucesso
- **Transfer & Excursões:** Página com tarifário, imagens SVG por veículo, mesmo carrinho e checkout que os packs
- **Reservas:** API para listar/criar reservas do utilizador, dashboard com “Minhas Reservas”, impressão de comprovativo
- **Admin Django:** Reservas com estatísticas (total, receita, confirmadas, hoje, mês), foto do produto na lista, ações (aprovar/cancelar/concluir), aspecto SO SAB
- **Perfil:** Estatísticas (total de reservas, total gasto, reservas confirmadas) a vir do servidor
- **Galeria:** Página com imagens da pasta estática
- **Contacto:** Página com morada, telefone, email e mapa
- **Stripe:** Checkout para múltiplos itens (carrinho), webhook para confirmar reserva
- **WhatsApp:** Widget de chat
- **Chatbot:** Endpoint de API (opcional, Ollama)

---

## 🔲 O que falta (por prioridade)

### 1. Recuperação de senha por email (importante para utilizadores)

- **Estado:** As views em `accounts/password_reset_views.py` existem, mas:
  - Não há rotas para elas em `accounts/urls.py` (nem em `tours_saas/urls.py`)
  - Não existem templates em `templates/registration/` (formulário “Esqueci a senha”, “email enviado”, “nova senha”, “senha alterada”)
  - Na página de login não há link “Esqueci a senha”
- **Para terminar:**
  - Adicionar rotas para as 4 views de password reset (form, done, confirm, complete)
  - Criar os 4 templates em `templates/registration/` (estilo alinhado ao resto do site)
  - Na página de login, adicionar link “Esqueci a senha” que aponta para a view de pedido de reset
  - Configurar email no `.env` (Gmail ou outro SMTP) para o Django conseguir enviar o link de recuperação

### 2. Configuração do Stripe em produção

- **Webhook:** No `.env` está `STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here`. É preciso:
  - No Stripe Dashboard → Developers → Webhooks, criar um endpoint com a URL de produção (ex.: `https://seudominio.com/api/stripe/webhook/`)
  - Selecionar o evento `checkout.session.completed` (e outros que usem no webhook)
  - Copiar o “Signing secret” e colar no `.env` como `STRIPE_WEBHOOK_SECRET`
- **Chaves:** Trocar para chaves de produção (Live) no `.env`: `STRIPE_SECRET_KEY` e `STRIPE_PUBLISHABLE_KEY`; no front (checkout/success) usar a publishable key de produção.

### 3. Formulário de contacto (opcional)

- A página Contacto mostra apenas texto e mapa. Se quiserem que os clientes enviem mensagem:
  - Formulário (nome, email, mensagem) que submete para uma view
  - View que envia email para vocês (usando o mesmo SMTP do ponto 1) ou que guarda num modelo “ContactMessage” e depois consultam no admin

### 4. Emails de confirmação de reserva (opcional)

- Existem templates em `bookings/templates/emails/` (ex.: confirmação e recibo). Falta:
  - Chamar o envio de email quando a reserva é confirmada (por exemplo no webhook do Stripe ou na view de confirmação)
  - Ter SMTP configurado no `.env` (igual ao ponto 1)

### 5. Preparação para produção (Django)

- **Checklist (resumo):**
  - [ ] `DEBUG=False` no `.env`
  - [ ] `DJANGO_SECRET_KEY` forte e único (gerar novo, não usar o de desenvolvimento)
  - [ ] `ALLOWED_HOSTS` em `settings.py` com o(s) domínio(s) de produção (remover `'*'` se estiver)
  - [ ] Base de dados: usar PostgreSQL (ou outro) em produção; configurar em `settings.py` via `.env` (DATABASE_URL ou variáveis individuais)
  - [ ] Ficheiros estáticos: `python manage.py collectstatic` e servir com Nginx/Apache ou CDN
  - [ ] HTTPS no servidor e, se aplicável, `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` em `settings.py`
  - [ ] Configurar domínio e, se for caso, variável `FRONTEND_URL` para as URLs de redirect (ex.: sucesso, login)

### 6. Outros detalhes (opcionais)

- **Página de contacto / success:** Adicionar link “Transfer & Excursões” no menu (como nas outras páginas) para consistência.
- **App `subscriptions`:** Existe no projeto mas não está em `INSTALLED_APPS`. Se não for usada, pode ficar assim; se for, adicionar à lista e criar migrações.
- **README:** Atualizar com Transfer & Excursões, galeria, admin SO SAB e, se fizerem recuperação de senha e contacto, referir isso também.

---

## Resumo muito breve

| Item                         | Estado        | Prioridade |
|-----------------------------|---------------|------------|
| Recuperação de senha        | Falta ligar + templates + email | Alta       |
| Stripe webhook (produção)   | Falta secret real + URL produção | Alta       |
| Stripe chaves produção      | Trocar no .env e no front        | Alta       |
| Formulário de contacto      | Opcional                          | Média      |
| Email de confirmação reserva| Opcional (templates já existem)   | Média      |
| Deploy (DEBUG, DB, HTTPS…)  | Checklist no README               | Alta       |

Quando a recuperação de senha estiver ligada e com templates, o Stripe de produção configurado e o deploy feito conforme o checklist, o projeto pode ser dado como terminado do ponto de vista funcional e de produção. O resto (contacto, emails de reserva, README) melhora a experiência e a operação.
