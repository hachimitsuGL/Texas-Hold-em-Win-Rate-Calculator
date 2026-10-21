"""Simple Flask UI for Texas_winrate.py."""

from flask import Flask, jsonify, render_template, request
from Texas_winrate import Card, RANKS, compare_set

app = Flask(__name__)

SUIT_CODES = {"S": "spade", "H": "heart", "D": "diamond", "C": "club"}


def parse_card(code):
    """Convert an SVG-style code (e.g. 'AS') to the original Card class."""
    if not isinstance(code, str) or len(code) != 2:
        raise ValueError("Invalid card code")
    rank, suit = code[0], code[1]
    if rank not in RANKS or suit not in SUIT_CODES:
        raise ValueError("Invalid card code")
    return Card(SUIT_CODES[suit], rank)


def calculate_win_rates(player1_cards, player2_cards, community_cards):
    # 実際の勝率計算はまだ実装していないため、現時点では勝者の勝率を100%として表示する
    result = compare_set(
        player1_cards + community_cards, player2_cards + community_cards
    )
    if result == 1:
        return 100.0, 0.0
    if result == -1:
        return 0.0, 100.0
    return 50.0, 50.0


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/compare")
def compare():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Expected JSON data"), 400

    community = data.get("community")
    players = data.get("players")
    if (
        not isinstance(community, list)
        or len(community) != 5
        or not isinstance(players, list)
        or len(players) != 2
        or any(not isinstance(hand, list) or len(hand) != 2 for hand in players)
    ):
        return (
            jsonify(error="Expected 5 community slots and 2 players with 2 slots each"),
            400,
        )

    all_slots = community + players[0] + players[1]
    selected = [code for code in all_slots if code is not None]
    if len(selected) != len(set(map(str, selected))):
        return jsonify(error="The same card cannot be used twice"), 400
    try:
        for code in selected:
            parse_card(code)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    if any(code is None for hand in players for code in hand):
        return jsonify(
            ready=False,
            message="両プレイヤーのホールカードをそれぞれ2枚選択してください。",
        )

    board_count = sum(code is not None for code in community)
    if board_count not in (0, 3, 4, 5):
        return jsonify(
            ready=False,
            message="比較するには、コミュニティカードが0枚、3枚、4枚、または5枚である必要があります。",
        )

    p1 = [parse_card(code) for code in players[0]]
    p2 = [parse_card(code) for code in players[1]]
    board = [parse_card(code) for code in community if code is not None]

    try:
        rate1, rate2 = calculate_win_rates(p1, p2, board)
    except Exception:
        app.logger.exception("Unable to compare the current cards")
        return (
            jsonify(error="比較に失敗しました。役の判定処理を確認してください。"),
            500,
        )

    if not (0 <= rate1 <= 100 and 0 <= rate2 <= 100):
        return (
            jsonify(
                error="勝率計算関数は0～100の範囲のパーセンテージを返す必要があります。"
            ),
            500,
        )

    if rate1 > rate2:
        message = "現在の役：Player 1 がリードしています（実際の勝率ではありません）"
    elif rate2 > rate1:
        message = "現在の役：Player 2 がリードしています（実際の勝率ではありません）"
    else:
        message = "現在の役：引き分け（または勝率が同じ）"
    return jsonify(ready=True, player1=rate1, player2=rate2, message=message)


if __name__ == "__main__":
    app.run(debug=True)
