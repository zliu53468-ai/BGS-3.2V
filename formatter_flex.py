from linebot.models import FlexSendMessage

def make_parlay_flex(resp, picks, risk_profile):
    channel = resp["channel"]
    p = picks[0]
    legs = []
    for leg in p["legs"]:
        legs.append({
            "type": "text",
            "text": f"{leg['game_id']}｜{leg['market']} {leg['side']} {leg.get('line','') or ''} @ {leg['odds']:.2f} (p={leg['p']*100:.1f}%)",
            "size": "sm", "wrap": True
        })
    bubble = {
      "type": "bubble",
      "body": { "type": "box", "layout": "vertical", "contents": [
          { "type": "text", "text": f"🎯 {len(p['legs'])}腿串關｜{risk_profile}｜{channel}",
            "weight": "bold", "size": "lg" },
          *legs,
          { "type": "separator", "margin": "md" },
          { "type": "text", "text": f"📈 組合命中率：{p['parlay_p']*100:.2f}%", "size": "sm" },
          { "type": "text", "text": f"💰 組合賠率：{p['parlay_odds']:.2f}", "size": "sm" },
          { "type": "text", "text": f"🔍 EV 預期值：{p['ev']*100:.1f}%", "size": "sm" },
          { "type": "text", "text": "⚠️ 風控提示：串關波動較大，請設定停損。", "color": "#888", "size": "xs", "wrap": True }
      ]},
      "footer": { "type": "box", "layout": "horizontal", "spacing": "md", "contents": [
          { "type": "button", "style": "primary",
            "action": { "type": "message", "label": "🔁 換一組", "text": "再一組" } },
          { "type": "button", "style": "secondary",
            "action": { "type": "message", "label": "📌 換管別", "text": "換管別" } }
      ]}
    }
    return FlexSendMessage(alt_text="串關推薦", contents=bubble)

def make_no_pick_flex(league, date):
    bubble = {
      "type": "bubble",
      "body": { "type": "box", "layout": "vertical", "contents": [
          { "type": "text", "text": f"今天 {league} 無合格串關", "weight": "bold", "size": "lg" },
          { "type": "text", "text": f"{date or ''} 賽程評估後無正期望值組合，建議觀望。", "size": "sm", "wrap": True }
      ]}
    }
    return FlexSendMessage(alt_text="無推薦", contents=bubble)
