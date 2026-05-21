// Overview — hero stats, donut, history sparkline, top issues
const OverviewView = () => {
  const { MAESTRO_FLOWS, APPIUM_TESTS, HISTORY, RUN_META, COMMITS } = window.QATARAT_DATA;

  const allTests = useMemo(() => {
    const appiumFlat = APPIUM_TESTS.flatMap(f => f.tests.map(t => ({ ...t, file: f.file, group: f.group })));
    return [...MAESTRO_FLOWS.map(f => ({ ...f, kind: "maestro" })), ...appiumFlat.map(t => ({ ...t, kind: "appium" }))];
  }, []);

  const counts = useMemo(() => {
    const c = { pass: 0, fail: 0, flaky: 0 };
    allTests.forEach(t => { c[t.status] = (c[t.status] || 0) + 1; });
    return c;
  }, [allTests]);

  const ranCount = allTests.filter(t => t.status !== "idle").length;
  const total = counts.pass + counts.fail + counts.flaky;
  const passRate = total > 0 ? (counts.pass / total) * 100 : 0;
  const neverRan = ranCount === 0;

  // Only build chart series from days that actually have data
  const historyWithData = HISTORY.filter(h => h.total > 0);
  const durationSeries = historyWithData.length > 0 ? historyWithData.map(h => h.duration) : [0];
  const passSeries = historyWithData.length > 0
    ? historyWithData.map(h => h.total > 0 ? (h.pass / h.total) * 100 : 0)
    : [0];

  const failingFlows = MAESTRO_FLOWS.filter(f => f.status === "fail" || f.status === "flaky");
  const failingAppium = APPIUM_TESTS.flatMap(f => f.tests.filter(t => t.status === "fail" || t.status === "flaky").map(t => ({ ...t, file: f.file })));

  return (
    <div className="grid" style={{ gap: 20 }}>
      {/* Not-run-yet banner */}
      {neverRan && (
        <div style={{
          padding: "14px 18px", borderRadius: 12,
          background: "var(--surface)", border: "1px solid var(--border)",
          display: "flex", alignItems: "center", gap: 14,
        }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: "var(--accent-2)", color: "var(--accent)", display: "grid", placeItems: "center", flexShrink: 0 }}>
            <Icon name="bolt" size={18} />
          </div>
          <div>
            <div style={{ fontWeight: 500, marginBottom: 3 }}>No test runs yet</div>
            <div style={{ fontSize: 13, color: "var(--text-2)" }}>
              Trigger a workflow from the <a href="../../actions" target="_blank" rel="noopener" style={{ color: "var(--accent)" }}>GitHub Actions tab</a> — results will appear here after the first run completes and the report is published.
            </div>
          </div>
        </div>
      )}
      {/* Hero header */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 24, alignItems: "end", marginBottom: 4 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
            <Pill kind="run">live · run #{RUN_META.id.slice(-4)}</Pill>
            <span className="mono" style={{ fontSize: 12, color: "var(--text-3)" }}>
              <Icon name="branch" size={12} /> {RUN_META.branch} · <Icon name="commit" size={12} /> {RUN_META.commit}
            </span>
          </div>
          <h1 className="h1">Test Suite Report</h1>
          <p className="lead">
            Qatarat (قطرات) — Flutter mobile app on Android &amp; iOS. {MAESTRO_FLOWS.length} Maestro flows, {APPIUM_TESTS.reduce((s, f) => s + f.tests.length, 0)} Appium deep tests, run continuously via GitHub Actions.
          </p>
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
          <span style={{ fontSize: 11, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: ".1em", fontWeight: 500 }}>Device</span>
          <span className="mono" style={{ fontSize: 12.5, color: "var(--text)" }}>{RUN_META.device}</span>
          <span className="mono" style={{ fontSize: 11.5, color: "var(--text-3)" }}>Flutter {RUN_META.flutterVersion}</span>
        </div>
      </div>

      {/* Stat row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
        <Stat label="Pass Rate" value={passRate} decimals={1} suffix="%" color={neverRan ? "var(--text-3)" : "var(--pass)"} sub={neverRan ? "no runs yet" : `${counts.pass} of ${total} tests`} />
        <Stat label="Total Tests" value={MAESTRO_FLOWS.length + APPIUM_TESTS.reduce((s, f) => s + f.tests.length, 0)} sub={`${MAESTRO_FLOWS.length} flows · ${APPIUM_TESTS.reduce((s, f) => s + f.tests.length, 0)} deep tests`} />
        <Stat label="Run Duration" value={RUN_META.duration / 60} decimals={1} suffix="m" sub={neverRan ? "no runs yet" : "this run"} />
        <Stat label="Executed" value={ranCount} sub={`of ${MAESTRO_FLOWS.length + APPIUM_TESTS.reduce((s, f) => s + f.tests.length, 0)} tests`} />
      </div>

      {/* Donut + History */}
      <div style={{ display: "grid", gridTemplateColumns: "minmax(260px, 320px) 1fr", gap: 16 }}>
        <div className="card">
          <div className="card-head"><h3>Run breakdown</h3><span className="sub">last execution</span></div>
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
                { label: "Passed", value: counts.pass, color: "var(--pass)" },
                { label: "Flaky",  value: counts.flaky, color: "var(--flaky)" },
                { label: "Failed", value: counts.fail, color: "var(--fail)" },
              ].map(s => (
                <div key={s.label} style={{ display: "flex", flexDirection: "column", gap: 2, padding: "8px 10px", background: "var(--surface-2)", borderRadius: 8, border: "1px solid var(--border)" }}>
                  <span style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "var(--text-3)" }}>
                    <span style={{ width: 6, height: 6, borderRadius: 50, background: s.color }} /> {s.label}
                  </span>
                  <span style={{ fontFamily: "Geist Mono", fontSize: 18, color: "var(--text)", fontWeight: 500 }}>{s.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-head between" style={{ display: "flex", justifyContent: "space-between" }}>
            <div className="row" style={{ gap: 10 }}>
              <h3>30-day trend</h3>
              <span className="sub">last 30 nightly runs</span>
            </div>
            <div className="row" style={{ gap: 16, fontSize: 11.5, color: "var(--text-3)" }}>
              <span style={{ display: "flex", alignItems: "center", gap: 6 }}><span style={{ width: 8, height: 8, borderRadius: 2, background: "var(--pass)" }} />pass</span>
              <span style={{ display: "flex", alignItems: "center", gap: 6 }}><span style={{ width: 8, height: 8, borderRadius: 2, background: "var(--flaky)" }} />flaky</span>
              <span style={{ display: "flex", alignItems: "center", gap: 6 }}><span style={{ width: 8, height: 8, borderRadius: 2, background: "var(--fail)" }} />fail</span>
            </div>
          </div>
          <div className="card-body" style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <BarChart data={HISTORY} height={130} />
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginTop: 4 }}>
              <div style={{ padding: 12, background: "var(--surface-2)", borderRadius: 10, border: "1px solid var(--border)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                  <span style={{ fontSize: 11.5, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: ".08em" }}>Pass rate</span>
                  <span className="mono" style={{ fontSize: 12, color: "var(--pass)" }}>{passSeries[passSeries.length - 1].toFixed(1)}%</span>
                </div>
                <Sparkline data={passSeries} color="oklch(74% 0.18 155)" height={36} width={260}
                           label="pass rate" format={(v) => `${v.toFixed(1)}%`}
                           labelForIndex={(i) => {
                             const days = passSeries.length - 1 - i;
                             return days === 0 ? "Today" : `${days} day${days===1?"":"s"} ago`;
                           }} />
              </div>
              <div style={{ padding: 12, background: "var(--surface-2)", borderRadius: 10, border: "1px solid var(--border)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                  <span style={{ fontSize: 11.5, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: ".08em" }}>Avg duration</span>
                  <span className="mono" style={{ fontSize: 12, color: "var(--accent)" }}>{fmtDur(durationSeries[durationSeries.length - 1])}</span>
                </div>
                <Sparkline data={durationSeries} color="var(--accent)" height={36} width={260}
                           label="run duration" format={fmtDur}
                           labelForIndex={(i) => {
                             const days = durationSeries.length - 1 - i;
                             return days === 0 ? "Today" : `${days} day${days===1?"":"s"} ago`;
                           }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Issues + commits */}
      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 16 }}>
        <div className="card">
          <div className="card-head">
            <h3>Issues to look at</h3>
            <span className="sub">{failingFlows.length + failingAppium.length} active</span>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            {[...failingFlows.map(f => ({
              kind: "Maestro flow", title: f.name, group: f.group, status: f.status, note: f.note,
            })), ...failingAppium.map(t => ({
              kind: "Appium test", title: t.name, group: t.file, status: t.status, note: t.error,
            }))].map((row, i) => (
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
                    {row.note || row.group}
                  </div>
                </div>
                <StatusPill status={row.status} />
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-head"><h3>Recent commits</h3><span className="sub">main branch</span></div>
          <div className="card-body" style={{ padding: 0 }}>
            {COMMITS.slice(0, 5).map(c => {
              const total = c.tests;
              return (
                <div key={c.sha} style={{ padding: "12px 16px", borderBottom: "1px solid var(--border)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                    <span className="mono" style={{ fontSize: 11.5, color: "var(--accent)", background: "var(--accent-2)", padding: "1px 6px", borderRadius: 4 }}>{c.sha}</span>
                    <span style={{ fontSize: 13, color: "var(--text)", flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{c.msg}</span>
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "auto 1fr auto", gap: 10, alignItems: "center" }}>
                    <span style={{ fontSize: 11, color: "var(--text-3)", fontFamily: "Geist Mono" }}>{c.author} · {c.time}</span>
                    <CoverageBar pass={c.pass} flaky={c.flaky} fail={c.fail} height={5} />
                    <span className="mono" style={{ fontSize: 11, color: "var(--text-3)" }}>{c.pass}/{total}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

window.OverviewView = OverviewView;
