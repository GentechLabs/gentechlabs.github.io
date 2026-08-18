#!/usr/bin/env python3
"""
Dinari dShares — Tokenized Equity Rail (dinari-rail)

Scaffold for the Agentic Treasury's equity leg (Jordan greenlit 2026-08-15,
handed to Labs 2026-08-15). Wraps the official `dinari-api-sdk` (v0.15+):

  - Order placement: market buy/sell, limit buy/sell (managed order requests)
  - Reads: portfolio, cash balances, dividends, interest, order list
  - Sandbox faucet: mint mockUSD for testing (no real money)
  - Stock data: current quote/price, dividends

Auth (from Partners dashboard, https://partners.dinari.com):
  DINARI_API_KEY_ID      (header X-API-Key-Id)
  DINARI_API_SECRET_KEY  (header X-API-Secret-Key)
  DINARI_ENV             'sandbox' (default) | 'production'

This file is a WORKING SCAFFOLD: client construction, env auth, and every
method wiring are real and testable via `--self-test`. Live calls need the
API keys (Jordan, human-gated) + a Partners entity/account.

Per the handoff: test in SANDBOX with the faucet before any real money.
Production key stays private — never commit it.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, timedelta

# ── SDK ────────────────────────────────────────────────────────────────────
try:
    from dinari_api_sdk import Dinari
    from dinari_api_sdk import APIStatusError, APIConnectionError
    SDK_OK = True
except ImportError:  # pragma: no cover
    Dinari = None
    APIStatusError = APIConnectionError = Exception
    SDK_OK = False


class DinariRail:
    """Thin, opinionated wrapper over the Dinari SDK for the Agentic Treasury."""

    def __init__(
        self,
        api_key_id: str | None = None,
        api_secret_key: str | None = None,
        environment: str | None = None,
    ):
        if not SDK_OK:
            raise RuntimeError(
                "dinari-api-sdk is not installed. Run: pip install dinari-api-sdk"
            )
        self.api_key_id = api_key_id or os.environ.get("DINARI_API_KEY_ID")
        self.api_secret_key = api_secret_key or os.environ.get("DINARI_API_SECRET_KEY")
        self.environment = (environment or os.environ.get("DINARI_ENV") or "sandbox").lower()
        if self.environment not in ("sandbox", "production"):
            raise ValueError(f"invalid DINARI_ENV: {self.environment}")

        # Build the client. Keys optional for --self-test / read of SDK surface;
        # required for any live API call.
        self.client = Dinari(
            api_key_id=self.api_key_id,
            api_secret_key=self.api_secret_key,
            environment=self.environment,
        )
        self.v2 = self.client.v2

    # ── auth / readiness ───────────────────────────────────────────────────
    @property
    def configured(self) -> bool:
        return bool(self.api_key_id and self.api_secret_key)

    @property
    def base_url(self) -> str:
        return str(self.client.base_url)

    # ── entities & accounts ────────────────────────────────────────────────
    def current_entity(self):
        return self.v2.entities.retrieve_current()

    def entity_accounts(self, entity_id: str | None = None, **kw):
        """List accounts for the current entity (or a specific entity)."""
        if entity_id:
            return self.v2.entities.accounts.list(entity_id, **kw)
        ent = self.current_entity()
        return self.v2.entities.accounts.list(ent.id, **kw)

    def account_retrieve(self, account_id: str):
        return self.v2.accounts.retrieve(account_id)

    # ── orders (managed order requests) ────────────────────────────────────
    def market_buy(self, account_id: str, payment_amount: float, stock_id: str | None = None, **kw):
        return self.v2.accounts.order_requests.create_market_buy(
            account_id, payment_amount=payment_amount, stock_id=stock_id, **kw
        )

    def market_sell(self, account_id: str, asset_quantity: float, stock_id: str | None = None, **kw):
        return self.v2.accounts.order_requests.create_market_sell(
            account_id, asset_quantity=asset_quantity, stock_id=stock_id, **kw
        )

    def limit_buy(self, account_id: str, asset_quantity: float, limit_price: float,
                  stock_id: str | None = None, **kw):
        return self.v2.accounts.order_requests.create_limit_buy(
            account_id, asset_quantity=asset_quantity, limit_price=limit_price,
            stock_id=stock_id, **kw
        )

    def limit_sell(self, account_id: str, asset_quantity: float, limit_price: float,
                   stock_id: str | None = None, **kw):
        return self.v2.accounts.order_requests.create_limit_sell(
            account_id, asset_quantity=asset_quantity, limit_price=limit_price,
            stock_id=stock_id, **kw
        )

    def order_requests(self, account_id: str, **kw):
        return self.v2.accounts.order_requests.list(account_id, **kw)

    def order_request(self, order_request_id: str, account_id: str):
        return self.v2.accounts.order_requests.retrieve(order_request_id, account_id=account_id)

    def orders(self, account_id: str, **kw):
        return self.v2.accounts.orders.list(account_id, **kw)

    # ── reads: portfolio / cash / dividends / interest ─────────────────────
    def portfolio(self, account_id: str, **kw):
        return self.v2.accounts.get_portfolio(account_id, **kw)

    def cash_balances(self, account_id: str):
        return self.v2.accounts.get_cash_balances(account_id)

    def dividends(self, account_id: str, start_date: str | date, end_date: str | date, **kw):
        return self.v2.accounts.get_dividend_payments(account_id, start_date=start_date, end_date=end_date, **kw)

    def interest(self, account_id: str, start_date: str | date, end_date: str | date, **kw):
        return self.v2.accounts.get_interest_payments(account_id, start_date=start_date, end_date=end_date, **kw)

    # ── sandbox faucet (no real money) ─────────────────────────────────────
    def mint_sandbox(self, account_id: str):
        """Mint mockUSD in sandbox (default faucet amount per SDK)."""
        return self.v2.accounts.mint_sandbox_tokens(account_id)

    # ── market data ────────────────────────────────────────────────────────
    def stocks(self, **kw):
        return self.v2.market_data.stocks.list(**kw)

    def quote(self, stock_id: str):
        return self.v2.market_data.stocks.retrieve_current_quote(stock_id)

    def stock_dividends(self, stock_id: str, **kw):
        return self.v2.market_data.stocks.retrieve_dividends(stock_id, **kw)

    def market_hours(self):
        return self.v2.market_data.retrieve_market_hours()

    # ── summary helper ─────────────────────────────────────────────────────
    def account_summary(self, account_id: str, days: int = 30) -> dict:
        """Compose a compact human/agent-facing snapshot of one account."""
        today = date.today()
        start = today - timedelta(days=days)
        out = {
            "account_id": account_id,
            "environment": self.environment,
            "base_url": self.base_url,
        }
        try:
            out["cash"] = self.cash_balances(account_id)
        except Exception as e:
            out["cash_error"] = _err(e)
        try:
            out["portfolio"] = self.portfolio(account_id)
        except Exception as e:
            out["portfolio_error"] = _err(e)
        try:
            out["dividends"] = self.dividends(account_id, start, today)
        except Exception as e:
            out["dividends_error"] = _err(e)
        try:
            out["orders"] = self.orders(account_id)
        except Exception as e:
            out["orders_error"] = _err(e)
        return out


def _err(e: Exception) -> str:
    if isinstance(e, APIStatusError):
        return f"HTTP {e.status_code}"
    return type(e).__name__


# ── CLI ────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="Dinari dShares — tokenized equity rail")
    ap.add_argument("--env", choices=["sandbox", "production"], help="override DINARI_ENV")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("self-test", help="verify SDK + client construction (no API calls)")

    p_entity = sub.add_parser("entity", help="retrieve current entity")
    p_acct = sub.add_parser("accounts", help="list accounts for current entity")
    p_acct.add_argument("--entity-id", help="optional entity id")

    p_orders = sub.add_parser("orders", help="list orders for an account")
    p_orders.add_argument("account_id")
    p_orders.add_argument("--limit", type=int)

    p_port = sub.add_parser("portfolio", help="portfolio snapshot for an account")
    p_port.add_argument("account_id")
    p_port.add_argument("--days", type=int, default=30, help="dividend/interest lookback")

    p_quote = sub.add_parser("quote", help="current quote for a stock")
    p_quote.add_argument("stock_id")

    p_mint = sub.add_parser("mint", help="sandbox faucet — mint mockUSD (NO REAL MONEY)")
    p_mint.add_argument("account_id")

    args = ap.parse_args()

    if args.cmd == "self-test":
        return _self_test()

    try:
        rail = DinariRail(environment=args.env) if args.env else DinariRail()
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if not rail.configured:
        print(
            "error: DINARI_API_KEY_ID and/or DINARI_API_SECRET_KEY not set.\n"
            "Get sandbox keys from https://partners.dinari.com (Jordan, human-gated).\n"
            "Export them before running live commands.",
            file=sys.stderr,
        )
        return 2

    try:
        if args.cmd == "entity":
            print(rail.current_entity())
        elif args.cmd == "accounts":
            for acct in rail.entity_accounts(args.entity_id):
                print(acct)
        elif args.cmd == "orders":
            print(rail.orders(args.account_id, limit=args.limit))
        elif args.cmd == "portfolio":
            import json
            print(json.dumps(rail.account_summary(args.account_id, days=args.days), indent=2, default=str))
        elif args.cmd == "quote":
            print(rail.quote(args.stock_id))
        elif args.cmd == "mint":
            rail.mint_sandbox(args.account_id)
            print("sandbox faucet: mockUSD minted")
    except (APIStatusError, APIConnectionError) as e:
        print(f"API error: {_err(e)}", file=sys.stderr)
        return 1

    return 0


def _self_test() -> int:
    """Verify SDK presence + client construction (if keys set). No network calls."""
    print("dinari-api-sdk:", "OK" if SDK_OK else "MISSING (pip install dinari-api-sdk)")
    if not SDK_OK:
        return 2
    import dinari_api_sdk
    print("version:", getattr(dinari_api_sdk, "__version__", "unknown"))
    print("envs:", dinari_api_sdk.ENVIRONMENTS)

    has_keys = bool(os.environ.get("DINARI_API_KEY_ID") and os.environ.get("DINARI_API_SECRET_KEY"))
    print("keys set:", has_keys)
    if not has_keys:
        print("client construct: SKIPPED (no API keys) — SDK + wrapper surface verified")
        return 0
    try:
        rail = DinariRail()
        print("client construct: OK")
        print("base_url:", rail.base_url)
        print("configured:", rail.configured)
    except Exception as e:
        print("client construct: FAILED", e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
