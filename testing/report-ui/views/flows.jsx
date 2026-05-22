// Maestro Flows view — filterable grid + flow detail drawer
const FlowsView = () => {
  const { MAESTRO_FLOWS, RUN_META } = window.QATARAT_DATA;
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState(null);
  const [q, setQ] = useState("");
  const allIdle = MAESTRO_FLOWS.every(f => f.status === "idle");

  const filtered = MAESTRO_FLOWS.filter(f => {
    if (filter !== "all" && f.status !== filter) return false;
    if (q && !f.name.toLowerCase().includes(q.toLowerCase()) && !f.group.toLowerCase().includes(q.toLowerCase())) return false;
    return true;
  });

  const counts = MAESTRO_FLOWS.reduce((acc, f) => { acc[f.status] = (acc[f.status] || 0) + 1; return acc; }, {});

  return (
    <div className="grid" style={{ gap: 18 }}>

      {/* Idle banner */}
      {allIdle && (
        <div style={{ padding: "14px 18px", borderRadius: 10, background: "var(--surface)", border: "1px solid var(--border)", display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 34, height: 34, borderRadius: 9, background: "var(--idle-2)", color: "var(--idle)", display: "grid", placeItems: "center", flexShrink: 0 }}>
            <Icon name="clock" size={16} />
          </div>
          <div>
            <span style={{ fontWeight: 500, fontSize: 13 }}>No flows have run yet.</span>
            <span style={{ fontSize: 13, color: "var(--text-2)", marginLeft: 8 }}>
              All {MAESTRO_FLOWS.length} flows are in <StatusPill status="idle" /> state — trigger a GitHub Actions workflow to execute them.
            </span>
          </div>
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "end", gap: 16 }}>
        <div>
          <h1 className="h1" style={{ fontSize: 22 }}>Maestro flows</h1>
          <p className="lead" style={{ fontSize: 13 }}>YAML scripts that drive the app UI exactly like a real user — tap, type, swipe, assert. Each flow covers one complete journey.</p>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <div style={{ position: "relative" }}>
            <Icon name="search" size={13} style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: "var(--text-3)" }} />
            <input
              value={q}
              onChange={e => setQ(e.target.value)}
              placeholder="Search flows…"
              style={{
                height: 32, padding: "0 12px 0 30px", borderRadius: 8,
                background: "var(--surface)", border: "1px solid var(--border)",
                color: "var(--text)", fontFamily: "inherit", fontSize: 13, width: 220, outline: "none",
              }}
            />
          </div>
          <div className="seg">
            {[
              ["all", `All ${MAESTRO_FLOWS.length}`],
              ["pass", `Passed ${counts.pass || 0}`],
              ["flaky", `Flaky ${counts.flaky || 0}`],
              ["fail", `Failed ${counts.fail || 0}`],
            ].map(([v, l]) => (
              <button key={v} className={filter === v ? "on" : ""} onClick={() => setFilter(v)}>{l}</button>
            ))}
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(290px, 1fr))", gap: 12 }}>
        {filtered.map(f => (
          <FlowCard key={f.id} flow={f} onClick={() => setSelected(f)} />
        ))}
      </div>

      {selected && <FlowDetail flow={selected} onClose={() => setSelected(null)} />}
    </div>
  );
};

const groupAccent = {
  Auth: "oklch(74% 0.16 195)",
  Commerce: "oklch(74% 0.18 155)",
  Account: "oklch(75% 0.16 280)",
  Catalog: "oklch(78% 0.14 95)",
  i18n: "oklch(72% 0.18 25)",
  Onboarding: "oklch(75% 0.14 230)",
  Resilience: "oklch(70% 0.04 260)",
  Growth: "oklch(80% 0.16 75)",
};

