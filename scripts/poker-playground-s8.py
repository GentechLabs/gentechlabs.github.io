#!/usr/bin/env python3
"""DevFun Poker — script-based watchdog. Polls, acts, stays quiet when nothing happens."""

import json, os, sys, time, urllib.request, urllib.error, http.client, random

BASE_URL = "https://arena.dev.fun/api/arena"
COMPETITION_ID = "cmrkmc9hk6ikwdqn0xs2px2yu"
STATE_FILE = "/root/.arena-poker-state"
CRED_FILE = "/root/.arena-credentials"

# ─── Multi-poll config ───
POLL_INTERVAL = 8     # seconds between polls
MAX_POLLS = 7         # 7 polls × 8s = 56s active (only ~4s gap between cron ticks)
DEADLINE_BUFFER = 4   # seconds before deadline to fallback (30s clock → 26s safe)

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

# ─── preflop ranges ───
# Premium pairs (QQ+, KK, AA)
PREMIUM_PAIRS = {RANK_IDX[r] for r in "QKA"}
# Mid pairs (TT, JJ)
MID_PAIRS = {RANK_IDX[r] for r in "TJ"}
# Small pairs (22-99)
SMALL_PAIRS = {RANK_IDX[r] for r in "23456789"}
# Broadways (JT+)
BROADWAY_HIGH = {RANK_IDX[r] for r in "QKA"}

def parse_card(s):
    """'Ah' -> ('A','h')"""
    if len(s) == 2:
        return s[0], s[1]
    return s[0], s[1]  # Td, etc

def hand_score(hole, board):
    """Return a simple strength bucket: 0=nothing, 1=pair, 2=top pair+, 3=two pair+, 4=trips+"""
    ranks = [RANK_IDX[parse_card(c)[0]] for c in hole + board]
    pairs = set(r for r in ranks if ranks.count(r) >= 2)
    trips = set(r for r in ranks if ranks.count(r) >= 3)
    quads = set(r for r in ranks if ranks.count(r) >= 4)

    is_flush = False
    suits = [parse_card(c)[1] for c in hole + board]
    if any(suits.count(s) >= 5 for s in SUITS):
        is_flush = True

    # Straight detection
    sorted_ranks = sorted(set(ranks))
    is_straight = False
    if len(sorted_ranks) >= 5:
        for i in range(len(sorted_ranks) - 4):
            if sorted_ranks[i+4] - sorted_ranks[i] == 4:
                is_straight = True
        if 0 in sorted_ranks and 12 in sorted_ranks:  # wheel
            is_straight = True

    hole_high = max(RANK_IDX[parse_card(hole[0])[0]], RANK_IDX[parse_card(hole[1])[0]])

    if quads or (trips and is_flush and is_straight) or (is_flush and is_straight):
        return 4
    if trips or (len(pairs) >= 2 and is_flush):
        return 3
    if len(pairs) >= 2:
        return 2
    if pairs:
        pair_rank = list(pairs)[0]
        # Top pair = our hole card is the pair or the pair is J+
        if pair_rank >= 9 or pair_rank in [RANK_IDX[parse_card(hole[0])[0]],
                                            RANK_IDX[parse_card(hole[1])[0]]]:
            return 2
        return 1
    if is_flush or is_straight:
        return 1
    return 0

