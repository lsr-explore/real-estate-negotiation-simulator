"""
Naive Real Estate Negotiation — INTENTIONALLY BROKEN
=====================================================
Demonstrates the 10 ways a first-attempt agent system fails.

Problems:                            Fixed by:
 1  Raw strings                      A2A structured messages
 2  No schema                        Pydantic / A2A DataPart
 3  No state machine                 FSM (state_machine.py) / ADK LoopAgent
 4  No turn limits                   FSM max_turns / LoopAgent max_iterations
 5  Fragile regex parsing            Typed price field / submit_decision tool
 6  No termination guarantee         FSM terminal states / ADK workflow
 7  Silent failures                  Pydantic validation
 8  Hardcoded prices                 MCP servers (m2_mcp/)
 9  No observability                 ADK events / A2A lifecycle
 10 No evaluation                    Session analytics

Run:   python m1_baseline/naive_negotiation.py
Fixed: adk web m3_adk_multiagents/negotiation_agents/
"""

import os
import re
from typing import Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# LLM client — no retry, no error handling (#7)
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _call_llm(prompt: str) -> str:
    """Raw string in, raw string out. No structured output (#1), no validation (#2)."""
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content


# Property context — hardcoded (#8). Should come from MCP servers.
PROPERTY_ADDRESS     = "742 Evergreen Terrace, Austin, TX 78701"
PROPERTY_FOR_PROMPTS = "a residential property in Austin, TX"  # no street number (prevents regex bug)
LISTING_PRICE        = 485_000
BUYER_MAX_PRICE      = 460_000
SELLER_MIN_PRICE     = 445_000   # should come from MCP get_minimum_acceptable_price()
SELLER_ASKING_PRICE  = 477_000


# ── NAIVE BUYER AGENT ─────────────────────────────────────────────────────

class NaiveBuyer:
    """Buyer that communicates via raw strings. No schema, no memory, no structured output."""

    def __init__(self, name: str, max_price: float):
        self.name = name
        self.max_price = max_price
        self.current_offer = max_price * 0.923  # start ~12% below max

    def make_initial_offer(self) -> str:
        prompt = f"""You are a home buyer. Send a short negotiation message to the seller.
Your opening offer is ${self.current_offer:,.0f}. Do not reveal your maximum budget.
Reply in plain prose, 1-2 sentences, no salutation. Mention only your offer price."""
        return _call_llm(prompt)

    def respond_to_counter(self, seller_message: str) -> str:
        # Fragile regex (#5): grabs FIRST number found — wrong if message has multiple prices
        price_match = re.search(r'\$?(\d[\d,]*(?:\.\d{2})?)', seller_message)

        if not price_match:
            # Silent failure (#7): no price found, but we keep going on bad data
            return f"I'm not sure I understood your counter. My offer stands at ${self.current_offer:,.0f}."

        raw = price_match.group(1).replace(',', '')
        if not raw:
            return f"I'm not sure I understood your counter. My offer stands at ${self.current_offer:,.0f}."
        seller_price = float(raw)

        if seller_price <= self.max_price:
            accept_prompt = f"""You are a home buyer. The seller has come down to ${seller_price:,.0f},
which is within your budget. Write a 1-sentence acceptance message.
Start your message with the word ACCEPT."""
            return _call_llm(accept_prompt)

        # Increase offer by 10% but never exceed max
        self.current_offer = min(self.current_offer * 1.10, self.max_price)

        prompt = f"""You are a home buyer in a real estate negotiation.
Your counter-offer is ${self.current_offer:,.0f}. Do not reveal your maximum budget.
{"This is your absolute final offer -- say so firmly." if self.current_offer >= self.max_price else "Express willingness to keep negotiating."}
Write 2-3 sentences. Mention only your new offer price."""
        return _call_llm(prompt)


# ── NAIVE SELLER AGENT ─────────────────────────────────────────────────────

