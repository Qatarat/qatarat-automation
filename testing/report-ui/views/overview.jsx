// Overview — hero stats, donut, history sparkline, top issues
const OverviewView = () => {
  const { MAESTRO_FLOWS, APPIUM_TESTS, HISTORY, RUN_META, COMMITS } = window.QATARAT_DATA;

  const allTests = useMemo(() => {
    const appiumFlat = APPIUM_TESTS.flatMap(f => f.tests.map(t => ({ ...t, file: f.file, group: f.group })));
    return [...MAESTRO_FLOWS.map(f => ({ ...f, kind: "maestro" })), ...appiumFlat.map(t => ({ ...t, kind: "appium" }))];
  }, []);

  const counts = useMemo(() => {
    const c = { pass: 0, fail: 0, flaky: 0, idle: 0 };
    allTests.forEach(t => { c[t.status] = (c[t.status] || 0) + 1; });
    return c;
  }, [allTests]);

  const ranCount = allTests.filter(t => t.status !== "idle").length;
  const total = counts.pass + counts.fail + counts.flaky;
  const passRate = total > 0 ? (counts.pass / total) * 100 : 0;
  const neverRan = RUN_META.neverRan || ranCount === 0;

  const historyWithData = HISTORY.filter(h => h.total > 0);
  const durationSeries = historyWithData.length > 0 ? historyWithData.map(h => h.duration) : [0];
  const passSeries = historyWithData.length > 0
    ? historyWithData.map(h => h.total > 0 ? (h.pass / h.total) * 100 : 0)
    : [0];

  const failingFlows = MAESTRO_FLOWS.filter(f => f.status === "fail" || f.status === "flaky");
  const failingAppium = APPIUM_TESTS.flatMap(f =>
    f.tests.filter(t => t.status === "fail" || t.status === "flaky").map(t => ({ ...t, file: f.file }))
  );
  const allIssues = [
    ...failingFlows.map(f => ({ kind: "Maestro flow", title: f.name, group: f.group, status: f.status, note: f.note })),
    ...failingAppium.map(t => ({ kind: "Appium test", title: t.name, group: t.file, status: t.status, note: t.error })),
  ];

  return (
    <div className="grid" style={{ gap: 20 }}>

      {/* ── Not-run-yet banner ── */}
      {neverRan && (
        <div style={{
          padding: "18px 20px", borderRadius: 12,
          background: "var(--surface)", border: "1px solid var(--border)",
        }}>
          <div style={{ display: "flex", alignItems: "flex-start", gap: 14, marginBottom: 16 }}>
            <div style={{ width: 38, height: 38, borderRadius: 10, background: "var(--accent-2)", color: "var(--accent)", display: "grid", placeItems: "center", flexShrink: 0, marginTop: 1 }}>
              <Icon name="bolt" size={18} />
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 4 }}>No test runs yet</div>
              <div style={{ fontSize: 13, color: "var(--text-2)", lineHeight: 1.6 }}>
                This report is ready — it will populate with real results after your first CI run completes.
                All data shown below reflects the <em>structure</em> of the test suite (16 flows + 22 deep tests),
                with every test in an <StatusPill status="idle" /> state until executed.
              </div>
            </div>
          </div>
          <div style={{ borderTop: "1px solid var(--border)", paddingTop: 14 }}>
            <div style={{ fontSize: 11.5, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: ".1em", fontWeight: 500, marginBottom: 10 }}>How to trigger your first run</div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 8 }}>
              {[
                { n: "1", text: "Open the Actions tab in your GitHub repository" },
                { n: "2", text: 'Select "Maestro — Smoke (Android)"' },
                { n: "3", text: 'Click "Run workflow" → confirm' },
                { n: "4", text: "Wait ~10 min — results publish automatically" },
              ].map(s => (
                <div key={s.n} style={{ display: "flex", gap: 10, alignItems: "flex-start", padding: "10px 12px", background: "var(--surface-2)", borderRadius: 8, border: "1px solid var(--border)" }}>
                  <span style={{ width: 20, height: 20, borderRadius: 50, background: "var(--accent-2)", color: "var(--accent)", fontFamily: "Geist Mono", fontSize: 11, fontWeight: 600, display: "grid", placeItems: "center", flexShrink: 0, marginTop: 1 }}>{s.n}</span>
                  <span style={{ fontSize: 12.5, color: "var(--text-2)", lineHeight: 1.5 }}>{s.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Hero header ── */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 24, alignItems: "end" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
            <Pill kind={neverRan ? "idle" : "run"}>
              {neverRan ? "awaiting first run" : `live · run #${RUN_META.id.slice(-4)}`}
            </Pill>
            {!neverRan && (
              <span className="mono" style={{ fontSize: 12, color: "var(--text-3)" }}>
                <Icon name="branch" size={12} /> {RUN_META.branch} · <Icon name="commit" size={12} /> {RUN_META.commit}
              </span>
            )}
          </div>
          <h1 className="h1">Test Suite Report</h1>
          <p className="lead">
            Qatarat (قطرات) · Flutter app for Android &amp; iOS.
            {" "}<strong style={{ color: "var(--text)", fontWeight: 500 }}>{MAESTRO_FLOWS.length} Maestro UI flows</strong> (YAML scripts that tap through the app like a real user) and{" "}
            <strong style={{ color: "var(--text)", fontWeight: 500 }}>{APPIUM_TESTS.reduce((s, f) => s + f.tests.length, 0)} Appium deep tests</strong> (Python/pytest that verify payment SDKs &amp; data integrity), run nightly via GitHub Actions.
          </p>
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
          <span style={{ fontSize: 11, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: ".1em", fontWeight: 500 }}>Device</span>
          <span className="mono" style={{ fontSize: 12.5, color: "var(--text)" }}>{RUN_META.device}</span>
          <span className="mono" style={{ fontSize: 11.5, color: "var(--text-3)" }}>Flutter {RUN_META.flutterVersion}</span>
        </div>
      </div>

      {/* ── Stat row ── */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
        <Stat
          label="Pass Rate"
          value={passRate} decimals={1} suffix="%"
          color={neverRan ? "var(--text-3)" : passRate >= 95 ? "var(--pass)" : passRate >= 80 ? "var(--flaky)" : "var(--fail)"}
          sub={neverRan ? "no runs yet" : `${counts.pass} passed · ${counts.fail} failed`}
        />
        <Stat
          label="Total Tests"
          value={MAESTRO_FLOWS.length + APPIUM_TESTS.reduce((s, f) => s + f.tests.length, 0)}
          sub={`${MAESTRO_FLOWS.length} UI flows · ${APPIUM_TESTS.reduce((s, f) => s + f.tests.length, 0)} deep tests`}
        />
        <Stat
          label="Run Duration"
          value={RUN_META.duration / 60} decimals={1} suffix="m"
          sub={neverRan ? "no runs yet" : "this run · all suites"}
        />
        <Stat
          label="Executed"
          value={ranCount}
          color={neverRan ? "var(--text-3)" : "var(--text)"}
          sub={neverRan ? "of " + (MAESTRO_FLOWS.length + APPIUM_TESTS.reduce((s, f) => s + f.tests.length, 0)) + " · waiting for first run" : `of ${MAESTRO_FLOWS.length + APPIUM_TESTS.reduce((s, f) => s + f.tests.length, 0)} tests`}
        />
      </div>

      {/* ── Donut + History ── */}
      <div style={{ display: "grid", gridTemplateColumns: "minmax(260px, 320px) 1fr", gap: 16 }}>
        <div className="card">
          <div className="card-head">
            <h3>Result breakdown</h3>
            <span className="sub">{neverRan ? "no data yet" : "latest run"}</span>
          </div>
          <div className="card-body" style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 18, paddingTop: 22 }}>
            <Donut
              size={160} thickness={16}
              centerLabel={neverRan ? "—" : `${passRate.toFixed(0)}%`}
              centerSub={neverRan ? "no runs" : "pass rate"}
              segments={neverRan
                ? [{ value: 1, color: "var(--surface-3)", label: "No data" }]
                : [
                    { value: Math.max(counts.pass, 0.001), color: "oklch(74% 0.18 155)", label: "Passed" },
                    { value: counts.flaky, color: "oklch(80% 0.16 75)", label: "Flaky" },
                    { value: counts.fail, color: "oklch(70% 0.22 18)", label: "Failed" },
                  ]
              }
            />
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, width: "100%" }}>
              {[
                { label: "Passed", value: counts.pass, color: "var(--pass)", hint: "All steps completed" },
                { label: "Flaky",  value: counts.flaky, color: "var(--flaky)", hint: "Passed after retry" },
                { label: "Failed", value: counts.fail, color: "var(--fail)", hint: "Did not complete" },
              ].map(s => (
                <div key={s.label} title={s.hint} style={{ display: "flex", flexDirection: "column", gap: 2, padding: "8px 10px", background: "var(--surface-2)", borderRadius: 8, border: "1px solid var(--border)", cursor: "default" }}>
                  <span style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "var(--text-3)" }}>
                    <span style={{ width: 6, height: 6, borderRadius: 50, background: s.color }} /> {s.label}
                  </span>
                  <span style={{ fontFamily: "Geist Mono", fontSize: 18, color: "var(--text)", fontWeight: 500 }}>{s.value}</span>
                </div>
              ))}
            </div>

            {/* Status guide */}
            <div style={{ width: "100%", padding: "10px 12px", background: "var(--surface-2)", borderRadius: 8, border: "1px solid var(--border)" }}>
              <div style={{ fontSize: 10.5, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: ".1em", marginBottom: 7, fontWeight: 500 }}>Status guide</div>
              {[
                { s: "pass",  desc: "Every step ran without error" },
                { s: "flaky", desc: "Passed on retry — investigate" },
                { s: "fail",  desc: "Stopped at a failing step" },
                { s: "idle",  desc: "Not yet executed" },
              ].map(g => (
                <div key={g.s} style={{ display: "flex", alignItems: "center", gap: 8, padding: "4px 0", borderBottom: "1px solid var(--border)" }}>
                  <StatusPill status={g.s} />
                  <span style={{ fontSize: 12, color: "var(--text-3)" }}>{g.desc}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-head between" style={{ display: "flex", justifyContent: "space-between" }}>
            <div className="row" style={{ gap: 10 }}>
              <h3>30-day trend</h3>
              <span className="sub">nightly runs · {historyWithData.length} days with data</span>
            </div>
            <div className="row" style={{ gap: 16, fontSize: 11.5, color: "var(--text-3)" }}>
              <span style={{ display: "flex", alignItems: "center", gap: 6 }}><span style={{ width: 8, height: 8, borderRadius: 2, background: "var(--pass)" }} />pass</span>
              <span style={{ display: "flex", alignItems: "center", gap: 6 }}><span style={{ width: 8, height: 8, borderRadius: 2, background: "var(--flaky)" }} />flaky</span>
              <span style={{ display: "flex", alignItems: "center", gap: 6 }}><span style={{ width: 8, height: 8, borderRadius: 2, background: "var(--fail)" }} />fail</span>
            </div>
          </div>
          <div className="card-body" style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {historyWithData.length === 0 ? (
              <div style={{ height: 130, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 8, color: "var(--text-3)", borderRadius: 8, border: "1px dashed var(--border)" }}>
                <Icon name="history" size={24} style={{ opacity: 0.4 }} />
                <span style={{ fontSize: 13 }}>No history yet — bars will appear after your first run</span>
              </div>
            ) : (
              <BarChart data={HISTORY} height={130} />
            )}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginTop: 4 }}>
              <div style={{ padding: 12, background: "var(--surface-2)", borderRadius: 10, border: "1px solid var(--border)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                  <span style={{ fontSize: 11.5, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: ".08em" }}>Pass rate</span>
                  <span className="mono" style={{ fontSize: 12, color: "var(--pass)" }}>
                    {historyWithData.length > 0 ? `${passSeries[passSeries.length - 1].toFixed(1)}%` : "—"}
                  </span>
                </div>
                {historyWithData.length > 0 ? (
                  <Sparkline data={passSeries} color="oklch(74% 0.18 155)" height={36} width={260}
                             label="pass rate" format={(v) => `${v.toFixed(1)}%`}
                             labelForIndex={(i) => {
                               const days = passSeries.length - 1 - i;
                               return days === 0 ? "Today" : `${days} day${days===1?"":"s"} ago`;
                             }} />
                ) : (
                  <div style={{ height: 36, display: "flex", alignItems: "center" }}>
                    <span style={{ fontSize: 12, color: "var(--text-3)" }}>No data yet</span>
                  </div>
                )}
              </div>
              <div style={{ padding: 12, background: "var(--surface-2)", borderRadius: 10, border: "1px solid var(--border)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                  <span style={{ fontSize: 11.5, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: ".08em" }}>Avg duration</span>
                  <span className="mono" style={{ fontSize: 12, color: "var(--accent)" }}>
                    {historyWithData.length > 0 ? fmtDur(durationSeries[durationSeries.length - 1]) : "—"}
                  </span>
                </div>
                {historyWithData.length > 0 ? (
                  <Sparkline data={durationSeries} color="var(--accent)" height={36} width={260}
                             label="run duration" format={fmtDur}
                             labelForIndex={(i) => {
                               const days = durationSeries.length - 1 - i;
                               return days === 0 ? "Today" : `${days} day${days===1?"":"s"} ago`;
                             }} />
                ) : (
                  <div style={{ height: 36, display: "flex", alignItems: "center" }}>
                    <span style={{ fontSize: 12, color: "var(--text-3)" }}>No data yet</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Issues + commits ── */}
      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 16 }}>
        <div className="card">
          <div className="card-head">
            <h3>Issues to look at</h3>
            <span className="sub">
              {neverRan ? "awaiting run" : allIssues.length === 0 ? "✓ all clear" : `${allIssues.length} active`}
            </span>
          </div>
          <div className="card-body" style={{ padding: allIssues.length === 0 ? 16 : 0 }}>
            {neverRan ? (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8, padding: "24px 0", color: "var(--text-3)", textAlign: "center" }}>
                <Icon name="clock" size={28} style={{ opacity: 0.4 }} />
                <span style={{ fontSize: 13 }}>Failures and flaky tests will appear here after the first run</span>
                <span style={{ fontSize: 12, color: "var(--text-3)", maxWidth: 280, lineHeight: 1.5 }}>
                  Each row shows which test failed, what group it belongs to, and the error message from CI logs.
                </span>
              </div>
            ) : allIssues.length === 0 ? (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8, padding: "24px 0", color: "var(--text-3)", textAlign: "center" }}>
                <div style={{ width: 44, height: 44, borderRadius: 12, background: "var(--pass-2)", color: "var(--pass)", display: "grid", placeItems: "center" }}>
                  <Icon name="check" size={22} />
                </div>
                <span style={{ fontSize: 14, fontWeight: 500, color: "var(--text)" }}>All tests passed!</span>
                <span style={{ fontSize: 12, color: "var(--text-3)" }}>No failures or flaky tests in this run.</span>
              </div>
            ) : (
              allIssues.map((row, i) => (
                <div key={i} style={{ display: "grid", gridTemplateColumns: "auto 1fr auto", gap: 14, alignItems: "center", padding: "14px 16px", borderBottom: "1px solid var(--border)" }}>
                  <div style={{ width: 30, height: 30, borderRadius: 8, background: row.status === "fail" ? "var(--fail-2)" : "var(--flaky-2)", color: row.status === "fail" ? "var(--fail)" : "var(--flaky)", display: "grid", placeItems: "center" }}>
                    <Icon name={row.status === "fail" ? "x" : "bolt"} size={14} />
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
                      <span style={{ fontWeight: 500, fontSize: 13.5 }}>{row.title}</span>
                      <span className="mono" style={{ fontSize: 11, color: "var(--text-3)" }}>· {row.kind}</span>
                    </div>
                    <div style={{ fontSize: 12, color: "var(--text-3)", fontFamily: "Geist Mono", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {row.note
                        ? row.note
                        : `Group: ${row.group} — open CI logs for step details`}
                    </div>
                  </div>
                  <StatusPill status={row.status} />
                </div>
              ))
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-head"><h3>Recent commits</h3><span className="sub">main branch</span></div>
          <div className="card-body" style={{ padding: COMMITS.length === 0 ? 16 : 0 }}>
            {COMMITS.length === 0 ? (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8, padding: "24px 0", color: "var(--text-3)", textAlign: "center" }}>
                <Icon name="commit" size={24} style={{ opacity: 0.4 }} />
                <span style={{ fontSize: 13 }}>No commit history available</span>
              </div>
            ) : COMMITS.slice(0, 5).map(c => {
              const hasData = c.hasData !== false && c.tests > 0;
              return (
                <div key={c.sha} style={{ padding: "12px 16px", borderBottom: "1px solid var(--border)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                    <span className="mono" style={{ fontSize: 11.5, color: "var(--accent)", background: "var(--accent-2)", padding: "1px 6px", borderRadius: 4 }}>{c.sha}</span>
                    <span style={{ fontSize: 13, color: "var(--text)", flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{c.msg}</span>
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "auto 1fr auto", gap: 10, alignItems: "center" }}>
                    <span style={{ fontSize: 11, color: "var(--text-3)", fontFamily: "Geist Mono" }}>{c.author} · {c.time}</span>
                    {hasData ? (
                      <CoverageBar pass={c.pass} flaky={c.flaky} fail={c.fail} height={5} />
                    ) : (
                      <div style={{ height: 5, background: "var(--surface-3)", borderRadius: 999 }} />
                    )}
                    <span className="mono" style={{ fontSize: 11, color: "var(--text-3)" }}>
                      {hasData ? `${c.pass}/${c.tests}` : "—"}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── Suite overview cards ── */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 12 }}>
        {[
          {
            title: "Maestro UI Flows",
            icon: "flows",
            color: "oklch(74% 0.18 155)",
            count: MAESTRO_FLOWS.length,
            ran: MAESTRO_FLOWS.filter(f => f.status !== "idle").length,
            passed: MAESTRO_FLOWS.filter(f => f.status === "pass").length,
            failed: MAESTRO_FLOWS.filter(f => f.status === "fail").length,
            desc: "YAML-defined sequences that drive the app UI exactly like a human would — tap, swipe, type, assert. Each flow covers a complete user journey end-to-end.",
            viewKey: "flows",
          },
          {
            title: "Appium Deep Tests",
            icon: "appium",
            color: "oklch(80% 0.16 75)",
            count: APPIUM_TESTS.reduce((s, f) => s + f.tests.length, 0),
            ran: APPIUM_TESTS.flatMap(f => f.tests).filter(t => t.status !== "idle").length,
            passed: APPIUM_TESTS.flatMap(f => f.tests).filter(t => t.status === "pass").length,
            failed: APPIUM_TESTS.flatMap(f => f.tests).filter(t => t.status === "fail").length,
            desc: "Python/pytest with appium-flutter-driver. Verifies payment SDKs (HyperPay, Tabby BNPL, bank transfer), gift cards, subscriptions, and account management at the API level.",
            viewKey: "appium",
          },
        ].map(s => (
          <div key={s.title} className="card">
            <div className="card-body">
              <div style={{ display: "flex", alignItems: "flex-start", gap: 12, marginBottom: 12 }}>
                <div style={{ width: 38, height: 38, borderRadius: 10, background: `color-mix(in oklch, ${s.color} 14%, transparent)`, border: `1px solid color-mix(in oklch, ${s.color} 30%, transparent)`, color: s.color, display: "grid", placeItems: "center", flexShrink: 0 }}>
                  <Icon name={s.icon} size={18} />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                    <span style={{ fontWeight: 600, fontSize: 14 }}>{s.title}</span>
                    <span className="mono" style={{ fontSize: 12.5, color: s.color }}>{s.count} tests</span>
                  </div>
                  <p style={{ margin: 0, fontSize: 12.5, color: "var(--text-2)", lineHeight: 1.5 }}>{s.desc}</p>
                </div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8 }}>
                {[
                  { l: "Executed", v: `${s.ran} / ${s.count}`, c: "var(--text)" },
                  { l: "Passed", v: s.passed, c: s.ran > 0 ? "var(--pass)" : "var(--text-3)" },
                  { l: "Failed", v: s.failed, c: s.failed > 0 ? "var(--fail)" : "var(--text-3)" },
                ].map(m => (
                  <div key={m.l} style={{ padding: "8px 10px", background: "var(--surface-2)", borderRadius: 8, border: "1px solid var(--border)", textAlign: "center" }}>
                    <div style={{ fontSize: 10.5, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: ".09em", marginBottom: 3 }}>{m.l}</div>
                    <div className="mono" style={{ fontSize: 16, fontWeight: 500, color: m.c }}>{m.v}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
};

window.OverviewView = OverviewView;
