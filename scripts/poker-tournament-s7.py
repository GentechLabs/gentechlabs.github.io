#!/usr/bin/env python3
"""DevFun Poker — Tournament S7 script. Multi-poll watchdog with 20s clock support."""
import json, os, sys, time, urllib.request, urllib.error, http.client, random

BASE_URL = "https://arena.dev.fun/api/arena"
COMPETITION_ID = "cmrkmbltp6juswa5d4re81nt2"  # Tournament S7
STATE_FILE = "/root/.arena-poker-state-tournament"
CRED_FILE = "/root/.arena-credentials"

# ─── Multi-poll config ───
POLL_INTERVAL = 8     # seconds between polls
MAX_POLLS = 4         # 4 polls × 8s = 32s active (leaves plenty of buffer)
DEADLINE_BUFFER = 4   # seconds before deadline to fallback (20s clock → 16s safe)

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def api(method, path, body=None):
    creds = load_json(CRED_FILE)
    key = creds["apiKey"]
    url = f"{BASE_URL}{path}"
    headers = {"x-arena-api-key": key, "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        try:
            return json.loads(body_text)
        except:
            return {"error": body_text}

def load_state():
    try:
        return load_json(STATE_FILE)
    except:
        return {"hands_played": 0, "hands_won": 0, "current_stack": 1000, "bankroll": 1000,
                "chip_state": "available", "biggest_pot": 0, "table_id": None, "rank": None}

def save_state(s):
    save_json(STATE_FILE, s)

# ─── hand rank evaluator ───
RANKS = "23456789TJQKA"
SUITS = "hdcs"
RANK_IDX = {r: i for i, r in enumerate(RANKS)}

def parse_card(s):
    if len(s) == 2:
        return s[0], s[1]
    return s[0], s[1]

def hand_score(hole, board):
    ranks = [RANK_IDX[parse_card(c)[0]] for c in hole + board]
    pairs = set(r for r in ranks if ranks.count(r) >= 2)
    trips = set(r for r in ranks if ranks.count(r) >= 3)
    quads = set(r for r in ranks if ranks.count(r) >= 4)

    suits = [parse_card(c)[1] for c in hole + board]
    is_flush = any(suits.count(s) >= 5 for s in SUITS)

    sorted_ranks = sorted(set(ranks))
    is_straight = False
    if len(sorted_ranks) >= 5:
        for i in range(len(sorted_ranks) - 4):
            if sorted_ranks[i+4] - sorted_ranks[i] == 4:
                is_straight = True
        if 0 in sorted_ranks and 12 in sorted_ranks:
            is_straight = True

    if quads or (trips and is_flush and is_straight) or (is_flush and is_straight):
        return 4
    if trips or (len(pairs) >= 2 and is_flush):
        return 3
    if len(pairs) >= 2:
        return 2
    if pairs:
        return 2 if list(pairs)[0] >= RANK_IDX.get('J', 9) else 1
    if is_flush or is_straight:
        return 1
    return 0

def preflop_decision(hole, position, pot, stack, deadline_ok):
    """Solid TAG — tight in EP, wider in LP, blind defense"""
    if not hole or len(hole) < 2:
        return "fold", 0
    r0 = RANK_IDX.get(parse_card(hole[0])[0])
    r1 = RANK_IDX.get(parse_card(hole[1])[0])
    if r0 is None or r1 is None:
        return "fold", 0
    suited = parse_card(hole[0])[1] == parse_card(hole[1])[1]
    high = max(r0, r1)
    low = min(r0, r1)
    pair = r0 == r1
    gap = high - low

    # ─── Always raise premiums ───
    if pair and high >= RANK_IDX['Q']:
        return "raise", min(stack, max(pot * 3.5, 30))
    if high == RANK_IDX['A'] and low == RANK_IDX['K']:
        return "raise", min(stack, max(pot * 3.5, 30))

    # ─── Early position ───
    if position <= 2:
        if pair and high >= RANK_IDX['T']:
            return "raise", min(stack, max(pot * 3, 20))
        if high == RANK_IDX['A'] and low >= RANK_IDX['Q']:
            return "raise", min(stack, max(pot * 3, 20))
        if pair and stack >= 200:
            return "call", 0
        if suited and high == RANK_IDX['A']:
            return "call", 0
        return "fold", 0

    # ─── Late position ───
    if pair:
        return ("raise" if high >= RANK_IDX['T'] else "call"), 0
    if high == RANK_IDX['A'] and low >= RANK_IDX['5']:
        return "raise" if suited else "call", 0
    if suited and high == RANK_IDX['K']:
        return "call", 0
    if suited and gap <= 3:
        return "call", 0
    if gap <= 2 and high >= RANK_IDX['8']:
        return "call", 0

    # ─── Blind defense ───
    if position >= 6:
        if suited or pair or high >= RANK_IDX['9']:
            return "call", 0
    return "fold", 0

def postflop_decision(score, pot, stack, committed, board, hole, deadline_ok):
    if not deadline_ok:
        return "check" if committed == 0 else "call", 0
    if score >= 3:  # trips+
        return "raise", min(stack, max(int(pot * 0.8), 20))
    if score >= 2:  # two pair+
        return "raise", min(stack, max(int(pot * 0.65), 15))
    if score >= 1:  # pair
        if committed == 0 and len(board) <= 3:
            return "raise", min(stack, max(int(pot * 0.5), 10))
        return "call", 0
    # Nothing — c-bet if we raised pre and board is dry
    if committed > 0 and len(board) <= 3 and hole:
        r0 = RANK_IDX.get(parse_card(hole[0])[0], 0)
        r1 = RANK_IDX.get(parse_card(hole[1])[0], 0)
        if max(r0, r1) >= RANK_IDX['A']:
            return "raise", min(stack, max(int(pot * 0.5), 10))
    return "check", 0

def generate_message(action, hole, board, street, pot):
    msgs = {
        "fold": ["Nothing here.", "Range doesn't connect.", "Wrong spot.",
                  "Not the board for this hand.", "Disciplined fold.",
                  "Saving chips.", "This flop misses me."],
        "check": ["Keeping it small.", "See what develops.", "Checking through.",
                   "No reason to build this pot yet.", "Pot control.",
                   "Taking the free card."],
        "call": ["Getting odds to see.", "Fair price.", "Let's see a turn.",
                  "Priced in.", "Calling — that sizing's reasonable.",
                  "Pot odds are there."],
        "raise": ["Sizing up for value.", "Time to build the pot.",
                   "That bet's too small.", "Protecting my hand.",
                   "Putting pressure on their weak range.",
                   "Let's find out where we stand."],
    }
    return random.choice(msgs.get(action, ["Playing my hand."]))

def handle_table(table, state):
    """Process one table. Returns True if we acted."""
    table_id = table.get("tableId")
    allowed_actions = table.get("allowedActions", {})
    self_seat = table.get("selfSeatNumber", 0)
    seats = table.get("seats", [])

    our_seat = {}
    for s in seats:
        if s.get("seatNumber") == self_seat:
            our_seat = s
            break

    hole = our_seat.get("holeCards", [])
    stack = our_seat.get("stackChips", state.get("current_stack", 1000)) or 0
    committed = our_seat.get("payoutChips", 0) or 0
    board = table.get("boardCards", [])
    pot = table.get("potChips", 0) or 0
    current_bet = table.get("currentBet", 0) or 0
    deadline = table.get("actionDeadlineAt", 0)

    position = min(self_seat - 1, 7) if self_seat else 0

    # 20s clock — tighter buffer
    now_ms = time.time() * 1000
    if deadline > 1e15:
        deadline_ok = (deadline > now_ms + DEADLINE_BUFFER * 1000)
    elif deadline > 1e9:
        deadline_ok = (deadline > time.time() + DEADLINE_BUFFER)
    else:
        deadline_ok = True

    street = table.get("street", "Preflop").lower()

    # Decision
    if street == "preflop":
        action, amount = preflop_decision(hole, position, pot, stack, deadline_ok)
    else:
        score = hand_score(hole, board)
        action, amount = postflop_decision(score, pot, stack, committed, board, hole, deadline_ok)

    # Deadline safety — buckle up
    if not deadline_ok:
        aa = allowed_actions.get("availableActions", [])
        if "check" in aa:
            action, amount = "check", 0
        elif "call" in aa:
            action, amount = "call", allowed_actions.get("callChips",
                                    allowed_actions.get("callAmount", 0))
        else:
            action, amount = "fold", 0

    available = allowed_actions.get("availableActions", [])
    if action not in available:
        action = available[0] if available else "fold"

    body = {"tableId": table_id, "action": action}
    if action == "raise":
        rr = allowed_actions.get("raiseRange", {})
        min_amt = rr.get("min", allowed_actions.get("minRaiseTo", 0))
        max_amt = rr.get("max", allowed_actions.get("maxCommit", stack))
        body["amount"] = max(min_amt, min(amount, max_amt))
    body["message"] = generate_message(action, hole, board, street, pot)

    result = api("POST", "/texas/action", body)
    # Track biggest pot
    if isinstance(result, dict) and result.get("potChips", 0) > state.get("biggest_pot", 0):
        state["biggest_pot"] = result.get("potChips", 0)
    return True

def main():
    start = time.time()
    state = load_state()
    acted_this_run = False

    for poll_num in range(MAX_POLLS):
        elapsed = time.time() - start
        if elapsed > 55:  # Stay under 60s to avoid cron overlap
            break

        state["last_tick_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # 1. Poll pending actions
        pending = api("GET", f"/texas/pending-actions?competitionId={COMPETITION_ID}")
        tables = pending.get("tables", [])
        participant = pending.get("participant", {})

        # Update state from API
        if participant:
            state["hands_played"] = participant.get("totalHands", state.get("hands_played", 0))
            state["hands_won"] = participant.get("handsWon", state.get("hands_won", 0))
            state["current_stack"] = participant.get("tableChips", state.get("current_stack", 1000))
            state["bankroll"] = participant.get("bankrollChips", state.get("bankroll", 0))
            state["chip_state"] = participant.get("chipState", state.get("chip_state", "available"))
            save_state(state)

        # 2. Handle tables
        if tables:
            for table in tables:
                handle_table(table, state)
                acted_this_run = True
            save_state(state)
            # After acting, poll again quickly (opponent may act fast on 20s clock)
            if poll_num < MAX_POLLS - 1:
                time.sleep(3)
                continue

        # 3. If no tables, check if we need to join or are busted
        if not tables:
            lobby = api("GET", f"/texas/lobby?competitionId={COMPETITION_ID}")
            chip_state = state.get("chip_state", "available")

            if isinstance(lobby, dict) and lobby.get("lobby") is None:
                if chip_state == "available":
                    result = api("POST", "/texas/join", {"competitionId": COMPETITION_ID})
                    # Update state from join response
                    if isinstance(result, dict):
                        part = result.get("participant", {})
                        if part:
                            state.update({
                                "hands_played": part.get("totalHands", state.get("hands_played", 0)),
                                "hands_won": part.get("handsWon", state.get("hands_won", 0)),
                                "current_stack": part.get("tableChips", 0),
                                "bankroll": part.get("bankrollChips", 0),
                                "chip_state": part.get("chipState", "available"),
                            })
                            save_state(state)
                elif chip_state == "busted":
                    # Print exit signal for cron to surface to Jordan
                    bust_msg = (f"BUSTED [Tournament S7] — {state.get('bankroll', 0)} bankroll, "
                                 f"{state.get('hands_played', 0)} hands played, "
                                 f"{state.get('hands_won', 0)} won.")
                    print(bust_msg, flush=True)
                    # Don't rebuy automatically — Jordan decides
                    # Bail out — no more polls needed
                    save_state(state)
                    return

        # 4. Wait before next poll
        if poll_num < MAX_POLLS - 1:
            time.sleep(POLL_INTERVAL)

    save_state(state)

if __name__ == "__main__":
    main()