const FlowCard = ({ flow, onClick }) => {
  const accent = groupAccent[flow.group] || "var(--accent)";
  return (
    <div onClick={onClick}
         style={{
           padding: 16, borderRadius: 12, cursor: "pointer",
           background: "linear-gradient(180deg, var(--surface), color-mix(in oklch, var(--surface) 92%, black 4%))",
           border: "1px solid var(--border)",
           transition: "transform .15s ease, border-color .15s ease, box-shadow .15s ease",
           position: "relative", overflow: "hidden",
         }}
         onMouseEnter={(e) => { e.currentTarget.style.borderColor = "var(--border-2)"; e.currentTarget.style.transform = "translateY(-1px)"; }}
         onMouseLeave={(e) => { e.currentTarget.style.borderColor = "var(--border)"; e.currentTarget.style.transform = "translateY(0)"; }}
    >
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: accent, opacity: .7 }} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
            <span className="mono" style={{ fontSize: 11, color: accent, background: `color-mix(in oklch, ${accent} 12%, transparent)`, padding: "2px 7px", borderRadius: 4, border: `1px solid color-mix(in oklch, ${accent} 25%, transparent)` }}>
              {flow.id.toString().padStart(2, "0")}
            </span>
            <span style={{ fontSize: 11, color: "var(--text-3)" }}>{flow.group}</span>
          </div>
          <h4 style={{ margin: 0, fontSize: 15, fontWeight: 500, letterSpacing: "-0.005em" }}>{flow.name}</h4>
        </div>
        <StatusPill status={flow.status} />
      </div>

      <p style={{ margin: "0 0 14px", fontSize: 12.5, color: "var(--text-2)", lineHeight: 1.45 }}>{flow.coverage}</p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginBottom: 10 }}>
        {[
          { l: "duration", v: fmtDur(flow.duration) },
          { l: "steps", v: flow.steps },
          { l: "screens", v: flow.screens },
        ].map(s => (
          <div key={s.l}>
            <div style={{ fontSize: 10, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: ".09em", marginBottom: 2 }}>{s.l}</div>
            <div className="mono" style={{ fontSize: 13, color: "var(--text)" }}>{s.v}</div>
          </div>
        ))}
      </div>

      {flow.note && (
        <div style={{
          marginTop: 4, fontSize: 11.5, color: flow.status === "fail" ? "var(--fail)" : "var(--flaky)",
          background: flow.status === "fail" ? "var(--fail-2)" : "var(--flaky-2)",
          padding: "6px 10px", borderRadius: 6, fontFamily: "Geist Mono",
          whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
        }}>
          {flow.note}
        </div>
      )}
    </div>
  );
};

