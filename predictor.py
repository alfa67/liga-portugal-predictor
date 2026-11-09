#!/usr/bin/env python3
"""
Liga Portugal Betclic - Modelo Preditivo Estatístico de Jogos
Executa na Nuvem (GitHub Actions) e envia relatórios via Telegram ou Markdown.
"""

import math
import os
import sys
from datetime import datetime

# ==========================================
# 1. BASE DE DADOS: DADOS ATUAIS DA LIGA
# ==========================================
TEAMS_DATA = {
    "FC Porto": {"attack": 2.45, "defense": 0.45, "points": 33, "played": 11},
    "SL Benfica": {"attack": 2.30, "defense": 0.82, "points": 28, "played": 11},
    "Sporting CP": {"attack": 1.95, "defense": 0.70, "points": 24, "played": 11},
    "Santa Clara": {"attack": 1.40, "defense": 1.05, "points": 22, "played": 11},
    "Académico de Viseu": {"attack": 1.35, "defense": 1.00, "points": 21, "played": 11},
    "FC Arouca": {"attack": 1.30, "defense": 1.15, "points": 20, "played": 11},
    "SC Braga": {"attack": 1.65, "defense": 1.10, "points": 17, "played": 11},
    "Gil Vicente FC": {"attack": 1.25, "defense": 1.15, "points": 15, "played": 11},
    "Moreirense FC": {"attack": 1.10, "defense": 1.20, "points": 14, "played": 11},
    "FC Famalicão": {"attack": 1.15, "defense": 1.20, "points": 13, "played": 11},
    "FC Alverca": {"attack": 1.05, "defense": 1.35, "points": 12, "played": 11},
    "Estrela da Amadora": {"attack": 1.00, "defense": 1.60, "points": 10, "played": 11},
    "Vitória SC": {"attack": 1.20, "defense": 1.45, "points": 9, "played": 11},
    "CS Marítimo": {"attack": 0.90, "defense": 1.40, "points": 8, "played": 10},
    "Casa Pia AC": {"attack": 0.85, "defense": 1.45, "points": 8, "played": 11},
    "Rio Ave FC": {"attack": 0.80, "defense": 1.60, "points": 7, "played": 11},
    "CD Nacional": {"attack": 0.80, "defense": 1.55, "points": 7, "played": 11},
    "Estoril Praia": {"attack": 0.70, "defense": 1.90, "points": 2, "played": 10},
}

# Fator de Vantagem de Jogar em Casa (Home Advantage Factor)
LEAGUE_AVG_GOALS = 1.35
HOME_ADVANTAGE = 1.18

# Jogos da Próxima Jornada (Jornada 12)
UPCOMING_FIXTURES = [
    {"home": "CS Marítimo", "away": "CD Nacional", "date": "27/11 20:15", "notes": "Dérbi da Madeira"},
    {"home": "FC Arouca", "away": "Rio Ave FC", "date": "28/11 15:30", "notes": ""},
    {"home": "Moreirense FC", "away": "Santa Clara", "date": "28/11 18:00", "notes": ""},
    {"home": "Académico de Viseu", "away": "FC Alverca", "date": "28/11 18:00", "notes": ""},
    {"home": "Vitória SC", "away": "Estrela da Amadora", "date": "29/11 15:30", "notes": ""},
    {"home": "Gil Vicente FC", "away": "Estoril Praia", "date": "29/11 18:00", "notes": ""},
    {"home": "FC Porto", "away": "Sporting CP", "date": "29/11 20:30", "notes": "🔥 Grande Clássico no Dragão"},
    {"home": "Casa Pia AC", "away": "SC Braga", "date": "30/11 20:15", "notes": ""},
    {"home": "SL Benfica", "away": "FC Famalicão", "date": "30/11 20:15", "notes": "Estádio da Luz"},
]

# ==========================================
# 2. MODELO ESTATÍSTICO DE POISSON
# ==========================================
def poisson_probability(k: int, lambd: float) -> float:
    """Calcula a probabilidade de ocorrer k golos com média lambd."""
    return (lambd ** k * math.exp(-lambd)) / math.factorial(k)

