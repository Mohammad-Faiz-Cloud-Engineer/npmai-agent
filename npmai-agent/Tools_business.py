"""
tools_business.py — Business Tools for NPM Agent
NPMAI ECOSYSTEM — Sonu Kumar
All tool classes for the Business vertical.
ToolResult and CredStore are imported from agent_core.
"""

import os
import sys
import json
import sqlite3
import subprocess
import tempfile
import shutil
import csv
import io
import math
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

def _ensure(pkg: str, imp: str = None):
    n = imp or pkg
    try:
        __import__(n)
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg, "-q"], check=False)

for _pkg, _imp in [
    ("stripe",                  "stripe"),
    ("razorpay",                "razorpay"),
    ("ShopifyAPI",              "shopify"),
    ("reportlab",               "reportlab"),
    ("Pillow",                  "PIL"),
    ("pypdf",                   "pypdf"),
    ("python-docx",             "docx"),
    ("pandas",                  "pandas"),
    ("forex-python",            "forex_python"),
    ("mailchimp-marketing",     "mailchimp_marketing"),
    ("google-analytics-data",   "google.analytics.data"),
    ("scipy",                   "scipy"),
    ("requests",                "requests"),
]:
    _ensure(_pkg, _imp)

from agent_core import ToolResult, CredStore


# ─────────────────────────────────────────────
# 1. StripeTool
# ─────────────────────────────────────────────

