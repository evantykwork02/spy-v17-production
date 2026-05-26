export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response("V17 Telegram Bot + Cloudflare Worker is live.");
    }

    let update;
    try {
      update = await request.json();
    } catch {
      return new Response("Invalid JSON", { status: 400 });
    }

    const message = update.message || update.edited_message;
    if (!message) return new Response("No message", { status: 200 });

    const chatId = message?.chat?.id?.toString();
    const text = (message?.text || "").trim();

    if (chatId !== env.TELEGRAM_CHAT_ID) {
      return new Response("Ignored", { status: 200 });
    }

    await handleCommand(env, chatId, text);
    return new Response("OK", { status: 200 });
  },

  async scheduled(event, env, ctx) {
    ctx.waitUntil(handleScheduledRun(event, env));
  },
};

const DEFAULT_CURRENCY = "SGD";

// ---------------------------------------------------------------------------
// Command routing
// ---------------------------------------------------------------------------

const COMMANDS = {
  signal: ["signal", "send signal", "check signal", "run signal", "/signal"],
  status: ["status", "live", "live status", "stats", "/status"],
  tracker: ["tracker", "report", "live tracker", "periods", "/tracker"],
  summary: ["summary", "week", "weekly", "performance", "/summary"],
  allocation: ["allocation", "weights", "position", "current", "/allocation"],
  injections: ["injections", "show injections", "list injections", "/injections"],
  help: ["help", "commands", "/start", "/help"],
};

function matchCommand(text) {
  const norm = text.toLowerCase().trim();
  for (const [cmd, aliases] of Object.entries(COMMANDS)) {
    if (aliases.includes(norm)) return cmd;
  }
  if (/^inject\b/i.test(norm) || /^add capital\b/i.test(norm)) return "inject";
  return null;
}

async function handleCommand(env, chatId, text) {
  const cmd = matchCommand(text);
  switch (cmd) {
    case "signal":
      await handleSignal(env, chatId);
      break;
    case "status":
      await handleStatus(env, chatId);
      break;
    case "tracker":
      await handleTracker(env, chatId);
      break;
    case "summary":
      await handleSummary(env, chatId);
      break;
    case "allocation":
      await handleAllocation(env, chatId);
      break;
    case "injections":
      await handleInjections(env, chatId);
      break;
    case "inject":
      await handleInject(env, chatId, text);
      break;
    case "help":
      await handleHelp(env, chatId);
      break;
    default:
      await sendMsg(env, chatId, "Unknown command. Send 'help' to see all commands.");
  }
}

// ---------------------------------------------------------------------------
// /signal - triggers GitHub Actions to run full model and send output back
// ---------------------------------------------------------------------------

async function handleSignal(env, chatId) {
  await sendMsg(
    env,
    chatId,
    "Running V17 signal with latest data...\nResults will arrive in ~2 minutes."
  );
  const result = await triggerWorkflow(env, { run_type: "send_signal" });
  if (!result.ok) {
    await sendMsg(
      env,
      chatId,
      `Failed to trigger signal run.\nStatus: ${result.status}\n${result.body.slice(0, 500)}`
    );
  }
}

// ---------------------------------------------------------------------------
// /status - reads live_summary.json, returns compact P&L table
// ---------------------------------------------------------------------------

async function handleStatus(env, chatId) {
  const [d, cfg, periodsCsv] = await Promise.all([
    fetchJson(env, "live_tracker/live_summary.json"),
    fetchJson(env, "config.json"),
    fetchRaw(env, "live_tracker/live_signal_periods.csv"),
  ]);

  if (!d) {
    await sendMsg(env, chatId, "No live data yet. Run 'signal' first to generate it.");
    return;
  }

  const currency = resolveCurrency(d?.currency, cfg?.currency, env.CAPITAL_CURRENCY, DEFAULT_CURRENCY);

  let startTradeDate = d.start_signal_date || "?";
  if (periodsCsv) {
    for (const line of periodsCsv.trim().split("\n").slice(1)) {
      const cols = parseCSVLine(line);
      if (cols.length < 10) continue;
      const [, trade_date, , status] = cols;
      if (status !== "PENDING_EXECUTION") {
        startTradeDate = trade_date;
        break;
      }
    }
  }

  const sp = (v) => fmtPctSigned(v);
  const sh = (v) => (bad(v) ? "n/a" : (+v).toFixed(2));
  const eq = (v) =>
    bad(v)
      ? "n/a"
      : (+v).toLocaleString("en-US", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        });

  const lines = [
    "V17 LIVE STATUS",
    "-".repeat(38),
    `Period:  ${startTradeDate} to ${d.last_data_date || "?"}`,
    "",
    "         Return   Sharpe   MaxDD",
    `Model:   ${sp(d.model_total_return).padEnd(9)}${sh(d.model_sharpe).padEnd(9)}${sp(d.model_max_drawdown)}`,
    `SPY:     ${sp(d.spy_total_return).padEnd(9)}${sh(d.spy_sharpe).padEnd(9)}${sp(d.spy_max_drawdown)}`,
    `Excess:  ${fmtExcess(d.model_total_return, d.spy_total_return)}`,
    "",
    `Equity:  ${eq(d.model_equity)} ${currency}`,
    "",
    `Signal:  ${d.latest_target_allocation || "n/a"}`,
  ];

  await sendCode(env, chatId, lines.join("\n"));
}