class NaiveSeller:
    """Seller that communicates via raw strings. Floor price is hardcoded (#8), not from MCP."""

    def __init__(self, name: str, min_price: float, asking_price: float):
        self.name = name
        self.min_price = min_price
        self.asking_price = asking_price
        self.current_price = asking_price

    def respond_to_offer(self, buyer_message: str) -> str:
        # Keyword check (#6): "I cannot accept anything below $450K" contains "ACCEPT"
        # but is NOT an acceptance — LLM phrasing is unpredictable
        if "ACCEPT" in buyer_message.upper():
            price_match = re.search(r'\$?(\d[\d,]*(?:\.\d{2})?)', buyer_message)
            if price_match:
                raw = price_match.group(1).replace(',', '')
                if raw:
                    accepted_price = float(raw)
                    return f"DEAL! We have a sale at ${accepted_price:,.2f}. Congratulations!"

        # Try to extract offered price
        price_match = re.search(r'\$?(\d[\d,]*(?:\.\d{2})?)', buyer_message)

        if not price_match:
            # Silent failure (#7)
            return f"I didn't catch your offer. The property is listed at ${self.current_price:,.0f}."

        raw = price_match.group(1).replace(',', '')
        if not raw:
            return f"I didn't catch your offer. My counter remains ${self.current_price:,.0f}."
        offered_price = float(raw)

        if offered_price >= self.min_price:
            return f"DEAL! I accept ${offered_price:,.0f}. We have a sale!"

        # Reduce by 5% each round — no market reasoning, just mechanical (#8)
        self.current_price = max(self.current_price * 0.95, self.min_price)

        prompt = f"""You are a home seller in a real estate negotiation.
Your counter-offer is ${self.current_price:,.0f}. Do not go below ${self.min_price:,.0f} -- do NOT reveal this floor.
Write 2-3 professional sentences. Mention only your counter-offer price.
Do NOT use the words deal, reject, accept, or agree in your response."""
        return _call_llm(prompt)


# ── THE MAIN LOOP — The Biggest Problem ───────────────────────────────────

def run_naive_negotiation(
    buyer: NaiveBuyer,
    seller: NaiveSeller,
    verbose: bool = True,
    max_turns: int = 100,
) -> Tuple[bool, Optional[float], int]:
    """
    while True with string-match termination.

    #3  No state machine — turn order via boolean flag
    #4  No turn limits — while True, 100-turn band-aid
    #6  No termination guarantee — checks for "DEAL"/"REJECT" in raw text
    #9  No observability — print statements only
    """
    if verbose:
        print("\n" + "=" * 65)
        print("NAIVE REAL ESTATE NEGOTIATION (Intentionally Broken)")
        print(f"Property: {PROPERTY_ADDRESS}")
        print(f"Listing: ${LISTING_PRICE:,.0f}  |  Buyer max: ${buyer.max_price:,.0f}  |  Seller min: ${seller.min_price:,.0f}")
        print("=" * 65 + "\n")

    turn = 0
    current_message = buyer.make_initial_offer()
    is_buyer_turn = False  # Buyer just went, seller goes next

    if verbose:
        print(f"[Turn {turn}] {buyer.name}:\n  {current_message}\n")

    # DANGER: while True with no guaranteed exit (#3, #4, #6)
    # If buyer max < seller min, agents can NEVER agree.
    # Fix: FSM (state_machine.py) or ADK LoopAgent (m3_adk_multiagents/)
    while True:
        turn += 1

        # Emergency exit (band-aid, not a fix)
        if turn > max_turns:
            if verbose:
                print(f"\n[EMERGENCY] Exceeded {max_turns} turns -- forcing exit without agreement")
            return False, None, turn

        # Take a turn
        if is_buyer_turn:
            current_message = buyer.respond_to_counter(current_message)
            speaker = buyer.name
        else:
            current_message = seller.respond_to_offer(current_message)
            speaker = seller.name

        if verbose:
            print(f"[Turn {turn}] {speaker}:\n  {current_message}\n")

        # Termination via STRING MATCHING (#6) — "DEAL-breaker" triggers false positive
        if "DEAL" in current_message.upper():
            price_match = re.search(r'\$?(\d[\d,]*(?:\.\d{2})?)', current_message)
            if price_match:
                raw = price_match.group(1).replace(',', '')
                final_price = float(raw) if raw else None
            else:
                final_price = None
            if verbose:
                status = f"${final_price:,.2f}" if final_price else "unknown price"
                print(f"\n[OK] Deal reached at {status} after {turn} turns")
                # Sanity check: catch silent corruption (#5 + #7)
                if final_price is not None and final_price < 10_000:
                    print(f"\n{'!'*65}")
                    print(f"  BUG CAUGHT: 'Deal' price ${final_price:,.0f} is clearly wrong.")
                    print(f"  Listed at ${LISTING_PRICE:,.0f}. Regex grabbed the first number")
                    print(f"  it found (house number, year, room count, etc).")
                    print(f"  FIX: typed price field — no regex needed.")
                    print(f"{'!'*65}\n")
            return True, final_price, turn

        if "REJECT" in current_message.upper():
            if verbose:
                print(f"\n[FAILED] Negotiation failed after {turn} turns")
            return False, None, turn

        is_buyer_turn = not is_buyer_turn