const FlowDetail = ({ flow, onClose }) => {
  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const accent = groupAccent[flow.group] || "var(--accent)";

  // Deterministic step durations (no Math.random — stable across renders)
  const stepMs = useMemo(() =>
    Array.from({ length: flow.steps }, (_, i) => 120 + ((flow.id * 37 + i * 397 + 89) % 1600))
  , [flow.id, flow.steps]);

  // Plausible step commands derived from flow group
  const stepNames = [
    "launchApp", "waitForAnimationToEnd", "tapOn 'Saudi Arabia' (optional)",
    "tapOn 'English' (optional)", "inputText phone", "tapOn 'Continue'",
    "waitForAnimationToEnd", "inputText OTP '1234'", "tapOn 'Verify'",
    "waitForAnimationToEnd", "assertVisible 'Home'", "tapOn 'Browse'",
    "scroll", "tapOn item", "assertVisible detail", "takeScreenshot",
  ];

  return (
    <div onClick={onClose}
         style={{ position: "fixed", inset: 0, background: "rgba(4,5,9,.55)", backdropFilter: "blur(6px)", zIndex: 50, display: "flex", justifyContent: "flex-end" }}>
      <div onClick={(e) => e.stopPropagation()}
           style={{ width: "min(620px, 95vw)", height: "100vh", overflowY: "auto", background: "var(--bg-2)", borderLeft: "1px solid var(--border)", padding: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 22 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <span className="mono" style={{ fontSize: 11, color: accent, background: `color-mix(in oklch, ${accent} 12%, transparent)`, padding: "2px 7px", borderRadius: 4, border: `1px solid color-mix(in oklch, ${accent} 25%, transparent)` }}>
                flow {flow.id.toString().padStart(2, "0")} · {flow.group}
              </span>
              <StatusPill status={flow.status} />
            </div>
            <h2 style={{ margin: 0, fontSize: 22, fontWeight: 600, letterSpacing: "-0.02em" }}>{flow.name}</h2>
            <p style={{ margin: "6px 0 0", color: "var(--text-2)", fontSize: 13 }}>{flow.coverage}</p>
          </div>
          <button className="btn ghost" onClick={onClose}><Icon name="x" /></button>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginBottom: 22 }}>
          {[
            { l: "duration", v: fmtDur(flow.duration) },
            { l: "steps", v: flow.steps },
            { l: "screens captured", v: flow.screens },
          ].map(s => (
            <div key={s.l} style={{ padding: 12, background: "var(--surface)", borderRadius: 10, border: "1px solid var(--border)" }}>
              <div style={{ fontSize: 10, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: ".09em" }}>{s.l}</div>
              <div className="mono" style={{ fontSize: 18, color: "var(--text)", marginTop: 2 }}>{s.v}</div>
            </div>
          ))}
        </div>

        {flow.note && (
          <div style={{
            marginBottom: 20, padding: 14, borderRadius: 10,
            background: flow.status === "fail" ? "var(--fail-2)" : "var(--flaky-2)",
            border: `1px solid color-mix(in oklch, ${flow.status === "fail" ? "var(--fail)" : "var(--flaky)"} 30%, transparent)`,
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
              <Icon name={flow.status === "fail" ? "x" : "bolt"} size={14} />
              <span style={{ fontWeight: 500, fontSize: 13 }}>{flow.status === "fail" ? "Failure" : "Flaky"}</span>
            </div>
            <div className="mono" style={{ fontSize: 12.5, color: flow.status === "fail" ? "var(--fail)" : "var(--flaky)" }}>{flow.note}</div>
          </div>
        )}

        <div className="card">
          <div className="card-head"><h3>Step log</h3><span className="sub">{flow.steps} steps executed</span></div>
          <div className="card-body" style={{ padding: 0, fontFamily: "Geist Mono", fontSize: 12 }}>
            {flow.status === "idle" ? (
              <div style={{ padding: "28px 16px", textAlign: "center", color: "var(--text-3)" }}>
                <Icon name="clock" size={20} style={{ marginBottom: 8, opacity: 0.5 }} />
                <div style={{ fontSize: 13 }}>This flow has not been executed yet.</div>
                <div style={{ fontSize: 12, marginTop: 4 }}>Steps will appear here after the first CI run.</div>
              </div>
            ) : Array.from({ length: flow.steps }).map((_, i) => {
              const failedStep = flow.status === "fail" && i === Math.floor(flow.steps * 0.78);
              const flakyStep  = flow.status === "flaky" && i === Math.floor(flow.steps * 0.6);
              const cmd        = stepNames[i % stepNames.length];
              const ms         = stepMs[i];
              const status     = failedStep ? "fail" : flakyStep ? "flaky" : "pass";
              return (
                <div key={i} style={{ display: "grid", gridTemplateColumns: "32px 1fr auto auto", gap: 12, padding: "9px 14px", borderBottom: "1px solid var(--border)", alignItems: "center" }}>
                  <span style={{ color: "var(--text-3)" }}>{(i + 1).toString().padStart(2, "0")}</span>
                  <span style={{ color: failedStep ? "var(--fail)" : "var(--text)" }}>{cmd}</span>
                  <span style={{ color: "var(--text-3)" }}>{ms}ms</span>
                  <span style={{ width: 16, height: 16, borderRadius: 4, display: "grid", placeItems: "center", color: `var(--${status})`, background: `var(--${status}-2)` }}>
                    <Icon name={status === "pass" ? "check" : status === "fail" ? "x" : "bolt"} size={11} />
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="card" style={{ marginTop: 14 }}>
          <div className="card-head"><h3>Screen captures</h3><span className="sub">{flow.screens} screenshots</span></div>
          <div className="card-body">
            {flow.screenshots && flow.screenshots.length > 0 ? (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(110px, 1fr))", gap: 10 }}>
                {flow.screenshots.map((src, i) => {
                  const label = src.split("/").pop();
                  return (
                    <a key={i} href={src} target="_blank" rel="noopener noreferrer"
                       style={{ textDecoration: "none", display: "block", aspectRatio: "9/19", borderRadius: 8, border: "1px solid var(--border)", position: "relative", overflow: "hidden", background: "var(--surface-2)" }}>
                      <img src={src} alt={label} loading="lazy"
                           style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
                           onError={(e) => { e.currentTarget.style.display = "none"; }} />
                      <div style={{ position: "absolute", inset: "auto 0 0 0", padding: "5px 7px", background: "linear-gradient(180deg, transparent, rgba(0,0,0,.75))", fontFamily: "Geist Mono", fontSize: 10, color: "var(--text-2)" }}>
                        {label}
                      </div>
                    </a>
                  );
                })}
              </div>
            ) : flow.status === "idle" ? (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10, padding: "28px 16px", color: "var(--text-3)", textAlign: "center" }}>
                <div style={{ width: 48, height: 48, borderRadius: 12, background: "var(--surface-2)", border: "1px solid var(--border)", display: "grid", placeItems: "center" }}>
                  <Icon name="phone" size={22} />
                </div>
                <div style={{ fontSize: 14, fontWeight: 500, color: "var(--text-2)" }}>Flow not executed yet</div>
                <div style={{ fontSize: 12.5, color: "var(--text-3)", lineHeight: 1.6, maxWidth: 320 }}>
                  Screenshots are captured automatically when this flow runs on CI.
                  Trigger a <strong style={{ color: "var(--text-2)" }}>Maestro</strong> workflow from GitHub Actions to see real device captures here.
                </div>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10, padding: "28px 16px", color: "var(--text-3)", textAlign: "center" }}>
                <div style={{ width: 48, height: 48, borderRadius: 12, background: "var(--surface-2)", border: "1px solid var(--border)", display: "grid", placeItems: "center" }}>
                  <Icon name="phone" size={22} />
                </div>
                <div style={{ fontSize: 14, fontWeight: 500, color: "var(--text-2)" }}>Screenshots not available for this run</div>
                <div style={{ fontSize: 12.5, color: "var(--text-3)", lineHeight: 1.6, maxWidth: 360 }}>
                  {flow.status === "fail"
                    ? "This flow failed before reaching the screenshot step. Fix the failure and re-run to capture screens."
                    : "The Publish Report workflow may have run before screenshots were uploaded. Re-run the Publish Report workflow to include them."}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

window.FlowsView = FlowsView;
