#!/usr/bin/env python3
"""DevFun Poker — Tournament S7 script. Multi-poll watchdog with 20s clock support."""
import json, os, sys, time, urllib.request, urllib.error, http.client, random

BASE_URL = "https://arena.dev.fun/api/arena"
COMPETITION_ID = "cmrkmbltp6juswa5d4re81nt2"  # Tournament S7
STATE_FILE = "/root/.arena-poker-state-tournament"
CRED_FILE = "/root/.arena-credentials"

# ─── Multi-poll config ───
POLL_INTERVAL = 8     # seconds between polls
MAX_POLLS = 7         # 7 polls × 8s = 56s active (only ~4s gap between cron ticks)
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

def generate_message(action, hole, board, street, pot):
    """Chat with GenTech attitude — confident, playful, reads between the lines"""
    import random
    fold_msgs = [
        "Not today, old friend.",
        "I respect that bet more than my hand.",
        "You win this one. I'll be back.",
        "Good fold? We'll never know.",
        "Saving my chips for a better story.",
        "That flop didn't like me and I didn't like it.",
        "Folding is also a strategy. Sometimes.",
        "Live to see another hand.",
        "You almost had me. Almost.",
        "This hand smells like a trap.",
    ]
    check_msgs = [
        "Free card? Don't mind if I do.",
        "Let's see what you've got.",
        "Checking with intent.",
        "Slow play is still play.",
        "No need to build this pot. Yet.",
        "I like my hand enough to check.",
        "Setting the trap. Bait's out.",
        "Patience, young grasshopper.",
    ]
    call_msgs = [
        "Alright, let's dance.",
        "I'm getting the right price for this show.",
        "Calling because I can.",
        "Odds say yes. Who am I to argue?",
        "Let's see a card. Or two.",
        "That bet's not scaring me.",
        "Alright, one more street.",
        "Priced in. Deal with it.",
    ]
    raise_msgs = [
        "Your bet is cute. Mine is cuter.",
        "Let's find out who's serious.",
        "Time to apply pressure.",
        "That's a small bet for a big dreamer.",
        "Raising for value. And ego.",
        "I know where I stand. Do you?",
        "Testing the waters with a cannonball.",
        "If you're bluffing, nice one. If not, oops.",
        "Let's put a number on it.",
        "This pot needs some personality.",
    ]
    action_map = {
        "fold": fold_msgs,
        "check": check_msgs,
        "call": call_msgs,
        "raise": raise_msgs,
    }
    return random.choice(action_map.get(action, ["Playing my hand."]))

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
                # Not queued — try to join
                result = api("POST", "/texas/join", {"competitionId": COMPETITION_ID})
                if isinstance(result, dict):
                    # Check if it's a 402 (needs payment)
                    if "paymentRequirements" in result:
                        # Skip silently — owner funds the wallet externally
                        pass
                    else:
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
                # Tournament S7 — rebuy costs MON, ask Jordan first
                bust_msg = (f"BUSTED [Tournament S7] — {state.get('bankroll', 0)} bankroll, "
                             f"{state.get('hands_played', 0)} hands played, "
                             f"{state.get('hands_won', 0)} won. "
                             f"Need MON rebuy to continue.")
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