def predict_match(home_team: str, away_team: str):
    """Calcula as probabilidades 1X2, Over/Under e resultado exato mais provável."""
    home_stats = TEAMS_DATA.get(home_team, {"attack": 1.0, "defense": 1.0})
    away_stats = TEAMS_DATA.get(away_team, {"attack": 1.0, "defense": 1.0})

    # Expected Goals (xG) estimado
    lambda_home = home_stats["attack"] * (away_stats["defense"] / LEAGUE_AVG_GOALS) * HOME_ADVANTAGE
    lambda_away = away_stats["attack"] * (home_stats["defense"] / LEAGUE_AVG_GOALS) / HOME_ADVANTAGE

    # Matriz de probabilidades até 6 golos por equipa
    max_goals = 7
    home_win_prob = 0.0
    draw_prob = 0.0
    away_win_prob = 0.0
    over_2_5_prob = 0.0

    score_matrix = {}

    for h in range(max_goals):
        for a in range(max_goals):
            p = poisson_probability(h, lambda_home) * poisson_probability(a, lambda_away)
            score_matrix[(h, a)] = p
            if h > a:
                home_win_prob += p
            elif h == a:
                draw_prob += p
            else:
                away_win_prob += p

            if h + a > 2.5:
                over_2_5_prob += p

    # Ordenar resultados mais prováveis
    sorted_scores = sorted(score_matrix.items(), key=lambda item: item[1], reverse=True)
    top_score_1 = sorted_scores[0]
    top_score_2 = sorted_scores[1]

    return {
        "home": home_team,
        "away": away_team,
        "lambda_home": round(lambda_home, 2),
        "lambda_away": round(lambda_away, 2),
        "prob_home": round(home_win_prob * 100, 1),
        "prob_draw": round(draw_prob * 100, 1),
        "prob_away": round(away_win_prob * 100, 1),
        "prob_over_2_5": round(over_2_5_prob * 100, 1),
        "top_score_1": f"{top_score_1[0][0]}–{top_score_1[0][1]}",
        "top_score_1_pct": round(top_score_1[1] * 100, 1),
        "top_score_2": f"{top_score_2[0][0]}–{top_score_2[0][1]}",
        "top_score_2_pct": round(top_score_2[1] * 100, 1),
    }

# ==========================================
# 3. GERAÇÃO DO RELATÓRIO
# ==========================================
def generate_report():
    results = [predict_match(f["home"], f["away"]) for f in UPCOMING_FIXTURES]
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    md_lines = [
        f"# ⚽ Boletim Preditivo da Liga Portugal Betclic",
        f"*Atualizado automaticamente na Nuvem em: {now}*",
        "",
        "### 📊 Previsões da 12.ª Jornada",
        "",
        "| Data | Jogo | 1X2 (%) | Mais/Menos 2.5 | Resultado Mais Provável | Nota |",
        "| :--- | :--- | :---: | :---: | :---: | :--- |",
    ]

    for fix, res in zip(UPCOMING_FIXTURES, results):
        prob_str = f"**{res['prob_home']}%** | {res['prob_draw']}% | {res['prob_away']}%"
        over_str = f"+2.5 ({res['prob_over_2_5']}%)" if res['prob_over_2_5'] > 50 else f"-2.5 ({100 - res['prob_over_2_5']}%)"
        exact_str = f"`{res['top_score_1']}` ({res['top_score_1_pct']}%) / `{res['top_score_2']}`"
        md_lines.append(f"| {fix['date']} | **{res['home']}** vs **{res['away']}** | {prob_str} | {over_str} | {exact_str} | {fix['notes']} |")

    md_lines.extend([
        "",
        "---",
        "### 🧠 Destaques Estatísticos:",
        "- **Maior Favoritismo:** SL Benfica (vence em casa ~70-75%) e Gil Vicente.",
        "- **Jogo Mais Tático e Disputado:** FC Porto vs Sporting CP (Menos de 2.5 golos provável).",
        "- **Tendência de Empate:** Marítimo vs CD Nacional (Dérbi da Madeira).",
        "",
        "> *Nota: As previsões baseiam-se na distribuição estatística de Poisson e métricas de desempenho recente.*"
    ])

    report_content = "\n".join(md_lines)
    with open("PREDICTIONS.md", "w", encoding="utf-8") as f:
        f.write(report_content)

    print("✅ Relatório PREDICTIONS.md gerado com sucesso!")
    return report_content

# ==========================================
# 4. ENVIO PARA TELEGRAM (OPCIONAL / GRÁTIS)
# ==========================================
def send_telegram_alert(report_text: str):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("ℹ️ Telegram não configurado (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID não definidos).")
        return

    try:
        import urllib.request
        import urllib.parse
        import json

        # Resumo compacto para Telegram
        msg = "⚽ *Liga Portugal - Previsões da 12ª Jornada*\n\n"
        for fix in UPCOMING_FIXTURES[:5]:
            p = predict_match(fix["home"], fix["away"])
            msg += f"📍 *{p['home']}* vs *{p['away']}*\n"
            msg += f"• 1X2: {p['prob_home']}% / {p['prob_draw']}% / {p['prob_away']}%\n"
            msg += f"• Placar provável: `{p['top_score_1']}`\n\n"

        msg += "👉 Consulta o relatório completo no repositório GitHub!"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = json.dumps({"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("📲 Notificação enviada para o Telegram com sucesso!")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem para o Telegram: {e}")

if __name__ == "__main__":
    report = generate_report()
    send_telegram_alert(report)