def preflop_decision(hole, position, pot, stack, deadline_ok):
    """Looser TAG — raise premiums, play more hands in position, defend blinds"""
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

    # ─── Early position (UTG/MP, seats 1-3) ───
    if position <= 2:
        # Raise 99+, AQ+, KQs
        if pair and high >= RANK_IDX['9']:
            return "raise", min(stack, max(pot * 3, 20))
        if high >= RANK_IDX['A'] and low >= RANK_IDX['Q']:
            return "raise", min(stack, max(pot * 3, 20))
        if suited and high == RANK_IDX['K'] and low >= RANK_IDX['Q']:
            return "raise", min(stack, max(pot * 3, 20))
        # Call small pairs (set mine) and suited aces
        if pair and stack >= 200:
            return "call", 0
        if suited and high == RANK_IDX['A']:
            return "call", 0
        if suited and high == RANK_IDX['K'] and low >= RANK_IDX['J']:
            return "call", 0
        if suited and high == RANK_IDX['Q'] and low >= RANK_IDX['J']:
            return "call", 0
        return "fold", 0

    # ─── Late position (CO/BTN, seats 4-6) — loose ───
    # Raise 99+, ATo+, KQo, all suited aces, suited broadways
    if pair:
        if high >= RANK_IDX['9']:
            return "raise", min(stack, max(pot * 3, 20))
        if high >= RANK_IDX['5']:
            return "call", 0  # set mine small pairs
    if high >= RANK_IDX['A'] and low >= RANK_IDX['T']:
        return "raise" if low >= RANK_IDX['Q'] else "call", min(stack, max(pot * 3, 20))
    if high >= RANK_IDX['K'] and low >= RANK_IDX['Q']:
        return "raise", min(stack, max(pot * 3, 20))
    if high >= RANK_IDX['K'] and low >= RANK_IDX['T']:
        return "call", 0
    if suited and high == RANK_IDX['A']:
        return "raise" if low >= RANK_IDX['7'] else "call", min(stack, max(pot * 3, 20))
    if suited and high >= RANK_IDX['K']:
        return "call", 0
    if suited and gap <= 2 and low >= RANK_IDX['4']:  # suited connectors 54s+
        return "call", 0
    if suited and gap <= 4 and high >= RANK_IDX['9']:  # suited gappers J9s+
        return "call", 0
    if high >= RANK_IDX['Q'] and low >= RANK_IDX['J']:
        return "call", 0  # QJo, JTo
    if high >= RANK_IDX['T'] and gap <= 2:
        return "call", 0  # broadways JT, QT, KT

    # ─── Blind defense (SB/BB, seats 7-8) — don't bleed chips ───
    if position >= 6:
        # Any ace, any king, any pair, any 2 suited, broadways
        if high == RANK_IDX['A']:
            return "call", 0
        if pair:
            return "call", 0
        if suited:
            return "call", 0
        if high == RANK_IDX['K']:
            return "call", 0
        if high >= RANK_IDX['Q'] and low >= RANK_IDX['9']:
            return "call", 0
        if high >= RANK_IDX['T'] and low >= RANK_IDX['8']:
            return "call", 0
        # Last-resort defense with any 2 overcards
        if high >= RANK_IDX['J'] and gap <= 2:
            return "call", 0
        return "fold", 0

    return "fold", 0

def postflop_decision(score, pot, stack, committed, board, hole, deadline_ok):
    """Exploit passive meta — heavy c-bets, double barrels, value thin"""
    if not deadline_ok:
        return "check" if committed == 0 else "call", 0

    # ─── Strong hands — go for max value ───
    if score >= 3:  # trips+
        return "raise", min(stack, int(pot * 1.0))  # pot-sized, field calls wide
    if score >= 2:  # two pair+
        return "raise", min(stack, max(int(pot * 0.75), 15))

    # ─── Top pair — value bet ───
    if score >= 1:
        if len(board) <= 3:
            return "raise", min(stack, max(int(pot * 0.6), 10))  # c-bet flop
        return "raise", min(stack, max(int(pot * 0.5), 10))  # value turn+

    # ─── Nothing (score == 0) ───
    # C-bet any flop we raised pre — field folds too much
    if committed > 0:  # we raised preflop
        if len(board) <= 3:
            return "raise", min(stack, max(int(pot * 0.5), 10))  # c-bet
        # Double barrel on scare turns
        if len(board) == 4:
            return "raise", min(stack, max(int(pot * 0.6), 12))  # second barrel
    # Give up on river with nothing
    return "check", 0