// ---------------------------------------------------------------------------
// /tracker - week-by-week P&L table from live_signal_periods.csv
// ---------------------------------------------------------------------------

async function handleTracker(env, chatId) {
  const [d, cfg, csvText] = await Promise.all([
    fetchJson(env, "live_tracker/live_summary.json"),
    fetchJson(env, "config.json"),
    fetchRaw(env, "live_tracker/live_signal_periods.csv"),
  ]);

  if (!d) {
    await sendMsg(env, chatId, "No tracker data yet. Run 'signal' first.");
    return;
  }

  const currency = resolveCurrency(d?.currency, cfg?.currency, env.CAPITAL_CURRENCY, DEFAULT_CURRENCY);

  const sp = (v) => fmtPctSigned(v);
  const sh = (v) => (bad(v) ? "n/a" : (+v).toFixed(2));
  const eq = (v) =>
    bad(v)
      ? "n/a"
      : (+v).toLocaleString("en-US", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        });

  const lines = [
    "V17 TRACKER - Weekly P&L",
    "-".repeat(46),
    `${"Trade".padEnd(12)} ${"Model".padEnd(8)} ${"SPY".padEnd(8)} ${"Excess".padEnd(8)} Status`,
    "-".repeat(46),
  ];

  let trackedWeeks = 0;

  if (csvText) {
    for (const row of csvText.trim().split("\n").slice(1)) {
      const cols = parseCSVLine(row);
      if (cols.length < 10) continue;

      const [, trade_date, , status, , , , m_ret, s_ret] = cols;
      if (status === "PENDING_EXECUTION") continue;

      trackedWeeks += 1;

      const label = status === "OPEN" ? "OPEN" : "DONE";
      lines.push(
        `${trade_date.padEnd(12)} ${sp(parseFloat(m_ret)).padEnd(8)} ${sp(parseFloat(s_ret)).padEnd(8)} ${fmtExcess(parseFloat(m_ret), parseFloat(s_ret)).padEnd(8)} ${label}`
      );
    }
  }

  if (!trackedWeeks && !bad(d.tracked_weeks)) {
    trackedWeeks = +d.tracked_weeks;
  }

  lines.push("-".repeat(46));
  lines.push(`Total:   Model ${sp(d.model_total_return)}  SPY ${sp(d.spy_total_return)}`);
  lines.push(`Excess:  ${fmtExcess(d.model_total_return, d.spy_total_return)}  Sharpe: ${sh(d.model_sharpe)}`);
  lines.push(`MaxDD:   ${sp(d.model_max_drawdown)}  Equity: ${eq(d.model_equity)} ${currency}`);
  lines.push(`Weeks tracked: ${trackedWeeks || "?"}`);

  await sendCode(env, chatId, lines.join("\n"));
}

// ---------------------------------------------------------------------------
// /summary - this week metrics + next week signal + last 10 weeks history
// ---------------------------------------------------------------------------