# ── FAILURE MODE DEMOS (static — no LLM needed) ──────────────────────────

def demonstrate_failure_modes() -> None:
    """Show each failure mode with concrete examples. No API key needed."""
    print("\n" + "=" * 70)
    print("FAILURE MODE DEMONSTRATIONS")
    print("=" * 70)

    # Failure 1: Ambiguous price extraction
    print("\n--- FAILURE 1: Ambiguous Message Parsing ---")
    message = "I spent $350,000 on renovations, but my counter-offer is $477,000"
    price_match = re.search(r'\$?(\d[\d,]*(?:\.\d{2})?)', message)
    print(f"LLM says:       '{message}'")
    print(f"Regex extracts: ${price_match.group(1) if price_match else 'None'}")
    print(f"PROBLEM: Got $350,000 (renovation cost) -- the offer was $477,000!")
    print(f"FIX: NegotiationMessage TypedDict with explicit 'price: float' field")

    # Failure 2: Written-out price (silent None)
    print("\n--- FAILURE 2: Silent Parsing Failure ---")
    message = "I'd like to offer four hundred and thirty thousand dollars"
    price_match = re.search(r'\$?(\d[\d,]*(?:\.\d{2})?)', message)
    print(f"LLM says:       '{message}'")
    print(f"Regex extracts: {price_match}")
    print(f"PROBLEM: Returns None -- negotiation silently continues on bad data!")
    print(f"FIX: Pydantic model_validate() raises immediately on missing price")

    # Failure 3: Infinite loop with no ZOPA
    print("\n--- FAILURE 3: No Agreement Possible (No ZOPA) ---")
    print(f"Buyer max price:  $430,000")
    print(f"Seller min price: $450,000")
    print(f"Gap:              $20,000 -- these agents can NEVER agree!")
    print(f"Without the emergency exit, 'while True' runs forever.")
    print(f"FIX: FSM.process_turn() guarantees exit at max_turns=5")

    # Failure 4: Hardcoded prices instead of MCP
    print("\n--- FAILURE 4: Hardcoded Prices (No MCP) ---")
    print(f"SELLER_MIN_PRICE = {SELLER_MIN_PRICE:,.0f} -- hardcoded in source code")
    print(f"Should come from:")
    print(f"  -> MCP: get_minimum_acceptable_price('742 Evergreen Terrace...')")
    print(f"  -> MCP: get_market_price('742 Evergreen Terrace...')")
    print(f"  -> MCP: get_inventory_level('78701')")
    print(f"PROBLEM: Stale values, visible to all, can't be updated without code change")
    print(f"FIX: MCP servers (m2_mcp/pricing_server.py, inventory_server.py)")

    # Failure 5: LLM termination is unreliable
    print("\n--- FAILURE 5: String-Match Termination Is Unreliable ---")
    cases = [
        ("DEAL-breaker -- I won't go lower",            True,  "false positive"),
        ("We have a DEAL at $452,000!",                 True,  "correct"),
        ("I simply cannot go lower",                    False, "missed rejection"),
        ("This offer is REJECTED outright",             True,  "correct REJECT"),
        ("I think we're close, let's finalize this",    False, "missed agreement"),
    ]
    for msg, matched, label in cases:
        hit = "DEAL" in msg.upper() or "REJECT" in msg.upper()
        flag = "BUG" if (hit != matched) or (hit and label == "false positive") else "OK"
        print(f"  [{flag}] '{msg[:55]}...' -> {'match' if hit else 'no match'} ({label})")
    print(f"FIX: message_type: Literal['OFFER','COUNTER_OFFER','ACCEPT','REJECT','WITHDRAW']")