def main():
    start = time.time()
    state = load_state()

    # 1. Check pending actions
    pending = api("GET", f"/texas/pending-actions?competitionId={COMPETITION_ID}")
    tables = pending.get("tables", [])
    participant = pending.get("participant", {})

    # Update state from participant (API is source of truth)
    if participant:
        state["hands_played"] = participant.get("totalHands", state.get("hands_played", 0))
        state["hands_won"] = participant.get("handsWon", state.get("hands_won", 0))
        state["current_stack"] = participant.get("tableChips", state.get("current_stack", 1000))
        state["bankroll"] = participant.get("bankrollChips", state.get("bankroll", 0))
        state["chip_state"] = participant.get("chipState", state.get("chip_state", "available"))
        save_state(state)

    # 2. Handle tables needing action
    acted = False
    for table in tables:
        table_id = table.get("tableId")
        allowed_actions = table.get("allowedActions", {})
        self_seat = table.get("selfSeatNumber", 0)

        # Extract our seat info from seats[] array
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

        # Calculate position based on seat number and total players
        # selfSeatNumber is 1-indexed from the dealer button (dealer=1, SB typically 2, BB 3)
        total_seats = len(seats)
        if total_seats > 0:
            position = self_seat - 1  # 0-indexed position
            # Normalize: early = 0-1, middle = 2-3, late = 4+, blind defense = last 2
        else:
            position = 0

        # Handle both ms and sec timestamps
        now_ms = time.time() * 1000
        if deadline > 1e15:  # already in ms
            deadline_ok = (deadline > now_ms + DEADLINE_BUFFER * 1000)
        elif deadline > 1e9:  # seconds
            deadline_ok = (deadline > time.time() + DEADLINE_BUFFER)
        else:
            deadline_ok = True  # No deadline = assume we can act

        street = table.get("street", "Preflop").lower()

        # Decision
        if street == "preflop":
            action, amount = preflop_decision(hole, position, pot, stack, deadline_ok)
        else:
            score = hand_score(hole, board)
            action, amount = postflop_decision(score, pot, stack, committed, board, hole, deadline_ok)

        # After decision, submit action (amount handled per official SDK)
        if not deadline_ok:
            aa = allowed_actions.get("availableActions", [])
            if "check" in aa:
                action = "check"
                amount = 0
            elif "call" in aa:
                amount = allowed_actions.get("callChips", allowed_actions.get("callAmount", 0))
                action = "call"
            else:
                action = "fold"
                amount = 0

        available = allowed_actions.get("availableActions", [])
        if action not in available:
            action = available[0] if available else "fold"
        body = {"tableId": table_id, "action": action}
        if action == "raise":
            rr = allowed_actions.get("raiseRange", {})
            min_amt = rr.get("min", allowed_actions.get("minRaiseTo", 0))
            max_amt = rr.get("max", allowed_actions.get("maxCommit", stack))
            body["amount"] = max(min_amt, min(amount, max_amt))
        # Official SDK: omit amount for fold/check/call — server computes it
        # callChips exists as allowedActions.callChips if needed
        body["message"] = generate_message(action, hole, board, street, pot)

        result = api("POST", "/texas/action", body)
        acted = True

    # 3. If no tables, check if we need to re-join
    if not tables:
        lobby = api("GET", f"/texas/lobby?competitionId={COMPETITION_ID}")
        if isinstance(lobby, dict) and lobby.get("lobby") is None:
            # Not queued and not at a table — join
            chip_state = state.get("chip_state", "available")
            if chip_state == "available":
                result = api("POST", "/texas/join", {"competitionId": COMPETITION_ID})

    # 4. Report — silent unless something meaningful changed
    if acted:
        pass  # Handled; heartbeat cron summarizes


def generate_message(action, hole, board, street, pot):
    """Short chat message per poker skill rules"""
    msgs = {
        "fold": ["Nothing here.", "Range doesn't connect.", "Wrong spot.",
                  "Not the board for this hand.", "Disciplined fold."],
        "check": ["Keeping it small.", "See what develops.", "Checking through.",
                   "No reason to build this pot yet.", "Pot control."],
        "call": ["Getting odds to see.", "Fair price.", "Let's see a turn.",
                  "Priced in.", "Calling — that sizing's reasonable."],
        "raise": ["Sizing up for value.", "Time to build the pot.",
                   "That bet's too small.", "Protecting my hand.",
                   "Putting pressure on their weak range."],
    }
    import random
    return random.choice(msgs.get(action, ["Playing my hand."]))

if __name__ == "__main__":
    main()
