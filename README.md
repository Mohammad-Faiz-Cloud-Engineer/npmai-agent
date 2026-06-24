<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0a0a1a,50:1a0a3a,100:0d1b4a&height=220&section=header&text=npmai-agent&fontSize=76&fontColor=00f5ff&fontAlignY=38&desc=1%2C371%20Tools.%20100%20Classes.%20One%20Package.&descColor=a78bfa&descAlignY=60&animation=twinkling" width="100%"/>

<a href="https://npmai.netlify.app">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=20&duration=2800&pause=900&color=00F5FF&center=true&vCenter=true&multiline=false&width=750&lines=1%2C371+verified+tools+across+100+classes;5-role+autonomous+LLM+pipeline;Plan+%E2%86%92+Select+%E2%86%92+Code+%E2%86%92+Audit+%E2%86%92+Verify;Zero+paid+APIs.+Free+forever.+Powered+by+NPMAI." alt="Typing SVG" />
</a>

<br/>

<p>
  <img src="https://img.shields.io/badge/PyPI-npmai--agent-00f5ff?style=for-the-badge&logo=pypi&logoColor=white&labelColor=0a0a1a"/>
  <img src="https://img.shields.io/badge/Version-1.0.0-a78bfa?style=for-the-badge&labelColor=0a0a1a"/>
  <img src="https://img.shields.io/badge/Python-3.9%2B-00f5ff?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0a1a"/>
  <img src="https://img.shields.io/badge/License-MIT-2affa0?style=for-the-badge&labelColor=0a0a1a"/>
  <img src="https://img.shields.io/badge/Status-Production%20Stable-2affa0?style=for-the-badge&labelColor=0a0a1a"/>
</p>

<p>
  <img src="https://img.shields.io/badge/Tools-1%2C371-ff6b9d?style=for-the-badge&labelColor=0a0a1a"/>
  <img src="https://img.shields.io/badge/Classes-100-a78bfa?style=for-the-badge&labelColor=0a0a1a"/>
  <img src="https://img.shields.io/badge/LLM%20Roles-5-00f5ff?style=for-the-badge&labelColor=0a0a1a"/>
  <img src="https://img.shields.io/badge/NPMAI-ECOSYSTEM-00f5ff?style=for-the-badge&labelColor=0a0a1a"/>
</p>

<br/>

