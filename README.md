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

I build and operate **high-volume email delivery infrastructure** — from raw SMTP and MTA tuning to authentication, reputation and inbox placement — and the full-stack products that sit on top of it. Right now that's **[Sendpilots](https://sendpilots.com)**.

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

  motto:     "If it didn't land in the inbox, it wasn't delivered."
```

## 🛰️ How mail moves through my stack

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/pipeline-dark.svg">
  <img src="assets/pipeline-light.svg" width="100%" alt="Email delivery pipeline: App → Queue (Redis/Celery) → MTA pool (Postal, KumoMTA, PowerMTA, Haraka) → Auth layer (SPF, DKIM, ARC, DMARC) → ISPs → Inbox, with 4xx retries and 5xx/FBL suppression looping back to the queue.">
</picture>

## 📡 On the wire

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/smtp-terminal-dark.svg">
  <img src="assets/smtp-terminal-light.svg" width="100%" alt="Animated terminal replaying an SMTP session: EHLO, STARTTLS with TLS 1.3, MAIL FROM, RCPT TO, DATA with a DKIM signature, and 250 OK with spf, dkim and dmarc all passing.">
</picture>

## 🚀 Featured builds

<p align="center">
  <a href="https://github.com/arunkuttysend/sendpilots"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/project-sendpilots-dark.svg"><img src="assets/project-sendpilots-light.svg" width="49%" alt="SendPilots Flow AI — AI-native multi-channel outreach platform with an autonomous FlowGPT campaign agent. Nuxt 4, FastAPI, Supabase, Celery, Redis, Claude API."></picture></a>
  <a href="https://github.com/arunkuttysend/new_email_app"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/project-email-platform-dark.svg"><img src="assets/project-email-platform-light.svg" width="49%" alt="Email Campaign Platform — campaigns, sequences, bounce handling and inbox management. Laravel 12, Livewire 3, PostgreSQL, Redis, Meilisearch, Caddy."></picture></a>
</p>

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

## 🔭 Now → Next

- **Now** — Sendpilots Flow AI: an autonomous campaign agent (FlowGPT) on FastAPI + Nuxt 4
- **Now** — real-time deliverability dashboard: Postmaster, SNDS and DMARC RUA ingestion in one view
- **Next** — multi-MTA failover with per-ISP throttling and automatic IP-pool rotation
- **Next** — an open-source IP-warming toolkit
- **Later** — multi-region MTA infrastructure, BIMI + VMC across the major mailbox providers

## 📊 Telemetry

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/stats/stats-dark.svg">
    <img src="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/stats/stats-light.svg" width="49%" alt="Contribution overview for the last 12 months: contributions, commits, pull requests, reviews, streaks and a weekly sparkline.">
  </picture>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/stats/langs-dark.svg">
    <img src="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/stats/langs-light.svg" width="49%" alt="Language mix by bytes across owned repositories.">
  </picture>
</p>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/stats/activity-dark.svg">
  <img src="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/stats/activity-light.svg" width="100%" alt="Contribution heatmap for the last 12 months with an animated scan wave.">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/github-contribution-grid-snake-dark.svg">
  <img src="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/github-contribution-grid-snake.svg" width="100%" alt="Snake eating my contribution graph">
</picture>

<details>
<summary><b>🧊 Deep metrics</b> — 3D calendar, coding habits, achievements</summary>
<br>
<img src="https://raw.githubusercontent.com/arunkuttysend/arunkuttysend/output/metrics.svg" width="100%" alt="Isometric contribution calendar, coding habits and achievements generated by lowlighter/metrics">
</details>

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

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/footer-dark.svg">
  <img src="assets/footer-light.svg" width="100%" alt="Thanks for stopping by — arun@sendpilots.com · sendpilots.com">
</picture>
