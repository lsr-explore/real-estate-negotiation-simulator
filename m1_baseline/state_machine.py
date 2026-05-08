"""
Finite State Machine for Negotiation
======================================
Fixes #3 (no state machine), #4 (no turn limits), #6 (no termination guarantee).

  naive_negotiation.py:  while True: ...           <- no guarantee it ever stops
  this file:             while not fsm.is_terminal(): ...  <- MUST stop

Terminal states have empty transition sets + turn_count is capped at max_turns.
Every path ends.

Run:   python m1_baseline/state_machine.py
Next:  adk web m3_adk_multiagents/negotiation_agents/  (ADK LoopAgent = FSM at agent scale)
"""

import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class NegotiationState(Enum):
    IDLE        = auto()
    NEGOTIATING = auto()
    AGREED      = auto()    # Terminal ✓
    FAILED      = auto()    # Terminal ✗


class FailureReason(Enum):
    MAX_TURNS_EXCEEDED  = auto()
    REJECTED_BY_BUYER   = auto()
    REJECTED_BY_SELLER  = auto()


@dataclass
class FSMContext:
    turn_count:        int                      = 0
    max_turns:         int                      = 5
    agreed_price:      Optional[float]          = None
    failure_reason:    Optional[FailureReason]   = None

class NegotiationFSM:

    # Empty set = terminal = no way out. That's the termination guarantee.
    TRANSITIONS: dict[NegotiationState, set[NegotiationState]] = {
        NegotiationState.IDLE:        {NegotiationState.NEGOTIATING, NegotiationState.FAILED},
        NegotiationState.NEGOTIATING: {NegotiationState.NEGOTIATING, NegotiationState.AGREED,
                                       NegotiationState.FAILED},
        NegotiationState.AGREED:      set(),   # TERMINAL
        NegotiationState.FAILED:      set(),   # TERMINAL
    }

    def __init__(self, max_turns: int = 5):
        # Exercise 1: Add deadline_seconds: float = 60.0 param
        self.state   = NegotiationState.IDLE
        self.context = FSMContext(max_turns=max_turns)

    @property
    def is_active(self) -> bool:
        return self.state == NegotiationState.NEGOTIATING

    def is_terminal(self) -> bool:
        return self.state in {NegotiationState.AGREED, NegotiationState.FAILED}

    def start(self) -> bool:
        """IDLE -> NEGOTIATING."""
        if self.state != NegotiationState.IDLE:
            return False
        self.state = NegotiationState.NEGOTIATING
        return True

    def process_turn(self) -> bool:
        """Record one turn. Returns False when max_turns hit -> FAILED."""
        if not self.is_active:
            return False

        self.context.turn_count += 1
        if self.context.turn_count >= self.context.max_turns:
            self.state = NegotiationState.FAILED
            self.context.failure_reason = FailureReason.MAX_TURNS_EXCEEDED
            return False
        return True

    def accept(self, price: float) -> bool:
        """NEGOTIATING -> AGREED."""
        if not self.is_active:
            return False
        self.state = NegotiationState.AGREED
        self.context.agreed_price = price
        return True

    def reject(self, by_buyer: bool = True) -> bool:
        """NEGOTIATING -> FAILED."""
        if not self.is_active:
            return False
        self.state = NegotiationState.FAILED
        self.context.failure_reason = (
            FailureReason.REJECTED_BY_BUYER if by_buyer
            else FailureReason.REJECTED_BY_SELLER
        )
        return True

    def check_invariants(self) -> bool:
        """Raises AssertionError if FSM is in an inconsistent state."""
        assert self.context.turn_count <= self.context.max_turns
        if self.state == NegotiationState.AGREED:
            assert self.context.agreed_price is not None
        if self.state == NegotiationState.FAILED:
            assert self.context.failure_reason is not None
        if self.is_terminal():
            assert len(self.TRANSITIONS[self.state]) == 0
        return True

    def __repr__(self) -> str:
        return (
            f"NegotiationFSM(state={self.state.name}, "
            f"turn={self.context.turn_count}/{self.context.max_turns})"
        )


def demo_fsm() -> None:
    print("=" * 65)
    print("NegotiationFSM — Termination Guarantee Demo")
    print("=" * 65)

    # Scenario 1: Deal reached
    print("\n--- Scenario 1: Deal Reached ---")
    fsm = NegotiationFSM(max_turns=5)
    print(f"Initial:        {fsm}")
    fsm.start()
    print(f"After start():  {fsm}")

    for round_num in range(1, 4):
        still_going = fsm.process_turn()
        print(f"Round {round_num}:        {fsm}  ->  continues={still_going}")

    fsm.accept(price=449_000)
    print(f"After accept(): {fsm}")
    print(f"is_terminal():  {fsm.is_terminal()}")
    print(f"agreed_price:   ${fsm.context.agreed_price:,.0f}")
    fsm.check_invariants()
    print("Invariants: PASS")

    # Scenario 2: Buyer walks away
    print("\n--- Scenario 2: Buyer Walks Away ---")
    fsm2 = NegotiationFSM(max_turns=5)
    fsm2.start()
    fsm2.process_turn()
    fsm2.process_turn()
    fsm2.reject(by_buyer=True)
    print(f"After reject(): {fsm2}")
    print(f"is_terminal():  {fsm2.is_terminal()}")
    print(f"failure_reason: {fsm2.context.failure_reason.name}")

    # Terminal states are sticky — accept after reject returns False
    result = fsm2.accept(price=440_000)
    print(f"accept() after reject: returned {result}  <- state is locked")
    fsm2.check_invariants()
    print("Invariants: PASS")

    # Scenario 3: Max turns exceeded
    print("\n--- Scenario 3: Max Turns Exceeded ---")
    fsm3 = NegotiationFSM(max_turns=5)
    fsm3.start()

    for i in range(1, 10):  # Try 9 rounds -- FSM stops at 5
        result = fsm3.process_turn()
        print(f"  Round {i}: returned={result}, state={fsm3.state.name}")
        if fsm3.is_terminal():
            print(f"  -> Terminated at round {i}")
            break

    print(f"\nFinal:          {fsm3}")
    print(f"failure_reason: {fsm3.context.failure_reason.name}")
    fsm3.check_invariants()
    print("Invariants: PASS")

    print("\n" + "=" * 65)
    print("KEY TAKEAWAY")
    print("=" * 65)
    print("""
TRANSITIONS[AGREED] = set()  <- empty = no way out
TRANSITIONS[FAILED] = set()  <- empty = no way out

Terminal state + turn cap = loop MUST end.

Next:  adk web m3_adk_multiagents/negotiation_agents/
    """)


if __name__ == "__main__":
    demo_fsm()
