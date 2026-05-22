// History view — 30-day heatmap + commit timeline
const HistoryView = () => {
  const { COMMITS, HISTORY } = window.QATARAT_DATA;
  const tip = useTip();

  const hasAnyData = HISTORY.some(d => d.total > 0);

  return (
    <div className="grid" style={{ gap: 18 }}>
      <div>
        <h1 className="h1" style={{ fontSize: 22 }}>Run history</h1>
        <p className="lead" style={{ fontSize: 13 }}>
          Every push to main runs the smoke suite. Nightly runs the full regression.
          Each cell in the heatmap below is one day — hover to see pass/fail counts.
        </p>
      </div>

      {/* Calendar heatmap */}
      <div className="card">
        <div className="card-head">
          <h3>30-day heatmap</h3>
          <span className="sub">pass rate per day · {HISTORY.filter(d => d.total > 0).length} days with data</span>
        </div>
        <div className="card-body">
          {!hasAnyData && (
            <div style={{ marginBottom: 14, padding: "10px 14px", borderRadius: 8, background: "var(--surface-2)", border: "1px solid var(--border)", fontSize: 12.5, color: "var(--text-3)", display: "flex", alignItems: "center", gap: 10 }}>
              <Icon name="history" size={15} style={{ flexShrink: 0 }} />
              No run history yet. All 30 cells will fill in as nightly runs execute over the coming days.
            </div>
          )}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(30, 1fr)", gap: 4 }}>
            {HISTORY.map((d, i) => {
              // Guard against div-by-zero: empty days have no colour, not "bad" colour
              const hasData = d.total > 0;
              const rate = hasData ? d.pass / d.total : null;
              const color = !hasData
                ? "var(--surface-2)"
                : rate >= 0.97 ? "oklch(74% 0.18 155)"
                : rate >= 0.90 ? "oklch(74% 0.18 155 / .55)"
                : rate >= 0.80 ? "oklch(80% 0.16 75 / .8)"
                : "oklch(70% 0.22 18 / .8)";
              const label = d.day === 0 ? "Today" : `${d.day} day${d.day === 1 ? "" : "s"} ago`;
              return (
                <div key={i}
                     onMouseEnter={(e) => tip.show(e, (
                       <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                         <div style={{ color: "var(--text)", fontWeight: 500, fontSize: 12.5 }}>{label}</div>
                         <div style={{ height: 1, background: "var(--border)", margin: "2px 0" }} />
                         {hasData ? (
                           <>
                             <TipRow label="passed"    value={d.pass}  color="oklch(74% 0.18 155)" />
                             {d.flaky > 0 && <TipRow label="flaky" value={d.flaky} color="oklch(80% 0.16 75)" />}
                             {d.fail  > 0 && <TipRow label="failed" value={d.fail} color="oklch(70% 0.22 18)" />}
                             <TipRow label="pass rate" value={`${(rate * 100).toFixed(1)}%`} />
                             <TipRow label="duration"  value={fmtDur(d.duration)} />
                           </>
                         ) : (
                           <div style={{ fontSize: 12, color: "var(--text-3)" }}>No run on this day</div>
                         )}
                       </div>
                     ))}
                     onMouseMove={tip.move}
                     onMouseLeave={tip.hide}
                     style={{
                       aspectRatio: "1", borderRadius: 4,
                       background: color,
                       border: "1px solid var(--border)",
                       cursor: hasData ? "pointer" : "default",
                       transition: "transform .12s ease",
                     }}
                     onPointerEnter={(e) => { if (hasData) e.currentTarget.style.transform = "scale(1.15)"; }}
                     onPointerLeave={(e) => e.currentTarget.style.transform = "scale(1)"} />
              );
            })}
          </div>

          {/* Legend */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 14, fontSize: 11, color: "var(--text-3)" }}>
            <span className="mono">30 days ago</span>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span>no data</span>
              <span style={{ width: 12, height: 12, borderRadius: 3, background: "var(--surface-2)", border: "1px solid var(--border)" }} />
              <span style={{ marginLeft: 6 }}>worse</span>
              {[0.3, 0.55, 0.8, 1].map((o, i) => (
                <span key={i} style={{ width: 12, height: 12, borderRadius: 3, background: `oklch(74% 0.18 155 / ${o})`, border: "1px solid var(--border)" }} />
              ))}
              <span>better</span>
            </div>
            <span className="mono">today</span>
          </div>
        </div>
      </div>

      {/* Commit timeline */}
      <div className="card">
        <div className="card-head">
          <h3>Commits</h3>
          <span className="sub">main branch · {COMMITS.length > 0 ? `last ${Math.min(COMMITS.length, 8)}` : "none yet"}</span>
        </div>
        <div className="card-body" style={{ padding: COMMITS.length === 0 ? 16 : 0 }}>
          {COMMITS.length === 0 ? (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8, padding: "24px 0", color: "var(--text-3)", textAlign: "center" }}>
              <Icon name="commit" size={26} style={{ opacity: 0.35 }} />
              <span style={{ fontSize: 13 }}>No commit history available yet</span>
              <span style={{ fontSize: 12, maxWidth: 300, lineHeight: 1.5 }}>
                Commit history is read from <span className="mono" style={{ fontSize: 11 }}>git log</span> at publish time.
                It will appear after your first CI run.
              </span>
            </div>
          ) : COMMITS.map((c, i) => {
            const hasData = c.hasData !== false && c.tests > 0;
            const overall = !hasData ? "idle" : c.fail > 0 ? "fail" : c.flaky > 0 ? "flaky" : "pass";
            return (
              <div key={c.sha} style={{
                position: "relative", display: "grid", gridTemplateColumns: "auto 1fr auto",
                gap: 16, padding: "16px 20px", borderBottom: "1px solid var(--border)",
              }}>
                {/* timeline rail */}
                <div style={{ position: "relative", display: "flex", justifyContent: "center", width: 24 }}>
                  {i < COMMITS.length - 1 && (
                    <div style={{ position: "absolute", top: 18, bottom: -16, width: 2, background: "var(--border)" }} />
                  )}
                  <div style={{
                    width: 14, height: 14, borderRadius: 50, marginTop: 4,
                    background: overall === "idle" ? "var(--surface-3)" : `var(--${overall})`,
                    boxShadow: overall === "idle" ? "none" : `0 0 0 4px color-mix(in oklch, var(--${overall}) 15%, transparent), inset 0 0 0 2px var(--bg-2)`,
                    border: overall === "idle" ? "1px solid var(--border)" : "none",
                    position: "relative", zIndex: 1,
                  }} />
                </div>
                <div style={{ minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
                    <span className="mono" style={{ fontSize: 12, color: "var(--accent)", background: "var(--accent-2)", padding: "2px 8px", borderRadius: 5, border: "1px solid color-mix(in oklch, var(--accent) 25%, transparent)" }}>{c.sha}</span>
                    <span style={{ fontSize: 14, color: "var(--text)", fontWeight: 500 }}>{c.msg}</span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 12, color: "var(--text-3)" }}>
                    <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
                      <Icon name="user" size={11} /> {c.author}
                    </span>
                    <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
                      <Icon name="clock" size={11} /> {c.time}
                    </span>
                    {hasData && (
                      <span className="mono" style={{ color: "var(--text-2)" }}>{c.pass} pass · {c.flaky} flaky · {c.fail} fail</span>
                    )}
                  </div>
                  {hasData && (
                    <div style={{ marginTop: 10, maxWidth: 360 }}>
                      <CoverageBar pass={c.pass} flaky={c.flaky} fail={c.fail} height={5} />
                    </div>
                  )}
                  {!hasData && (
                    <div style={{ marginTop: 6, fontSize: 11.5, color: "var(--text-3)", fontFamily: "Geist Mono" }}>
                      No test run data for this commit
                    </div>
                  )}
                </div>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 8 }}>
                  {hasData ? (
                    <StatusPill status={overall} />
                  ) : (
                    <StatusPill status="idle" />
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

window.HistoryView = HistoryView;
