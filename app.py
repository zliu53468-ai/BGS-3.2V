# app.py — LINE webhook router（根目錄版）
from fastapi import APIRouter, Request
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage

from config import CFG
from parse import parse_user_text        # 根目錄匯入
from server import parlay_api            # 直接呼叫本機 API 函式
from formatter_flex import make_parlay_flex, make_no_pick_flex  # 修正：非相對匯入

router = APIRouter()

line_bot_api = LineBotApi(CFG["LINE_CHANNEL_ACCESS_TOKEN"])
parser = WebhookParser(CFG["LINE_CHANNEL_SECRET"])

@router.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = (await request.body()).decode("utf-8")

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        return "Signature mismatch", 400

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            user_text = event.message.text.strip()
            q = parse_user_text(user_text)

            resp = parlay_api(
                league=q["league"], date=q["date"], legs=q["legs"],
                market_filter=q["market"], channel=q["channel"]
            )
            picks = resp["parlays"]
            flex = make_no_pick_flex(q["league"], q["date"]) if not picks else make_parlay_flex(resp, picks, q["risk"])
            line_bot_api.reply_message(event.reply_token, flex)

    return "OK", 200