async function handleSummary(env, chatId) {
  const [d, cfg, periodsCsv, histCsv] = await Promise.all([
    fetchJson(env, "live_tracker/live_summary.json"),
    fetchJson(env, "config.json"),
    fetchRaw(env, "live_tracker/live_signal_periods.csv"),
    fetchRaw(env, "outputs_v17_conservative/weekly_returns.csv"),
  ]);

  if (!d) {
    await sendMsg(env, chatId, "No live data yet. Run 'signal' first.");
    return;
  }

  const currency = resolveCurrency(d?.currency, cfg?.currency, env.CAPITAL_CURRENCY, DEFAULT_CURRENCY);
  const sp = (v) => fmtPctSigned(v);
  const sh = (v) => (bad(v) ? "n/a" : (+v).toFixed(2));
  const eq = (v) =>
    bad(v)
      ? "n/a"
      : (+v).toLocaleString("en-US", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        });

  const trackedDates = new Set();
  let pendingRow = null;
  let thisWeekLive = null;

  if (periodsCsv) {
    for (const line of periodsCsv.trim().split("\n").slice(1)) {
      const cols = parseCSVLine(line);
      if (cols.length < 10) continue;

      const [sig_date, trade_date, period_end, status, regime, v17_signal, target_alloc, m_ret, s_ret] = cols;

      if (status === "PENDING_EXECUTION") {
        pendingRow = { sig_date, trade_date, regime, v17_signal, target_alloc };
      } else {
        trackedDates.add(sig_date);
        thisWeekLive = {
          sig_date,
          trade_date,
          period_end: period_end === "pending" ? "?" : period_end,
          status,
          regime,
          m_ret: parseFloat(m_ret),
          s_ret: parseFloat(s_ret),
        };
      }
    }
  }

  const histRows = [];
  if (histCsv) {
    for (const line of histCsv.trim().split("\n").slice(1)) {
      const cols = parseCSVLine(line);
      if (cols.length < 4) continue;

      const [date, spy_ret, model_ret, regime] = cols;
      histRows.push({
        date,
        m_ret: parseFloat(model_ret),
        s_ret: parseFloat(spy_ret),
        regime,
        tracked: trackedDates.has(date),
      });
    }
  }

  const lines = ["V17 WEEKLY SUMMARY", "=".repeat(36)];

  lines.push("");
  if (thisWeekLive) {
    lines.push(`THIS WEEK  (${thisWeekLive.trade_date} to ${thisWeekLive.period_end})`);
    lines.push("-".repeat(36));
    lines.push(`Model:   ${sp(thisWeekLive.m_ret)}`);
    lines.push(`SPY:     ${sp(thisWeekLive.s_ret)}`);
    lines.push(`Excess:  ${fmtExcess(thisWeekLive.m_ret, thisWeekLive.s_ret)}`);
    lines.push(`Regime:  ${thisWeekLive.regime}`);
  } else if (histRows.length > 0) {
    const last = histRows[histRows.length - 1];
    lines.push(`THIS WEEK  (${last.date})`);
    lines.push("-".repeat(36));
    lines.push(`Model:   ${sp(last.m_ret)}`);
    lines.push(`SPY:     ${sp(last.s_ret)}`);
    lines.push(`Excess:  ${fmtExcess(last.m_ret, last.s_ret)}`);
    lines.push(`Regime:  ${last.regime}`);
  } else {
    lines.push("THIS WEEK");
    lines.push("-".repeat(36));
    lines.push("No data available.");
  }

  const nTracked = trackedDates.size || (!bad(d.tracked_weeks) ? +d.tracked_weeks : 0);
  lines.push("");
  lines.push(`TOTAL TO DATE  (${nTracked} week${nTracked !== 1 ? "s" : ""} tracked)`);
  lines.push("-".repeat(36));
  lines.push(`Model:   ${sp(d.model_total_return).padEnd(10)}Sharpe: ${sh(d.model_sharpe)}`);
  lines.push(`SPY:     ${sp(d.spy_total_return).padEnd(10)}Sharpe: ${sh(d.spy_sharpe)}`);
  lines.push(`Excess:  ${fmtExcess(d.model_total_return, d.spy_total_return)}`);
  lines.push(`MaxDD:   ${sp(d.model_max_drawdown)}`);
  lines.push(`Equity:  ${eq(d.model_equity)} ${currency}`);

  lines.push("");
  lines.push("NEXT WEEK SIGNAL");
  lines.push("-".repeat(36));
  if (pendingRow) {
    lines.push(`Trade:   ${pendingRow.trade_date}`);
    lines.push(`Alloc:   ${pendingRow.target_alloc}`);
    lines.push(`Regime:  ${pendingRow.regime}`);
    lines.push(`Signal:  ${pendingRow.v17_signal}`);
  } else {
    lines.push(`Date:    ${d.latest_signal_date || "n/a"}`);
    lines.push(`Alloc:   ${d.latest_target_allocation || "n/a"}`);
  }

  const recentRows = histRows.slice(-10);
  if (recentRows.length > 0) {
    lines.push("");
    lines.push(`RECENT WEEKS  (${recentRows.length} shown)`);
    lines.push("-".repeat(36));
    lines.push(`${"Date".padEnd(12)}${"Model".padEnd(9)}${"SPY".padEnd(9)}Excess`);
    for (const r of recentRows) {
      const flag = r.tracked ? " *" : "";
      lines.push(
        `${r.date.padEnd(12)}${sp(r.m_ret).padEnd(9)}${sp(r.s_ret).padEnd(9)}${fmtExcess(r.m_ret, r.s_ret)}${flag}`
      );
    }
    lines.push("  * = live tracked");
  }

  await sendCode(env, chatId, lines.join("\n"));
}

