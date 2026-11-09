# ⚽ Previsor Estatístico da Liga Portugal Betclic (100% Cloud)

Sistema autónomo na nuvem que calcula previsões de resultados da Liga Portugal utilizando **distribuição de Poisson**, forças ofensivas/defensivas e vantagem em casa (*Home Advantage*).

---

## ☁️ Como funciona na Nuvem (Com o computador desligado):

1. **GitHub Actions (Grátis):**
   * O fluxo agendado em [`.github/workflows/weekly_predictions.yml`](.github/workflows/weekly_predictions.yml) acorda automaticamente na nuvem **duas vezes por semana** (segundas e sextas-feiras às 09:00 UTC).
   * Executa [`predictor.py`](predictor.py), calcula as probabilidades e atualiza o ficheiro [`PREDICTIONS.md`](PREDICTIONS.md).
   * Faz commit automático do novo relatório para o repositório.

2. **Execução Manual (A qualquer momento):**
   * No separador **Actions** do seu repositório GitHub, clique em **Previsões Automáticas da Liga Portugal** e no botão **Run workflow**.

---

## 📱 Notificações Gratuitas no Telegram (Opcional):

Para receber as previsões diretamente no seu telemóvel:

1. No Telegram, procure por `@BotFather`, envie `/newbot` e guarde o **Token** gerado.
2. Envie uma mensagem para o seu novo bot ou procure por `@userinfobot` para obter o seu **Chat ID**.
3. No seu repositório GitHub:
   * Vá a **Settings** > **Secrets and variables** > **Actions** > **New repository secret**.
   * Adicione:
     * `TELEGRAM_BOT_TOKEN`: o token fornecido pelo BotFather.
     * `TELEGRAM_CHAT_ID`: o seu ID numérico.

A partir desse momento, antes de cada jornada, o bot envia o resumo das previsões para o seu telemóvel!