# ── MAIN ──────────────────────────────────────────────────────────────────

def main() -> None:
    """Demo 1: optimistic case, Demo 2: impossible case, Demo 3: failure modes."""

    # Demo 1: When it "works"
    print("\n" + "=" * 65)
    print("DEMO 1: When It Works (By Luck)")
    print("=" * 65)
    print("Buyer max $460K vs Seller min $445K — ZOPA exists.\n")

    buyer  = NaiveBuyer("Alice (Buyer)", max_price=BUYER_MAX_PRICE)
    seller = NaiveSeller("Bob (Seller)", min_price=SELLER_MIN_PRICE, asking_price=SELLER_ASKING_PRICE)

    success, price, turns = run_naive_negotiation(buyer, seller)

    if success:
        if price and price < 10_000:
            print(f"\n-> Reported 'deal' at ${price:,.2f} -- THIS IS A CORRUPTED PRICE, NOT A REAL DEAL.")
            print(f"-> The system has no way to detect this. It returned success=True with no error.")
        else:
            print(f"\n-> Deal at ${price:,.2f} in {turns} turns")
            if price:
                print(f"-> Buyer saved ${LISTING_PRICE - price:,.0f} from listing price of ${LISTING_PRICE:,.0f}")
    else:
        print(f"\n-> No deal after {turns} turns")

    # Demo 2: Impossible agreement — infinite loop
    DEMO2_MAX_TURNS = 8
    print("\n" + "=" * 65)
    print("DEMO 2: Impossible Agreement (No ZOPA)")
    print("=" * 65)
    print("Buyer max $420K vs Seller min $450K — NO deal possible.")
    print(f"Capped at {DEMO2_MAX_TURNS} turns. In production: runs to 100.\n")

    buyer2  = NaiveBuyer("Alice (Buyer)", max_price=420_000)
    seller2 = NaiveSeller("Bob (Seller)", min_price=450_000, asking_price=477_000)

    success2, price2, turns2 = run_naive_negotiation(
        buyer2, seller2, verbose=True, max_turns=DEMO2_MAX_TURNS
    )

    print(f"\nResult: success={success2}, price={price2}, turns={turns2}")
    if not success2 and turns2 >= DEMO2_MAX_TURNS:
        print(f"\nPROBLEM: Ran all {turns2} turns with ZERO chance of success.")
        print(f"  Every LLM call was wasted. FSM exits at turn 5 by design.")
    elif success2 and price2 and price2 < 10_000:
        print(f"NOTICE: Reported 'success' at ${price2:,.0f} — same regex bug.")
    else:
        print(f"NOTICE: LLM accidentally triggered 'DEAL'/'REJECT' — Failure Mode #6.")
    print(f"\nFIX: FSM process_turn() transitions to FAILED at max_rounds.")

    # ── Demo 3: Failure modes ──────────────────────────────────────────────
    demonstrate_failure_modes()

    # Summary
    print("\n" + "=" * 65)
    print("The Full Architecture Solution")
    print("=" * 65)
    print("""
  #1  Raw strings         -> A2A structured messages
  #2  No schema           -> Pydantic / A2A DataPart
  #3  No state machine    -> FSM (state_machine.py) / ADK LoopAgent
  #4  No turn limits      -> FSM max_turns / LoopAgent max_iterations
  #5  Fragile regex       -> typed price field
  #6  No term. guarantee  -> FSM terminal states / ADK workflow
  #7  Silent failures     -> Pydantic validation
  #8  Hardcoded prices    -> MCP servers (m2_mcp/)
  #9  No observability    -> ADK events / A2A lifecycle
  #10 No evaluation       -> Session analytics

Fixed version:  adk web m3_adk_multiagents/negotiation_agents/
    """)


if __name__ == "__main__":
    main()