// ---------------------------------------------------------------------------
// /allocation - current allocation one-liner
// ---------------------------------------------------------------------------

async function handleAllocation(env, chatId) {
  const d = await fetchJson(env, "live_tracker/live_summary.json");
  if (!d) {
    await sendMsg(env, chatId, "No data yet. Run 'signal' first.");
    return;
  }

  await sendCode(
    env,
    chatId,
    [
      "CURRENT ALLOCATION",
      "-".repeat(28),
      d.latest_target_allocation || "n/a",
      "",
      `Last updated: ${d.last_data_date || "n/a"}`,
    ].join("\n")
  );
}

// ---------------------------------------------------------------------------
// inject <amount> [YYYY-MM-DD]
// ---------------------------------------------------------------------------

async function handleInject(env, chatId, text) {
  const parsed = parseInjectCommand(text);
  if (!parsed) {
    await sendMsg(
      env,
      chatId,
      "Invalid format. Examples:\n" +
        "  inject 2000\n" +
        "  inject 2000 2026-06-01\n\n" +
        "Amount must be a positive number.\n" +
        "Date must be YYYY-MM-DD (defaults to today if omitted)."
    );
    return;
  }

  const cfg = await fetchJson(env, "config.json");
  const { amount, date } = parsed;
  const currency = resolveCurrency(cfg?.currency, env.CAPITAL_CURRENCY, DEFAULT_CURRENCY);

  await sendMsg(
    env,
    chatId,
    `Processing capital injection...\n\n` +
      `Amount: ${amount} ${currency}\n` +
      `Date:   ${date}\n\n` +
      "Updating config.json and tracker (~2 minutes)."
  );

  const result = await triggerWorkflow(env, {
    run_type: "capital_inject",
    inject_amount: amount.toString(),
    inject_date: date,
  });

  if (!result.ok) {
    await sendMsg(
      env,
      chatId,
      `Failed to trigger capital injection.\nStatus: ${result.status}\n${result.body.slice(0, 500)}`
    );
  }
}

function parseInjectCommand(text) {
  const stripped = text.trim().replace(/^(inject|add\s+capital)\s+/i, "");
  const parts = stripped.trim().split(/\s+/);

  const amount = parseFloat(parts[0]);
  if (Number.isNaN(amount) || amount <= 0) return null;

  let date;
  if (parts.length >= 2) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(parts[1])) return null;
    date = parts[1];
  } else {
    const now = new Date();
    const sgt = new Date(now.getTime() + 8 * 60 * 60 * 1000);
    date = sgt.toISOString().slice(0, 10);
  }

  return { amount, date };
}

// ---------------------------------------------------------------------------
// /injections - shows capital_injections from config.json
// ---------------------------------------------------------------------------

async function handleInjections(env, chatId) {
  const cfg = await fetchJson(env, "config.json");
  if (!cfg) {
    await sendMsg(env, chatId, "Could not fetch config. Try again.");
    return;
  }

  const injections = cfg.capital_injections || [];
  const currency = resolveCurrency(cfg.currency, env.CAPITAL_CURRENCY, DEFAULT_CURRENCY);

  if (injections.length === 0) {
    await sendMsg(env, chatId, "No capital injections on record.");
    return;
  }

  const lines = ["CAPITAL INJECTIONS", "-".repeat(30)];

  let total = 0;
  for (const inj of injections) {
    lines.push(`${inj.date}   +${inj.amount} ${currency}`);
    total += parseFloat(inj.amount) || 0;
  }

  lines.push("-".repeat(30));
  lines.push(`Total injected: ${total} ${currency}`);

  await sendCode(env, chatId, lines.join("\n"));
}

// ---------------------------------------------------------------------------
// /help
// ---------------------------------------------------------------------------

async function handleHelp(env, chatId) {
  await sendCode(
    env,
    chatId,
    [
      "V17 BOT COMMANDS",
      "=".repeat(36),
      "signal      Run signal, send output",
      "status      Return / Sharpe / MaxDD / equity",
      "tracker     Week-by-week P&L table",
      "summary     This week + total to date + signal",
      "allocation  Current position weights",
      "injections  Capital injection log",
      "inject <amount> [YYYY-MM-DD]",
      "            inject 2000",
      "            inject 2000 2026-06-01",
      "help        This message",
      "",
      "Auto-runs (SGT):",
      "  Sat 9:00 AM  weekly signal",
      "  Tue 9:32 PM  mid-week update",
    ].join("\n")
  );
}

