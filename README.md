<!--
  Profile README for @arunkuttysend
  ─────────────────────────────────
  • assets/*.svg        hand-built animated SVGs  →  python3 scripts/build_assets.py
  • output branch       live stats / snake / metrics, rebuilt every 8h by .github/workflows/profile.yml
  Every visual ships in a dark + light variant and is served from this repo, so nothing depends
  on third-party widget uptime.
-->

<a href="https://sendpilots.com"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg"><img src="assets/hero-light.svg" width="100%" alt="Arun Kumar — Email Infrastructure Engineer and Full-Stack Developer. Animated banner showing an MTA routing mail to Gmail, Outlook, Yahoo and iCloud."></picture></a>

<p align="center">
  <a href="https://sendpilots.com"><img src="https://img.shields.io/badge/sendpilots.com-0d1117?style=for-the-badge&logo=googlechrome&logoColor=58a6ff" alt="sendpilots.com"></a>
  <a href="mailto:arun@sendpilots.com"><img src="https://img.shields.io/badge/arun@sendpilots.com-0d1117?style=for-the-badge&logo=gmail&logoColor=f778ba" alt="Email"></a>
  <a href="https://github.com/arunkuttysend?tab=followers"><img src="https://img.shields.io/github/followers/arunkuttysend?style=for-the-badge&logo=github&label=followers&color=0d1117&labelColor=0d1117" alt="Followers"></a>
  <img src="https://komarev.com/ghpvc/?username=arunkuttysend&style=for-the-badge&color=0d1117&label=PROFILE+VIEWS" alt="Profile views">
</p>

## `$ whoami`

I build and operate **high-volume email delivery infrastructure** — from raw SMTP and MTA tuning to authentication, reputation and inbox placement — and the full-stack products that sit on top of it. Right now that's **[Sendpilots](https://sendpilots.com)** — and I build it AI-native, with a fleet of coding agents and hard engineering guardrails.

```yaml
arun:
  role:      Email Infrastructure Engineer · Full-Stack Developer
  building:  Sendpilots — email delivery + AI-native outreach
  timezone:  IST (UTC+05:30)

  mta:       [Postal, Postfix, Haraka, PowerMTA, KumoMTA, OpenSMTPD, Exim]
  auth:      [SPF, DKIM, DMARC, BIMI, ARC, MTA-STS, TLS-RPT, DANE]
  filtering: [Rspamd, SpamAssassin, Amavis, Postscreen, ClamAV, Milter]
  product:   [Laravel, Livewire, FastAPI, Next.js, Nuxt, TypeScript, Python]
  infra:     [Docker, Nginx, Caddy, Redis, Celery, PostgreSQL, Linux]
  cloud:     [AWS, Hetzner, DigitalOcean, Cloudflare]
  ai:        [Claude Code, Cursor, Codex, Gemini CLI, Hermes, Kiro, MCP]

  motto:     "If it didn't land in the inbox, it wasn't delivered."
```

## 🌍 Global delivery mesh

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/global-mesh-dark.svg"><img src="assets/global-mesh-light.svg" width="100%" alt="Animated world map: routes from India through EU (Hetzner), US-East (AWS) and APAC (DigitalOcean) relays to mailbox providers worldwide — Gmail, Outlook, Yahoo, UOL, GMX, Naver, QQ Mail, Yahoo JP, Telstra and Zoho."></picture>

## 🛰️ How mail moves through my stack

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/pipeline-dark.svg"><img src="assets/pipeline-light.svg" width="100%" alt="Email delivery pipeline: App → Queue (Redis/Celery) → MTA pool (Postal, KumoMTA, PowerMTA, Haraka) → Auth layer (SPF, DKIM, ARC, DMARC) → ISPs → Inbox, with 4xx retries and 5xx/FBL suppression looping back to the queue."></picture>

## 📡 On the wire

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/smtp-terminal-dark.svg"><img src="assets/smtp-terminal-light.svg" width="100%" alt="Animated terminal replaying an SMTP session: EHLO, STARTTLS with TLS 1.3, MAIL FROM, RCPT TO, DATA with a DKIM signature, and 250 OK with spf, dkim and dmarc all passing."></picture>

## 📬 Deliverability research · 2026

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/rulebook-2026-dark.svg"><img src="assets/rulebook-2026-light.svg" width="100%" alt="2026 bulk-sender rules: Gmail, Yahoo and Outlook requirements, spam-rate thresholds (0.1% target, 0.3% hard enforcement), BIMI with VMC or CMC, and the enforcement timeline from Feb 2024 to 2026."></picture>

<details>
<summary><b>📑 The checklist I run before any domain sends at volume</b> — with sources</summary>
<br>

| # | Check | Why it matters in 2026 |
|:-:|---|---|
| 1 | SPF **and** DKIM pass, DMARC published and aligned | Required by Gmail, Yahoo and Outlook for 5,000+/day senders. Outlook rejects non-compliant mail with `550 5.7.515` (since 5 May 2025). |
| 2 | DMARC with `rua=` reporting, then ramp `p=none → quarantine → reject` | `p=none` is the minimum; enforcement is what unlocks BIMI and stops spoofing. |
| 3 | User-reported spam rate **< 0.1%**, never **≥ 0.3%** | Google escalated from spam-foldering to permanent 5xx rejects in Nov 2025. My own ceiling is 0.08%. |
| 4 | One-click unsubscribe (`List-Unsubscribe` + `List-Unsubscribe-Post`, RFC 8058), honoured within 2 days | Required for marketing mail at Gmail and Yahoo. |
| 5 | Valid PTR / forward-confirmed rDNS that matches HELO, TLS on every hop | Cheapest reputation win; missing rDNS is still a top rejection cause. |
| 6 | Split transactional vs marketing IP pools and domains; warm new IPs on a schedule | One bad campaign shouldn't take password resets down with it. |
| 7 | BIMI: DMARC at enforcement + VMC (trademark) or CMC (no trademark, Gmail supports it) | Verified logo = trust signal in the inbox. |

**Sources:**
[Google sender guidelines](https://support.google.com/a/answer/81126) ·
[Google sender guidelines FAQ](https://support.google.com/a/answer/14229414) ·
[Microsoft: Outlook requirements for high-volume senders](https://techcommunity.microsoft.com/blog/microsoftdefenderforoffice365blog/strengthening-email-ecosystem-outlook%e2%80%99s-new-requirements-for-high%e2%80%90volume-senders/4399730) ·
[Microsoft: fix NDR 550 5.7.515](https://support.microsoft.com/en-us/outlook/fix-ndr-error-550-5-7-515-in-outlook-com) ·
[BIMI Group: Common Mark Certificates](https://bimigroup.org/announcing-common-mark-certificates/) ·
[RFC 8058](https://www.rfc-editor.org/rfc/rfc8058) ·
[Red Sift 2026 bulk-sender guide](https://redsift.com/guides/bulk-email-sender-requirements)

</details>

## 🤖 AI-native builder

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/agent-fleet-dark.svg"><img src="assets/agent-fleet-light.svg" width="100%" alt="Agent fleet: Arun orchestrating Claude Code, Cursor, Codex CLI, Gemini CLI, Hermes Agent, Kiro, Grok CLI, Cline, Goose, Copilot, Kimi Code, OpenCode, Factory Droid and Antigravity — with a spec → parallel agents → MCP tools → guardrails → ship workflow."></picture>

> I'm a vibe-coder with a senior engineer's checklist: agents write a lot of the code, but **specs, tests, CI and review decide what ships.** Every repo carries its own agent context (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.cursor/`, `.kiro/`, `.mcp.json`) so any agent can pick up the work cold.

## 🧪 The Lab

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/lab-dark.svg"><img src="assets/lab-light.svg" width="100%" alt="Case studies from private repos: Mailcore (Rust mail server, 242 tests), LeadQ v2 (Go SMTP/IMAP outreach engine), FlowMail AI (4 AI agents), SendPilots (live SaaS), SendPilot Flow (email, voice, LinkedIn), Nova Warmup, Postal × Sendpilots, a realtime ClickHouse SaaS and a multi-channel engagement platform."></picture>

## 🗓️ Build log

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/build-log-dark.svg"><img src="assets/build-log-light.svg" width="100%" alt="Timeline from August 2025 to now: engagement platform, Gmail automation R&D, Yahoo/Outlook warmup, Nova Warmup, Mailcore in Rust, SendPilots v2 to v3, FlowMail AI, SendPilot Flow, Mailu research, LeadQ v2 in Go."></picture>

## 🚀 Featured public builds

<p align="center">
  <a href="https://github.com/arunkuttysend/sendpilots"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/project-sendpilots-dark.svg"><img src="assets/project-sendpilots-light.svg" width="49%" alt="SendPilots Flow AI — AI-native multi-channel outreach platform with an autonomous FlowGPT campaign agent."></picture></a>
  <a href="https://github.com/arunkuttysend/new_email_app"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/project-email-platform-dark.svg"><img src="assets/project-email-platform-light.svg" width="49%" alt="Email Campaign Platform — campaigns, sequences, bounce handling and inbox management on Laravel 12."></picture></a>
</p>

## 🌐 Open source & community

| Project | Role | What I'm doing with it |
|---|---|---|
| [Mailu/Mailu](https://github.com/Mailu/Mailu) | fork → [Mailu_sp](https://github.com/arunkuttysend/Mailu_sp) | Containerised mail-server stack research |
| [Billionmail/BillionMail](https://github.com/Billionmail/BillionMail) | fork → [BilemailPL](https://github.com/arunkuttysend/BilemailPL) | Studying a self-hosted mail + newsletter platform |
| [sendx/email-skills](https://github.com/sendx/email-skills) | fork → [email-skills](https://github.com/arunkuttysend/email-skills) | Deliverability & compliance skills for AI agents |
| [KumoCorp/kumomta](https://github.com/KumoCorp/kumomta) | ⭐ watching | High-performance open-source MTA |
| [postalsys/emailengine](https://github.com/postalsys/emailengine) | ⭐ watching | Headless email client / IMAP API |
| [maileroo/email-specter](https://github.com/maileroo/email-specter) | ⭐ watching | KumoMTA delivery-log monitoring |

## 🧰 Toolbox

<p align="center">
  <img src="https://skillicons.dev/icons?i=php,laravel,python,fastapi,ts,nextjs,nuxtjs,nodejs,tailwind,supabase&perline=10" alt="PHP, Laravel, Python, FastAPI, TypeScript, Next.js, Nuxt, Node.js, Tailwind, Supabase"><br><br>
  <img src="https://skillicons.dev/icons?i=docker,nginx,redis,postgres,mysql,linux,aws,cloudflare,githubactions,grafana,prometheus,selenium&perline=12" alt="Docker, Nginx, Redis, PostgreSQL, MySQL, Linux, AWS, Cloudflare, GitHub Actions, Grafana, Prometheus, Selenium">
</p>

<table>
  <tr>
    <td><b>MTAs</b></td>
    <td>
      <img src="https://img.shields.io/badge/Postal-production-6D28D9?style=flat-square" alt="Postal">
      <img src="https://img.shields.io/badge/Postfix-production-6D28D9?style=flat-square" alt="Postfix">
      <img src="https://img.shields.io/badge/Haraka-production-6D28D9?style=flat-square" alt="Haraka">
      <img src="https://img.shields.io/badge/PowerMTA-1M%2B%2Fhr-6D28D9?style=flat-square" alt="PowerMTA">
      <img src="https://img.shields.io/badge/KumoMTA-working-8B5CF6?style=flat-square" alt="KumoMTA">
      <img src="https://img.shields.io/badge/OpenSMTPD-working-8B5CF6?style=flat-square" alt="OpenSMTPD">
      <img src="https://img.shields.io/badge/Exim-working-8B5CF6?style=flat-square" alt="Exim">
    </td>
  </tr>
  <tr>
    <td><b>Authentication</b></td>
    <td>
      <img src="https://img.shields.io/badge/SPF-2ea043?style=flat-square" alt="SPF">
      <img src="https://img.shields.io/badge/DKIM-2ea043?style=flat-square" alt="DKIM">
      <img src="https://img.shields.io/badge/DMARC-p%3Dreject-2ea043?style=flat-square" alt="DMARC">
      <img src="https://img.shields.io/badge/BIMI-2ea043?style=flat-square" alt="BIMI">
      <img src="https://img.shields.io/badge/ARC-2ea043?style=flat-square" alt="ARC">
      <img src="https://img.shields.io/badge/MTA--STS-2ea043?style=flat-square" alt="MTA-STS">
      <img src="https://img.shields.io/badge/TLS--RPT-2ea043?style=flat-square" alt="TLS-RPT">
      <img src="https://img.shields.io/badge/DANE-2ea043?style=flat-square" alt="DANE">
    </td>
  </tr>
  <tr>
    <td><b>Filtering</b></td>
    <td>
      <img src="https://img.shields.io/badge/Rspamd-d73a49?style=flat-square" alt="Rspamd">
      <img src="https://img.shields.io/badge/SpamAssassin-d73a49?style=flat-square" alt="SpamAssassin">
      <img src="https://img.shields.io/badge/Amavis-d73a49?style=flat-square" alt="Amavis">
      <img src="https://img.shields.io/badge/Postscreen-d73a49?style=flat-square" alt="Postscreen">
      <img src="https://img.shields.io/badge/ClamAV-d73a49?style=flat-square" alt="ClamAV">
    </td>
  </tr>
  <tr>
    <td><b>ESP APIs</b></td>
    <td>
      <img src="https://img.shields.io/badge/Amazon%20SES-FF9900?style=flat-square&logo=amazonaws&logoColor=white" alt="Amazon SES">
      <img src="https://img.shields.io/badge/SendGrid-1A82E2?style=flat-square" alt="SendGrid">
      <img src="https://img.shields.io/badge/Mailgun-F06B66?style=flat-square" alt="Mailgun">
      <img src="https://img.shields.io/badge/Postmark-FFDE00?style=flat-square&logoColor=black" alt="Postmark">
      <img src="https://img.shields.io/badge/SparkPost%2FBird-F44336?style=flat-square" alt="SparkPost">
      <img src="https://img.shields.io/badge/Brevo-0B996E?style=flat-square" alt="Brevo">
    </td>
  </tr>
  <tr>
    <td><b>Reputation</b></td>
    <td>
      <img src="https://img.shields.io/badge/Google%20Postmaster-4285F4?style=flat-square&logo=google&logoColor=white" alt="Google Postmaster Tools">
      <img src="https://img.shields.io/badge/Microsoft%20SNDS%20%2B%20JMRP-0078D4?style=flat-square" alt="Microsoft SNDS">
      <img src="https://img.shields.io/badge/GlockApps-FF6B35?style=flat-square" alt="GlockApps">
      <img src="https://img.shields.io/badge/Mail--Tester-34A853?style=flat-square" alt="Mail-Tester">
      <img src="https://img.shields.io/badge/MXToolbox-E74C3C?style=flat-square" alt="MXToolbox">
    </td>
  </tr>
  <tr>
    <td><b>AI agents</b></td>
    <td>
      <img src="https://img.shields.io/badge/Claude%20Code-D97757?style=flat-square&logo=anthropic&logoColor=white" alt="Claude Code">
      <img src="https://img.shields.io/badge/Cursor-000000?style=flat-square" alt="Cursor">
      <img src="https://img.shields.io/badge/Codex%20CLI-412991?style=flat-square&logo=openai&logoColor=white" alt="Codex CLI">
      <img src="https://img.shields.io/badge/Gemini%20CLI-8E75B2?style=flat-square&logo=googlegemini&logoColor=white" alt="Gemini CLI">
      <img src="https://img.shields.io/badge/Hermes%20Agent-2b2d42?style=flat-square" alt="Hermes Agent">
      <img src="https://img.shields.io/badge/Kiro-7c3aed?style=flat-square" alt="Kiro">
      <img src="https://img.shields.io/badge/MCP-servers-0891b2?style=flat-square" alt="MCP">
    </td>
  </tr>
  <tr>
    <td><b>Also</b></td>
    <td>
      <img src="https://img.shields.io/badge/Playwright-2EAD33?style=flat-square&logo=playwright&logoColor=white" alt="Playwright">
      <img src="https://img.shields.io/badge/Celery-37814A?style=flat-square&logo=celery&logoColor=white" alt="Celery">
      <img src="https://img.shields.io/badge/Caddy-1F88C0?style=flat-square&logo=caddy&logoColor=white" alt="Caddy">
      <img src="https://img.shields.io/badge/Hetzner-D50C2D?style=flat-square&logo=hetzner&logoColor=white" alt="Hetzner">
      <img src="https://img.shields.io/badge/DigitalOcean-0080FF?style=flat-square&logo=digitalocean&logoColor=white" alt="DigitalOcean">
      <img src="https://img.shields.io/badge/Razorpay-0C2451?style=flat-square&logo=razorpay&logoColor=white" alt="Razorpay">
      <img src="https://img.shields.io/badge/Stripe-635BFF?style=flat-square&logo=stripe&logoColor=white" alt="Stripe">
    </td>
  </tr>
</table>

## 📊 Live telemetry

<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/stats/stats-dark.svg"><img src="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/stats/stats-light.svg" width="49%" alt="Contribution overview for the last 12 months: contributions, commits, pull requests, reviews, streaks and a weekly sparkline."></picture>
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/stats/langs-dark.svg"><img src="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/stats/langs-light.svg" width="49%" alt="Language mix by bytes across owned repositories."></picture>
</p>

<picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/stats/pulse-dark.svg"><img src="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/stats/pulse-light.svg" width="100%" alt="Coding pulse: commits by hour of day in IST on a 24-hour radial clock, commits by weekday, peak window and after-hours share over the last 90 days."></picture>

<picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/stats/activity-dark.svg"><img src="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/stats/activity-light.svg" width="100%" alt="Contribution heatmap for the last 12 months with an animated scan wave."></picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/github-contribution-grid-snake-dark.svg">
  <img src="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/github-contribution-grid-snake.svg" width="100%" alt="Snake eating my contribution graph">
</picture>

<details>
<summary><b>🧊 Deep metrics</b> — 3D calendar, coding habits, achievements</summary>
<br>
<img src="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/metrics.svg" width="100%" alt="Isometric contribution calendar, coding habits and achievements generated by lowlighter/metrics">
</details>

## 🔭 Now → Next

- **Now** — LeadQ v2: finishing phases 6–8 on top of the Go SMTP/IMAP engine
- **Now** — FlowMail AI agents: reply triage, A/B recommendations and flow optimisation on Claude
- **Next** — Mailcore: hardening the Rust mail server (242 tests today) toward a real pilot
- **Next** — multi-MTA failover with per-ISP throttling and automatic IP-pool rotation
- **Later** — open-source IP-warming toolkit · multi-region MTA infrastructure · BIMI + CMC for every sending domain

<details>
<summary><b>🗄️ Production email DNS cheat-sheet</b></summary>

```dns
; Complete production email DNS setup
@                MX   10 mail.yourdomain.com.
mail             A    <SERVER_IP>
; PTR <SERVER_IP> → mail.yourdomain.com. (set at your host; must match HELO)
@                TXT  "v=spf1 ip4:<SERVER_IP> -all"
sp1._domainkey   TXT  "v=DKIM1; k=rsa; p=<PUBKEY>"            ; 2048-bit, rotate yearly
_dmarc           TXT  "v=DMARC1; p=reject; adkim=s; aspf=s; rua=mailto:dmarc@yourdomain.com"
_mta-sts         TXT  "v=STSv1; id=<TIMESTAMP>"
_smtp._tls       TXT  "v=TLSRPTv1; rua=mailto:tls@yourdomain.com"
default._bimi    TXT  "v=BIMI1; l=https://yourdomain.com/logo.svg; a=https://yourdomain.com/vmc.pem"
```

**Operating rules I ship by**

- Warm new IPs on a schedule (0 → 1M+/day), segment transactional vs. marketing pools
- Soft bounces (4xx) retry with exponential backoff; hard bounces (5xx) and FBL complaints suppress permanently
- Keep complaint rate under 0.08%; watch Google Postmaster + Microsoft SNDS daily
- Seed-list placement tests across 100+ mailbox providers before every major send
- Parse DMARC aggregate (RUA) reports and alert on new unauthenticated sources
- CAN-SPAM, GDPR and CASL compliance baked into the product, not bolted on

</details>

<br>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/footer-dark.svg"><img src="assets/footer-light.svg" width="100%" alt="Thanks for stopping by — arun@sendpilots.com · sendpilots.com"></picture>
