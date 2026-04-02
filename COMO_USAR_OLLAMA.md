# 🤖 Como Usar Ollama com o Chatbot

O chatbot agora suporta **Ollama** - uma IA gratuita e local que roda no seu computador!

## 📋 Opções Disponíveis

### Opção 1: Usar Respostas Inteligentes (Padrão - Sem Instalação)
O chatbot já funciona com respostas inteligentes baseadas em padrões. **Não precisa instalar nada!**

### Opção 2: Usar Ollama (IA Local Gratuita)

#### Passo 1: Instalar Ollama
```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Ou baixe de: https://ollama.com/download
```

#### Passo 2: Baixar um Modelo
```bash
# Modelo pequeno e rápido (recomendado)
ollama pull llama3.2

# Ou modelo maior (mais inteligente, mas mais lento)
ollama pull llama3.1
```

#### Passo 3: Iniciar Ollama
```bash
ollama serve
```

#### Passo 4: Configurar no .env
Edite o arquivo `.env` e adicione:
```env
USE_OLLAMA=True
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.2
```

#### Passo 5: Reiniciar o Django
```bash
python3 manage.py runserver
```

## ✅ Pronto!

Agora o chatbot usará Ollama para gerar respostas mais inteligentes e naturais!

## 🔧 Troubleshooting

### Ollama não está respondendo?
- Verifique se `ollama serve` está rodando
- Teste: `curl http://localhost:11434/api/tags`
- Verifique se o modelo está instalado: `ollama list`

### Quer usar outro modelo?
- Veja modelos disponíveis: https://ollama.com/library
- Altere `OLLAMA_MODEL` no `.env`

### Não quer usar Ollama?
- Deixe `USE_OLLAMA=False` no `.env`
- O chatbot continuará funcionando com respostas inteligentes

## 💡 Vantagens do Ollama

✅ **100% Gratuito**
✅ **Roda localmente** (seus dados não saem do seu computador)
✅ **Sem limites de uso**
✅ **Funciona offline**
✅ **Respostas mais naturais e inteligentes**