// ---------------------------------------------------------------------------
// Scheduled runs
// ---------------------------------------------------------------------------

async function handleScheduledRun(event, env) {
  const cron = event.cron;
  let runType;
  let msg;

  if (cron === "0 1 * * SAT") {
    runType = "saturday_signal";
    msg = "Cloudflare schedule: triggering Saturday signal now.";
  } else if (cron === "32 13 * * TUE") {
    runType = "tuesday_active";
    msg = "Cloudflare schedule: triggering Tuesday update now.";
  } else {
    await sendMsg(
      env,
      env.TELEGRAM_CHAT_ID,
      `Unknown cron fired: ${cron}. No workflow triggered.`
    );
    return;
  }

  await sendMsg(env, env.TELEGRAM_CHAT_ID, msg);
  const result = await triggerWorkflow(env, { run_type: runType });
  if (!result.ok) {
    await sendMsg(
      env,
      env.TELEGRAM_CHAT_ID,
      `GitHub trigger failed: ${result.status}\n${result.body.slice(0, 1000)}`
    );
  }
}

// ---------------------------------------------------------------------------
// GitHub Actions dispatch
// ---------------------------------------------------------------------------

async function triggerWorkflow(env, inputs) {
  const workflowFile = env.GITHUB_WORKFLOW_FILE || "v17_scheduled_signal_reports.yml";
  const branch = env.GITHUB_BRANCH || "main";
  const url = `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/actions/workflows/${workflowFile}/dispatches`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "telegram-v17-signal-bot",
    },
    body: JSON.stringify({ ref: branch, inputs }),
  });

  const body = await response.text();
  return { ok: response.ok, status: response.status, body };
}

// ---------------------------------------------------------------------------
// GitHub raw file helpers
// ---------------------------------------------------------------------------

async function fetchJson(env, path) {
  try {
    const resp = await fetchRawResp(env, path);
    if (!resp || !resp.ok) return null;
    return await resp.json();
  } catch {
    return null;
  }
}

async function fetchRaw(env, path) {
  try {
    const resp = await fetchRawResp(env, path);
    if (!resp || !resp.ok) return null;
    return await resp.text();
  } catch {
    return null;
  }
}

async function fetchRawResp(env, path) {
  const owner = env.GITHUB_OWNER;
  const repo = env.GITHUB_REPO;
  const branch = env.GITHUB_BRANCH || "main";
  const url = `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/${path}`;
  return fetch(url, { headers: { "Cache-Control": "no-cache" } });
}

// ---------------------------------------------------------------------------
// Telegram helpers
// ---------------------------------------------------------------------------

async function sendMsg(env, chatId, text) {
  const truncated = text.length > 4000 ? text.slice(0, 4000) + "\n...(truncated)" : text;
  return fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, text: truncated }),
  });
}

async function sendCode(env, chatId, text) {
  const escaped = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const truncated = escaped.length > 3900 ? escaped.slice(0, 3900) + "\n...(truncated)" : escaped;
  return fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text: `<pre>${truncated}</pre>`,
      parse_mode: "HTML",
    }),
  });
}

// ---------------------------------------------------------------------------
// CSV parser
// ---------------------------------------------------------------------------

function parseCSVLine(line) {
  const cols = [];
  let cur = "";
  let inQ = false;

  for (let i = 0; i < line.length; i++) {
    const ch = line[i];

    if (ch === '"') {
      if (inQ && line[i + 1] === '"') {
        cur += '"';
        i += 1;
      } else {
        inQ = !inQ;
      }
    } else if (ch === "," && !inQ) {
      cols.push(cur);
      cur = "";
    } else {
      cur += ch;
    }
  }

  cols.push(cur);
  return cols;
}

// ---------------------------------------------------------------------------
// Formatting helpers
// ---------------------------------------------------------------------------

function resolveCurrency(...values) {
  for (const value of values) {
    const currency = String(value || "").trim().toUpperCase();
    if (currency) return currency;
  }
  return DEFAULT_CURRENCY;
}

function bad(v) {
  return v == null || v === undefined || Number.isNaN(+v);
}

function fmtPctSigned(v) {
  if (bad(v)) return "n/a";
  const n = +v * 100;
  return `${n >= 0 ? "+" : ""}${n.toFixed(2)}%`;
}

function fmtExcess(modelV, spyV) {
  if (bad(modelV) || bad(spyV)) return "n/a";
  const m = Math.round(+modelV * 10000) / 100;
  const s = Math.round(+spyV * 10000) / 100;
  const e = Math.round((m - s) * 100) / 100;
  return `${e >= 0 ? "+" : ""}${e.toFixed(2)}%`;
}