class StripeTool:
    name = "stripe"
    description = "Complete Stripe payment processing: customers, payments, subscriptions, invoices, coupons, payouts, balance"
    use = (
        """Name of Tool:- StripeTool

Purpose of Tool:- 
The StripeTool serves as a comprehensive programmatic wrapper around the official Stripe Payment API ecosystem. It abstracts complex transactional workflows into structured, atomic operations. The tool programmatically manages user-facing identity sets (customers), processes asynchronous checkout frameworks (payment intents, direct charges, captures, and refunds), scales recurring monetization configurations (products, multi-tier pricing models, and time-bound subscriptions), issues formal point-of-sale reporting templates (invoices, coupons, and hosted payment links), and audits operational business parameters (ledger balances, transactional history tracking, and manual or automated payout clearances).

Methods:-
- create_customer: Registers a unique consumer profile entry inside the Stripe database.
- get_customer: Retrieves structural profile objects matching specific customer identifiers.
- update_customer: Mutates variable properties associated with a registered user entity.
- list_customers: Generates paginated blocks of historical customer profile metadata records.
- delete_customer: Discards a distinct customer account data entity out of active database logs.
- create_payment_intent: Sets up a multi-stage transaction ledger object designed to safely authorize and track a currency trade event.
- confirm_payment: Authorizes and captures a staged billing transaction status.
- create_charge: Fires immediate direct single-pass payment transactions.
- capture_charge: Claims pre-authorized funds locked on a customer's payment instrument.
- refund_charge: Reverses individual transaction event flows by issuing a total or fractional currency payback.
- list_charges: Generates a complete chronological transactional history table.
- create_subscription: Links a specific customer to automatic billing cycles driven by chosen pricing components.
- cancel_subscription: Terminates an active billing contract either immediately or at the expiration of the current period window.
- update_subscription: Dynamically mutates pricing rulesets or product tiers for active user agreements.
- list_subscriptions: Filters and arrays historical membership structures by chosen status modes.
- create_product: Registers an item entry to create a baseline for future commerce interactions.
- create_price: Encapsulates localized cost metrics and structural intervals beneath a specific target product identification code.
- create_invoice: Spawns a custom invoice layout statement tracking line items assigned to a user account.
- finalize_invoice: Transitions a draft statement into an unalterable formal request for payment.
- pay_invoice: Attempts to reconcile an open invoice balance using on-file payment configurations.
- list_invoices: Fetches historical statement lists filtered by state profiles or identity constraints.
- send_invoice: Dispatches localized bill representations directly to a user's target destination address.
- create_coupon: Structures percent-based markdown discount macros to modify checkout price loops.
- apply_coupon: Assigns structural discount configurations to a target customer profile scope.
- create_payment_link: Compiles direct web URLs pointing to a fully hosted Checkout interface.
- list_payment_methods: Queries a user's profile to extract arrays of recorded financial token signatures.
- get_balance: Quantifies immediate liquid holdings alongside pending currency flows awaiting bank ledger settlement.
- list_transactions: Audits deep internal movement logs mapping fees, payouts, and adjustments across available ledger histories.
- create_payout: Triggers manual fund migrations transferring corporate liquid balances out to linked banking systems.

How to use Tool Methods:-

1. create_customer:
   - Purpose: Injects a new customer workspace entity inside the centralized financial cloud architecture.
   - Arguments:
     a) email: str - Primary messaging contact destination address identifying the user profile.
     b) name: str (default: "") - Legal personal representation name string matching the customer.
     c) phone: str (default: "") - Contact system string tracking telephone details.
     d) metadata: dict (default: None) - Structural key-value custom tagging parameters passed straight to account properties.
     e) cred_key: str (default: "stripe") - Configuration storage key pointer targeting secure operational secret keys.
   - Returns: ToolResult presenting unique identification tokens and copying baseline account metadata.
   - How to call: StripeTool.create_customer(email="teendev@example.com", name="Alex Dev", metadata={"tier": "premium"})

2. get_customer:
   - Purpose: Extracts complete structural objects defining a customer's specific records.
   - Arguments:
     a) customer_id: str - Explicit identifier code string identifying the target customer entry (e.g., `cus_...`).
     b) cred_key: str (default: "stripe") - Configuration key referencing validation secrets.
   - Returns: ToolResult holding dictionary property sets outlining matching user account states.
   - How to call: StripeTool.get_customer(customer_id="cus_H1k2J3l4")

3. update_customer:
   - Purpose: Updates a customer's registered meta properties or address logs.
   - Arguments:
     a) customer_id: str - target validation key referencing the chosen user account profile.
     b) data: dict - Map definitions highlighting exact properties destined for updates.
     c) cred_key: str (default: "stripe") - Encryption validation key pointer tracking secrets.
   - Returns: ToolResult indicating successful configuration updates.
   - How to call: StripeTool.update_customer(customer_id="cus_H1k2J3l4", data={"description": "Updated billing preferences"})

4. list_customers:
   - Purpose: Extracts historical lists mapping out accounts configured inside system boundaries.
   - Arguments:
     a) limit: int (default: 10) - Total record ceiling cap returned during paging steps.
     b) email: str (default: "") - Query pattern string to restrict results to individual matching user accounts.
     c) cred_key: str (default: "stripe") - Platform access credential pointer reference.
   - Returns: ToolResult displaying serialized arrays containing client identifiers, email lists, and name strings.
   - How to call: StripeTool.list_customers(limit=5, email="tester@domain.com")

5. delete_customer:
   - Purpose: Safely removes target consumers from active runtime directory structures.
   - Arguments:
     a) customer_id: str - Root identifier tag pointing to the victim database row entity.
     b) cred_key: str (default: "stripe") - Secret profile lookup indicator.
   - Returns: ToolResult confirming operational status updates.
   - How to call: StripeTool.delete_customer(customer_id="cus_H1k2J3l4")

6. create_payment_intent:
   - Purpose: Sets up the transaction framework necessary to safely execute and track a user transaction.
   - Arguments:
     a) amount: int - Transaction volume quantified completely in the chosen currency's smallest denominational fraction (e.g., **1000** for $10.00).
     b) currency: str (default: "usd") - Three-letter standard international ISO currency format token string.
     c) customer_id: str (default: "") - Optional customer identity string matching the buyer profile.
     d) metadata: dict (default: None) - Custom data structures tracking localized internal project flags.
     e) cred_key: str (default: "stripe") - Cryptographic runtime authorization identifier tracking secrets.
   - Returns: ToolResult framing unique authorization tokens (`pi_...`), state messages, and client authorization hashes.
   - How to call: StripeTool.create_payment_intent(amount=2500, currency="usd", customer_id="cus_H1k2J3l4")

7. confirm_payment:
   - Purpose: Completes a payment workflow loop after a user's authorization checks are validated.
   - Arguments:
     a) intent_id: str - Explicit transaction token identifier code requiring capture logic completion (`pi_...`).
     b) cred_key: str (default: "stripe") - Target authentication storage lookup coordinate.
   - Returns: ToolResult mapping validation results and reporting finalized payment statuses (e.g., `succeeded`).
   - How to call: StripeTool.confirm_payment(intent_id="pi_3Mas95Lk")

8. create_charge:
   - Purpose: Processes non-staged, single-pass charge tasks using straight token identifiers.
   - Arguments:
     a) amount: int - Value magnitude counted entirely inside lowest structural monetary subunits (e.g., cents).
     b) currency: str (default: "usd") - Standard tracking token characterizing system currencies.
     c) source: str (default: "") - Legacy target token identifier representing payment instruments (e.g., `tok_visa`).
     d) customer_id: str (default: "") - Unique database identifier referencing structural consumer entries.
     e) description: str (default: "") - Contextual ledger annotation detailing individual transactions.
     e) cred_key: str (default: "stripe") - Credentials validation store locator.
   - Returns: ToolResult holding authorization records and recording structural output logs.
   - How to call: StripeTool.create_charge(amount=1500, currency="usd", source="tok_visa", description="Single Item Purchase")

9. capture_charge:
   - Purpose: Collects pre-authorized fund holds that were previously locked to safeguard a future service fulfillment event.
   - Arguments:
     a) charge_id: str - Target tracking identification token mapping back to initialized charge records (`ch_...`).
     b) cred_key: str (default: "stripe") - Authorization profile coordinate.
   - Returns: ToolResult validating transaction execution status updates.
   - How to call: StripeTool.capture_charge(charge_id="ch_1Oq2W3e4")

10. refund_charge:
    - Purpose: Resolves disputes or buyer returns by sending capital straight back to source accounts.
    - Arguments:
      a) charge_id: str - Transaction identifier code linked to an accomplished sale transaction event.
      b) amount: int (default: 0) - Fractional subunit limit value constraint; leaving it at 0 triggers total absolute refunds.
      b) reason: str (default: "requested_by_customer") - Explanatory classification tag capturing transactional return metrics.
      c) cred_key: str (default: "stripe") - Runtime key credential store address mapping.
    - Returns: ToolResult tracking registration tracking metrics alongside operational balance returns statuses.
    - How to call: StripeTool.refund_charge(charge_id="ch_1Oq2W3e4", amount=500, reason="fraudulent")

11. list_charges:
    - Purpose: Aggregates historical checkout events into visible inspection list matrices.
    - Arguments:
      a) customer_id: str (default: "") - Restricts search scopes down to isolated singular buyer accounts.
      b) limit: int (default: 10) - Slices historical outputs down to designated total maximum item ceilings.
      c) cred_key: str (default: "stripe") - API validation authorization token locator address.
    - Returns: ToolResult housing object logs detailing total values, structural currencies, and state outcomes.
    - How to call: StripeTool.list_charges(customer_id="cus_H1k2J3l4", limit=20)

12. create_subscription:
    - Purpose: Generates a persistent contract tracking recurring membership payments.
    - Arguments:
      a) customer_id: str - Identification token mapping straight to targeted consumer rows.
      b) price_id: str - Structural cost reference token designating target subscription packages (`price_...`).
      c) trial_days: int (default: 0) - Life interval window quantified in whole days where fee collection is skipped.
      d) metadata: dict (default: None) - Structural property map defining customized processing metadata variables.
      e) cred_key: str (default: "stripe") - Active ecosystem secret profile selection key pointer.
    - Returns: ToolResult providing dynamic contract codes (`sub_...`) and monitoring activation behaviors.
    - How to call: StripeTool.create_subscription(customer_id="cus_H1k2J3l4", price_id="price_1Nx888", trial_days=14)

13. cancel_subscription:
    - Purpose: Deactivates persistent billing sequences to prevent unauthorized ledger updates.
    - Arguments:
      a) subscription_id: str - Core subscription row indicator code slated for destruction (`sub_...`).
      b) at_period_end: bool (default: True) - Defers formal execution termination actions until active cycles exhaust naturally.
      c) cred_key: str (default: "stripe") - System security platform authorization reference pointer.
    - Returns: ToolResult documenting cancellation behaviors and reflecting structural outcomes.
    - How to call: StripeTool.cancel_subscription(subscription_id="sub_9sA8d7F6", at_period_end=False)

14. update_subscription:
    - Purpose: Implements adjustments regarding billing items, product quantities, or structural tiers.
    - Arguments:
      a) subscription_id: str - Active target contract tracking asset code reference.
      b) price_id: str (default: "") - Alternative tier structure designation code shifting operational billing maps.
      c) quantity: int (default: 0) - Scale integer updating total purchased item units inside targeted agreements.
      d) cred_key: str (default: "stripe") - Access token secret authorization dictionary path identifier.
    - Returns: ToolResult displaying status verification statements.
    - How to call: StripeTool.update_subscription(subscription_id="sub_9sA8d7F6", quantity=5)

15. list_subscriptions:
    - Purpose: Filters and arrays persistent subscription models active on cloud ledgers.
    - Arguments:
      a) customer_id: str (default: "") - Direct consumer identification code constraint limits.
      b) status: str (default: "active") - State constraints filtering targeting (e.g., `trialing`, `past_due`).
      c) cred_key: str (default: "stripe") - Core framework security identification profile label.
    - Returns: ToolResult organizing arrays capturing contracts, status records, and customer owners.
    - How to call: StripeTool.list_subscriptions(status="trialing")

16. create_product:
    - Purpose: Maps real-world inventory offerings or application utility features straight onto global platforms.
    - Arguments:
      a) name: str - Display nomenclature text labeling the inventory asset.
      b) description: str (default: "") - Extended product context text profiling structural data parameters.
      c) metadata: dict (default: None) - Custom data attributes assigned to product records.
      d) cred_key: str (default: "stripe") - Platform authentication credential store locator.
    - Returns: ToolResult reflecting generation events and detailing custom product identifiers (`prod_...`).
    - How to call: StripeTool.create_product(name="SaaS Pro Plan", description="Unlimited api orchestration tools Access")

17. create_price:
    - Purpose: Binds numeric cost values and structural billing intervals to an inventory item.
    - Arguments:
      a) product_id: str - Target base commodity catalog identifier code link (`prod_...`).
      b) amount: int - Cost structure tracked in elemental currency fragments (e.g., **5000** means $50.00).
      c) currency: str (default: "usd") - Three-letter string formatting global currency types.
      d) interval: str (default: "") - Recurrence metric establishing charging intervals (e.g., `month`, `year`). Leave blank for single checkout events.
      e) cred_key: str (default: "stripe") - Private operational authentication profile selector.
    - Returns: ToolResult delivering specialized token pointers (`price_...`) back to configuration scripts.
    - How to call: StripeTool.create_price(product_id="prod_K8s9j2f", amount=1999, interval="month")

18. create_invoice:
    - Purpose: Sets up draft transaction request configurations bound to specific consumer ledger files.
    - Arguments:
      a) customer_id: str - Target client identification code reference.
      b) auto_advance: bool (default: True) - Enables automated payment processing transitions.
      c) cred_key: str (default: "stripe") - Key value index fetching authorization data mappings.
    - Returns: ToolResult housing invoice metadata fields (`in_...`) and state properties.
    - How to call: StripeTool.create_invoice(customer_id="cus_H1k2J3l4", auto_advance=True)

19. finalize_invoice:
    - Purpose: Locks pending invoice layouts to transform draft information frameworks into finalized debt representations.
    - Arguments:
      a) invoice_id: str - Target statement identifier string mapping elements (`in_...`).
      b) cred_key: str (default: "stripe") - Security cloud validation credential locator profile tag.
    - Returns: ToolResult reporting task completion metrics.
    - How to call: StripeTool.finalize_invoice(invoice_id="in_1Oq5X6y7")

20. pay_invoice:
    - Purpose: Automatically executes an active, un-reconciled final statement transaction against stored user balances.
    - Arguments:
      a) invoice_id: str - Target document validation tracker code reference string.
      b) cred_key: str (default: "stripe") - Platform infrastructure access credential pointer directory.
    - Returns: ToolResult reflecting successful account balancing operations.
    - How to call: StripeTool.pay_invoice(invoice_id="in_1Oq5X6y7")

21. list_invoices:
    - Purpose: Compiles a data table tracking past corporate billing documentation arrays.
    - Arguments:
      a) customer_id: str (default: "") - Restricts statement searches to individual targeted users.
      b) status: str (default: "") - Progress state markers narrowing search frameworks (e.g., `paid`, `open`, `uncollectible`).
      c) cred_key: str (default: "stripe") - Secret runtime credential locator flag setup parameters.
    - Returns: ToolResult returning object maps listing billing statements, financial totals, and transaction states.
    - How to call: StripeTool.list_invoices(status="open")

22. send_invoice:
    - Purpose: Distributes finalized payment documentation out through email networks to prompt manually triggered payment steps.
    - Arguments:
      a) invoice_id: str - Unique target invoice artifact identifier string.
      b) cred_key: str (default: "stripe") - Authorization workspace dictionary key lookup variable.
    - Returns: ToolResult confirming messaging delivery completions.
    - How to call: StripeTool.send_invoice(invoice_id="in_1Oq5X6y7")

23. create_coupon:
    - Purpose: Structures global markdown tokens designed to apply promotional adjustments during runtime price resolutions.
    - Arguments:
      a) percent_off: float - Relative markdown percentage constraint metrics quantified inside standard decimal notation values (e.g., **20.0** defines a 20% discount).
      b) duration: str (default: "once") - Lifespan interval persistence behavior patterns (e.g., `once`, `repeating`, `forever`).
      c) name: str (default: "") - Text description tracking marketing titles shown during client interactions.
      d) cred_key: str (default: "stripe") - Security credential lookup dictionary map address tracker.
    - Returns: ToolResult generating token shortcuts (`20_OFF`) or random system identification codes.
    - How to call: StripeTool.create_coupon(percent_off=15.5, duration="forever", name="Summer Launch Sale")

24. apply_coupon:
    - Purpose: Grants specific markdown discount permissions straight to consumer profile configurations.
    - Arguments:
      a) customer_id: str - Target profile identity code tracking consumers.
      b) coupon_id: str - Markdown identity reference token targeting discount profiles.
      c) cred_key: str (default: "stripe") - Operational framework secret encryption verification file reference.
    - Returns: ToolResult tracking registration modification achievements.
    - How to call: StripeTool.apply_coupon(customer_id="cus_H1k2J3l4", coupon_id="Summer Launch Sale")

25. create_payment_link:
    - Purpose: Automates payment loops by distilling custom prices into hosted standalone page link strings.
    - Arguments:
      a) price_id: str - The product configuration identifier code tracking cost components.
      b) quantity: int (default: 1) - Baseline scale integer specifying item volume constraints.
      c) cred_key: str (default: "stripe") - Secure private ecosystem lookup index address.
    - Returns: ToolResult outputting valid hosted webpage URLs (`https://buy.stripe.com/...`).
    - How to call: StripeTool.create_payment_link(price_id="price_1Nx888", quantity=1)

26. list_payment_methods:
    - Purpose: Audits card networks saved behind consumer portfolios.
    - Arguments:
      a) customer_id: str - The explicit client identifier code being checked.
      b) cred_key: str (default: "stripe") - Cryptographic master profile clearance selector key.
    - Returns: ToolResult outputting structured arrays summarizing card networks, termination expiration points, and trailing four digits.
    - How to call: StripeTool.list_payment_methods(customer_id="cus_H1k2J3l4")

27. get_balance:
    - Purpose: Reviews asset positions held across transaction networks.
    - Arguments:
      a) cred_key: str (default: "stripe") - Secret system credential platform dictionary indicator code.
    - Returns: ToolResult sorting cash metrics into immediately cleared holdings and rolling settlement balances.
    - How to call: StripeTool.get_balance()

28. list_transactions:
    - Purpose: Extracts a comprehensive log documenting structural ledger modifications.
    - Arguments:
      a) limit: int (default: 20) - Numeric collection bounds limiting history log elements.
      b) cred_key: str (default: "stripe") - Cloud environment profile validator address tracking keys.
    - Returns: ToolResult containing system event logs profiling transaction values, currency targets, types, and statuses.
    - How to call: StripeTool.list_transactions(limit=5)

29. create_payout:
    - Purpose: Forces settlement procedures migrating stored liquidity to connected commercial bank accounts.
    - Arguments:
      a) amount: int - Value magnitude counted entirely inside lowest structural monetary subunits (e.g., cents).
      b) currency: str (default: "usd") - Target physical fiat distribution setting specification language token string.
      c) cred_key: str (default: "stripe") - Core platform infrastructure configuration secret identification key index.
    - Returns: ToolResult tracking clearance numbers (`po_...`) and outputting transaction initiation logs.
    - How to call: StripeTool.create_payout(amount=100000, currency="usd")
    """)
    
    @staticmethod
    def _s(cred_key: str = "stripe"):
        import stripe as _stripe
        key = CredStore.load(cred_key).get("secret_key", "")
        if not key:
            raise ValueError("No Stripe secret key. CredStore.save('stripe', {'secret_key': 'sk_...'}).")
        _stripe.api_key = key
        return _stripe

    # ── Customers ──

    @staticmethod
    def create_customer(email: str, name: str = "", phone: str = "", metadata: Dict = None, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            cust = s.Customer.create(email=email, name=name, phone=phone, metadata=metadata or {})
            return ToolResult(True, f"✓ Customer created: {cust.id}", {"id": cust.id, "email": cust.email})
        except Exception as e:
            return ToolResult(False, f"✗ Create customer failed: {e}")

    @staticmethod
    def get_customer(customer_id: str, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            cust = s.Customer.retrieve(customer_id)
            return ToolResult(True, f"✓ Customer {customer_id}", dict(cust))
        except Exception as e:
            return ToolResult(False, f"✗ Get customer failed: {e}")

    @staticmethod
    def update_customer(customer_id: str, data: Dict, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            cust = s.Customer.modify(customer_id, **data)
            return ToolResult(True, f"✓ Customer {customer_id} updated")
        except Exception as e:
            return ToolResult(False, f"✗ Update customer failed: {e}")

    @staticmethod
    def list_customers(limit: int = 10, email: str = "", cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            kwargs = {"limit": limit}
            if email:
                kwargs["email"] = email
            custs = s.Customer.list(**kwargs)
            data = [{"id": c.id, "email": c.email, "name": c.name} for c in custs.auto_paging_iter()]
            return ToolResult(True, f"✓ {len(data)} customers", data)
        except Exception as e:
            return ToolResult(False, f"✗ List customers failed: {e}")

    @staticmethod
    def delete_customer(customer_id: str, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            s.Customer.delete(customer_id)
            return ToolResult(True, f"✓ Customer {customer_id} deleted")
        except Exception as e:
            return ToolResult(False, f"✗ Delete customer failed: {e}")

    # ── Payments ──

    @staticmethod
    def create_payment_intent(amount: int, currency: str = "usd", customer_id: str = "", metadata: Dict = None, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            kwargs = {"amount": amount, "currency": currency, "metadata": metadata or {}}
            if customer_id:
                kwargs["customer"] = customer_id
            pi = s.PaymentIntent.create(**kwargs)
            return ToolResult(True, f"✓ PaymentIntent {pi.id} created (client_secret available)", {"id": pi.id, "client_secret": pi.client_secret, "status": pi.status})
        except Exception as e:
            return ToolResult(False, f"✗ Create payment intent failed: {e}")

    @staticmethod
    def confirm_payment(intent_id: str, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            pi = s.PaymentIntent.confirm(intent_id)
            return ToolResult(True, f"✓ PaymentIntent {intent_id} confirmed — status: {pi.status}", {"status": pi.status})
        except Exception as e:
            return ToolResult(False, f"✗ Confirm payment failed: {e}")

    @staticmethod
    def create_charge(amount: int, currency: str = "usd", source: str = "", customer_id: str = "", description: str = "", cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            kwargs = {"amount": amount, "currency": currency, "description": description}
            if source:
                kwargs["source"] = source
            if customer_id:
                kwargs["customer"] = customer_id
            charge = s.Charge.create(**kwargs)
            return ToolResult(True, f"✓ Charge {charge.id}: {charge.status}", {"id": charge.id, "status": charge.status})
        except Exception as e:
            return ToolResult(False, f"✗ Create charge failed: {e}")

    @staticmethod
    def capture_charge(charge_id: str, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            charge = s.Charge.capture(charge_id)
            return ToolResult(True, f"✓ Charge {charge_id} captured")
        except Exception as e:
            return ToolResult(False, f"✗ Capture charge failed: {e}")

    @staticmethod
    def refund_charge(charge_id: str, amount: int = 0, reason: str = "requested_by_customer", cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            kwargs = {"charge": charge_id, "reason": reason}
            if amount:
                kwargs["amount"] = amount
            ref = s.Refund.create(**kwargs)
            return ToolResult(True, f"✓ Refund {ref.id} created — status: {ref.status}", {"id": ref.id, "status": ref.status})
        except Exception as e:
            return ToolResult(False, f"✗ Refund failed: {e}")

    @staticmethod
    def list_charges(customer_id: str = "", limit: int = 10, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            kwargs = {"limit": limit}
            if customer_id:
                kwargs["customer"] = customer_id
            charges = s.Charge.list(**kwargs)
            data = [{"id": c.id, "amount": c.amount, "currency": c.currency, "status": c.status} for c in charges.auto_paging_iter()]
            return ToolResult(True, f"✓ {len(data)} charges", data)
        except Exception as e:
            return ToolResult(False, f"✗ List charges failed: {e}")

    # ── Subscriptions ──

    @staticmethod
    def create_subscription(customer_id: str, price_id: str, trial_days: int = 0, metadata: Dict = None, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            kwargs = {"customer": customer_id, "items": [{"price": price_id}], "metadata": metadata or {}}
            if trial_days:
                kwargs["trial_period_days"] = trial_days
            sub = s.Subscription.create(**kwargs)
            return ToolResult(True, f"✓ Subscription {sub.id} created — status: {sub.status}", {"id": sub.id, "status": sub.status})
        except Exception as e:
            return ToolResult(False, f"✗ Create subscription failed: {e}")

    @staticmethod
    def cancel_subscription(subscription_id: str, at_period_end: bool = True, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            if at_period_end:
                sub = s.Subscription.modify(subscription_id, cancel_at_period_end=True)
            else:
                sub = s.Subscription.cancel(subscription_id)
            return ToolResult(True, f"✓ Subscription {subscription_id} cancelled — status: {sub.status}")
        except Exception as e:
            return ToolResult(False, f"✗ Cancel subscription failed: {e}")

    @staticmethod
    def update_subscription(subscription_id: str, price_id: str = "", quantity: int = 0, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            sub = s.Subscription.retrieve(subscription_id)
            item_id = sub["items"]["data"][0]["id"]
            update_data: Dict[str, Any] = {}
            if price_id:
                update_data["items"] = [{"id": item_id, "price": price_id}]
            if quantity:
                update_data.setdefault("items", [{"id": item_id}])
                update_data["items"][0]["quantity"] = quantity
            s.Subscription.modify(subscription_id, **update_data)
            return ToolResult(True, f"✓ Subscription {subscription_id} updated")
        except Exception as e:
            return ToolResult(False, f"✗ Update subscription failed: {e}")

    @staticmethod
    def list_subscriptions(customer_id: str = "", status: str = "active", cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            kwargs = {"status": status, "limit": 50}
            if customer_id:
                kwargs["customer"] = customer_id
            subs = s.Subscription.list(**kwargs)
            data = [{"id": sub.id, "status": sub.status, "customer": sub.customer} for sub in subs.auto_paging_iter()]
            return ToolResult(True, f"✓ {len(data)} subscriptions", data)
        except Exception as e:
            return ToolResult(False, f"✗ List subscriptions failed: {e}")

    # ── Products & Prices ──

    @staticmethod
    def create_product(name: str, description: str = "", metadata: Dict = None, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            prod = s.Product.create(name=name, description=description, metadata=metadata or {})
            return ToolResult(True, f"✓ Product {prod.id} created", {"id": prod.id, "name": prod.name})
        except Exception as e:
            return ToolResult(False, f"✗ Create product failed: {e}")

    @staticmethod
    def create_price(product_id: str, amount: int, currency: str = "usd", interval: str = "", cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            kwargs: Dict[str, Any] = {"product": product_id, "unit_amount": amount, "currency": currency}
            if interval:
                kwargs["recurring"] = {"interval": interval}
            price = s.Price.create(**kwargs)
            return ToolResult(True, f"✓ Price {price.id} created", {"id": price.id, "amount": price.unit_amount})
        except Exception as e:
            return ToolResult(False, f"✗ Create price failed: {e}")

    # ── Invoices ──

    @staticmethod
    def create_invoice(customer_id: str, auto_advance: bool = True, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            inv = s.Invoice.create(customer=customer_id, auto_advance=auto_advance)
            return ToolResult(True, f"✓ Invoice {inv.id} created", {"id": inv.id, "status": inv.status})
        except Exception as e:
            return ToolResult(False, f"✗ Create invoice failed: {e}")

    @staticmethod
    def finalize_invoice(invoice_id: str, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            inv = s.Invoice.finalize_invoice(invoice_id)
            return ToolResult(True, f"✓ Invoice {invoice_id} finalized")
        except Exception as e:
            return ToolResult(False, f"✗ Finalize invoice failed: {e}")

    @staticmethod
    def pay_invoice(invoice_id: str, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            inv = s.Invoice.pay(invoice_id)
            return ToolResult(True, f"✓ Invoice {invoice_id} paid — status: {inv.status}")
        except Exception as e:
            return ToolResult(False, f"✗ Pay invoice failed: {e}")

    @staticmethod
    def list_invoices(customer_id: str = "", status: str = "", cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            kwargs: Dict[str, Any] = {"limit": 50}
            if customer_id:
                kwargs["customer"] = customer_id
            if status:
                kwargs["status"] = status
            invs = s.Invoice.list(**kwargs)
            data = [{"id": i.id, "status": i.status, "amount_due": i.amount_due, "currency": i.currency} for i in invs.auto_paging_iter()]
            return ToolResult(True, f"✓ {len(data)} invoices", data)
        except Exception as e:
            return ToolResult(False, f"✗ List invoices failed: {e}")

    @staticmethod
    def send_invoice(invoice_id: str, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            s.Invoice.send_invoice(invoice_id)
            return ToolResult(True, f"✓ Invoice {invoice_id} sent to customer")
        except Exception as e:
            return ToolResult(False, f"✗ Send invoice failed: {e}")

    # ── Coupons ──

    @staticmethod
    def create_coupon(percent_off: float, duration: str = "once", name: str = "", cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            kwargs: Dict[str, Any] = {"percent_off": percent_off, "duration": duration}
            if name:
                kwargs["name"] = name
            coupon = s.Coupon.create(**kwargs)
            return ToolResult(True, f"✓ Coupon {coupon.id} created ({percent_off}% off)", {"id": coupon.id})
        except Exception as e:
            return ToolResult(False, f"✗ Create coupon failed: {e}")

    @staticmethod
    def apply_coupon(customer_id: str, coupon_id: str, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            s.Customer.modify(customer_id, coupon=coupon_id)
            return ToolResult(True, f"✓ Coupon {coupon_id} applied to {customer_id}")
        except Exception as e:
            return ToolResult(False, f"✗ Apply coupon failed: {e}")

    # ── Payment Links & Methods ──

    @staticmethod
    def create_payment_link(price_id: str, quantity: int = 1, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            link = s.PaymentLink.create(line_items=[{"price": price_id, "quantity": quantity}])
            return ToolResult(True, f"✓ Payment link created: {link.url}", {"id": link.id, "url": link.url})
        except Exception as e:
            return ToolResult(False, f"✗ Create payment link failed: {e}")

    @staticmethod
    def list_payment_methods(customer_id: str, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            methods = s.PaymentMethod.list(customer=customer_id, type="card")
            data = [{"id": m.id, "brand": m.card.brand, "last4": m.card.last4, "exp": f"{m.card.exp_month}/{m.card.exp_year}"} for m in methods.auto_paging_iter()]
            return ToolResult(True, f"✓ {len(data)} payment methods", data)
        except Exception as e:
            return ToolResult(False, f"✗ List payment methods failed: {e}")

    # ── Balance & Payouts ──

    @staticmethod
    def get_balance(cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            bal = s.Balance.retrieve()
            available = [{"amount": b.amount, "currency": b.currency} for b in bal.available]
            pending   = [{"amount": b.amount, "currency": b.currency} for b in bal.pending]
            return ToolResult(True, "✓ Balance retrieved", {"available": available, "pending": pending})
        except Exception as e:
            return ToolResult(False, f"✗ Get balance failed: {e}")

    @staticmethod
    def list_transactions(limit: int = 20, cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            txns = s.BalanceTransaction.list(limit=limit)
            data = [{"id": t.id, "amount": t.amount, "currency": t.currency, "type": t.type, "status": t.status} for t in txns.auto_paging_iter()]
            return ToolResult(True, f"✓ {len(data)} transactions", data)
        except Exception as e:
            return ToolResult(False, f"✗ List transactions failed: {e}")

    @staticmethod
    def create_payout(amount: int, currency: str = "usd", cred_key: str = "stripe") -> ToolResult:
        try:
            s = StripeTool._s(cred_key)
            payout = s.Payout.create(amount=amount, currency=currency)
            return ToolResult(True, f"✓ Payout {payout.id} created — status: {payout.status}", {"id": payout.id, "status": payout.status})
        except Exception as e:
            return ToolResult(False, f"✗ Create payout failed: {e}")


# ─────────────────────────────────────────────
# 2. RazorpayTool
# ─────────────────────────────────────────────

class RazorpayTool:
    name = "razorpay"
    description = "Razorpay Indian payment gateway: orders, payments, refunds, subscriptions, plans, payment links, QR codes, settlements"
    use = (
        """Name of Tool:- RazorpayTool

Purpose of Tool:- 
The RazorpayTool acts as a Python-based programmatic interface wrapper for the Razorpay payment gateway ecosystem, which is primarily optimized for Indian financial contexts. 
It encapsulates operations for managing multi-tiered transactional steps (orders, dynamic payment capturing, and targeted partial/full refunds), consumer registries (customers), and recurring billing architectures (period-based plans and customer-bound subscriptions). 
Additionally, the tool facilitates instant-collection touchpoints (payment links and static/dynamic UPI QR code strings) and financial reconciliations (monitoring settlement batches and their breakdown transactions) via isolated, authenticated client connections.

Methods:-
- create_order: Generates a verified transaction shell object to initialize secure payments.
- get_order: Retrieves specific data structures tied to an existing order identifier.
- list_orders: Fetches historical collection arrays containing created order objects.
- fetch_payment: Pulls comprehensive transaction profiles matching a distinct payment token.
- capture_payment: Explicitly claims authorized currency holds within designated compliance windows.
- refund_payment: Initiates a direct refund process instance explicitly scoped through payment endpoints.
- list_payments: Queries chronological tables tracking processed consumer checkouts.
- create_refund: Instantiates formal tracking items inside the core refund subsystem for auditing returns.
- create_customer: Registers an individual identifier profile containing contact details.
- get_customer: Extracts individual customer records matching a targeted identity parameter.
- create_subscription: Binds consumers to automatic billing cycles driven by structured catalog assets.
- create_plan: Formulates specific recurrence intervals and pricing metrics to serve as templates for memberships.
- list_plans: Displays available global membership product layouts.
- create_payment_link: Compiles localized, sharable checkout link references with optional client notifications.
- list_payment_links: Aggregates active tracking registers housing all created billing links.
- create_qr_code: Generates digital UPI image paths and target payment configuration matrices.
- get_settlements: Reviews operational cycles transferring aggregated gateway revenue into registered commercial bank accounts.
- get_settlement_transactions: Extracts itemized transaction files mapped under a chosen settlement batch.

How to use Tool Methods:-

1. create_order:
   - Purpose: Injects a necessary, pre-validated order shell object into the platform registry prior to starting checkout screens.
   - Arguments:
     a) amount: int - The absolute value magnitude counted entirely inside the smallest currency subunit (e.g., **50000** means 500.00 INR).
     b) currency: str (default: "INR") - Standard international ISO currency tracking flag token.
     c) receipt: str (default: "") - An optional localized invoice/receipt tracking identifier.
     d) notes: dict (default: None) - Key-value custom tracking dictionary metadata assigned to the order.
     e) cred_key: str (default: "razorpay") - Configuration pointer mapping targeted security API credential blocks.
   - Returns: ToolResult storing the populated platform order entity tracking fields (`order_...`).
   - How to call: RazorpayTool.create_order(amount=29900, currency="INR", receipt="inv_001", notes={"course_id": "math_101"})

2. get_order:
   - Purpose: Reviews real-time status arrays on a custom order lifecycle frame.
   - Arguments:
     a) order_id: str - target platform identifier reference code string (`order_...`).
     b) cred_key: str (default: "razorpay") - Authentication validation storage lookup index.
   - Returns: ToolResult holding structural keys mapping current payment progress data.
   - How to call: RazorpayTool.get_order(order_id="order_N7b2V8m3")

3. list_orders:
   - Purpose: Compiles historical arrays filtering project order records.
   - Arguments:
     a) count: int (default: 10) - Total upper ceiling limit of matching items returned in the batch.
     b) from_date: str (default: "") - Optional lower bounding date string structured under standard format layouts (`YYYY-MM-DD`).
     c) to_date: str (default: "") - Optional upper bounding threshold check date string (`YYYY-MM-DD`).
     d) cred_key: str (default: "razorpay") - Framework API credential locator index reference.
   - Returns: ToolResult capturing matching entity dictionaries.
   - How to call: RazorpayTool.list_orders(count=5, from_date="2026-01-01")

4. fetch_payment:
   - Purpose: Audits granular parameters characterizing an absolute individual transaction.
   - Arguments:
     a) payment_id: str - Explicit individual payment identity indicator tracking string (`pay_...`).
     b) cred_key: str (default: "razorpay") - Security lookup credential folder path index.
   - Returns: ToolResult documenting methods used, internal routing metadata, and payment states.
   - How to call: RazorpayTool.fetch_payment(payment_id="pay_K1l2M3n4")

5. capture_payment:
   - Purpose: Transitions a transaction state from `authorized` to `captured` to legally claim the funds.
   - Arguments:
     a) payment_id: str - Target execution key reference tracking the payment.
     b) amount: int - Explicit fund scale value calculated inside minimum subunit bounds.
     c) currency: str (default: "INR") - Localized fiat monetary tracking standard token.
     d) cred_key: str (default: "razorpay") - Platform key validation dictionary identifier locator.
   - Returns: ToolResult validating transaction finality logs.
   - How to call: RazorpayTool.capture_payment(payment_id="pay_K1l2M3n4", amount=15000)

6. refund_payment:
   - Purpose: Triggers standard transaction rollback operations straight through localized payment pipelines.
   - Arguments:
     a) payment_id: str - Core active payment transaction identifier reference string.
     b) amount: int (default: 0) - Amount to be rolled back; leaving it at 0 processes total absolute adjustments.
     c) notes: dict (default: None) - Explicit justification descriptors passed alongside records.
     d) cred_key: str (default: "razorpay") - Authentication lookup coordinate mapping parameters.
   - Returns: ToolResult recording refund structural states.
   - How to call: RazorpayTool.refund_payment(payment_id="pay_K1l2M3n4", amount=5000)

7. list_payments:
   - Purpose: Reviews overall chronological records mapping processed transaction objects.
   - Arguments:
     a) count: int (default: 10) - Numeric bounds specifying extraction constraints.
     b) from_date: str (default: "") - Starting time limit string token layouts (`YYYY-MM-DD`).
     c) to_date: str (default: "") - Closing checkpoint date window mapping (`YYYY-MM-DD`).
     d) cred_key: str (default: "razorpay") - Storage clearance token key variable.
   - Returns: ToolResult storing complete historical transaction objects.
   - How to call: RazorpayTool.list_payments(count=20, to_date="2026-06-15")

8. create_refund:
   - Purpose: Submits formal items straight to centralized gateway refund controllers to reverse balances.
   - Arguments:
     a) payment_id: str - Explicit transaction tracking identity token code pointer.
     b) amount: int - Segmental currency subunit value marking total payout targets.
     c) notes: dict (default: None) - Meta dictionary fields capturing accounting information details.
     d) cred_key: str (default: "razorpay") - Security identity clearance selector flag.
   - Returns: ToolResult presenting initialized refund system entries (`rfnd_...`).
   - How to call: RazorpayTool.create_refund(payment_id="pay_K1l2M3n4", amount=2500)

9. create_customer:
   - Purpose: Registers a consumer profile database instance tracking direct identities.
   - Arguments:
     a) name: str - Client identification text name string label.
     b) email: str - Messaging communication mailbox path context direction.
     c) contact: str - Telephone numerical string array identifier (e.g., `+919876543210`).
     d) fail_existing: bool (default: False) - Demands immediate failure feedback pipelines if match rules overlap on existing entries.
     e) cred_key: str (default: "razorpay") - Security credentials target map file location pointer.
   - Returns: ToolResult housing unique validation identifiers (`cust_...`).
   - How to call: RazorpayTool.create_customer(name="Rohan Sharma", email="rohan@domain.in", contact="+919999999999")

10. get_customer:
    - Purpose: Extracts complete context schemas tracing targeted consumer history information blocks.
    - Arguments:
      a) customer_id: str - Explicit consumer tracking register entry identification token string.
      b) cred_key: str (default: "razorpay") - Infrastructure credential system pointer label.
    - Returns: ToolResult packing profile maps.
    - How to call: RazorpayTool.get_customer(customer_id="cust_F8s7d6f5")

11. create_subscription:
    - Purpose: Establishes an automatic recurring payment contract associated with a chosen consumer card or account profile.
    - Arguments:
      a) plan_id: str - Structural billing template macro identity reference token string (`plan_...`).
      b) customer_id: str - Target profile user reference code.
      c) total_count: int - Whole maximum iteration ceiling numbers denoting contract lengths.
      d) quantity: int (default: 1) - Multiplier constant specifying relative item volume layers.
      e) cred_key: str (default: "razorpay") - Active target environment private storage lookups indicator.
    - Returns: ToolResult returning subscription asset configurations (`sub_...`).
    - How to call: RazorpayTool.create_subscription(plan_id="plan_P9o8i7u6", customer_id="cust_F8s7d6f5", total_count=12)

12. create_plan:
    - Purpose: Formulates baseline definitions governing interval tracking and fee rulesets for commercial packages.
    - Arguments:
      a) period: str - Timing pacing evaluation frequency labels (e.g., `daily`, `weekly`, `monthly`, `yearly`).
      b) interval: int - Step constant defining step frequency values based on chosen periods (e.g., period="monthly", interval=3 means quarterly cycles).
      c) item_name: str - Baseline visual name indexing the specific catalog entry.
      d) amount: int - Base value quantified using fractional minimum units.
      e) currency: str (default: "INR") - Standardization symbol specifying currency tracking indices.
      f) cred_key: str (default: "razorpay") - Encryption profile access control array pointer lookup values.
    - Returns: ToolResult presenting valid template code identifiers (`plan_...`).
    - How to call: RazorpayTool.create_plan(period="monthly", interval=1, item_name="SaaS Premium Access", amount=99900)

13. list_plans:
    - Purpose: Extracts active recurring membership layout frameworks built across workspace targets.
    - Arguments:
      a) cred_key: str (default: "razorpay") - API validation permission indicator flag settings.
    - Returns: ToolResult holding tracking items matching existing catalog setups.
    - How to call: RazorpayTool.list_plans()

14. create_payment_link:
    - Purpose: Initalizes standalone checkout interfaces, mapping specific transaction profiles to direct public URL targets.
    - Arguments:
      a) amount: int - Cost parameters captured inside basic currency subunits.
      b) currency: str (default: "INR") - Standard formatting token variable.
      c) description: str (default: "") - Item display summaries shown on client screens.
      d) customer: dict (default: None) - Embedded map strings capturing buyer profile info.
      e) notify: dict (default: None) - Notification directives handling distribution steps (e.g., `{"sms": True, "email": True}`).
      f) cred_key: str (default: "razorpay") - Cloud configuration key indexing private secret validation flags.
    - Returns: ToolResult providing dynamic redirect URL endpoints (`https://rzp.io/i/...`).
    - How to call: RazorpayTool.create_payment_link(amount=150000, description="Consulting Retainer Fee", notify={"email": True})

15. list_payment_links:
    - Purpose: Gathers past billing links organized in an open data register format.
    - Arguments:
      a) cred_key: str (default: "razorpay") - Cryptographic secure master authorization file key pointer.
    - Returns: ToolResult displaying generated tracking components.
    - How to call: RazorpayTool.list_payment_links()

16. create_qr_code:
    - Purpose: Renders localized UPI-compliant transaction models into public machine-readable structures.
    - Arguments:
      a) type: str (default: "upi_qr") - Configuration standard selecting physical scanning types.
      b) name: str (default: "") - Operational business name identification label.
      c) usage: str (default: "single_use") - Lifecycle tracking rules constraints (e.g., `single_use`, `multiple_use`).
      b) fixed_amount: bool (default: True) - Restricts scanning actions by hardcoding explicit fee expectations.
      c) amount: int (default: 0) - Target fee parameter required when fixed amounts are requested.
      d) description: str (default: "") - Annotation text assigned behind the dynamic item asset profile.
      e) cred_key: str (default: "razorpay") - Secret operational runtime authorization environment tracker.
    - Returns: ToolResult delivering complete context configurations tracking image URLs.
    - How to call: RazorpayTool.create_qr_code(name="Store Counter QR", fixed_amount=True, amount=25000, description="Invoice #104")

17. get_settlements:
    - Purpose: Audits corporate clearing operations moving consolidated assets out to corporate banking locations.
    - Arguments:
      a) cred_key: str (default: "razorpay") - Target platform secret identification validation storage coordinate lookup index.
    - Returns: ToolResult listing settlement timestamps, total volumes, unique transfer tracking keys, and batch states.
    - How to call: RazorpayTool.get_settlements()

18. get_settlement_transactions:
    - Purpose: Breaks down an isolated bank clearance event into its base ledger transactions for precise reconciliation.
    - Arguments:
      a) settlement_id: str - Explicit clear operation batch reference identifier code string (`setl_...`).
      b) cred_key: str (default: "razorpay") - Platform key credential index reference mapping.
    - Returns: ToolResult displaying arrays mapping original capture entries, dynamic system cuts, taxes, and net totals.
    - How to call: RazorpayTool.get_settlement_transactions(settlement_id="setl_X1y2Z3w4")
    """)
    
    @staticmethod
    def _rz(cred_key: str = "razorpay"):
        import razorpay
        c = CredStore.load(cred_key)
        key_id  = c.get("key_id", "")
        key_secret = c.get("key_secret", "")
        if not key_id or not key_secret:
            raise ValueError("No Razorpay credentials. CredStore.save('razorpay', {'key_id': '...', 'key_secret': '...'}).")
        return razorpay.Client(auth=(key_id, key_secret))

    @staticmethod
    def create_order(amount: int, currency: str = "INR", receipt: str = "", notes: Dict = None, cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            data = {"amount": amount, "currency": currency, "receipt": receipt or f"rcpt_{datetime.now().strftime('%Y%m%d%H%M%S')}", "notes": notes or {}}
            order = rz.order.create(data=data)
            return ToolResult(True, f"✓ Order {order['id']} created", order)
        except Exception as e:
            return ToolResult(False, f"✗ Create order failed: {e}")

    @staticmethod
    def get_order(order_id: str, cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            order = rz.order.fetch(order_id)
            return ToolResult(True, f"✓ Order {order_id}", order)
        except Exception as e:
            return ToolResult(False, f"✗ Get order failed: {e}")

    @staticmethod
    def list_orders(count: int = 10, from_date: str = "", to_date: str = "", cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            params: Dict[str, Any] = {"count": count}
            if from_date:
                params["from"] = int(datetime.strptime(from_date, "%Y-%m-%d").timestamp())
            if to_date:
                params["to"] = int(datetime.strptime(to_date, "%Y-%m-%d").timestamp())
            orders = rz.order.all(params)
            return ToolResult(True, f"✓ {len(orders.get('items', []))} orders", orders)
        except Exception as e:
            return ToolResult(False, f"✗ List orders failed: {e}")

    @staticmethod
    def fetch_payment(payment_id: str, cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            payment = rz.payment.fetch(payment_id)
            return ToolResult(True, f"✓ Payment {payment_id}", payment)
        except Exception as e:
            return ToolResult(False, f"✗ Fetch payment failed: {e}")

    @staticmethod
    def capture_payment(payment_id: str, amount: int, currency: str = "INR", cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            payment = rz.payment.capture(payment_id, amount, {"currency": currency})
            return ToolResult(True, f"✓ Payment {payment_id} captured", payment)
        except Exception as e:
            return ToolResult(False, f"✗ Capture payment failed: {e}")

    @staticmethod
    def refund_payment(payment_id: str, amount: int = 0, notes: Dict = None, cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            data: Dict[str, Any] = {"notes": notes or {}}
            if amount:
                data["amount"] = amount
            refund = rz.payment.refund(payment_id, amount or 0, data)
            return ToolResult(True, f"✓ Refund {refund['id']} created", refund)
        except Exception as e:
            return ToolResult(False, f"✗ Refund payment failed: {e}")

    @staticmethod
    def list_payments(count: int = 10, from_date: str = "", to_date: str = "", cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            params: Dict[str, Any] = {"count": count}
            if from_date:
                params["from"] = int(datetime.strptime(from_date, "%Y-%m-%d").timestamp())
            if to_date:
                params["to"] = int(datetime.strptime(to_date, "%Y-%m-%d").timestamp())
            payments = rz.payment.all(params)
            return ToolResult(True, f"✓ {len(payments.get('items', []))} payments", payments)
        except Exception as e:
            return ToolResult(False, f"✗ List payments failed: {e}")

    @staticmethod
    def create_refund(payment_id: str, amount: int, notes: Dict = None, cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            refund = rz.refund.create({"payment_id": payment_id, "amount": amount, "notes": notes or {}})
            return ToolResult(True, f"✓ Refund {refund['id']} created", refund)
        except Exception as e:
            return ToolResult(False, f"✗ Create refund failed: {e}")

    @staticmethod
    def create_customer(name: str, email: str, contact: str, fail_existing: bool = False, cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            data = {"name": name, "email": email, "contact": contact, "fail_existing": 1 if fail_existing else 0}
            cust = rz.customer.create(data)
            return ToolResult(True, f"✓ Customer {cust['id']} created", cust)
        except Exception as e:
            return ToolResult(False, f"✗ Create customer failed: {e}")

    @staticmethod
    def get_customer(customer_id: str, cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            cust = rz.customer.fetch(customer_id)
            return ToolResult(True, f"✓ Customer {customer_id}", cust)
        except Exception as e:
            return ToolResult(False, f"✗ Get customer failed: {e}")

    @staticmethod
    def create_subscription(plan_id: str, customer_id: str, total_count: int, quantity: int = 1, cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            data = {"plan_id": plan_id, "customer_id": customer_id, "total_count": total_count, "quantity": quantity}
            sub = rz.subscription.create(data)
            return ToolResult(True, f"✓ Subscription {sub['id']} created", sub)
        except Exception as e:
            return ToolResult(False, f"✗ Create subscription failed: {e}")

    @staticmethod
    def create_plan(period: str, interval: int, item_name: str, amount: int, currency: str = "INR", cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            data = {"period": period, "interval": interval, "item": {"name": item_name, "amount": amount, "currency": currency}}
            plan = rz.plan.create(data)
            return ToolResult(True, f"✓ Plan {plan['id']} created", plan)
        except Exception as e:
            return ToolResult(False, f"✗ Create plan failed: {e}")

    @staticmethod
    def list_plans(cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            plans = rz.plan.all()
            return ToolResult(True, f"✓ Plans", plans)
        except Exception as e:
            return ToolResult(False, f"✗ List plans failed: {e}")

    @staticmethod
    def create_payment_link(amount: int, currency: str = "INR", description: str = "", customer: Dict = None, notify: Dict = None, cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            data: Dict[str, Any] = {"amount": amount, "currency": currency, "description": description}
            if customer:
                data["customer"] = customer
            if notify:
                data["notify"] = notify
            link = rz.payment_link.create(data)
            return ToolResult(True, f"✓ Payment link: {link.get('short_url', link.get('id'))}", link)
        except Exception as e:
            return ToolResult(False, f"✗ Create payment link failed: {e}")

    @staticmethod
    def list_payment_links(cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            links = rz.payment_link.all()
            return ToolResult(True, "✓ Payment links", links)
        except Exception as e:
            return ToolResult(False, f"✗ List payment links failed: {e}")

    @staticmethod
    def create_qr_code(type: str = "upi_qr", name: str = "", usage: str = "single_use", fixed_amount: bool = True, amount: int = 0, description: str = "", cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            data: Dict[str, Any] = {"type": type, "name": name, "usage": usage, "fixed_amount": fixed_amount, "description": description}
            if fixed_amount and amount:
                data["payment_amount"] = amount
            qr = rz.qr_code.create(data)
            return ToolResult(True, f"✓ QR code {qr['id']} created — image_url: {qr.get('image_url', 'N/A')}", qr)
        except Exception as e:
            return ToolResult(False, f"✗ Create QR code failed: {e}")

    @staticmethod
    def get_settlements(cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            settlements = rz.settlement.all()
            return ToolResult(True, "✓ Settlements", settlements)
        except Exception as e:
            return ToolResult(False, f"✗ Get settlements failed: {e}")

    @staticmethod
    def get_settlement_transactions(settlement_id: str, cred_key: str = "razorpay") -> ToolResult:
        try:
            rz = RazorpayTool._rz(cred_key)
            txns = rz.settlement.transactions(settlement_id)
            return ToolResult(True, f"✓ Transactions for settlement {settlement_id}", txns)
        except Exception as e:
            return ToolResult(False, f"✗ Get settlement transactions failed: {e}")


# ─────────────────────────────────────────────
# 3. ShopifyTool
# ─────────────────────────────────────────────

class ShopifyTool:
    name = "shopify"
    description = "Complete Shopify store management: products, variants, orders, fulfillment, customers, inventory, collections, discounts, analytics"
    use = (
        """Name of Tool:- ShopifyTool

Purpose of Tool:- 
The ShopifyTool provides an absolute programmatic wrapper that hooks directly into the official Shopify REST Admin API. It handles full-scale cloud retail operations by condensing administrative shop actions into clean, isolated python methods. The tool manages localized inventory assets (products, product variants, and smart/custom product collections), processes backend fulfillment loops (order retrievals, customer-prompted order cancellations, and shipping courier tracking updates), logs customer profile metrics (customer lists, specialized detail search strings, and client-tied sales history data), adjusts multi-location stock levels, injects seasonal marketing parameters (dynamic price discount rules), and generates critical financial health reporting frameworks (aggregating multi-day store analytics covering order volume trends, net revenue, and average cart metrics).

Methods:-
- list_products: Fetches historical catalogs filtered by lifecycle states or distribution vendors.
- get_product: Extracts deep object definitions modeling an individual inventory product instance.
- create_product: Builds and registers a new inventory item array containing pricing tiers and item variants.
- update_product: Modifies target asset attributes directly in the cloud database.
- delete_product: Completely discards individual target products out of the database workspace logs.
- list_variants: Exposes item variant trees attached to baseline commodity structures.
- update_variant: Overwrites prices, physical weight constraints, and baseline quantities on unique variants.
- list_orders: Aggregates global store checkouts sorted by operational or settlement states.
- get_order: Returns full payload parameters characterising a chosen invoice order asset.
- update_order: Alters live transaction schema metadata entries matching target transaction profiles.
- cancel_order: Halts active processing workflows, safely handling target stock counts based on criteria rulesets.
- fulfill_order: Finalizes transactional agreements by assigning fulfillment location keys and shipping tracking identifiers.
- list_customers: Generates paginated client contact logs tracked across the store ecosystem.
- get_customer: Queries structural profile fields containing target buyer metrics.
- create_customer: Registers an explicit customer entry mapping email, contact, and personal name structures.
- search_customers: Executes search queries to instantly parse matching customer entities.
- list_customer_orders: Compiles itemized transaction lists tied directly to an individual customer identification key.
- get_inventory_levels: Queries stock counts across distinct fulfillment storage facilities.
- adjust_inventory: Updates physical stock tallies across targeted warehouse locations.
- list_collections: Displays active item categorization containers saved within the storefront setup.
- create_collection: Generates smart structural grouping frameworks sorted by chosen display rule properties.
- create_discount: Sets up targeted markdown rule mechanisms using percentage adjustments or flat values.
- get_shop_info: Extracts core company properties, registration metrics, and base currency flags.
- list_locations: Reviews physical warehouse nodes used to track and store active items.
- get_analytics: Compiles store performance metrics covering revenues, total receipts, and relative transactional mean benchmarks over set timeframes.

How to use Tool Methods:-

1. list_products:
   - Purpose: Extracts arrays detailing catalog items matching chosen active status states.
   - Arguments:
     a) limit: int (default: 50) - Slices total response elements to a requested record ceiling.
     b) status: str (default: "active") - State configuration flag boundaries (e.g., `active`, `archived`, `draft`).
     c) vendor: str (default: "") - Filters products down to chosen wholesale supplier names.
     d) cred_key: str (default: "shopify") - Access token database key lookup coordinate pointing to secure secrets.
   - Returns: ToolResult presenting lists of product objects.
   - How to call: ShopifyTool.list_products(limit=10, status="active", vendor="Acme Corp")

2. get_product:
   - Purpose: Pulls comprehensive description profiles, variants, and image locations for an individual item.
   - Arguments:
     a) product_id: int - Explicit numerical entity token string identifying the product.
     b) cred_key: str (default: "shopify") - Security framework authorization locator flag.
   - Returns: ToolResult mapping matching database fields.
   - How to call: ShopifyTool.get_product(product_id=876543210)

3. create_product:
   - Purpose: Injects an item asset straight into the storefront inventory directory.
   - Arguments:
     a) title: str - Primary visual display name identifier text labeling the item.
     b) body: str (default: "") - Body context descriptive paragraph formatted inside standard HTML structures.
     c) vendor: str (default: "") - Label tagging supply manufacturers or distribution vendors.
     d) product_type: str (default: "") - Category definition string sorting store catalog indices.
     b) variants: List[Dict] (default: None) - Nested collection arrays describing properties, weight targets, and unique pricing metrics.
     c) images: List[Dict] (default: None) - Target dictionary files linking direct web asset URLs.
     d) cred_key: str (default: "shopify") - Credentials database address value index tracking storage settings.
   - Returns: ToolResult storing the populated platform item entry tracking fields.
   - How to call: ShopifyTool.create_product(title="Vintage Canvas Backpack", product_type="Bags", variants=[{"price": "49.99", "sku": "BP-VNTG-01"}])

4. update_product:
   - Purpose: Overwrites chosen parameter values on a registered catalog item.
   - Arguments:
     a) product_id: int - Explicit item key mapping records inside cloud datastores.
     b) data: dict - Configuration map variables identifying updated properties.
     c) cred_key: str (default: "shopify") - Private environment store credentials key tracker.
   - Returns: ToolResult outputting verified updated objects.
   - How to call: ShopifyTool.update_product(product_id=876543210, data={"title": "Premium Canvas Backpack"})

5. delete_product:
   - Purpose: Erases structural elements mapping specific items out of inventory indexes.
   - Arguments:
     a) product_id: int - Unique item catalog indexing number identifier.
     b) cred_key: str (default: "shopify") - Core platform authentication tracking path settings.
   - Returns: ToolResult showing operational boolean status confirmations.
   - How to call: ShopifyTool.delete_product(product_id=876543210)

6. list_variants:
   - Purpose: Exposes sub-item configuration fields that track varying sizes, shades, or secondary SKU parameters.
   - Arguments:
     a) product_id: int - Parent structural artifact code linked to general products.
     b) cred_key: str (default: "shopify") - Configuration storage selection address selector flag.
   - Returns: ToolResult displaying available child structural variants.
   - How to call: ShopifyTool.list_variants(product_id=876543210)

7. update_variant:
   - Purpose: Instantly alters critical trading values, stock counts, or physical weight measurements for a distinct item variant.
   - Arguments:
     a) variant_id: int - System identity target marking specific variants.
     b) price: str (default: "") - Price value tracked via text currency formats (e.g., `"19.99"`).
     c) inventory: int (default: -1) - Overwrites physical storage quantities when set to 0 or greater.
     d) weight: float (default: -1) - Adjusts item physical dimensions in metrics used by courier fulfillment loops.
     e) cred_key: str (default: "shopify") - Security access key identifier lookups string pointer.
   - Returns: ToolResult displaying detailed verification schemas.
   - How to call: ShopifyTool.update_variant(variant_id=432109876, price="24.99", inventory=150)

8. list_orders:
   - Purpose: Gathers past historical checkout transactions completed by storefront shoppers.
   - Arguments:
     a) limit: int (default: 50) - Extraction batch total constraint limits.
     b) status: str (default: "any") - Lifecycle states sorting options (e.g., `open`, `closed`, `cancelled`, `any`).
     c) financial_status: str (default: "") - Accounting settlement filters (e.g., `authorized`, `paid`, `refunded`).
     d) fulfillment_status: str (default: "") - Operational fulfillment milestone filter criteria (e.g., `fulfilled`, `unfulfilled`).
     e) cred_key: str (default: "shopify") - System key authorization dictionary path validation index string.
   - Returns: ToolResult housing full tracking orders datasets.
   - How to call: ShopifyTool.list_orders(limit=25, financial_status="paid", fulfillment_status="unfulfilled")

9. get_order:
   - Purpose: Reviews specific delivery addresses, tax configurations, and item breakdowns for an individual order.
   - Arguments:
     a) order_id: int - Unique identification numbers verifying single orders.
     b) cred_key: str (default: "shopify") - Gateway workspace credentials identifier reference pointer.
   - Returns: ToolResult mapping entire purchase ledger profiles.
   - How to call: ShopifyTool.get_order(order_id=987654321)

10. update_order:
    - Purpose: Attaches additional internal project flags or status modifications to an open order record.
    - Arguments:
      a) order_id: int - Target purchase document validation record reference.
      b) data: dict - Structural map updates passed to internal order metadata logs.
      c) cred_key: str (default: "shopify") - Identity authentication security validation index identifier pointer.
    - Returns: ToolResult rendering modified transaction parameters.
    - How to call: ShopifyTool.update_order(order_id=987654321, data={"note": "Customer requested packaging changes"})

11. cancel_order:
    - Purpose: Halts processing loops on active orders, offering automatic item restock parameters.
    - Arguments:
      a) order_id: int - Active verification reference marking transactions intended for cancellation.
      b) reason: str (default: "customer") - Informational categorization flags explaining cancellation tracking (e.g., `customer`, `fraud`, `inventory`).
      c) restock: bool (default: True) - Automatically returns purchased line items back to the active inventory catalog when true.
      d) cred_key: str (default: "shopify") - Cryptographic secure verification file index mapping.
    - Returns: ToolResult outlining adjusted cancellation outputs.
    - How to call: ShopifyTool.cancel_order(order_id=987654321, reason="customer", restock=True)

12. fulfill_order:
    - Purpose: Ships out items from a physical facility and adds carrier routing codes to notify the buyer.
    - Arguments:
      a) order_id: int - Target invoice identifier number tracking shipping requests.
      b) location_id: int - Core physical warehouse component identifier pointing to items.
      c) tracking_number: str (default: "") - Shipping barcode identification code provided by logistics companies.
      d) tracking_company: str (default: "") - Delivery transport provider titles (e.g., `"FedEx"`, `"UPS"`).
      e) cred_key: str (default: "shopify") - Access clearance token dictionary directory lookup key.
    - Returns: ToolResult returning full shipping tracking details.
    - How to call: ShopifyTool.fulfill_order(order_id=987654321, location_id=123456, tracking_number="1Z999AA10123456784", tracking_company="UPS")

13. list_customers:
    - Purpose: Displays systemic history rows defining registered users.
    - Arguments:
      a) limit: int (default: 50) - Extraction batch size limit values.
      b) since_id: int (default: 0) - Returns records created sequentially after this customer ID to handle data paging.
      c) created_at_min: str (default: "") - ISO timestamp string tracking earliest creation dates.
      d) cred_key: str (default: "shopify") - Private authentication security parameters lookup directory address index string.
    - Returns: ToolResult storing lists of client account fields.
    - How to call: ShopifyTool.list_customers(limit=30, created_at_min="2026-01-01T00:00:00Z")

14. get_customer:
    - Purpose: Fetches the primary addresses, contact strings, and life metrics for a chosen buyer account.
    - Arguments:
      a) customer_id: int - Core target registration numbers mapping customer profiles.
      b) cred_key: str (default: "shopify") - API access clearance dictionary file position pointer strings.
    - Returns: ToolResult outputting contextual customer datasets.
    - How to call: ShopifyTool.get_customer(customer_id=543210987)

15. create_customer:
    - Purpose: Creates a user account block within the store database registry.
    - Arguments:
      a) first: str - Given first personal identification name text label string.
      b) last: str - Family identification surname name tracking string components.
      c) email: str - Target communication mailbox context destination coordinates.
      d) phone: str (default: "") - Optional telephone numerical string.
      e) cred_key: str (default: "shopify") - Master secret validation environment config identifier locator code.
    - Returns: ToolResult storing newly created account tracking elements.
    - How to call: ShopifyTool.create_customer(first="Jane", last="Doe", email="jane.doe@example.com")

16. search_customers:
    - Purpose: Searches customer files to isolate buyers using text strings, names, or locations.
    - Arguments:
      a) query: str - Search term parameters matching fields (e.g., `country:United States`).
      b) cred_key: str (default: "shopify") - Platform framework identity token validation coordinate lookups map index string.
    - Returns: ToolResult displaying all profiles matching search metrics.
    - How to call: ShopifyTool.search_customers(query="Bob shopify")

17. list_customer_orders:
    - Purpose: Reviews all past storefront transaction items requested by a specific user profile.
    - Arguments:
      a) customer_id: int - Selected consumer database record registration reference token numbers.
      b) cred_key: str (default: "shopify") - Authorization file mapping lookup path tags settings configuration values.
    - Returns: ToolResult displaying historical transactions matching the targeted account profile.
    - How to call: ShopifyTool.list_customer_orders(customer_id=543210987)

18. get_inventory_levels:
    - Purpose: Reviews raw available quantities for an array of items across selected warehouse networks.
    - Arguments:
      a) location_id: int - Unique warehouse system token code identifying location contexts.
      b) inventory_item_ids: List[int] - Array strings listing specific item variant tracking identifiers.
      c) cred_key: str (default: "shopify") - Private validation key parameters profile selection address pointer location tags.
    - Returns: ToolResult array matrices mapping available numbers across item layers.
    - How to call: ShopifyTool.get_inventory_levels(location_id=123456, inventory_item_ids=[9876, 5432])

19. adjust_inventory:
    - Purpose: Adjusts physical items stock up or down relative to current counts.
    - Arguments:
      a) inventory_item_id: int - Targeted systemic product inventory identification token components.
      b) location_id: int - Designated storage facility identifier reference.
      c) adjustment: int - Positive or negative whole numbers to shift available units (e.g., **-5** subtracts five units).
      d) cred_key: str (default: "shopify") - Platform infrastructure access credential locator folder paths array maps index.
    - Returns: ToolResult reporting updated facility inventory states.
    - How to call: ShopifyTool.adjust_inventory(inventory_item_id=9876, location_id=123456, adjustment=25)

20. list_collections:
    - Purpose: Collects grouping matrices used to map items onto web categories.
    - Arguments:
      a) limit: int (default: 50) - Numeric ceilings constraining returned list responses items.
      b) cred_key: str (default: "shopify") - Encryption runtime token directory path reference indices.
    - Returns: ToolResult organizing collection layout categories properties fields.
    - How to call: ShopifyTool.list_collections(limit=10)

21. create_collection:
    - Purpose: Builds custom group sets to catalog products manually or through automated tags.
    - Arguments:
      a) title: str - Display nomenclature text labeling collection titles.
      b) rules: List[Dict] (default: None) - Array rules used to automatically filter items into categories (e.g., price conditions).
      c) sort_order: str (default: "best-selling") - Sequence controls prioritizing web layouts (e.g., `alpha-asc`, `price-desc`, `best-selling`).
      d) cred_key: str (default: "shopify") - Infrastructure authentication platform key dictionary indicator identifier values.
    - Returns: ToolResult presenting initialized category metadata blocks configurations.
    - How to call: ShopifyTool.create_collection(title="Summer Essentials", sort_order="best-selling")

22. create_discount:
    - Purpose: Sets up promotion variables that calculate markdown prices when applied at checkout.
    - Arguments:
      a) value: float - The markdown size metric calculated down based on requested adjustment types (e.g., **15.0** means 15%).
      b) value_type: str (default: "percentage") - Math configuration modes modifying price calculations (e.g., `fixed_amount`, `percentage`).
      c) entitled_product_ids: List[int] (default: None) - Restricts markdown promotions by targeting specific inventory product tracking entries.
      d) starts_at: str (default: "") - ISO launch date token activating rules; defaults to immediate startup when left empty.
      e) ends_at: str (default: "") - ISO expiration checkpoint window strings that disable active rules.
      f) cred_key: str (default: "shopify") - Secret operational authentication profile selector parameters index values.
    - Returns: ToolResult tracking price rule initialization properties logs.
    - How to call: ShopifyTool.create_discount(value=20.0, value_type="percentage", ends_at="2026-12-31T23:59:59Z")

23. get_shop_info:
    - Purpose: Audits registration data parameters defining general store profiles.
    - Arguments:
      a) cred_key: str (default: "shopify") - Active cloud storage credential lookup address selector.
    - Returns: ToolResult outlining operating constraints, base locations, and platform tiers.
    - How to call: ShopifyTool.get_shop_info()

24. list_locations:
    - Purpose: Discovers operating physical facility nodes registered behind inventory operations.
    - Arguments:
      a) cred_key: str (default: "shopify") - Gateway profile authentication directory access token mapping tags settings tracking variables.
    - Returns: ToolResult compiling active tracking storage identifiers.
    - How to call: ShopifyTool.list_locations()

25. get_analytics:
    - Purpose: Synthesizes multi-day sales data parameters into clean financial overview trackers.
    - Arguments:
      a) period: str (default: "last_7_days") - Standard tracking intervals defining metrics scopes (e.g., `last_7_days`, `last_30_days`, `last_90_days`).
      b) cred_key: str (default: "shopify") - Cloud security platform authorization keys pointer directory indices tags.
    - Returns: ToolResult sorting values into order tallies, gross revenue, and aggregate average cart values.
    - How to call: ShopifyTool.get_analytics(period="last_30_days")
    """)
    
    @staticmethod
    def _headers(cred_key: str = "shopify") -> Tuple[str, Dict]:
        import requests
        c = CredStore.load(cred_key)
        store = c.get("store", "")         # e.g. my-store.myshopify.com
        token = c.get("access_token", "")
        if not store or not token:
            raise ValueError("CredStore.save('shopify', {'store': 'x.myshopify.com', 'access_token': '...'}).")
        base = f"https://{store}/admin/api/2024-01"
        hdrs = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
        return base, hdrs

    @staticmethod
    def _get(endpoint: str, params: Dict = None, cred_key: str = "shopify") -> Any:
        import requests
        base, hdrs = ShopifyTool._headers(cred_key)
        r = requests.get(f"{base}/{endpoint}", headers=hdrs, params=params or {}, timeout=20)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def _post(endpoint: str, payload: Dict, cred_key: str = "shopify") -> Any:
        import requests
        base, hdrs = ShopifyTool._headers(cred_key)
        r = requests.post(f"{base}/{endpoint}", headers=hdrs, json=payload, timeout=20)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def _put(endpoint: str, payload: Dict, cred_key: str = "shopify") -> Any:
        import requests
        base, hdrs = ShopifyTool._headers(cred_key)
        r = requests.put(f"{base}/{endpoint}", headers=hdrs, json=payload, timeout=20)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def _delete(endpoint: str, cred_key: str = "shopify") -> bool:
        import requests
        base, hdrs = ShopifyTool._headers(cred_key)
        r = requests.delete(f"{base}/{endpoint}", headers=hdrs, timeout=20)
        return r.status_code in (200, 204)

    # ── Products ──

    @staticmethod
    def list_products(limit: int = 50, status: str = "active", vendor: str = "", cred_key: str = "shopify") -> ToolResult:
        try:
            params: Dict[str, Any] = {"limit": limit, "status": status}
            if vendor:
                params["vendor"] = vendor
            data = ShopifyTool._get("products.json", params, cred_key)
            products = data.get("products", [])
            return ToolResult(True, f"✓ {len(products)} products", products)
        except Exception as e:
            return ToolResult(False, f"✗ List products failed: {e}")

    @staticmethod
    def get_product(product_id: int, cred_key: str = "shopify") -> ToolResult:
        try:
            data = ShopifyTool._get(f"products/{product_id}.json", cred_key=cred_key)
            return ToolResult(True, f"✓ Product {product_id}", data.get("product", {}))
        except Exception as e:
            return ToolResult(False, f"✗ Get product failed: {e}")

    @staticmethod
    def create_product(title: str, body: str = "", vendor: str = "", product_type: str = "", variants: List[Dict] = None, images: List[Dict] = None, cred_key: str = "shopify") -> ToolResult:
        try:
            payload = {"product": {"title": title, "body_html": body, "vendor": vendor, "product_type": product_type, "variants": variants or [], "images": images or []}}
            data = ShopifyTool._post("products.json", payload, cred_key)
            prod = data.get("product", {})
            return ToolResult(True, f"✓ Product {prod.get('id')} created", prod)
        except Exception as e:
            return ToolResult(False, f"✗ Create product failed: {e}")

    @staticmethod
    def update_product(product_id: int, data: Dict, cred_key: str = "shopify") -> ToolResult:
        try:
            result = ShopifyTool._put(f"products/{product_id}.json", {"product": data}, cred_key)
            return ToolResult(True, f"✓ Product {product_id} updated", result.get("product", {}))
        except Exception as e:
            return ToolResult(False, f"✗ Update product failed: {e}")

    @staticmethod
    def delete_product(product_id: int, cred_key: str = "shopify") -> ToolResult:
        try:
            ok = ShopifyTool._delete(f"products/{product_id}.json", cred_key)
            return ToolResult(ok, f"{'✓ Product deleted' if ok else '✗ Delete failed'}")
        except Exception as e:
            return ToolResult(False, f"✗ Delete product failed: {e}")

    @staticmethod
    def list_variants(product_id: int, cred_key: str = "shopify") -> ToolResult:
        try:
            data = ShopifyTool._get(f"products/{product_id}/variants.json", cred_key=cred_key)
            return ToolResult(True, f"✓ Variants for {product_id}", data.get("variants", []))
        except Exception as e:
            return ToolResult(False, f"✗ List variants failed: {e}")

    @staticmethod
    def update_variant(variant_id: int, price: str = "", inventory: int = -1, weight: float = -1, cred_key: str = "shopify") -> ToolResult:
        try:
            update: Dict[str, Any] = {"id": variant_id}
            if price:
                update["price"] = price
            if inventory >= 0:
                update["inventory_quantity"] = inventory
            if weight >= 0:
                update["weight"] = weight
            result = ShopifyTool._put(f"variants/{variant_id}.json", {"variant": update}, cred_key)
            return ToolResult(True, f"✓ Variant {variant_id} updated", result.get("variant", {}))
        except Exception as e:
            return ToolResult(False, f"✗ Update variant failed: {e}")

    # ── Orders ──

    @staticmethod
    def list_orders(limit: int = 50, status: str = "any", financial_status: str = "", fulfillment_status: str = "", cred_key: str = "shopify") -> ToolResult:
        try:
            params: Dict[str, Any] = {"limit": limit, "status": status}
            if financial_status:
                params["financial_status"] = financial_status
            if fulfillment_status:
                params["fulfillment_status"] = fulfillment_status
            data = ShopifyTool._get("orders.json", params, cred_key)
            orders = data.get("orders", [])
            return ToolResult(True, f"✓ {len(orders)} orders", orders)
        except Exception as e:
            return ToolResult(False, f"✗ List orders failed: {e}")

    @staticmethod
    def get_order(order_id: int, cred_key: str = "shopify") -> ToolResult:
        try:
            data = ShopifyTool._get(f"orders/{order_id}.json", cred_key=cred_key)
            return ToolResult(True, f"✓ Order {order_id}", data.get("order", {}))
        except Exception as e:
            return ToolResult(False, f"✗ Get order failed: {e}")

    @staticmethod
    def update_order(order_id: int, data: Dict, cred_key: str = "shopify") -> ToolResult:
        try:
            result = ShopifyTool._put(f"orders/{order_id}.json", {"order": data}, cred_key)
            return ToolResult(True, f"✓ Order {order_id} updated", result.get("order", {}))
        except Exception as e:
            return ToolResult(False, f"✗ Update order failed: {e}")

    @staticmethod
    def cancel_order(order_id: int, reason: str = "customer", restock: bool = True, cred_key: str = "shopify") -> ToolResult:
        try:
            result = ShopifyTool._post(f"orders/{order_id}/cancel.json", {"reason": reason, "restock": restock}, cred_key)
            return ToolResult(True, f"✓ Order {order_id} cancelled", result.get("order", {}))
        except Exception as e:
            return ToolResult(False, f"✗ Cancel order failed: {e}")

    @staticmethod
    def fulfill_order(order_id: int, location_id: int, tracking_number: str = "", tracking_company: str = "", cred_key: str = "shopify") -> ToolResult:
        try:
            payload: Dict[str, Any] = {"fulfillment": {"location_id": location_id, "notify_customer": True}}
            if tracking_number:
                payload["fulfillment"]["tracking_number"] = tracking_number
            if tracking_company:
                payload["fulfillment"]["tracking_company"] = tracking_company
            result = ShopifyTool._post(f"orders/{order_id}/fulfillments.json", payload, cred_key)
            return ToolResult(True, f"✓ Order {order_id} fulfilled", result.get("fulfillment", {}))
        except Exception as e:
            return ToolResult(False, f"✗ Fulfill order failed: {e}")

    # ── Customers ──

    @staticmethod
    def list_customers(limit: int = 50, since_id: int = 0, created_at_min: str = "", cred_key: str = "shopify") -> ToolResult:
        try:
            params: Dict[str, Any] = {"limit": limit}
            if since_id:
                params["since_id"] = since_id
            if created_at_min:
                params["created_at_min"] = created_at_min
            data = ShopifyTool._get("customers.json", params, cred_key)
            return ToolResult(True, f"✓ {len(data.get('customers', []))} customers", data.get("customers", []))
        except Exception as e:
            return ToolResult(False, f"✗ List customers failed: {e}")

    @staticmethod
    def get_customer(customer_id: int, cred_key: str = "shopify") -> ToolResult:
        try:
            data = ShopifyTool._get(f"customers/{customer_id}.json", cred_key=cred_key)
            return ToolResult(True, f"✓ Customer {customer_id}", data.get("customer", {}))
        except Exception as e:
            return ToolResult(False, f"✗ Get customer failed: {e}")

    @staticmethod
    def create_customer(first: str, last: str, email: str, phone: str = "", cred_key: str = "shopify") -> ToolResult:
        try:
            payload = {"customer": {"first_name": first, "last_name": last, "email": email, "phone": phone}}
            data = ShopifyTool._post("customers.json", payload, cred_key)
            return ToolResult(True, f"✓ Customer {data.get('customer', {}).get('id')} created", data.get("customer", {}))
        except Exception as e:
            return ToolResult(False, f"✗ Create customer failed: {e}")

    @staticmethod
    def search_customers(query: str, cred_key: str = "shopify") -> ToolResult:
        try:
            data = ShopifyTool._get("customers/search.json", {"query": query}, cred_key)
            return ToolResult(True, f"✓ Search results", data.get("customers", []))
        except Exception as e:
            return ToolResult(False, f"✗ Search customers failed: {e}")

    @staticmethod
    def list_customer_orders(customer_id: int, cred_key: str = "shopify") -> ToolResult:
        try:
            data = ShopifyTool._get(f"customers/{customer_id}/orders.json", cred_key=cred_key)
            return ToolResult(True, f"✓ Orders for customer {customer_id}", data.get("orders", []))
        except Exception as e:
            return ToolResult(False, f"✗ List customer orders failed: {e}")

    # ── Inventory ──

    @staticmethod
    def get_inventory_levels(location_id: int, inventory_item_ids: List[int], cred_key: str = "shopify") -> ToolResult:
        try:
            ids = ",".join(str(i) for i in inventory_item_ids)
            data = ShopifyTool._get("inventory_levels.json", {"location_ids": location_id, "inventory_item_ids": ids}, cred_key)
            return ToolResult(True, "✓ Inventory levels", data.get("inventory_levels", []))
        except Exception as e:
            return ToolResult(False, f"✗ Get inventory levels failed: {e}")

    @staticmethod
    def adjust_inventory(inventory_item_id: int, location_id: int, adjustment: int, cred_key: str = "shopify") -> ToolResult:
        try:
            payload = {"location_id": location_id, "inventory_item_id": inventory_item_id, "available_adjustment": adjustment}
            result = ShopifyTool._post("inventory_levels/adjust.json", payload, cred_key)
            return ToolResult(True, f"✓ Inventory adjusted by {adjustment}", result.get("inventory_level", {}))
        except Exception as e:
            return ToolResult(False, f"✗ Adjust inventory failed: {e}")

    # ── Collections, Discounts, Info ──

    @staticmethod
    def list_collections(limit: int = 50, cred_key: str = "shopify") -> ToolResult:
        try:
            data = ShopifyTool._get("custom_collections.json", {"limit": limit}, cred_key)
            return ToolResult(True, f"✓ {len(data.get('custom_collections', []))} collections", data.get("custom_collections", []))
        except Exception as e:
            return ToolResult(False, f"✗ List collections failed: {e}")

    @staticmethod
    def create_collection(title: str, rules: List[Dict] = None, sort_order: str = "best-selling", cred_key: str = "shopify") -> ToolResult:
        try:
            payload: Dict[str, Any] = {"custom_collection": {"title": title, "sort_order": sort_order}}
            if rules:
                payload["custom_collection"]["rules"] = rules
            data = ShopifyTool._post("custom_collections.json", payload, cred_key)
            return ToolResult(True, f"✓ Collection created", data.get("custom_collection", {}))
        except Exception as e:
            return ToolResult(False, f"✗ Create collection failed: {e}")

    @staticmethod
    def create_discount(value: float, value_type: str = "percentage", entitled_product_ids: List[int] = None, starts_at: str = "", ends_at: str = "", cred_key: str = "shopify") -> ToolResult:
        try:
            payload: Dict[str, Any] = {"price_rule": {"title": f"Discount-{int(value)}", "target_type": "line_item", "target_selection": "entitled" if entitled_product_ids else "all", "allocation_method": "across", "value_type": value_type, "value": f"-{value}", "customer_selection": "all", "starts_at": starts_at or datetime.utcnow().isoformat() + "Z"}}
            if entitled_product_ids:
                payload["price_rule"]["entitled_product_ids"] = entitled_product_ids
            if ends_at:
                payload["price_rule"]["ends_at"] = ends_at
            data = ShopifyTool._post("price_rules.json", payload, cred_key)
            return ToolResult(True, f"✓ Discount created", data.get("price_rule", {}))
        except Exception as e:
            return ToolResult(False, f"✗ Create discount failed: {e}")

    @staticmethod
    def get_shop_info(cred_key: str = "shopify") -> ToolResult:
        try:
            data = ShopifyTool._get("shop.json", cred_key=cred_key)
            return ToolResult(True, "✓ Shop info", data.get("shop", {}))
        except Exception as e:
            return ToolResult(False, f"✗ Get shop info failed: {e}")

    @staticmethod
    def list_locations(cred_key: str = "shopify") -> ToolResult:
        try:
            data = ShopifyTool._get("locations.json", cred_key=cred_key)
            return ToolResult(True, f"✓ Locations", data.get("locations", []))
        except Exception as e:
            return ToolResult(False, f"✗ List locations failed: {e}")

    @staticmethod
    def get_analytics(period: str = "last_7_days", cred_key: str = "shopify") -> ToolResult:
        try:
            end = datetime.utcnow()
            days_map = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90}
            days = days_map.get(period, 7)
            start = (end - timedelta(days=days)).strftime("%Y-%m-%d")
            end_str = end.strftime("%Y-%m-%d")
            orders_data = ShopifyTool._get("orders.json", {"status": "any", "created_at_min": start + "T00:00:00Z", "created_at_max": end_str + "T23:59:59Z", "limit": 250}, cred_key)
            orders = orders_data.get("orders", [])
            total_revenue = sum(float(o.get("total_price", 0)) for o in orders)
            summary = {"period": period, "orders_count": len(orders), "total_revenue": round(total_revenue, 2), "avg_order_value": round(total_revenue / len(orders), 2) if orders else 0}
            return ToolResult(True, f"✓ Analytics for {period}", summary)
        except Exception as e:
            return ToolResult(False, f"✗ Get analytics failed: {e}")


# ─────────────────────────────────────────────
# 4. InvoiceTool
# ─────────────────────────────────────────────

class InvoiceTool:
    name = "invoice"
    description = "Professional invoice, quote, receipt, and PO generation; send via email; batch create; AI data extraction"

    @staticmethod
    def _draw_pdf_table(c_obj, items: List[Dict], x: float, y: float, col_widths: List[float], headers: List[str]) -> float:
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib.units import inch
        header_row = headers
        data_rows = []
        for item in items:
            row = [str(item.get(h.lower().replace(" ", "_"), item.get(h, ""))) for h in headers]
            data_rows.append(row)
        table_data = [header_row] + data_rows
        t = Table(table_data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 9),
            ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("ALIGN",      (0, 0), (-1, -1), "LEFT"),
        ]))
        t.wrapOn(c_obj, 0, 0)
        t.drawOn(c_obj, x, y - t._height)
        return y - t._height - 10

    @staticmethod
    def create_invoice(invoice_number: str, date: str, due_date: str, from_details: Dict, to_details: Dict, items: List[Dict], tax_rate: float = 0.0, currency: str = "USD", logo: str = "", output: str = "invoice.pdf") -> ToolResult:
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.units import inch, mm

            W, H = A4
            c = canvas.Canvas(output, pagesize=A4)

            # Header
            c.setFillColor(colors.HexColor("#1a1a2e"))
            c.rect(0, H - 80, W, 80, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 24)
            c.drawString(40, H - 50, "INVOICE")
            c.setFont("Helvetica", 10)
            c.drawRightString(W - 40, H - 35, f"Invoice #: {invoice_number}")
            c.drawRightString(W - 40, H - 50, f"Date: {date}")
            c.drawRightString(W - 40, H - 65, f"Due: {due_date}")

            # Logo
            if logo and Path(logo).exists():
                try:
                    c.drawImage(logo, 40, H - 75, width=120, height=60, preserveAspectRatio=True)
                except Exception:
                    pass

            # From / To blocks
            y = H - 110
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(40, y, "FROM")
            c.drawString(300, y, "BILL TO")
            y -= 15
            c.setFont("Helvetica", 9)
            for key in ["name", "address", "city", "email", "phone"]:
                val = from_details.get(key, "")
                if val:
                    c.drawString(40, y, str(val))
                    y2 = y
                to_val = to_details.get(key, "")
                if to_val:
                    c.drawString(300, y, str(to_val))
                y -= 13

            # Items table
            y -= 20
            subtotal = 0.0
            table_items = []
            for item in items:
                qty   = float(item.get("qty", item.get("quantity", 1)))
                price = float(item.get("price", item.get("unit_price", 0)))
                total = qty * price
                subtotal += total
                table_items.append({"Description": item.get("description", item.get("name", "")), "Qty": str(qty), "Unit Price": f"{currency} {price:.2f}", "Total": f"{currency} {total:.2f}"})

            col_widths = [250, 60, 100, 100]
            y = InvoiceTool._draw_pdf_table(c, table_items, 40, y, col_widths, ["Description", "Qty", "Unit Price", "Total"])

            # Totals
            tax = subtotal * tax_rate / 100
            grand_total = subtotal + tax
            y -= 10
            c.setFont("Helvetica", 10)
            c.drawRightString(W - 40, y,       f"Subtotal: {currency} {subtotal:.2f}")
            c.drawRightString(W - 40, y - 15,  f"Tax ({tax_rate}%): {currency} {tax:.2f}")
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(colors.HexColor("#1a1a2e"))
            c.drawRightString(W - 40, y - 35,  f"TOTAL: {currency} {grand_total:.2f}")

            # Footer
            c.setFillColor(colors.grey)
            c.setFont("Helvetica", 8)
            c.drawCentredString(W / 2, 30, "Thank you for your business! Generated by NPM Agent — NPMAI ECOSYSTEM")
            c.save()
            return ToolResult(True, f"✓ Invoice saved: {output}", {"path": output, "total": grand_total})
        except Exception as e:
            return ToolResult(False, f"✗ Create invoice failed: {e}")

    @staticmethod
    def create_quote(quote_number: str, date: str, valid_until: str, from_details: Dict, to_details: Dict, items: List[Dict], discount: float = 0.0, output: str = "quote.pdf") -> ToolResult:
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            W, H = A4
            c = canvas.Canvas(output, pagesize=A4)
            c.setFillColor(colors.HexColor("#0f3460"))
            c.rect(0, H - 80, W, 80, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 24)
            c.drawString(40, H - 50, "QUOTATION")
            c.setFont("Helvetica", 10)
            c.drawRightString(W - 40, H - 35, f"Quote #: {quote_number}")
            c.drawRightString(W - 40, H - 50, f"Date: {date}")
            c.drawRightString(W - 40, H - 65, f"Valid Until: {valid_until}")
            y = H - 110
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(40, y, "FROM"); c.drawString(300, y, "PREPARED FOR")
            y -= 15
            c.setFont("Helvetica", 9)
            for key in ["name", "address", "city", "email"]:
                if from_details.get(key): c.drawString(40, y, from_details[key])
                if to_details.get(key):   c.drawString(300, y, to_details[key])
                y -= 13
            y -= 20
            subtotal = sum(float(i.get("qty", 1)) * float(i.get("price", 0)) for i in items)
            disc_amt = subtotal * discount / 100
            total = subtotal - disc_amt
            table_items = [{"Description": i.get("description", ""), "Qty": str(i.get("qty", 1)), "Price": f"{i.get('price', 0):.2f}", "Total": f"{float(i.get('qty', 1)) * float(i.get('price', 0)):.2f}"} for i in items]
            y = InvoiceTool._draw_pdf_table(c, table_items, 40, y, [250, 60, 100, 100], ["Description", "Qty", "Price", "Total"])
            y -= 10
            c.setFont("Helvetica", 10)
            c.drawRightString(W - 40, y, f"Subtotal: {subtotal:.2f}")
            c.drawRightString(W - 40, y - 15, f"Discount ({discount}%): -{disc_amt:.2f}")
            c.setFont("Helvetica-Bold", 12)
            c.drawRightString(W - 40, y - 35, f"TOTAL: {total:.2f}")
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.grey)
            c.drawCentredString(W / 2, 30, "This quote is valid until " + valid_until + " | Generated by NPM Agent")
            c.save()
            return ToolResult(True, f"✓ Quote saved: {output}", {"path": output, "total": total})
        except Exception as e:
            return ToolResult(False, f"✗ Create quote failed: {e}")

    @staticmethod
    def create_receipt(transaction_id: str, date: str, items: List[Dict], payment_method: str, from_details: Dict, to_details: Dict, output: str = "receipt.pdf") -> ToolResult:
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            W, H = A4
            c = canvas.Canvas(output, pagesize=A4)
            c.setFillColor(colors.HexColor("#16213e"))
            c.rect(0, H - 80, W, 80, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 24)
            c.drawString(40, H - 50, "RECEIPT")
            c.setFont("Helvetica", 10)
            c.drawRightString(W - 40, H - 35, f"Txn ID: {transaction_id}")
            c.drawRightString(W - 40, H - 50, f"Date: {date}")
            c.drawRightString(W - 40, H - 65, f"Payment: {payment_method}")
            y = H - 110
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(40, y, from_details.get("name", ""))
            c.drawString(300, y, to_details.get("name", ""))
            y -= 30
            total = sum(float(i.get("qty", 1)) * float(i.get("price", 0)) for i in items)
            table_items = [{"Item": i.get("description", ""), "Qty": str(i.get("qty", 1)), "Price": f"{i.get('price', 0):.2f}", "Amount": f"{float(i.get('qty', 1)) * float(i.get('price', 0)):.2f}"} for i in items]
            y = InvoiceTool._draw_pdf_table(c, table_items, 40, y, [250, 60, 100, 100], ["Item", "Qty", "Price", "Amount"])
            y -= 15
            c.setFont("Helvetica-Bold", 14)
            c.drawRightString(W - 40, y, f"TOTAL PAID: {total:.2f}")
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.grey)
            c.drawCentredString(W / 2, 30, "✓ Payment Confirmed — Thank you! | NPM Agent")
            c.save()
            return ToolResult(True, f"✓ Receipt saved: {output}", {"path": output, "total": total})
        except Exception as e:
            return ToolResult(False, f"✗ Create receipt failed: {e}")

    @staticmethod
    def create_purchase_order(po_number: str, date: str, vendor: Dict, items: List[Dict], ship_to: Dict, output: str = "po.pdf") -> ToolResult:
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            W, H = A4
            c = canvas.Canvas(output, pagesize=A4)
            c.setFillColor(colors.HexColor("#533483"))
            c.rect(0, H - 80, W, 80, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 22)
            c.drawString(40, H - 50, "PURCHASE ORDER")
            c.setFont("Helvetica", 10)
            c.drawRightString(W - 40, H - 35, f"PO #: {po_number}")
            c.drawRightString(W - 40, H - 50, f"Date: {date}")
            y = H - 110
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(40, y, "VENDOR"); c.drawString(300, y, "SHIP TO")
            y -= 15
            c.setFont("Helvetica", 9)
            for key in ["name", "address", "city", "email", "phone"]:
                if vendor.get(key):   c.drawString(40, y, vendor[key])
                if ship_to.get(key):  c.drawString(300, y, ship_to[key])
                y -= 13
            y -= 20
            total = sum(float(i.get("qty", 1)) * float(i.get("unit_price", 0)) for i in items)
            table_items = [{"Item": i.get("name", ""), "Qty": str(i.get("qty", 1)), "Unit Price": f"{i.get('unit_price', 0):.2f}", "Total": f"{float(i.get('qty', 1)) * float(i.get('unit_price', 0)):.2f}"} for i in items]
            y = InvoiceTool._draw_pdf_table(c, table_items, 40, y, [250, 60, 100, 100], ["Item", "Qty", "Unit Price", "Total"])
            y -= 15
            c.setFont("Helvetica-Bold", 12)
            c.drawRightString(W - 40, y, f"PO TOTAL: {total:.2f}")
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.grey)
            c.drawCentredString(W / 2, 30, "Authorized Purchase Order | NPM Agent — NPMAI ECOSYSTEM")
            c.save()
            return ToolResult(True, f"✓ PO saved: {output}", {"path": output, "total": total})
        except Exception as e:
            return ToolResult(False, f"✗ Create PO failed: {e}")

    @staticmethod
    def send_invoice_email(invoice_path: str, to_email: str, subject: str = "Your Invoice", message: str = "Please find your invoice attached.", cc: str = "", cred_key: str = "gmail") -> ToolResult:
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.base import MIMEBase
            from email import encoders as email_encoders
            creds = CredStore.load(cred_key)
            user  = creds.get("email", "")
            pwd   = creds.get("password", "")
            host  = creds.get("smtp_host", "smtp.gmail.com")
            port  = int(creds.get("smtp_port", 587))
            if not user or not pwd:
                return ToolResult(False, "No email credentials configured.")
            msg = MIMEMultipart()
            msg["From"] = user; msg["To"] = to_email; msg["Subject"] = subject
            if cc: msg["Cc"] = cc
            msg.attach(MIMEText(message, "plain"))
            with open(invoice_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            email_encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{Path(invoice_path).name}"')
            msg.attach(part)
            recipients = [to_email] + ([cc] if cc else [])
            with smtplib.SMTP(host, port) as s:
                s.starttls(); s.login(user, pwd); s.sendmail(user, recipients, msg.as_string())
            return ToolResult(True, f"✓ Invoice emailed to {to_email}")
        except Exception as e:
            return ToolResult(False, f"✗ Send invoice email failed: {e}")

    @staticmethod
    def batch_create_invoices(data_csv: str, template: Dict, output_folder: str) -> ToolResult:
        try:
            import csv as csv_mod
            Path(output_folder).mkdir(parents=True, exist_ok=True)
            created = []
            with open(data_csv, newline="") as f:
                reader = csv_mod.DictReader(f)
                for i, row in enumerate(reader):
                    inv_num = row.get("invoice_number", f"INV-{i+1:04d}")
                    out_path = str(Path(output_folder) / f"{inv_num}.pdf")
                    to_details = {k: row.get(k, "") for k in ["name", "address", "city", "email"]}
                    items = json.loads(row.get("items_json", "[]")) or template.get("items", [])
                    result = InvoiceTool.create_invoice(
                        invoice_number=inv_num,
                        date=row.get("date", datetime.now().strftime("%Y-%m-%d")),
                        due_date=row.get("due_date", ""),
                        from_details=template.get("from_details", {}),
                        to_details=to_details,
                        items=items,
                        tax_rate=float(row.get("tax_rate", template.get("tax_rate", 0))),
                        currency=row.get("currency", template.get("currency", "USD")),
                        output=out_path,
                    )
                    if result.success:
                        created.append(out_path)
            return ToolResult(True, f"✓ {len(created)} invoices created in {output_folder}", created)
        except Exception as e:
            return ToolResult(False, f"✗ Batch create invoices failed: {e}")

    @staticmethod
    def extract_invoice_data(invoice_pdf: str, model: str = "llama3.2:3b") -> ToolResult:
        try:
            from pypdf import PdfReader
            text = "\n".join(p.extract_text() or "" for p in PdfReader(invoice_pdf).pages)
            try:
                from npmai import Ollama
                llm = Ollama(model=model, temperature=0.1, change=True, Models=["mistral:7b"])
                prompt = f"""Extract structured data from this invoice text. Return ONLY valid JSON with keys:
invoice_number, date, due_date, from_name, to_name, items (list of {{description, qty, price, total}}), subtotal, tax, total, currency.

Invoice text:
{text[:3000]}

JSON only:"""
                raw = llm.invoke(prompt)
                import re
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                data = json.loads(match.group()) if match else {"raw_text": text[:500]}
            except Exception:
                data = {"raw_text": text[:1000]}
            return ToolResult(True, "✓ Invoice data extracted", data)
        except Exception as e:
            return ToolResult(False, f"✗ Extract invoice data failed: {e}")

    @staticmethod
    def create_recurring_invoice(template: Dict, schedule: str, output_folder: str) -> ToolResult:
        """schedule: 'monthly' | 'weekly' | 'quarterly'"""
        try:
            Path(output_folder).mkdir(parents=True, exist_ok=True)
            today = datetime.now()
            due_map = {"monthly": 30, "weekly": 7, "quarterly": 90}
            days = due_map.get(schedule, 30)
            due_date = (today + timedelta(days=days)).strftime("%Y-%m-%d")
            inv_num = f"REC-{today.strftime('%Y%m%d')}-{schedule[:3].upper()}"
            out_path = str(Path(output_folder) / f"{inv_num}.pdf")
            result = InvoiceTool.create_invoice(
                invoice_number=inv_num,
                date=today.strftime("%Y-%m-%d"),
                due_date=due_date,
                from_details=template.get("from_details", {}),
                to_details=template.get("to_details", {}),
                items=template.get("items", []),
                tax_rate=template.get("tax_rate", 0),
                currency=template.get("currency", "USD"),
                output=out_path,
            )
            return ToolResult(result.success, f"✓ Recurring invoice ({schedule}) created: {out_path}", {"path": out_path})
        except Exception as e:
            return ToolResult(False, f"✗ Create recurring invoice failed: {e}")


# ─────────────────────────────────────────────
# 5. AccountingTool
# ─────────────────────────────────────────────

class AccountingTool:
    name = "accounting"
    description = "Financial calculations: GST, VAT, P&L, balance sheet, cash flow, depreciation, currency conversion, tax liability, expense tracking"

    @staticmethod
    def calculate_gst(amount: float, rate: float = 18.0, type: str = "exclusive") -> ToolResult:
        try:
            if type == "exclusive":
                gst = amount * rate / 100
                total = amount + gst
            else:
                gst = amount - amount * 100 / (100 + rate)
                total = amount
                amount = total - gst
            result = {"base_amount": round(amount, 2), "gst_rate": rate, "cgst": round(gst / 2, 2), "sgst": round(gst / 2, 2), "total_gst": round(gst, 2), "total_amount": round(total, 2)}
            return ToolResult(True, f"✓ GST calculated: ₹{round(gst, 2)} on ₹{round(amount, 2)}", result)
        except Exception as e:
            return ToolResult(False, f"✗ GST calculation failed: {e}")

    @staticmethod
    def calculate_vat(amount: float, rate: float, country: str = "UK") -> ToolResult:
        try:
            vat = amount * rate / 100
            total = amount + vat
            result = {"country": country, "base_amount": round(amount, 2), "vat_rate": rate, "vat_amount": round(vat, 2), "total": round(total, 2)}
            return ToolResult(True, f"✓ VAT {rate}%: {round(vat, 2)}", result)
        except Exception as e:
            return ToolResult(False, f"✗ VAT calculation failed: {e}")

    @staticmethod
    def generate_profit_loss(revenue_items: List[Dict], expense_items: List[Dict], period: str = "", output: str = "") -> ToolResult:
        try:
            total_revenue = sum(float(i.get("amount", 0)) for i in revenue_items)
            total_expenses = sum(float(i.get("amount", 0)) for i in expense_items)
            gross_profit = total_revenue - total_expenses
            margin = (gross_profit / total_revenue * 100) if total_revenue else 0
            report = {
                "period": period or datetime.now().strftime("%B %Y"),
                "revenue": {"items": revenue_items, "total": round(total_revenue, 2)},
                "expenses": {"items": expense_items, "total": round(total_expenses, 2)},
                "gross_profit": round(gross_profit, 2),
                "profit_margin_%": round(margin, 2),
                "generated_at": datetime.now().isoformat(),
            }
            if output:
                Path(output).parent.mkdir(parents=True, exist_ok=True)
                Path(output).write_text(json.dumps(report, indent=2))
            summary = f"Revenue: {total_revenue:.2f} | Expenses: {total_expenses:.2f} | Net: {gross_profit:.2f} ({margin:.1f}% margin)"
            return ToolResult(True, f"✓ P&L: {summary}", report)
        except Exception as e:
            return ToolResult(False, f"✗ P&L generation failed: {e}")

    @staticmethod
    def generate_balance_sheet(assets: Dict, liabilities: Dict, equity: Dict, date: str = "", output: str = "") -> ToolResult:
        try:
            total_assets = sum(float(v) for v in assets.values())
            total_liabilities = sum(float(v) for v in liabilities.values())
            total_equity = sum(float(v) for v in equity.values())
            balanced = abs((total_liabilities + total_equity) - total_assets) < 0.01
            sheet = {
                "date": date or datetime.now().strftime("%Y-%m-%d"),
                "assets": {"items": assets, "total": round(total_assets, 2)},
                "liabilities": {"items": liabilities, "total": round(total_liabilities, 2)},
                "equity": {"items": equity, "total": round(total_equity, 2)},
                "balanced": balanced,
            }
            if output:
                Path(output).parent.mkdir(parents=True, exist_ok=True)
                Path(output).write_text(json.dumps(sheet, indent=2))
            return ToolResult(True, f"✓ Balance Sheet — Assets: {total_assets:.2f} | {'BALANCED' if balanced else 'UNBALANCED'}", sheet)
        except Exception as e:
            return ToolResult(False, f"✗ Balance sheet failed: {e}")

    @staticmethod
    def generate_cash_flow(operating: List[Dict], investing: List[Dict], financing: List[Dict], period: str = "", output: str = "") -> ToolResult:
        try:
            def _sum(items): return sum(float(i.get("amount", 0)) for i in items)
            op_total  = _sum(operating)
            inv_total = _sum(investing)
            fin_total = _sum(financing)
            net_cash  = op_total + inv_total + fin_total
            report = {
                "period": period or datetime.now().strftime("%B %Y"),
                "operating": {"items": operating, "total": round(op_total, 2)},
                "investing": {"items": investing, "total": round(inv_total, 2)},
                "financing": {"items": financing, "total": round(fin_total, 2)},
                "net_cash_flow": round(net_cash, 2),
            }
            if output:
                Path(output).parent.mkdir(parents=True, exist_ok=True)
                Path(output).write_text(json.dumps(report, indent=2))
            return ToolResult(True, f"✓ Cash Flow — Net: {net_cash:.2f}", report)
        except Exception as e:
            return ToolResult(False, f"✗ Cash flow failed: {e}")

    @staticmethod
    def depreciation_schedule(asset_name: str, cost: float, salvage: float, life: int, method: str = "straight_line", output: str = "") -> ToolResult:
        try:
            schedule = []
            book_value = cost
            if method == "straight_line":
                annual_dep = (cost - salvage) / life
                for year in range(1, life + 1):
                    dep = min(annual_dep, book_value - salvage)
                    book_value -= dep
                    schedule.append({"year": year, "depreciation": round(dep, 2), "accumulated": round(cost - book_value, 2), "book_value": round(book_value, 2)})
            elif method == "double_declining":
                rate = 2 / life
                for year in range(1, life + 1):
                    dep = min(book_value * rate, book_value - salvage)
                    if dep <= 0: dep = 0
                    book_value -= dep
                    schedule.append({"year": year, "depreciation": round(dep, 2), "accumulated": round(cost - book_value, 2), "book_value": round(book_value, 2)})
            result = {"asset": asset_name, "cost": cost, "salvage": salvage, "life_years": life, "method": method, "schedule": schedule}
            if output:
                Path(output).parent.mkdir(parents=True, exist_ok=True)
                Path(output).write_text(json.dumps(result, indent=2))
            return ToolResult(True, f"✓ Depreciation schedule for '{asset_name}' ({method})", result)
        except Exception as e:
            return ToolResult(False, f"✗ Depreciation schedule failed: {e}")

    @staticmethod
    def currency_convert(amount: float, from_currency: str, to_currency: str) -> ToolResult:
        try:
            import requests
            r = requests.get(f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}", timeout=10)
            rates = r.json().get("rates", {})
            rate = rates.get(to_currency.upper(), 0)
            if not rate:
                return ToolResult(False, f"✗ Currency '{to_currency}' not found in exchange rates")
            converted = amount * rate
            return ToolResult(True, f"✓ {amount} {from_currency} = {converted:.4f} {to_currency}", {"from": from_currency, "to": to_currency, "rate": rate, "result": round(converted, 4)})
        except Exception as e:
            return ToolResult(False, f"✗ Currency convert failed: {e}")

    @staticmethod
    def get_exchange_rates(base: str = "USD", currencies: List[str] = None) -> ToolResult:
        try:
            import requests
            r = requests.get(f"https://api.exchangerate-api.com/v4/latest/{base.upper()}", timeout=10)
            all_rates = r.json().get("rates", {})
            if currencies:
                rates = {c: all_rates.get(c.upper(), None) for c in currencies}
            else:
                rates = all_rates
            return ToolResult(True, f"✓ Exchange rates for {base}", rates)
        except Exception as e:
            return ToolResult(False, f"✗ Get exchange rates failed: {e}")

    @staticmethod
    def track_expenses(transactions_csv: str, categories: Dict[str, List[str]] = None, output_folder: str = "") -> ToolResult:
        try:
            import pandas as pd
            df = pd.read_csv(transactions_csv)
            required = ["date", "description", "amount"]
            for col in required:
                if col not in df.columns:
                    return ToolResult(False, f"✗ CSV missing column: {col}")
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
            # Auto-categorise
            if categories:
                def _categorise(desc):
                    desc_lower = str(desc).lower()
                    for cat, keywords in categories.items():
                        if any(kw.lower() in desc_lower for kw in keywords):
                            return cat
                    return "Other"
                df["category"] = df["description"].apply(_categorise)
            summary = df.groupby("category")["amount"].agg(["sum", "count"]).reset_index().rename(columns={"sum": "total", "count": "transactions"}).to_dict("records") if "category" in df.columns else []
            total = float(df["amount"].sum())
            result = {"total_expenses": round(total, 2), "transactions": len(df), "by_category": summary}
            if output_folder:
                Path(output_folder).mkdir(parents=True, exist_ok=True)
                df.to_csv(str(Path(output_folder) / "expenses_categorised.csv"), index=False)
                Path(output_folder, "expense_summary.json").write_text(json.dumps(result, indent=2))
            return ToolResult(True, f"✓ Tracked {len(df)} expenses — Total: {total:.2f}", result)
        except Exception as e:
            return ToolResult(False, f"✗ Track expenses failed: {e}")

    @staticmethod
    def calculate_tax_liability(income: float, deductions: float, country: str = "IN", filing_status: str = "individual") -> ToolResult:
        try:
            taxable = max(0, income - deductions)
            tax = 0.0
            breakdown = []
            if country.upper() == "IN":
                # India new tax regime FY 2024-25
                slabs = [(300000, 0.0), (600000, 0.05), (900000, 0.10), (1200000, 0.15), (1500000, 0.20), (float("inf"), 0.30)]
                prev = 0
                for limit, rate in slabs:
                    if taxable <= prev: break
                    chunk = min(taxable - prev, limit - prev)
                    t = chunk * rate
                    tax += t
                    if t > 0: breakdown.append({"slab": f"Up to {limit}", "rate": f"{int(rate*100)}%", "tax": round(t, 2)})
                    prev = limit
                cess = tax * 0.04
                total_tax = tax + cess
                result = {"country": country, "income": income, "deductions": deductions, "taxable_income": taxable, "income_tax": round(tax, 2), "cess_4%": round(cess, 2), "total_tax": round(total_tax, 2), "effective_rate": round(total_tax / income * 100, 2) if income else 0, "slabs": breakdown}
            elif country.upper() == "US":
                # US 2024 brackets (single)
                brackets = [(11600, 0.10), (47150, 0.12), (100525, 0.22), (191950, 0.24), (243725, 0.32), (609350, 0.35), (float("inf"), 0.37)]
                prev = 0
                for limit, rate in brackets:
                    if taxable <= prev: break
                    chunk = min(taxable - prev, limit - prev)
                    t = chunk * rate
                    tax += t
                    if t > 0: breakdown.append({"bracket": f"Up to {limit}", "rate": f"{int(rate*100)}%", "tax": round(t, 2)})
                    prev = limit
                result = {"country": country, "filing_status": filing_status, "income": income, "deductions": deductions, "taxable_income": taxable, "total_tax": round(tax, 2), "effective_rate": round(tax / income * 100, 2) if income else 0, "brackets": breakdown}
            else:
                tax = taxable * 0.20
                result = {"country": country, "income": income, "taxable_income": taxable, "estimated_tax_20%": round(tax, 2)}
            return ToolResult(True, f"✓ Tax liability for {country}: {round(tax, 2)}", result)
        except Exception as e:
            return ToolResult(False, f"✗ Tax calculation failed: {e}")


# ─────────────────────────────────────────────
# 6. CRMTool
# ─────────────────────────────────────────────

class CRMTool:
    name = "crm"
    description = "Lightweight local CRM (SQLite): contacts, deals, pipeline, activities, reminders, sales reports, conversion rates"

    DB_PATH = str(Path.home() / ".npmai_agent" / "crm.db")

    @staticmethod
    def _db():
        Path(CRMTool.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(CRMTool.DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, email TEXT, phone TEXT, company TEXT,
                tags TEXT, notes TEXT, created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, value REAL, stage TEXT, contact_id INTEGER,
                close_date TEXT, won INTEGER DEFAULT 0, created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER, type TEXT, description TEXT,
                date TEXT, duration_minutes INTEGER, created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER, message TEXT, remind_at TEXT, done INTEGER DEFAULT 0
            );
        """)
        conn.commit()
        return conn

    @staticmethod
    def add_contact(name: str, email: str = "", phone: str = "", company: str = "", tags: str = "", notes: str = "") -> ToolResult:
        try:
            conn = CRMTool._db()
            cur  = conn.cursor()
            cur.execute("INSERT INTO contacts (name,email,phone,company,tags,notes,created_at) VALUES (?,?,?,?,?,?,?)",
                        (name, email, phone, company, tags, notes, datetime.now().isoformat()))
            conn.commit(); cid = cur.lastrowid; conn.close()
            return ToolResult(True, f"✓ Contact #{cid} '{name}' added", {"id": cid})
        except Exception as e:
            return ToolResult(False, f"✗ Add contact failed: {e}")

    @staticmethod
    def update_contact(contact_id: int, data: Dict) -> ToolResult:
        try:
            conn = CRMTool._db()
            sets = ", ".join(f"{k}=?" for k in data.keys())
            conn.execute(f"UPDATE contacts SET {sets} WHERE id=?", list(data.values()) + [contact_id])
            conn.commit(); conn.close()
            return ToolResult(True, f"✓ Contact #{contact_id} updated")
        except Exception as e:
            return ToolResult(False, f"✗ Update contact failed: {e}")

    @staticmethod
    def delete_contact(contact_id: int) -> ToolResult:
        try:
            conn = CRMTool._db()
            conn.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
            conn.commit(); conn.close()
            return ToolResult(True, f"✓ Contact #{contact_id} deleted")
        except Exception as e:
            return ToolResult(False, f"✗ Delete contact failed: {e}")

    @staticmethod
    def list_contacts(filter: str = "", sort: str = "name") -> ToolResult:
        try:
            conn = CRMTool._db()
            if filter:
                rows = conn.execute(f"SELECT * FROM contacts WHERE name LIKE ? OR email LIKE ? OR company LIKE ? ORDER BY {sort}", (f"%{filter}%",) * 3).fetchall()
            else:
                rows = conn.execute(f"SELECT * FROM contacts ORDER BY {sort}").fetchall()
            conn.close()
            data = [dict(r) for r in rows]
            return ToolResult(True, f"✓ {len(data)} contacts", data)
        except Exception as e:
            return ToolResult(False, f"✗ List contacts failed: {e}")

    @staticmethod
    def search_contacts(query: str) -> ToolResult:
        try:
            conn = CRMTool._db()
            q = f"%{query}%"
            rows = conn.execute("SELECT * FROM contacts WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? OR company LIKE ? OR tags LIKE ?", (q, q, q, q, q)).fetchall()
            conn.close()
            data = [dict(r) for r in rows]
            return ToolResult(True, f"✓ {len(data)} matches for '{query}'", data)
        except Exception as e:
            return ToolResult(False, f"✗ Search contacts failed: {e}")

    @staticmethod
    def import_contacts_csv(path: str) -> ToolResult:
        try:
            with open(path, newline="") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    CRMTool.add_contact(
                        name=row.get("name", ""), email=row.get("email", ""),
                        phone=row.get("phone", ""), company=row.get("company", ""),
                        tags=row.get("tags", ""), notes=row.get("notes", "")
                    )
                    count += 1
            return ToolResult(True, f"✓ Imported {count} contacts from {path}")
        except Exception as e:
            return ToolResult(False, f"✗ Import contacts failed: {e}")

    @staticmethod
    def export_contacts(format: str = "csv", filter: str = "", output: str = "contacts_export") -> ToolResult:
        try:
            result = CRMTool.list_contacts(filter=filter)
            if not result.success:
                return result
            data = result.data
            out_path = output if output.endswith(f".{format}") else f"{output}.{format}"
            if format == "csv":
                import csv as csv_mod
                if data:
                    with open(out_path, "w", newline="") as f:
                        writer = csv_mod.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader(); writer.writerows(data)
            elif format == "json":
                Path(out_path).write_text(json.dumps(data, indent=2))
            return ToolResult(True, f"✓ Exported {len(data)} contacts to {out_path}")
        except Exception as e:
            return ToolResult(False, f"✗ Export contacts failed: {e}")

    @staticmethod
    def merge_duplicate_contacts() -> ToolResult:
        try:
            conn = CRMTool._db()
            rows = conn.execute("SELECT email, COUNT(*) as cnt FROM contacts WHERE email != '' GROUP BY email HAVING cnt > 1").fetchall()
            merged = 0
            for row in rows:
                email = row["email"]
                dupes = conn.execute("SELECT id FROM contacts WHERE email=? ORDER BY id", (email,)).fetchall()
                keep_id = dupes[0]["id"]
                remove_ids = [d["id"] for d in dupes[1:]]
                for rid in remove_ids:
                    conn.execute("DELETE FROM contacts WHERE id=?", (rid,))
                    merged += 1
            conn.commit(); conn.close()
            return ToolResult(True, f"✓ Merged {merged} duplicate contacts")
        except Exception as e:
            return ToolResult(False, f"✗ Merge duplicates failed: {e}")

    @staticmethod
    def add_deal(name: str, value: float, stage: str, contact_id: int = 0, close_date: str = "") -> ToolResult:
        try:
            conn = CRMTool._db()
            cur  = conn.cursor()
            cur.execute("INSERT INTO deals (name,value,stage,contact_id,close_date,created_at) VALUES (?,?,?,?,?,?)",
                        (name, value, stage, contact_id, close_date, datetime.now().isoformat()))
            conn.commit(); did = cur.lastrowid; conn.close()
            return ToolResult(True, f"✓ Deal #{did} '{name}' added to '{stage}'", {"id": did})
        except Exception as e:
            return ToolResult(False, f"✗ Add deal failed: {e}")

    @staticmethod
    def update_deal(deal_id: int, data: Dict) -> ToolResult:
        try:
            conn = CRMTool._db()
            sets = ", ".join(f"{k}=?" for k in data.keys())
            conn.execute(f"UPDATE deals SET {sets} WHERE id=?", list(data.values()) + [deal_id])
            conn.commit(); conn.close()
            return ToolResult(True, f"✓ Deal #{deal_id} updated")
        except Exception as e:
            return ToolResult(False, f"✗ Update deal failed: {e}")

    @staticmethod
    def close_deal(deal_id: int, won: bool = True) -> ToolResult:
        try:
            conn = CRMTool._db()
            conn.execute("UPDATE deals SET won=?, stage=? WHERE id=?", (1 if won else 0, "Won" if won else "Lost", deal_id))
            conn.commit(); conn.close()
            return ToolResult(True, f"✓ Deal #{deal_id} marked as {'Won' if won else 'Lost'}")
        except Exception as e:
            return ToolResult(False, f"✗ Close deal failed: {e}")

    @staticmethod
    def list_deals(stage: str = "", owner: str = "", date_range: Tuple = None) -> ToolResult:
        try:
            conn = CRMTool._db()
            q = "SELECT * FROM deals WHERE 1=1"
            params = []
            if stage:
                q += " AND stage=?"; params.append(stage)
            if date_range:
                q += " AND close_date BETWEEN ? AND ?"; params.extend(date_range)
            rows = conn.execute(q, params).fetchall()
            conn.close()
            data = [dict(r) for r in rows]
            return ToolResult(True, f"✓ {len(data)} deals", data)
        except Exception as e:
            return ToolResult(False, f"✗ List deals failed: {e}")

    @staticmethod
    def get_pipeline_value(stage: str = "") -> ToolResult:
        try:
            conn = CRMTool._db()
            if stage:
                rows = conn.execute("SELECT stage, SUM(value) as total, COUNT(*) as count FROM deals WHERE stage=? GROUP BY stage", (stage,)).fetchall()
            else:
                rows = conn.execute("SELECT stage, SUM(value) as total, COUNT(*) as count FROM deals GROUP BY stage").fetchall()
            conn.close()
            data = [dict(r) for r in rows]
            grand_total = sum(r["total"] for r in data if r["total"])
            return ToolResult(True, f"✓ Pipeline value: {grand_total:.2f}", {"pipeline": data, "total": round(grand_total, 2)})
        except Exception as e:
            return ToolResult(False, f"✗ Get pipeline value failed: {e}")

    @staticmethod
    def add_activity(contact_id: int, type: str, description: str, date: str = "", duration: int = 0) -> ToolResult:
        try:
            conn = CRMTool._db()
            conn.execute("INSERT INTO activities (contact_id,type,description,date,duration_minutes,created_at) VALUES (?,?,?,?,?,?)",
                         (contact_id, type, description, date or datetime.now().isoformat(), duration, datetime.now().isoformat()))
            conn.commit(); conn.close()
            return ToolResult(True, f"✓ Activity '{type}' logged for contact #{contact_id}")
        except Exception as e:
            return ToolResult(False, f"✗ Add activity failed: {e}")

    @staticmethod
    def list_activities(contact_id: int = 0, type: str = "", date_range: Tuple = None) -> ToolResult:
        try:
            conn = CRMTool._db()
            q = "SELECT * FROM activities WHERE 1=1"
            params = []
            if contact_id:
                q += " AND contact_id=?"; params.append(contact_id)
            if type:
                q += " AND type=?"; params.append(type)
            rows = conn.execute(q + " ORDER BY date DESC", params).fetchall()
            conn.close()
            data = [dict(r) for r in rows]
            return ToolResult(True, f"✓ {len(data)} activities", data)
        except Exception as e:
            return ToolResult(False, f"✗ List activities failed: {e}")

    @staticmethod
    def set_reminder(contact_id: int, message: str, remind_at: str) -> ToolResult:
        try:
            conn = CRMTool._db()
            conn.execute("INSERT INTO reminders (contact_id,message,remind_at) VALUES (?,?,?)", (contact_id, message, remind_at))
            conn.commit(); conn.close()
            return ToolResult(True, f"✓ Reminder set for {remind_at}")
        except Exception as e:
            return ToolResult(False, f"✗ Set reminder failed: {e}")

    @staticmethod
    def generate_sales_report(period: str = "monthly", breakdown: str = "stage", output: str = "") -> ToolResult:
        try:
            conn = CRMTool._db()
            deals = [dict(r) for r in conn.execute("SELECT * FROM deals").fetchall()]
            contacts = len(conn.execute("SELECT id FROM contacts").fetchall())
            won = [d for d in deals if d["won"] == 1]
            total_revenue = sum(d["value"] for d in won)
            by_stage = {}
            for d in deals:
                s = d["stage"]
                by_stage.setdefault(s, {"count": 0, "value": 0})
                by_stage[s]["count"] += 1
                by_stage[s]["value"] += d["value"]
            report = {
                "period": period, "generated_at": datetime.now().isoformat(),
                "total_contacts": contacts, "total_deals": len(deals),
                "won_deals": len(won), "total_revenue": round(total_revenue, 2),
                "conversion_rate": round(len(won) / len(deals) * 100, 1) if deals else 0,
                "by_stage": by_stage,
            }
            conn.close()
            if output:
                Path(output).parent.mkdir(parents=True, exist_ok=True)
                Path(output).write_text(json.dumps(report, indent=2))
            return ToolResult(True, f"✓ Sales report — Revenue: {total_revenue:.2f} | Deals won: {len(won)}/{len(deals)}", report)
        except Exception as e:
            return ToolResult(False, f"✗ Sales report failed: {e}")

    @staticmethod
    def get_conversion_rate(stage_from: str, stage_to: str, period: str = "") -> ToolResult:
        try:
            conn = CRMTool._db()
            total_from = conn.execute("SELECT COUNT(*) as c FROM deals WHERE stage=?", (stage_from,)).fetchone()["c"]
            total_to   = conn.execute("SELECT COUNT(*) as c FROM deals WHERE stage=?", (stage_to,)).fetchone()["c"]
            conn.close()
            rate = round(total_to / total_from * 100, 2) if total_from else 0
            return ToolResult(True, f"✓ Conversion {stage_from}→{stage_to}: {rate}%", {"from": stage_from, "to": stage_to, "rate_%": rate, "from_count": total_from, "to_count": total_to})
        except Exception as e:
            return ToolResult(False, f"✗ Conversion rate failed: {e}")


# ─────────────────────────────────────────────
# 7. EmailMarketingTool
# ─────────────────────────────────────────────

class EmailMarketingTool:
    name = "email_marketing"
    description = "Mailchimp campaign management: lists, subscribers, campaigns, schedules, automations, templates, stats, unsubscribes"

    @staticmethod
    def _mc(cred_key: str = "mailchimp"):
        import mailchimp_marketing as MailchimpMarketing
        c = CredStore.load(cred_key)
        key    = c.get("api_key", "")
        server = c.get("server_prefix", "us1")
        if not key:
            raise ValueError("CredStore.save('mailchimp', {'api_key': '...', 'server_prefix': 'us1'}).")
        client = MailchimpMarketing.Client()
        client.set_config({"api_key": key, "server": server})
        return client

    @staticmethod
    def create_campaign(name: str, subject: str, from_name: str, from_email: str, content: str, list_id: str, cred_key: str = "mailchimp") -> ToolResult:
        try:
            mc = EmailMarketingTool._mc(cred_key)
            campaign = mc.campaigns.create({
                "type": "regular",
                "recipients": {"list_id": list_id},
                "settings": {"subject_line": subject, "from_name": from_name, "reply_to": from_email, "title": name},
            })
            cid = campaign["id"]
            mc.campaigns.set_content(cid, {"html": content})
            return ToolResult(True, f"✓ Campaign '{name}' created (ID: {cid})", {"id": cid})
        except Exception as e:
            return ToolResult(False, f"✗ Create campaign failed: {e}")

    @staticmethod
    def schedule_campaign(campaign_id: str, send_time: str, cred_key: str = "mailchimp") -> ToolResult:
        try:
            mc = EmailMarketingTool._mc(cred_key)
            mc.campaigns.schedule(campaign_id, {"schedule_time": send_time})
            return ToolResult(True, f"✓ Campaign {campaign_id} scheduled for {send_time}")
        except Exception as e:
            return ToolResult(False, f"✗ Schedule campaign failed: {e}")

    @staticmethod
    def send_campaign_now(campaign_id: str, cred_key: str = "mailchimp") -> ToolResult:
        try:
            mc = EmailMarketingTool._mc(cred_key)
            mc.campaigns.send(campaign_id)
            return ToolResult(True, f"✓ Campaign {campaign_id} sent!")
        except Exception as e:
            return ToolResult(False, f"✗ Send campaign failed: {e}")

    @staticmethod
    def create_list(name: str, from_name: str = "NPM Agent", from_email: str = "", cred_key: str = "mailchimp") -> ToolResult:
        try:
            mc = EmailMarketingTool._mc(cred_key)
            lst = mc.lists.create_list({
                "name": name,
                "contact": {"company": "NPM Agent", "address1": "", "city": "", "country": "IN"},
                "permission_reminder": "You signed up for our newsletter.",
                "campaign_defaults": {"from_name": from_name, "from_email": from_email or "noreply@example.com", "subject": "", "language": "en"},
                "email_type_option": False,
            })
            return ToolResult(True, f"✓ List '{name}' created (ID: {lst['id']})", {"id": lst["id"]})
        except Exception as e:
            return ToolResult(False, f"✗ Create list failed: {e}")

    @staticmethod
    def add_subscriber(list_id: str, email: str, name: str = "", custom_fields: Dict = None, cred_key: str = "mailchimp") -> ToolResult:
        try:
            mc = EmailMarketingTool._mc(cred_key)
            parts = name.split(" ", 1)
            merge_fields: Dict[str, Any] = {"FNAME": parts[0], "LNAME": parts[1] if len(parts) > 1 else ""}
            if custom_fields:
                merge_fields.update(custom_fields)
            mc.lists.add_list_member(list_id, {"email_address": email, "status": "subscribed", "merge_fields": merge_fields})
            return ToolResult(True, f"✓ Subscriber {email} added to list {list_id}")
        except Exception as e:
            return ToolResult(False, f"✗ Add subscriber failed: {e}")

    @staticmethod
    def remove_subscriber(list_id: str, email: str, cred_key: str = "mailchimp") -> ToolResult:
        try:
            import hashlib
            mc = EmailMarketingTool._mc(cred_key)
            subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
            mc.lists.update_list_member(list_id, subscriber_hash, {"status": "unsubscribed"})
            return ToolResult(True, f"✓ {email} unsubscribed from list {list_id}")
        except Exception as e:
            return ToolResult(False, f"✗ Remove subscriber failed: {e}")

    @staticmethod
    def import_subscribers(list_id: str, csv_path: str, cred_key: str = "mailchimp") -> ToolResult:
        try:
            mc = EmailMarketingTool._mc(cred_key)
            members = []
            with open(csv_path, newline="") as f:
                for row in csv.DictReader(f):
                    members.append({"email_address": row.get("email", ""), "status": "subscribed", "merge_fields": {"FNAME": row.get("first_name", row.get("name", "")), "LNAME": row.get("last_name", "")}})
            result = mc.lists.batch_list_members(list_id, {"members": members, "update_existing": True})
            added = result.get("total_created", 0)
            updated = result.get("total_updated", 0)
            return ToolResult(True, f"✓ Imported: {added} new, {updated} updated", result)
        except Exception as e:
            return ToolResult(False, f"✗ Import subscribers failed: {e}")

    @staticmethod
    def get_campaign_stats(campaign_id: str, cred_key: str = "mailchimp") -> ToolResult:
        try:
            mc = EmailMarketingTool._mc(cred_key)
            report = mc.reports.get_campaign_report(campaign_id)
            stats = {
                "emails_sent": report.get("emails_sent", 0),
                "opens": report.get("opens", {}).get("opens_total", 0),
                "unique_opens": report.get("opens", {}).get("unique_opens", 0),
                "open_rate": report.get("opens", {}).get("open_rate", 0),
                "clicks": report.get("clicks", {}).get("clicks_total", 0),
                "click_rate": report.get("clicks", {}).get("click_rate", 0),
                "unsubscribes": report.get("unsubscribes", 0),
                "bounces": report.get("bounces", {}).get("hard_bounces", 0) + report.get("bounces", {}).get("soft_bounces", 0),
            }
            return ToolResult(True, f"✓ Campaign stats for {campaign_id}", stats)
        except Exception as e:
            return ToolResult(False, f"✗ Get campaign stats failed: {e}")

    @staticmethod
    def get_list_stats(list_id: str, cred_key: str = "mailchimp") -> ToolResult:
        try:
            mc = EmailMarketingTool._mc(cred_key)
            lst = mc.lists.get_list(list_id)
            stats = lst.get("stats", {})
            return ToolResult(True, f"✓ List stats for {list_id}", stats)
        except Exception as e:
            return ToolResult(False, f"✗ Get list stats failed: {e}")

    @staticmethod
    def create_automation(name: str, trigger: str, actions: List[Dict], cred_key: str = "mailchimp") -> ToolResult:
        try:
            mc = EmailMarketingTool._mc(cred_key)
            automation = mc.automations.create({
                "recipients": {"list_id": actions[0].get("list_id", "") if actions else ""},
                "trigger_settings": {"workflow_type": trigger},
                "settings": {"title": name},
            })
            return ToolResult(True, f"✓ Automation '{name}' created (ID: {automation.get('id')})", {"id": automation.get("id")})
        except Exception as e:
            return ToolResult(False, f"✗ Create automation failed: {e}")

    @staticmethod
    def create_template(name: str, html: str, text: str = "", cred_key: str = "mailchimp") -> ToolResult:
        try:
            mc = EmailMarketingTool._mc(cred_key)
            tpl = mc.templates.create({"name": name, "html": html})
            return ToolResult(True, f"✓ Template '{name}' created (ID: {tpl.get('id')})", {"id": tpl.get("id")})
        except Exception as e:
            return ToolResult(False, f"✗ Create template failed: {e}")

    @staticmethod
    def unsubscribe(email: str, reason: str = "", cred_key: str = "mailchimp") -> ToolResult:
        try:
            import hashlib
            mc = EmailMarketingTool._mc(cred_key)
            lists = mc.lists.get_all_lists()
            count = 0
            for lst in lists.get("lists", []):
                try:
                    subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
                    mc.lists.update_list_member(lst["id"], subscriber_hash, {"status": "unsubscribed"})
                    count += 1
                except Exception:
                    pass
            return ToolResult(True, f"✓ {email} unsubscribed from {count} lists")
        except Exception as e:
            return ToolResult(False, f"✗ Unsubscribe failed: {e}")

    @staticmethod
    def get_unsubscribes(list_id: str, date_range: Tuple = None, cred_key: str = "mailchimp") -> ToolResult:
        try:
            mc = EmailMarketingTool._mc(cred_key)
            params: Dict[str, Any] = {"status": "unsubscribed"}
            members = mc.lists.get_list_members_info(list_id, **params)
            data = [{"email": m["email_address"], "name": m.get("full_name", ""), "unsubscribed_at": m.get("timestamp_opt", "")} for m in members.get("members", [])]
            return ToolResult(True, f"✓ {len(data)} unsubscribes", data)
        except Exception as e:
            return ToolResult(False, f"✗ Get unsubscribes failed: {e}")


# ─────────────────────────────────────────────
# 8. AnalyticsTool
# ─────────────────────────────────────────────

class AnalyticsTool:
    name = "analytics"
    description = "Google Analytics 4 reporting: sessions, top pages, traffic sources, conversions, realtime users, custom reports, weekly summaries"

    @staticmethod
    def _ga_client(credentials_path: str = "", cred_key: str = "google_analytics"):
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.oauth2 import service_account
        if credentials_path and Path(credentials_path).exists():
            creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/analytics.readonly"])
        else:
            creds_data = CredStore.load(cred_key)
            if not creds_data:
                raise ValueError("No Google Analytics credentials. CredStore.save('google_analytics', {...service_account_json...}).")
            creds = service_account.Credentials.from_service_account_info(creds_data, scopes=["https://www.googleapis.com/auth/analytics.readonly"])
        return BetaAnalyticsDataClient(credentials=creds)

    @staticmethod
    def connect_google_analytics(credentials: str, cred_key: str = "google_analytics") -> ToolResult:
        try:
            if Path(credentials).exists():
                data = json.loads(Path(credentials).read_text())
                CredStore.save(cred_key, data)
                return ToolResult(True, f"✓ Google Analytics credentials saved from {credentials}")
            return ToolResult(False, f"✗ Credentials file not found: {credentials}")
        except Exception as e:
            return ToolResult(False, f"✗ Connect GA failed: {e}")

    @staticmethod
    def get_sessions(property_id: str, start_date: str, end_date: str, dimensions: List[str] = None, cred_key: str = "google_analytics") -> ToolResult:
        try:
            from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
            client = AnalyticsTool._ga_client(cred_key=cred_key)
            dims = [Dimension(name=d) for d in (dimensions or ["date"])]
            request = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                metrics=[Metric(name="sessions"), Metric(name="users")],
                dimensions=dims,
            )
            response = client.run_report(request)
            rows = []
            for row in response.rows:
                r = {d.name: row.dimension_values[i].value for i, d in enumerate(dims)}
                r["sessions"] = row.metric_values[0].value
                r["users"]    = row.metric_values[1].value
                rows.append(r)
            return ToolResult(True, f"✓ {len(rows)} session rows", rows)
        except Exception as e:
            return ToolResult(False, f"✗ Get sessions failed: {e}")

    @staticmethod
    def get_top_pages(property_id: str, start_date: str, end_date: str, limit: int = 10, cred_key: str = "google_analytics") -> ToolResult:
        try:
            from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
            client = AnalyticsTool._ga_client(cred_key=cred_key)
            request = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                metrics=[Metric(name="screenPageViews"), Metric(name="sessions")],
                dimensions=[Dimension(name="pagePath")],
                limit=limit,
            )
            response = client.run_report(request)
            rows = [{"page": r.dimension_values[0].value, "views": r.metric_values[0].value, "sessions": r.metric_values[1].value} for r in response.rows]
            return ToolResult(True, f"✓ Top {len(rows)} pages", rows)
        except Exception as e:
            return ToolResult(False, f"✗ Get top pages failed: {e}")

    @staticmethod
    def get_traffic_sources(property_id: str, start_date: str, end_date: str, cred_key: str = "google_analytics") -> ToolResult:
        try:
            from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
            client = AnalyticsTool._ga_client(cred_key=cred_key)
            request = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                metrics=[Metric(name="sessions"), Metric(name="users")],
                dimensions=[Dimension(name="sessionSource"), Dimension(name="sessionMedium")],
            )
            response = client.run_report(request)
            rows = [{"source": r.dimension_values[0].value, "medium": r.dimension_values[1].value, "sessions": r.metric_values[0].value, "users": r.metric_values[1].value} for r in response.rows]
            return ToolResult(True, f"✓ {len(rows)} traffic sources", rows)
        except Exception as e:
            return ToolResult(False, f"✗ Get traffic sources failed: {e}")

    @staticmethod
    def get_conversions(property_id: str, goal_id: str, start_date: str, end_date: str, cred_key: str = "google_analytics") -> ToolResult:
        try:
            from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
            client = AnalyticsTool._ga_client(cred_key=cred_key)
            request = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                metrics=[Metric(name="conversions"), Metric(name="eventCount")],
                dimensions=[Dimension(name="eventName")],
                dimension_filter={"filter": {"field_name": "eventName", "string_filter": {"value": goal_id}}},
            )
            response = client.run_report(request)
            rows = [{"event": r.dimension_values[0].value, "conversions": r.metric_values[0].value, "event_count": r.metric_values[1].value} for r in response.rows]
            return ToolResult(True, f"✓ Conversions for '{goal_id}'", rows)
        except Exception as e:
            return ToolResult(False, f"✗ Get conversions failed: {e}")

    @staticmethod
    def get_realtime_users(property_id: str, cred_key: str = "google_analytics") -> ToolResult:
        try:
            from google.analytics.data_v1beta.types import RunRealtimeReportRequest, Metric
            client = AnalyticsTool._ga_client(cred_key=cred_key)
            request = RunRealtimeReportRequest(property=f"properties/{property_id}", metrics=[Metric(name="activeUsers")])
            response = client.run_realtime_report(request)
            users = response.rows[0].metric_values[0].value if response.rows else "0"
            return ToolResult(True, f"✓ {users} active users right now", {"active_users": users})
        except Exception as e:
            return ToolResult(False, f"✗ Get realtime users failed: {e}")

    @staticmethod
    def create_custom_report(property_id: str, metrics: List[str], dimensions: List[str], filters: Dict = None, start_date: str = "30daysAgo", end_date: str = "today", output: str = "", cred_key: str = "google_analytics") -> ToolResult:
        try:
            from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
            client = AnalyticsTool._ga_client(cred_key=cred_key)
            request = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                metrics=[Metric(name=m) for m in metrics],
                dimensions=[Dimension(name=d) for d in dimensions],
            )
            response = client.run_report(request)
            rows = []
            for row in response.rows:
                r = {dimensions[i]: row.dimension_values[i].value for i in range(len(dimensions))}
                for j, m in enumerate(metrics):
                    r[m] = row.metric_values[j].value
                rows.append(r)
            if output:
                Path(output).write_text(json.dumps(rows, indent=2))
            return ToolResult(True, f"✓ Custom report: {len(rows)} rows", rows)
        except Exception as e:
            return ToolResult(False, f"✗ Custom report failed: {e}")

    @staticmethod
    def generate_weekly_report(property_id: str, output: str = "weekly_analytics.json", cred_key: str = "google_analytics") -> ToolResult:
        try:
            end = datetime.now().strftime("%Y-%m-%d")
            start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            sessions = AnalyticsTool.get_sessions(property_id, start, end, cred_key=cred_key)
            pages    = AnalyticsTool.get_top_pages(property_id, start, end, limit=5, cred_key=cred_key)
            sources  = AnalyticsTool.get_traffic_sources(property_id, start, end, cred_key=cred_key)
            report   = {"period": f"{start} to {end}", "sessions": sessions.data, "top_pages": pages.data, "traffic_sources": sources.data, "generated_at": datetime.now().isoformat()}
            Path(output).write_text(json.dumps(report, indent=2))
            return ToolResult(True, f"✓ Weekly report saved to {output}", report)
        except Exception as e:
            return ToolResult(False, f"✗ Weekly report failed: {e}")

    @staticmethod
    def track_event(category: str, action: str, label: str = "", value: int = 0, measurement_id: str = "", api_secret: str = "", cred_key: str = "google_analytics") -> ToolResult:
        try:
            import requests
            c = CredStore.load(cred_key)
            mid = measurement_id or c.get("measurement_id", "")
            sec = api_secret or c.get("api_secret", "")
            if not mid or not sec:
                return ToolResult(False, "✗ measurement_id and api_secret required.")
            payload = {"client_id": "npmai-agent", "events": [{"name": action, "params": {"event_category": category, "event_label": label, "value": value}}]}
            r = requests.post(f"https://www.google-analytics.com/mp/collect?measurement_id={mid}&api_secret={sec}", json=payload, timeout=10)
            return ToolResult(r.ok, f"✓ Event tracked: {category}/{action}" if r.ok else f"✗ Track event failed: {r.status_code}")
        except Exception as e:
            return ToolResult(False, f"✗ Track event failed: {e}")


# ─────────────────────────────────────────────
# 9. InventoryTool
# ─────────────────────────────────────────────

class InventoryTool:
    name = "inventory"
    description = "Stock and inventory management via SQLite: add/update products, record sales/purchases, low stock alerts, demand forecasting, reports"

    DB_PATH = str(Path.home() / ".npmai_agent" / "inventory.db")

    @staticmethod
    def _db():
        Path(InventoryTool.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(InventoryTool.DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS products (
                sku TEXT PRIMARY KEY, name TEXT, quantity INTEGER DEFAULT 0,
                cost_price REAL, sell_price REAL, location TEXT,
                reorder_point INTEGER DEFAULT 10, created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, sku TEXT, type TEXT,
                quantity INTEGER, price REAL, party TEXT, note TEXT, date TEXT
            );
        """)
        conn.commit()
        return conn

    @staticmethod
    def add_product(sku: str, name: str, quantity: int, cost_price: float, sell_price: float, location: str = "", reorder_point: int = 10) -> ToolResult:
        try:
            conn = InventoryTool._db()
            conn.execute("INSERT OR REPLACE INTO products VALUES (?,?,?,?,?,?,?,?)",
                         (sku, name, quantity, cost_price, sell_price, location, reorder_point, datetime.now().isoformat()))
            conn.commit(); conn.close()
            return ToolResult(True, f"✓ Product '{sku}' added/updated")
        except Exception as e:
            return ToolResult(False, f"✗ Add product failed: {e}")

    @staticmethod
    def update_stock(sku: str, quantity_change: int, reason: str = "") -> ToolResult:
        try:
            conn = InventoryTool._db()
            cur  = conn.execute("SELECT quantity FROM products WHERE sku=?", (sku,)).fetchone()
            if not cur:
                return ToolResult(False, f"✗ SKU '{sku}' not found")
            new_qty = cur["quantity"] + quantity_change
            conn.execute("UPDATE products SET quantity=? WHERE sku=?", (new_qty, sku))
            conn.execute("INSERT INTO transactions (sku,type,quantity,price,note,date) VALUES (?,?,?,?,?,?)",
                         (sku, "adjustment", quantity_change, 0, reason, datetime.now().isoformat()))
            conn.commit(); conn.close()
            return ToolResult(True, f"✓ Stock for '{sku}' updated: {cur['quantity']} → {new_qty}")
        except Exception as e:
            return ToolResult(False, f"✗ Update stock failed: {e}")

    @staticmethod
    def get_stock_level(sku: str) -> ToolResult:
        try:
            conn = InventoryTool._db()
            row  = conn.execute("SELECT * FROM products WHERE sku=?", (sku,)).fetchone()
            conn.close()
            if not row:
                return ToolResult(False, f"✗ SKU '{sku}' not found")
            data = dict(row)
            below_reorder = data["quantity"] <= data["reorder_point"]
            return ToolResult(True, f"✓ {sku}: {data['quantity']} units{' ⚠ LOW STOCK' if below_reorder else ''}", data)
        except Exception as e:
            return ToolResult(False, f"✗ Get stock level failed: {e}")

    @staticmethod
    def list_low_stock(threshold: int = 0) -> ToolResult:
        try:
            conn = InventoryTool._db()
            if threshold:
                rows = conn.execute("SELECT * FROM products WHERE quantity <= ?", (threshold,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM products WHERE quantity <= reorder_point").fetchall()
            conn.close()
            data = [dict(r) for r in rows]
            return ToolResult(True, f"✓ {len(data)} low-stock items", data)
        except Exception as e:
            return ToolResult(False, f"✗ List low stock failed: {e}")

    @staticmethod
    def list_out_of_stock() -> ToolResult:
        try:
            conn = InventoryTool._db()
            rows = conn.execute("SELECT * FROM products WHERE quantity <= 0").fetchall()
            conn.close()
            data = [dict(r) for r in rows]
            return ToolResult(True, f"✓ {len(data)} out-of-stock items", data)
        except Exception as e:
            return ToolResult(False, f"✗ List out of stock failed: {e}")

    @staticmethod
    def get_inventory_value() -> ToolResult:
        try:
            conn = InventoryTool._db()
            rows = conn.execute("SELECT sku, name, quantity, cost_price, sell_price FROM products").fetchall()
            conn.close()
            total_cost  = sum(r["quantity"] * r["cost_price"] for r in rows if r["cost_price"])
            total_retail = sum(r["quantity"] * r["sell_price"] for r in rows if r["sell_price"])
            return ToolResult(True, f"✓ Inventory value — Cost: {total_cost:.2f} | Retail: {total_retail:.2f}", {"cost_value": round(total_cost, 2), "retail_value": round(total_retail, 2), "items": len(rows)})
        except Exception as e:
            return ToolResult(False, f"✗ Get inventory value failed: {e}")

    @staticmethod
    def record_sale(sku: str, quantity: int, price: float, customer: str = "") -> ToolResult:
        try:
            conn = InventoryTool._db()
            row  = conn.execute("SELECT quantity FROM products WHERE sku=?", (sku,)).fetchone()
            if not row:
                return ToolResult(False, f"✗ SKU '{sku}' not found")
            if row["quantity"] < quantity:
                return ToolResult(False, f"✗ Insufficient stock: {row['quantity']} available, {quantity} requested")
            new_qty = row["quantity"] - quantity
            conn.execute("UPDATE products SET quantity=? WHERE sku=?", (new_qty, sku))
            conn.execute("INSERT INTO transactions (sku,type,quantity,price,party,date) VALUES (?,?,?,?,?,?)",
                         (sku, "sale", quantity, price, customer, datetime.now().isoformat()))
            conn.commit(); conn.close()
            return ToolResult(True, f"✓ Sale recorded: {quantity}x {sku} @ {price} | Remaining: {new_qty}")
        except Exception as e:
            return ToolResult(False, f"✗ Record sale failed: {e}")

    @staticmethod
    def record_purchase(sku: str, quantity: int, cost: float, supplier: str = "") -> ToolResult:
        try:
            conn = InventoryTool._db()
            row  = conn.execute("SELECT quantity FROM products WHERE sku=?", (sku,)).fetchone()
            if not row:
                return ToolResult(False, f"✗ SKU '{sku}' not found. Add product first.")
            new_qty = row["quantity"] + quantity
            conn.execute("UPDATE products SET quantity=?, cost_price=? WHERE sku=?", (new_qty, cost, sku))
            conn.execute("INSERT INTO transactions (sku,type,quantity,price,party,date) VALUES (?,?,?,?,?,?)",
                         (sku, "purchase", quantity, cost, supplier, datetime.now().isoformat()))
            conn.commit(); conn.close()
            return ToolResult(True, f"✓ Purchase recorded: {quantity}x {sku} @ {cost} | New stock: {new_qty}")
        except Exception as e:
            return ToolResult(False, f"✗ Record purchase failed: {e}")

    @staticmethod
    def generate_stock_report(output: str = "") -> ToolResult:
        try:
            conn = InventoryTool._db()
            products = [dict(r) for r in conn.execute("SELECT * FROM products ORDER BY quantity ASC").fetchall()]
            txns = conn.execute("SELECT type, SUM(quantity) as qty, SUM(price*quantity) as revenue FROM transactions GROUP BY type").fetchall()
            conn.close()
            summary = {"products": len(products), "total_items": sum(p["quantity"] for p in products), "low_stock": sum(1 for p in products if p["quantity"] <= p["reorder_point"]), "out_of_stock": sum(1 for p in products if p["quantity"] <= 0), "transactions": {r["type"]: {"qty": r["qty"], "value": round(r["revenue"] or 0, 2)} for r in txns}}
            report = {"summary": summary, "products": products, "generated_at": datetime.now().isoformat()}
            if output:
                Path(output).parent.mkdir(parents=True, exist_ok=True)
                Path(output).write_text(json.dumps(report, indent=2))
            return ToolResult(True, f"✓ Stock report — {summary['products']} products, {summary['out_of_stock']} OOS", report)
        except Exception as e:
            return ToolResult(False, f"✗ Generate stock report failed: {e}")

    @staticmethod
    def forecast_demand(sku: str, days_ahead: int = 30) -> ToolResult:
        try:
            conn = InventoryTool._db()
            rows = conn.execute("SELECT date, quantity FROM transactions WHERE sku=? AND type='sale' ORDER BY date", (sku,)).fetchall()
            conn.close()
            if len(rows) < 2:
                return ToolResult(False, f"✗ Insufficient sales data for '{sku}' (need at least 2 transactions)")
            sales = [r["quantity"] for r in rows]
            avg_daily_sales = sum(sales) / max(len(rows), 1)
            forecast = round(avg_daily_sales * days_ahead)
            current = InventoryTool.get_stock_level(sku)
            current_stock = current.data.get("quantity", 0) if current.success else 0
            stockout_days = round(current_stock / avg_daily_sales) if avg_daily_sales > 0 else 999
            reorder_needed = current_stock < forecast
            result = {"sku": sku, "avg_daily_sales": round(avg_daily_sales, 2), "forecast_demand": forecast, "days_ahead": days_ahead, "current_stock": current_stock, "stockout_in_days": stockout_days, "reorder_recommended": reorder_needed, "suggested_order_qty": max(0, forecast - current_stock)}
            return ToolResult(True, f"✓ Demand forecast for '{sku}': {forecast} units in {days_ahead} days", result)
        except Exception as e:
            return ToolResult(False, f"✗ Forecast demand failed: {e}")

    @staticmethod
    def export_inventory(format: str = "csv", output: str = "inventory_export") -> ToolResult:
        try:
            conn = InventoryTool._db()
            rows = [dict(r) for r in conn.execute("SELECT * FROM products").fetchall()]
            conn.close()
            out_path = output if output.endswith(f".{format}") else f"{output}.{format}"
            if format == "csv":
                if rows:
                    with open(out_path, "w", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                        writer.writeheader(); writer.writerows(rows)
            elif format == "json":
                Path(out_path).write_text(json.dumps(rows, indent=2))
            return ToolResult(True, f"✓ Inventory exported to {out_path} ({len(rows)} products)")
        except Exception as e:
            return ToolResult(False, f"✗ Export inventory failed: {e}")

    @staticmethod
    def import_inventory(csv_path: str) -> ToolResult:
        try:
            with open(csv_path, newline="") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    InventoryTool.add_product(
                        sku=row.get("sku", ""), name=row.get("name", ""),
                        quantity=int(row.get("quantity", 0)),
                        cost_price=float(row.get("cost_price", 0)),
                        sell_price=float(row.get("sell_price", 0)),
                        location=row.get("location", ""),
                        reorder_point=int(row.get("reorder_point", 10)),
                    )
                    count += 1
            return ToolResult(True, f"✓ Imported {count} products from {csv_path}")
        except Exception as e:
            return ToolResult(False, f"✗ Import inventory failed: {e}")


# ─────────────────────────────────────────────
# 10. ContractTool
# ─────────────────────────────────────────────

class ContractTool:
    name = "contract"
    description = "Contract and legal document automation: NDA, service agreements, employment contracts, template filling, AI extraction, comparison"

    @staticmethod
    def _pdf_header(c_obj, title: str, subtitle: str, W: float, H: float):
        from reportlab.lib import colors
        c_obj.setFillColor(colors.HexColor("#1a1a2e"))
        c_obj.rect(0, H - 90, W, 90, fill=1, stroke=0)
        c_obj.setFillColor(colors.white)
        c_obj.setFont("Helvetica-Bold", 20)
        c_obj.drawCentredString(W / 2, H - 45, title)
        c_obj.setFont("Helvetica", 11)
        c_obj.drawCentredString(W / 2, H - 65, subtitle)
        c_obj.setFillColor(colors.black)

    @staticmethod
    def _write_text_block(c_obj, text: str, x: float, y: float, W: float, font: str = "Helvetica", size: int = 10, max_width: float = 500) -> float:
        from reportlab.lib.utils import simpleSplit
        c_obj.setFont(font, size)
        for line in text.split("\n"):
            parts = simpleSplit(line, font, size, max_width)
            for part in parts:
                if y < 60:
                    c_obj.showPage()
                    y = W - 80
                    c_obj.setFont(font, size)
                c_obj.drawString(x, y, part)
                y -= size + 4
        return y

    @staticmethod
    def create_nda(parties: Dict, effective_date: str, duration: str = "2 years", jurisdiction: str = "India", output: str = "nda.pdf") -> ToolResult:
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            W, H = A4
            c = canvas.Canvas(output, pagesize=A4)
            ContractTool._pdf_header(c, "NON-DISCLOSURE AGREEMENT", f"Effective Date: {effective_date}", W, H)
            y = H - 110
            party_a = parties.get("party_a", {})
            party_b = parties.get("party_b", {})
            body = f"""
PARTIES
This Non-Disclosure Agreement ("Agreement") is entered into as of {effective_date}, between:

  Party A: {party_a.get('name', '')} ("Disclosing Party")
  Address: {party_a.get('address', '')}
  
  Party B: {party_b.get('name', '')} ("Receiving Party")
  Address: {party_b.get('address', '')}

1. DEFINITION OF CONFIDENTIAL INFORMATION
   "Confidential Information" means any information disclosed by the Disclosing Party to the Receiving Party, directly or indirectly, in writing, orally, or by inspection of tangible objects.

2. OBLIGATIONS OF RECEIVING PARTY
   The Receiving Party agrees to: (a) keep the Confidential Information strictly confidential; (b) not disclose the Confidential Information to any third parties without prior written consent; (c) use the Confidential Information solely for the purpose of evaluating the business relationship between the parties.

3. EXCLUSIONS
   This Agreement does not apply to information that: (a) is or becomes publicly known; (b) was rightfully known to the Receiving Party prior to disclosure; (c) is required to be disclosed by law or court order.

4. TERM
   This Agreement shall remain in effect for {duration} from the effective date, unless terminated earlier by mutual written agreement.

5. JURISDICTION
   This Agreement shall be governed by the laws of {jurisdiction}.

6. REMEDIES
   The parties agree that monetary damages may be inadequate and that injunctive relief may be appropriate to prevent breach of this Agreement.

SIGNATURES

Party A: ________________________________  Date: __________
  {party_a.get('name', '')}

Party B: ________________________________  Date: __________
  {party_b.get('name', '')}
"""
            ContractTool._write_text_block(c, body.strip(), 50, y, W, size=9)
            c.save()
            return ToolResult(True, f"✓ NDA created: {output}")
        except Exception as e:
            return ToolResult(False, f"✗ Create NDA failed: {e}")

    @staticmethod
    def create_service_agreement(provider: Dict, client: Dict, services: str, payment: Dict, output: str = "service_agreement.pdf") -> ToolResult:
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            W, H = A4
            c = canvas.Canvas(output, pagesize=A4)
            today = datetime.now().strftime("%Y-%m-%d")
            ContractTool._pdf_header(c, "SERVICE AGREEMENT", f"Date: {today}", W, H)
            y = H - 110
            body = f"""
SERVICE AGREEMENT

This Service Agreement is entered into as of {today}, between:

  Service Provider: {provider.get('name', '')} | {provider.get('email', '')}
  Client:           {client.get('name', '')}   | {client.get('email', '')}

1. SERVICES
   Provider agrees to perform the following services:
   {services}

2. PAYMENT TERMS
   Amount:       {payment.get('amount', '')} {payment.get('currency', 'INR')}
   Payment Due:  {payment.get('due', 'Upon completion')}
   Late Fee:     {payment.get('late_fee', '2% per month')}

3. INTELLECTUAL PROPERTY
   All work product created by Provider under this Agreement shall, upon full payment, be the sole property of Client.

4. CONFIDENTIALITY
   Both parties agree to maintain the confidentiality of each other's proprietary information.

5. TERMINATION
   Either party may terminate this agreement with {payment.get('notice_days', '14')} days written notice.

6. LIMITATION OF LIABILITY
   Provider's liability is limited to the total fees paid under this agreement.

7. GOVERNING LAW
   This agreement is governed by Indian law and disputes shall be resolved in {provider.get('city', 'the jurisdiction of Provider')}.

SIGNATURES

Provider: ________________________________  Date: __________
  {provider.get('name', '')}

Client:   ________________________________  Date: __________
  {client.get('name', '')}
"""
            ContractTool._write_text_block(c, body.strip(), 50, y, W, size=9)
            c.save()
            return ToolResult(True, f"✓ Service agreement created: {output}")
        except Exception as e:
            return ToolResult(False, f"✗ Create service agreement failed: {e}")

    @staticmethod
    def create_employment_contract(employer: Dict, employee: Dict, role: str, salary: Dict, start_date: str, output: str = "employment_contract.pdf") -> ToolResult:
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            W, H = A4
            c = canvas.Canvas(output, pagesize=A4)
            ContractTool._pdf_header(c, "EMPLOYMENT CONTRACT", f"Start Date: {start_date}", W, H)
            y = H - 110
            body = f"""
EMPLOYMENT CONTRACT

This Employment Contract is made between:

  Employer: {employer.get('name', '')} | {employer.get('address', '')}
  Employee: {employee.get('name', '')} | {employee.get('address', '')}

1. POSITION AND DUTIES
   Employee is hired as: {role}
   Start Date: {start_date}
   Employment Type: {salary.get('type', 'Full-time')}

2. COMPENSATION
   Basic Salary: {salary.get('currency', '₹')}{salary.get('amount', '')} per {salary.get('period', 'month')}
   Benefits: {salary.get('benefits', 'As per company policy')}
   Probation Period: {salary.get('probation', '3 months')}

3. WORKING HOURS
   Standard working hours: {employer.get('hours', '9am–6pm, Monday to Friday')}
   Location: {employer.get('location', 'Office or remote as agreed')}

4. LEAVE ENTITLEMENT
   Annual Leave: 15 days
   Sick Leave: 10 days
   Public Holidays: As per national calendar

5. CONFIDENTIALITY AND NON-COMPETE
   Employee agrees to keep company information confidential during and after employment.
   Non-compete period: {salary.get('non_compete', '6 months')} after termination.

6. TERMINATION
   Notice period: {salary.get('notice_period', '30 days')} by either party.
   Grounds for immediate termination: gross misconduct, breach of confidentiality.

7. GOVERNING LAW
   This contract is governed by the laws of India.

SIGNATURES

Employer: ________________________________  Date: __________
  {employer.get('name', '')}

Employee: ________________________________  Date: __________
  {employee.get('name', '')}
"""
            ContractTool._write_text_block(c, body.strip(), 50, y, W, size=9)
            c.save()
            return ToolResult(True, f"✓ Employment contract created: {output}")
        except Exception as e:
            return ToolResult(False, f"✗ Create employment contract failed: {e}")

    @staticmethod
    def fill_template(template_path: str, data_dict: Dict, output: str) -> ToolResult:
        try:
            content = Path(template_path).read_text()
            for key, value in data_dict.items():
                content = content.replace(f"{{{{{key}}}}}", str(value))
                content = content.replace(f"[{key}]", str(value))
                content = content.replace(f"<<{key}>>", str(value))
            if output.endswith(".pdf"):
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import A4
                W, H = A4
                c = canvas.Canvas(output, pagesize=A4)
                y = H - 50
                for line in content.splitlines():
                    if y < 50:
                        c.showPage(); y = H - 50
                    c.setFont("Helvetica", 10)
                    c.drawString(50, y, line)
                    y -= 14
                c.save()
            elif output.endswith(".docx"):
                from docx import Document
                doc = Document()
                for line in content.splitlines():
                    doc.add_paragraph(line)
                doc.save(output)
            else:
                Path(output).write_text(content)
            return ToolResult(True, f"✓ Template filled and saved to {output}")
        except Exception as e:
            return ToolResult(False, f"✗ Fill template failed: {e}")

    @staticmethod
    def extract_key_terms(contract_pdf: str, model: str = "llama3.2:3b") -> ToolResult:
        try:
            from pypdf import PdfReader
            text = "\n".join(p.extract_text() or "" for p in PdfReader(contract_pdf).pages)
            try:
                from npmai import Ollama
                llm = Ollama(model=model, temperature=0.1, change=True, Models=["mistral:7b"])
                prompt = f"""Extract key terms from this contract. Return JSON with:
parties, effective_date, duration, payment_terms, termination_clause, jurisdiction, key_obligations, penalties

Contract:
{text[:4000]}

JSON only:"""
                raw = llm.invoke(prompt)
                import re
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                data = json.loads(match.group()) if match else {"text_preview": text[:500]}
            except Exception:
                data = {"text_preview": text[:500]}
            return ToolResult(True, "✓ Key terms extracted", data)
        except Exception as e:
            return ToolResult(False, f"✗ Extract key terms failed: {e}")

    @staticmethod
    def summarize_contract(contract_pdf: str, model: str = "llama3.2:3b") -> ToolResult:
        try:
            from pypdf import PdfReader
            text = "\n".join(p.extract_text() or "" for p in PdfReader(contract_pdf).pages)
            try:
                from npmai import Ollama
                llm = Ollama(model=model, temperature=0.2, change=True, Models=["mistral:7b"])
                prompt = f"""Summarize this contract in plain language. Cover: what it is, who the parties are, main obligations, payment, duration, key risks. Be concise (under 300 words).

Contract:
{text[:5000]}

Summary:"""
                summary = llm.invoke(prompt)
            except Exception:
                summary = text[:800]
            return ToolResult(True, "✓ Contract summarized", summary)
        except Exception as e:
            return ToolResult(False, f"✗ Summarize contract failed: {e}")

    @staticmethod
    def check_contract_dates(contract_pdf: str) -> ToolResult:
        try:
            import re
            from pypdf import PdfReader
            text = "\n".join(p.extract_text() or "" for p in PdfReader(contract_pdf).pages)
            patterns = [r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', r'\b(\d{4}-\d{2}-\d{2})\b', r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b']
            dates_found = []
            for pat in patterns:
                dates_found.extend(re.findall(pat, text, re.IGNORECASE))
            today = datetime.now()
            alerts = []
            for d_str in dates_found:
                for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
                    try:
                        d = datetime.strptime(str(d_str).strip(), fmt)
                        if d < today:
                            alerts.append(f"⚠ PAST DATE: {d_str}")
                        elif (d - today).days <= 30:
                            alerts.append(f"⏰ DUE SOON (<30 days): {d_str}")
                        break
                    except Exception:
                        pass
            return ToolResult(True, f"✓ Found {len(dates_found)} dates. {len(alerts)} alerts.", {"dates": dates_found, "alerts": alerts})
        except Exception as e:
            return ToolResult(False, f"✗ Check contract dates failed: {e}")

    @staticmethod
    def compare_contracts(contract1: str, contract2: str, output: str = "contract_diff.txt") -> ToolResult:
        try:
            from pypdf import PdfReader
            import difflib
            def _extract(path):
                return "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
            text1 = _extract(contract1).splitlines()
            text2 = _extract(contract2).splitlines()
            diff = list(difflib.unified_diff(text1, text2, fromfile=Path(contract1).name, tofile=Path(contract2).name, lineterm=""))
            diff_text = "\n".join(diff)
            Path(output).write_text(diff_text)
            added   = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
            removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
            return ToolResult(True, f"✓ Contracts compared: +{added} additions, -{removed} removals → {output}", {"added": added, "removed": removed, "diff_path": output})
        except Exception as e:
            return ToolResult(False, f"✗ Compare contracts failed: {e}")

    @staticmethod
    def add_signature_field(pdf: str, name: str, position: Tuple = (100, 100), output: str = "") -> ToolResult:
        try:
            from pypdf import PdfReader, PdfWriter
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            import io
            reader = PdfReader(pdf)
            out_path = output or pdf.replace(".pdf", "_with_sig.pdf")
            packet = io.BytesIO()
            W, H = A4
            c = canvas.Canvas(packet, pagesize=A4)
            x, y = position
            c.setStrokeColorRGB(0, 0, 0)
            c.rect(x, y, 200, 40)
            c.setFont("Helvetica", 8)
            c.drawString(x + 5, y + 5, f"Signature: {name}")
            c.drawString(x + 5, y - 12, "Date: __________")
            c.save()
            packet.seek(0)
            overlay = PdfReader(packet)
            writer = PdfWriter()
            for i, page in enumerate(reader.pages):
                if i == 0:
                    page.merge_page(overlay.pages[0])
                writer.add_page(page)
            with open(out_path, "wb") as f:
                writer.write(f)
            return ToolResult(True, f"✓ Signature field added for '{name}': {out_path}")
        except Exception as e:
            return ToolResult(False, f"✗ Add signature field failed: {e}")

    @staticmethod
    def verify_signature(pdf: str) -> ToolResult:
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf)
            fields = reader.get_fields() or {}
            sig_fields = {k: v for k, v in fields.items() if "sig" in k.lower() or "sign" in k.lower()}
            metadata = dict(reader.metadata) if reader.metadata else {}
            return ToolResult(True, f"✓ PDF analysis: {len(sig_fields)} signature fields found", {"signature_fields": list(sig_fields.keys()), "pages": len(reader.pages), "metadata": metadata})
        except Exception as e:
            return ToolResult(False, f"✗ Verify signature failed: {e}")


# ─────────────────────────────────────────────
# Registry
# ─────────────────────────────────────────────

BUSINESS_TOOLS = {
    "stripe":           StripeTool,
    "razorpay":         RazorpayTool,
    "shopify":          ShopifyTool,
    "invoice":          InvoiceTool,
    "accounting":       AccountingTool,
    "crm":              CRMTool,
    "email_marketing":  EmailMarketingTool,
    "analytics":        AnalyticsTool,
    "inventory":        InventoryTool,
    "contract":         ContractTool,
}

BUSINESS_TOOLS_SUMMARY = "\n".join(
    f"- {k}: {v.description}" for k, v in BUSINESS_TOOLS.items()
)