**[`🌐 Website`](https://npmai.netlify.app)** · **[`📦 PyPI`](https://pypi.org/project/npmai-agent)** · **[`🐙 GitHub`](https://github.com/sonuramashishnpm/npmai-agent)** · **[`📖 Docs`](#-documentation)** · **[`💬 Community`](https://npmai.netlify.app)**

</div>

---

## ✦ What is `npmai-agent`?

> **`npmai-agent`** is a production-grade, open-source autonomous AI agent framework with **1,371 verified tools across 100 classes** — the largest open-source local tool registry in existence. A **5-role LLM pipeline** (Planner → Tool Manager → Coder → Auditor → Verifier) executes any plain-English task on your computer, completely free.

No GPT-4. No Gemini. No monthly bills. No API keys to buy.  
Everything runs on **45+ open-source LLMs** served free by the **NPMAI ECOSYSTEM**.

```bash
pip install npmai-agent
```

```python
from npmai_agents import AgentBrain

brain = AgentBrain()
brain.run_task("Scrape the top 10 AI papers from arXiv, summarise each one, create an Excel report, and email it to me")
# The agent plans → selects tools → writes code → audits → executes → verifies. By itself.
```

---

## 🏛️ Built by NPMAI ECOSYSTEM

**`npmai-agent`** is an official product of the **[NPMAI ECOSYSTEM](https://npmai.netlify.app)** — a free, open-source AI research and development platform.

<table>
<tr>
<td width="50%">

**👤 Founder**
**Sonu Kumar** *(Bihar Viral Boy)*
15-year-old self-taught AI developer,
TEDx Speaker & Constitutional Researcher
from Bihar, India · Kota, Rajasthan

</td>
<td width="50%">

**🌍 Ecosystem Stats**
`2,000,000+` PyPI downloads
`45+` community LLMs
`6+` deployed AI products
`0₹` cost to users — forever

</td>
</tr>
</table>

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-sonuramashishnpm-0a0a1a?style=flat-square&logo=github&logoColor=00f5ff)](https://github.com/sonuramashishnpm)
[![PyPI](https://img.shields.io/badge/PyPI-npmai-0a0a1a?style=flat-square&logo=pypi&logoColor=a78bfa)](https://pypi.org/project/npmai)
[![Website](https://img.shields.io/badge/Website-npmai.netlify.app-0a0a1a?style=flat-square&logo=netlify&logoColor=2affa0)](https://npmai.netlify.app)

</div>

---

## ⚡ Why npmai-agent?

| 🔴 Problem | 🟢 npmai-agent Solution |
|---|---|
| LLM wastes tokens reverse-engineering API docs | **`use` variable** — pre-compiled tool knowledge per class |
| Too many tools crash LLM context window | **2-level lazy discovery** — index first, deep-dive only when needed |
| Paid APIs (GPT-4, Claude, Gemini) | **45+ free LLMs** via NPMAI load balancer |
| Single-model agents hallucinate | **5 specialized LLM roles** — each optimised for its job |
| Finding the right tool takes trial and error | **Tool Manager LLM** — recommends exact classes for any task |
| Plain-text credential storage | **Fernet-encrypted CredStore** with machine-specific key |
| No memory between sessions | **4 persistent Memory contexts** — plan, code, chat, tasks |
| Fragile single-attempt execution | **12 auto-retries per step** with error feedback loop |

---

## 🏗️ Architecture

```
User Plain-English Task
         │
         ▼
┌─────────────────────┐
│   1. WORKSPACE      │  ◀─ scans Desktop, Downloads, Documents...
│      SCANNER        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   2. PLANNER LLM    │  ◀─ breaks task → 2-5 steps + concise summary
│   llama3.2:3b       │     sees: 100-class one-line index only
└──────────┬──────────┘
           │ (task summary)
           ▼
┌─────────────────────┐
│   3. TOOL MANAGER   │  ◀─ phase 1: shortlists 2-6 classes from index
│      LLM            │     phase 2: fetches full `use` docs, confirms
└──────────┬──────────┘     returns: exact method signatures to Coder
           │ (selected tool docs)
           ▼
    ╔═════════════════╗   ┌────────────────────────────┐
    ║  per step loop  ║   │ retries up to 12×           │
    ║                 ║   │ feeds error back to Coder   │
    ║  4. CODER LLM   ║◀──┤ sees: selected tool docs   │
    ║  codellama:7b   ║   │ only — no noise             │
    ║                 ║   └────────────────────────────┘
    ║  5. AUDITOR LLM ║  ◀─ sees: code only (security focus)
    ║  qwen2.5-coder  ║
    ║                 ║
    ║  6. EXECUTE     ║  ◀─ subprocess isolation
    ║                 ║
    ║  7. VERIFIER    ║  ◀─ sees: step + output only
    ╚═════════════════╝
           │
           ▼
      Task Complete ✓
```

| Role | Default Model | Fallback | Sees |
|---|---|---|---|
| 🗺️ **Planner** | `llama3.2:3b` | `mistral:7b` | 100-class one-line index |
| 🔎 **Tool Manager** | `llama3.2` | `gemma3:12b` | Index → selected `use` docs |
| 💻 **Coder** | `codellama:7b-instruct` | `deepseek-coder:6.7b` | Selected `use` docs only |
| 🛡️ **Auditor** | `qwen2.5-coder:7b` | `falcon:7b-instruct` | Code only |
| ✅ **Verifier** | `llama3.2:3b` | `mistral:7b` | Step + output only |

---

## 📦 Installation

```bash
# Minimal install — agent auto-installs tool dependencies at runtime
pip install npmai-agent

# Full install — all 1,371 tool dependencies pre-installed
pip install npmai-agent[full]
```

```python
# Import styles
from npmai_agents import AgentBrain                          # just the brain
from npmai_agents import StripeTool, GitHubTool, FFmpegTool # specific tools
from npmai_agents import *                                   # everything
```

---

## 📖 Documentation

> **1,371 tools across 100 classes — verified count from source code.**
> Each method = 1 tool. `__init__` excluded from count.

---

### 🔐 CredStore — Encrypted Credential Vault

**Purpose:** Store API keys, tokens, passwords once. All 100 tool classes read from here automatically. Stored at `~/.npmai_agent/creds.json` with a machine-specific Fernet encryption key — never plain text.

**Tools: 4** — `save`, `load`, `all_keys`, `delete`

```python
from npmai_agents import CredStore

CredStore.save("github",   {"token": "ghp_xxxx"})
CredStore.save("slack",    {"bot_token": "xoxb-xxxx"})
CredStore.save("stripe",   {"secret_key": "sk_live_xxxx"})
CredStore.save("openai",   {"api_key": "sk-xxxx"})

creds = CredStore.load("github")
print(CredStore.all_keys())   # ['github', 'slack', 'stripe', 'openai']
CredStore.delete("openai")
```

---

### 🖥️ Workspace

**Purpose:** Scans the user's file system and builds a live context profile fed to the Planner LLM before every task — so the agent knows your OS, home directory, and file layout.

**Tools: 3** — `scan`, `update_profile`, `context_summary`

```python
from npmai_agents import Workspace

ws = Workspace()
profile = ws.scan()
print(profile["os"], profile["home"])
print(ws.context_summary())   # text fed to Planner
```

---

## 🛠️ Developer & CLI Tools — 155 tools across 10 classes

---

### GitTool — 24 tools
**Purpose:** Complete local git workflow without leaving Python.

```python
from npmai_agents import GitTool

GitTool.init("/home/sonu/project")
GitTool.clone("https://github.com/sonuramashishnpm/npmai.git", "/home/sonu/npmai")
GitTool.add("/home/sonu/npmai", ".")
GitTool.commit("/home/sonu/npmai", "feat: add tool manager")
GitTool.push("/home/sonu/npmai", "main")
GitTool.create_branch("/home/sonu/npmai", "feature/voice-input")
GitTool.merge("/home/sonu/npmai", "feature/voice-input")
GitTool.log("/home/sonu/npmai", limit=10)
GitTool.diff("/home/sonu/npmai")
GitTool.stash("/home/sonu/npmai")
GitTool.rebase("/home/sonu/npmai", "main")
GitTool.tag("/home/sonu/npmai", "v1.0.0")
```

**All 24 tools:** `init` `clone` `status` `add` `commit` `push` `pull` `fetch` `create_branch` `checkout` `merge` `log` `diff` `stash` `stash_pop` `tag` `reset` `rebase` `cherry_pick` `blame` `show` `remote_add` `remote_list` `submodule_init`

---

### GitHubTool — 24 tools
**Purpose:** Full GitHub API — repos, issues, PRs, releases, files, Actions, collaborators.

```python
from npmai_agents import GitHubTool

GitHubTool.create_issue("sonuramashishnpm/npmai", "Add voice input", "Feature request...", labels=["enhancement"])
GitHubTool.create_pr("sonuramashishnpm/npmai", "feat: voice input", "main", "feature/voice")
GitHubTool.push_file("sonuramashishnpm/npmai", "README.md", "# NPMAI\n...", "docs: update")
GitHubTool.create_release("sonuramashishnpm/npmai", "v1.0.0", "Production release")
GitHubTool.trigger_workflow("sonuramashishnpm/npmai", "deploy.yml")
```

**All 24 tools:** `create_repo` `delete_repo` `fork_repo` `create_issue` `close_issue` `list_issues` `create_pr` `merge_pr` `list_prs` `review_pr` `push_file` `delete_file` `get_file` `list_files` `create_release` `get_actions_status` `trigger_workflow` `list_branches` `protect_branch` `add_collaborator` `create_gist` `get_user_info` `star_repo` `watch_repo`

---

### GitLabTool — 16 tools
**Purpose:** GitLab projects, issues, merge requests, pipelines, members.

**All 16 tools:** `create_project` `list_projects` `get_project` `create_issue` `close_issue` `create_mr` `merge_mr` `list_pipelines` `trigger_pipeline` `get_pipeline_jobs` `retry_job` `push_file` `list_branches` `create_branch` `list_members` `add_member`

---

### DockerTool — 26 tools
**Purpose:** Full Docker control — images, containers, networks, volumes, Compose.

```python
from npmai_agents import DockerTool

DockerTool.build_image("/home/sonu/app", tag="npmai-app:latest")
DockerTool.run_container("npmai-app:latest", name="npmai", ports={"8080": "80"})
DockerTool.compose_up("/home/sonu/app")
DockerTool.get_logs("npmai", tail=50)
DockerTool.exec_in_container("npmai", "python manage.py migrate")
```

**All 26 tools:** `build_image` `push_image` `pull_image` `tag_image` `remove_image` `list_images` `run_container` `stop_container` `start_container` `remove_container` `exec_in_container` `get_logs` `list_containers` `inspect_container` `create_network` `list_networks` `remove_network` `create_volume` `list_volumes` `remove_volume` `compose_up` `compose_down` `compose_logs` `compose_ps` `login` `system_prune`

---

### PackageManagerTool — 22 tools
**Purpose:** pip, npm, yarn, cargo, go — all package managers in one class.

**All 22 tools:** `pip_install` `pip_uninstall` `pip_list` `pip_show` `pip_freeze` `npm_install` `npm_uninstall` `npm_run` `npm_build` `npm_publish` `npm_list` `npm_update` `npm_audit` `yarn_install` `yarn_add` `yarn_remove` `cargo_build` `cargo_test` `cargo_run` `go_build` `go_test` `go_get`

---

### VSCodeTool — 13 tools
**Purpose:** Control VS Code programmatically — open files, install extensions, run tasks, apply settings.

**All 13 tools:** `open_file` `open_folder` `install_extension` `uninstall_extension` `list_extensions` `run_task` `open_terminal` `apply_settings` `get_settings` `format_file` `lint_workspace` `create_workspace` `open_workspace`

---

### TerminalTool — 15 tools
**Purpose:** Shell execution, environment variables, process management, tool detection.

**All 15 tools:** `run` `run_interactive` `run_script` `run_in_new_terminal` `set_env_var` `get_env_var` `list_env_vars` `source_file` `which` `is_installed` `install_via_package_manager` `create_alias` `list_processes` `kill_process` `get_process_info`

---

### MakefileTool — 4 tools
**Purpose:** Makefile build system — run targets, list, create, edit.

**All 4 tools:** `run_target` `list_targets` `create_makefile` `add_target`

---

### CMakeTool — 5 tools
**Purpose:** CMake build system — configure, build, install, test.

**All 5 tools:** `configure` `build` `install` `clean` `run_ctest`

---

### DebuggerTool — 6 tools
**Purpose:** Python debugging, profiling, memory analysis, deadlock detection.

**All 6 tools:** `run_python_with_pdb` `analyze_traceback` `profile_script` `memory_profile` `find_deadlocks` `strace_process`

---

## 💼 Business & Payments — 152 tools across 10 classes

---

### StripeTool — 29 tools
**Purpose:** Complete Stripe integration — customers, payments, subscriptions, invoices, payouts.

```python
from npmai_agents import StripeTool

StripeTool.create_customer(email="user@example.com", name="Sonu Kumar")
StripeTool.create_subscription(customer_id="cus_xxx", price_id="price_xxx")
StripeTool.create_invoice(customer_id="cus_xxx")
StripeTool.finalize_invoice(invoice_id="in_xxx")
StripeTool.pay_invoice(invoice_id="in_xxx")
StripeTool.create_payout(amount=50000, currency="inr")
```

**All 29 tools:** `create_customer` `get_customer` `update_customer` `list_customers` `delete_customer` `create_payment_intent` `confirm_payment` `create_charge` `capture_charge` `refund_charge` `list_charges` `create_subscription` `cancel_subscription` `update_subscription` `list_subscriptions` `create_product` `create_price` `create_invoice` `finalize_invoice` `pay_invoice` `list_invoices` `send_invoice` `create_coupon` `apply_coupon` `create_payment_link` `list_payment_methods` `get_balance` `list_transactions` `create_payout`

---

### RazorpayTool — 18 tools
**Purpose:** Razorpay Indian payment gateway — orders, capture, refunds, subscriptions, QR codes.

**All 18 tools:** `create_order` `get_order` `list_orders` `fetch_payment` `capture_payment` `refund_payment` `list_payments` `create_refund` `create_customer` `get_customer` `create_subscription` `create_plan` `list_plans` `create_payment_link` `list_payment_links` `create_qr_code` `get_settlements` `get_settlement_transactions`

---

### ShopifyTool — 25 tools
**Purpose:** Complete Shopify store management — products, orders, customers, inventory, discounts.

**All 25 tools:** `list_products` `get_product` `create_product` `update_product` `delete_product` `list_variants` `update_variant` `list_orders` `get_order` `update_order` `cancel_order` `fulfill_order` `list_customers` `get_customer` `create_customer` `search_customers` `list_customer_orders` `get_inventory_levels` `adjust_inventory` `list_collections` `create_collection` `create_discount` `get_shop_info` `list_locations` `get_analytics`

---

### InvoiceTool — 8 tools
**Purpose:** Professional invoice, quote, receipt, PO generation with email delivery and AI data extraction.

**All 8 tools:** `create_invoice` `create_quote` `create_receipt` `create_purchase_order` `send_invoice_email` `batch_create_invoices` `extract_invoice_data` `create_recurring_invoice`

---

### AccountingTool — 10 tools
**Purpose:** Financial calculations — GST, VAT, P&L, balance sheet, cash flow, depreciation, tax.

**All 10 tools:** `calculate_gst` `calculate_vat` `generate_profit_loss` `generate_balance_sheet` `generate_cash_flow` `depreciation_schedule` `currency_convert` `get_exchange_rates` `track_expenses` `calculate_tax_liability`

---

### CRMTool — 18 tools
**Purpose:** Local SQLite CRM — contacts, deals, pipeline tracking, activities, reminders, reports.

**All 18 tools:** `add_contact` `update_contact` `delete_contact` `list_contacts` `search_contacts` `import_contacts_csv` `export_contacts` `merge_duplicate_contacts` `add_deal` `update_deal` `close_deal` `list_deals` `get_pipeline_value` `add_activity` `list_activities` `set_reminder` `generate_sales_report` `get_conversion_rate`

---

### EmailMarketingTool — 13 tools
**Purpose:** Mailchimp campaigns — lists, subscribers, campaigns, schedules, automations, stats.

**All 13 tools:** `create_campaign` `schedule_campaign` `send_campaign_now` `create_list` `add_subscriber` `remove_subscriber` `import_subscribers` `get_campaign_stats` `get_list_stats` `create_automation` `create_template` `unsubscribe` `get_unsubscribes`

---

### AnalyticsTool — 9 tools
**Purpose:** Google Analytics 4 — sessions, pages, traffic sources, conversions, realtime, custom reports.

**All 9 tools:** `connect_google_analytics` `get_sessions` `get_top_pages` `get_traffic_sources` `get_conversions` `get_realtime_users` `create_custom_report` `generate_weekly_report` `track_event`

---

### InventoryTool — 12 tools
**Purpose:** Stock management — add products, track levels, record sales/purchases, forecast demand.

**All 12 tools:** `add_product` `update_stock` `get_stock_level` `list_low_stock` `list_out_of_stock` `get_inventory_value` `record_sale` `record_purchase` `generate_stock_report` `forecast_demand` `export_inventory` `import_inventory`

---

### ContractTool — 10 tools
**Purpose:** Legal document automation — NDA, service agreements, employment contracts, key term extraction.

**All 10 tools:** `create_nda` `create_service_agreement` `create_employment_contract` `fill_template` `extract_key_terms` `summarize_contract` `check_contract_dates` `compare_contracts` `add_signature_field` `verify_signature`

---

## ☁️ Cloud & DevOps — 149 tools across 10 classes

**Classes:** `AWSS3Tool` (16) · `AWSLambdaTool` (12) · `AWSECSTool` (11) · `CloudflareTool` (20) · `VercelTool` (13) · `NetlifyTool` (13) · `RailwayTool` (10) · `KubernetesTool` (24) · `TerraformTool` (16) · `MonitoringTool` (14)

```python
from npmai_agents import AWSS3Tool, CloudflareTool, KubernetesTool, TerraformTool

AWSS3Tool.upload_file("mybucket", "/home/sonu/report.pdf", "reports/report.pdf")
AWSS3Tool.get_presigned_url("mybucket", "reports/report.pdf", expires=3600)

CloudflareTool.create_dns_record(zone_id="xxx", type="A", name="api", content="1.2.3.4")
CloudflareTool.purge_cache(zone_id="xxx")

KubernetesTool.scale_deployment("npmai-app", replicas=3)
KubernetesTool.helm_install("npmai", "./charts/npmai")

TerraformTool.init("/home/sonu/infra")
TerraformTool.plan("/home/sonu/infra")
TerraformTool.apply("/home/sonu/infra", auto_approve=True)
```

---

## 📡 Communication — 95 tools across 10 classes

**Classes:** `MicrosoftTeamsTool` (5) · `ZoomTool` (10) · `TwilioTool` (12) · `SendGridTool` (14) · `PushNotificationTool` (7) · `RSSFeedTool` (9) · `WebhookTool` (8) · `CalendarTool` (11) · `ChatOpsAutomationTool` (9) · `SMTPAdvancedTool` (10)

```python
from npmai_agents import TwilioTool, SendGridTool, CalendarTool, ZoomTool

TwilioTool.send_sms(to="+919876543210", body="Task complete ✓")
TwilioTool.make_call(to="+919876543210", message="Your AI agent completed the task.")

SendGridTool.send_with_template(to="user@example.com", template_id="d-xxx", data={"name": "Sonu"})
SendGridTool.create_campaign(list_id="xxx", subject="NPMAI Launch", template_id="d-xxx")

CalendarTool.create_event(summary="NPMAI Demo", start="2026-07-01T10:00:00", end="2026-07-01T11:00:00")
CalendarTool.find_free_slots(duration_minutes=60, days_ahead=7)

ZoomTool.create_meeting(topic="NPMAI Investor Call", start_time="2026-07-01T10:00:00", duration=60)
```

---

## 🎨 Creative & Design — 97 tools across 10 classes

**Classes:** `FigmaTool` (13) · `BlenderTool` (11) · `SVGTool` (10) · `CanvaTool` (9) · `FontTool` (10) · `ColorTool` (11) · `IconTool` (7) · `DiagramTool` (10) · `PrintTool` (8) · `ThreeDTool` (8)

```python
from npmai_agents import DiagramTool, SVGTool, ColorTool, FigmaTool

DiagramTool.create_flowchart(steps=["Plan", "Code", "Audit", "Execute", "Verify"], out="pipeline.png")
DiagramTool.render_mermaid("graph TD; A-->B; B-->C", out="flow.png")

SVGTool.create_svg(width=800, height=400, out="banner.svg")
SVGTool.convert_to_png("banner.svg", out="banner.png")

ColorTool.generate_palette(base_color="#00f5ff", scheme="triadic")
ColorTool.check_contrast_ratio("#00f5ff", "#0a0a1a")

FigmaTool.export_asset(file_key="xxx", node_id="yyy", format="PNG", scale=2)
```

---

## 📊 Data & Research — 137 tools across 10 classes

**Classes:** `DataAnalysisTool` (15) · `VisualizationTool` (15) · `WebScrapingAdvancedTool` (12) · `SearchResearchTool` (11) · `FinancialDataTool` (14) · `SocialMediaDataTool` (14) · `WeatherGeoTool` (12) · `TextAnalyticsTool` (14) · `DatabaseTool` (22) · `ReportGeneratorTool` (8)

```python
from npmai_agents import DataAnalysisTool, SearchResearchTool, DatabaseTool, TextAnalyticsTool

DataAnalysisTool.load("/home/sonu/data.csv")
DataAnalysisTool.clean(remove_nulls=True, remove_duplicates=True)
DataAnalysisTool.natural_language_query("Show me top 5 revenue months")
DataAnalysisTool.auto_visualize(out_dir="/home/sonu/charts")

SearchResearchTool.search_arxiv("multi-agent LLM systems", max_results=20)
SearchResearchTool.get_citations(paper_id="2312.xxxxx")

DatabaseTool.connect_postgres(host="localhost", db="npmai", user="sonu", password="xxx")
DatabaseTool.execute_query("SELECT COUNT(*) FROM users WHERE active = true")

TextAnalyticsTool.sentiment_analysis("npmai-agent is incredible!")
TextAnalyticsTool.summarize("/home/sonu/paper.pdf", max_words=200)
```

---

## 🎬 Media & Audio/Video — 123 tools across 10 classes

**Classes:** `FFmpegTool` (32) · `YouTubeDownloaderTool` (9) · `AudioTool` (15) · `ImageAdvancedTool` (20) · `ScreenRecorderTool` (7) · `TextToSpeechTool` (7) · `VideoEditingTool` (10) · `PodcastTool` (8) · `StreamingTool` (6) · `MediaMetadataTool` (9)

```python
from npmai_agents import FFmpegTool, AudioTool, ImageAdvancedTool, TextToSpeechTool

FFmpegTool.compress_video("/home/sonu/demo.mp4", out="demo_compressed.mp4", crf=28)
FFmpegTool.create_gif("/home/sonu/demo.mp4", start=10, duration=5, out="demo.gif")
FFmpegTool.add_subtitles("/home/sonu/video.mp4", srt="/home/sonu/subs.srt", out="with_subs.mp4")

AudioTool.transcribe("/home/sonu/podcast.mp3")
AudioTool.remove_silence("/home/sonu/recording.wav", out="clean.wav")

ImageAdvancedTool.remove_background("/home/sonu/photo.jpg", out="no_bg.png")
ImageAdvancedTool.upscale("/home/sonu/logo.png", scale=4, out="logo_4x.png")

TextToSpeechTool.generate(text="NPMAI agent task complete.", voice="en-US-Neural2-J", out="tts.mp3")
```

---

## ✅ Productivity & Project Management — 176 tools across 10 classes

**Classes:** `GoogleWorkspaceTool` (21) · `NotionAdvancedTool` (19) · `LinearTool` (19) · `AsanaTool` (19) · `TrelloTool` (20) · `ClickUpTool` (17) · `TodoistTool` (17) · `ObsidianTool` (15) · `BookmarkManagerTool` (12) · `TimeTrackingTool` (17)

```python
from npmai_agents import GoogleWorkspaceTool, NotionAdvancedTool, AsanaTool, TimeTrackingTool

GoogleWorkspaceTool.sheets_write(sheet_id="1Bxi...", range_="Sheet1!A1", data=[["Name", "Score"]])
GoogleWorkspaceTool.drive_share(file_id="xxx", email="team@company.com", role="writer")
GoogleWorkspaceTool.docs_create(title="NPMAI Report", content="Auto-generated by npmai-agent.")

NotionAdvancedTool.query_database(db_id="xxx", filter={"property": "Status", "select": {"equals": "Done"}})
NotionAdvancedTool.create_kanban_view(db_id="xxx", group_by="Status")

AsanaTool.create_task(project_id="xxx", name="Integrate Tool Manager", due="2026-07-01", notes="See agent_core.py")
TimeTrackingTool.start_timer(project="npmai-agent", description="Tool Manager integration")
```

---

## 🔒 Security & AI — 122 tools across 10 classes

**Classes:** `SecurityScannerTool` (14) · `CryptographyTool` (16) · `PenetrationTestingTool` (11) · `AIImageGenerationTool` (8) · `AITextGenerationAdvancedTool` (12) · `MLModelTool` (11) · `SpeechAITool` (8) · `ComputerVisionTool` (14) · `AutomationWorkflowTool` (14) · `KnowledgeBaseTool` (14)

```python
from npmai_agents import CryptographyTool, ComputerVisionTool, KnowledgeBaseTool, MLModelTool

CryptographyTool.generate_rsa_keypair(bits=4096, out_dir="/home/sonu/.keys")
CryptographyTool.aes_encrypt("/home/sonu/secret.pdf", key="my-secret-key", out="secret.enc")
CryptographyTool.generate_totp_secret(issuer="NPMAI", account="sonu@npmai.ai")

ComputerVisionTool.detect_objects("/home/sonu/photo.jpg", model="yolov8")
ComputerVisionTool.read_text_ocr("/home/sonu/scan.png")
ComputerVisionTool.scan_qr_barcode("/home/sonu/qr.png")

KnowledgeBaseTool.create_kb(name="npmai_research")
KnowledgeBaseTool.add_url_to_kb(kb_name="npmai_research", url="https://npmai.netlify.app")
KnowledgeBaseTool.answer_with_sources(kb_name="npmai_research", question="What is LARA architecture?")

MLModelTool.train_classifier(X_path="features.csv", y_path="labels.csv", model_type="random_forest")
MLModelTool.deploy_model_api(model_path="model.pkl", port=8000)
```

---

## ⚙️ System & Hardware — 165 tools across 10 classes

**Classes:** `SystemAdvancedTool` (22) · `NetworkAdvancedTool` (21) · `FileSystemAdvancedTool` (17) · `ProcessAutomationTool` (20) · `PrinterTool` (11) · `ClipboardAdvancedTool` (15) · `HardwareMonitorTool` (13) · `RaspberryPiTool` (17) · `MQTTIoTTool` (12) · `VirtualizationTool` (17)

```python
from npmai_agents import SystemAdvancedTool, ProcessAutomationTool, RaspberryPiTool, MQTTIoTTool

SystemAdvancedTool.create_cron_job(name="daily_backup", schedule="0 2 * * *", command="python /home/sonu/backup.py")
SystemAdvancedTool.manage_firewall(action="allow", port=8080, protocol="tcp")

ProcessAutomationTool.find_window("Chrome")
ProcessAutomationTool.click_at(x=500, y=300)
ProcessAutomationTool.type_text("npmai-agent automated this")
ProcessAutomationTool.record_macro("/home/sonu/macro.json")

RaspberryPiTool.setup_pin(pin=18, mode="output")
RaspberryPiTool.control_servo(pin=12, angle=90)
RaspberryPiTool.read_temperature_sensor(pin=4, sensor_type="DHT22")

MQTTIoTTool.connect(broker="192.168.1.100", port=1883)
MQTTIoTTool.publish_sensor_data(topic="home/temp", value=24.5, unit="C")
MQTTIoTTool.control_home_assistant_entity(entity_id="light.living_room", action="turn_on")
```

---

## 🤖 AgentBrain — The Autonomous Pipeline

```python
from npmai_agents import AgentBrain

# Default — uses NPMAI free LLMs
brain = AgentBrain()

# Custom LLM backends (any LLMBackend subclass)
from npmai_agents import OpenAIBackend, GroqBackend
brain = AgentBrain(
    planner = GroqBackend(api_key="...", model="llama-3.3-70b-versatile"),
    coder   = OpenAIBackend(api_key="...", model="gpt-4o"),
    # auditor, verifier, chatter → fall back to NPMAI free defaults
)

# Run any task
brain.run_task("Find all duplicate files in my Downloads and delete them, then send me an email summary")
brain.run_task("Pull latest from GitHub, run tests, and post results to our Slack #dev channel")
brain.run_task("Read all invoices in my Documents/Invoices folder and create an Excel summary with totals")

# Kill mid-task
killed = [False]
import threading
t = threading.Thread(target=brain.run_task, args=("Long running task",), kwargs={"killed_flag": killed})
t.start()
killed[0] = True

# Task history
for h in AgentBrain.load_task_history():
    print("✓" if h["success"] else "✗", h["task"], h["time"])
```

---

## 🔢 Tool Count — Verified from Source

| Category | Classes | Tools |
|---|---|---|
| Developer & CLI | 10 | 155 |
| Business & Payments | 10 | 152 |
| Cloud & DevOps | 10 | 149 |
| Communication | 10 | 95 |
| Creative & Design | 10 | 97 |
| Data & Research | 10 | 137 |
| Media & Audio/Video | 10 | 123 |
| Productivity & PM | 10 | 176 |
| Security & AI | 10 | 122 |
| System & Hardware | 10 | 165 |
| **TOTAL** | **100** | **1,371** |

> Count verified programmatically from source code. Each public method = 1 tool. `__init__` excluded.

---

## 📋 Version History

| Version | Status | Notes |
|---|---|---|
| `1.0.0` | ✅ Production Stable | 1,371 tools · 100 classes · 5-role pipeline · Tool Manager |
| `0.0.1` | 🗄️ Archived | Initial alpha — 21 tool classes |

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1a0a3a,50:0a0a1a,100:0d1b4a&height=130&section=footer&text=NPMAI+ECOSYSTEM&fontSize=30&fontColor=00f5ff&fontAlignY=65&desc=Open+Source+AI+Research+%26+Development+%C2%B7+Free+Forever&descColor=a78bfa&descSize=14&descAlignY=85" width="100%"/>

**Built with ❤️ by [Sonu Kumar](https://github.com/sonuramashishnpm) · [npmai.netlify.app](https://npmai.netlify.app)**

*"Promoting AI tools to every nation's village — free and open forever."*

</div>
