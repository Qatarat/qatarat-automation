// App shell — sidebar nav, tweaks, view router
const { OverviewView, FlowsView, AppiumView, PipelineView, HistoryView } = window;

// Hex → accent OKLCH mapping. TweakColor stores hex; we translate to CSS vars.
const ACCENTS = {
  "#34cdda": { color: "oklch(74% 0.16 195)", glow: "oklch(74% 0.16 195 / .14)" }, // teal
  "#4dd396": { color: "oklch(74% 0.18 155)", glow: "oklch(74% 0.18 155 / .14)" }, // emerald
  "#b48dff": { color: "oklch(74% 0.18 290)", glow: "oklch(74% 0.18 290 / .14)" }, // violet
  "#ff6b8a": { color: "oklch(72% 0.20 15)",  glow: "oklch(72% 0.20 15 / .14)" },  // rose
  "#f5b94d": { color: "oklch(80% 0.16 75)",  glow: "oklch(80% 0.16 75 / .14)" },  // amber
};

const App = () => {
  const defaults = window.__QATARAT_DEFAULTS;
  const [t, setTweak] = useTweaks(defaults);
  const view = t.view || "overview";
  const { RUN_META } = window.QATARAT_DATA;
  const neverRan = RUN_META.neverRan || !RUN_META.startedAt;

  // Apply accent + density to root
  useEffect(() => {
    const a = ACCENTS[t.accent] || ACCENTS["#34cdda"];
    document.documentElement.style.setProperty("--accent", a.color);
    document.documentElement.style.setProperty("--accent-2", a.glow);
    document.documentElement.setAttribute("data-density", t.density || "cozy");
  }, [t.accent, t.density]);

  const navItems = [
    { id: "overview", label: "Overview",      icon: "overview", count: null },
    { id: "flows",    label: "Maestro flows", icon: "flows",    count: window.QATARAT_DATA.MAESTRO_FLOWS.length },
    { id: "appium",   label: "Appium tests",  icon: "appium",   count: window.QATARAT_DATA.APPIUM_TESTS.reduce((s, f) => s + f.tests.length, 0) },
    { id: "pipeline", label: "CI / CD",       icon: "pipeline", count: window.QATARAT_DATA.CI_WORKFLOWS.length },
    { id: "history",  label: "History",       icon: "history",  count: null },
  ];

  const ViewCmp = { overview: OverviewView, flows: FlowsView, appium: AppiumView, pipeline: PipelineView, history: HistoryView }[view];
  const crumbLabel = navItems.find(n => n.id === view)?.label || "Overview";

  return (
    <div className="app">
      <aside className="side" data-screen-label="Sidebar">
        <div className="brand">
          <div className="brand-mark" />
          <div className="brand-name">
            <b>Qatarat</b>
            <span>قطرات · test suite</span>
          </div>
        </div>

        <nav className="nav">
          <div className="nav-section">Reports</div>
          {navItems.map(n => (
            <div key={n.id} className={`nav-item ${view === n.id ? "active" : ""}`} onClick={() => setTweak("view", n.id)}>
              <span className="ico"><Icon name={n.icon} size={15} /></span>
              <span>{n.label}</span>
              {n.count != null && <span className="count">{n.count}</span>}
            </div>
          ))}

          <div className="nav-section">Targets</div>
          <div className="nav-item">
            <span className="ico"><Icon name="phone" size={15} /></span>
            <span>Android · API 34</span>
            <span style={{ width: 6, height: 6, borderRadius: 50, background: "var(--pass)", boxShadow: "0 0 8px var(--pass)" }} />
          </div>
          <div className="nav-item">
            <span className="ico"><Icon name="phone" size={15} /></span>
            <span>iOS · Simulator</span>
            <span style={{ width: 6, height: 6, borderRadius: 50, background: "var(--idle)" }} />
          </div>
        </nav>

        <div className="side-foot">
          <div className="row">
            <div className="avatar">M</div>
            <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.15 }}>
              <span style={{ fontSize: 12.5, color: "var(--text)", fontWeight: 500 }}>mejbaurbahar</span>
              <span style={{ fontSize: 11, color: "var(--text-3)" }}>QA · Owner</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main">
        <div className="topbar">
          <div className="crumbs">
            <span>Qatarat</span>
            <span className="sep">/</span>
            <b>{crumbLabel}</b>
          </div>
          <div className="top-actions">
            <span className="mono" style={{ fontSize: 11.5, color: "var(--text-3)", display: "flex", alignItems: "center", gap: 8 }}>
              {neverRan ? (
                <>
                  <span style={{ width: 6, height: 6, borderRadius: 50, background: "var(--idle)" }} />
                  no runs yet · trigger a workflow to populate
                </>
              ) : (
                <>
                  <span style={{ width: 6, height: 6, borderRadius: 50, background: "var(--pass)", boxShadow: "0 0 8px var(--pass)" }} />
                  last run · {RUN_META.startedAt}
                </>
              )}
            </span>
          </div>
        </div>

        <div className="content" data-screen-label={crumbLabel}>
          {ViewCmp && <ViewCmp />}
          <footer style={{
            marginTop: 56, paddingTop: 24, paddingBottom: 8,
            borderTop: "1px solid var(--border)",
            display: "flex", justifyContent: "space-between", alignItems: "center", gap: 20, flexWrap: "wrap",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
              <div style={{
                width: 42, height: 42, borderRadius: 12,
                background: "linear-gradient(135deg, color-mix(in oklch, var(--accent) 30%, var(--surface-2)), var(--surface-2))",
                border: "1px solid color-mix(in oklch, var(--accent) 25%, var(--border))",
                display: "grid", placeItems: "center",
                color: "var(--accent)", fontFamily: "Geist", fontWeight: 600, fontSize: 16, letterSpacing: "-0.02em",
              }}>MBF</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                <span style={{ fontSize: 10.5, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: ".12em", fontWeight: 500 }}>Built by</span>
                <span style={{ fontSize: 15, color: "var(--text)", fontWeight: 500, letterSpacing: "-0.005em" }}>Mejbaur Bahar Fagun</span>
                <span style={{ fontSize: 12, color: "var(--text-2)" }}>Senior Software Engineer · QA (IV)</span>
              </div>
            </div>
            <a href="https://www.linkedin.com/in/mejbaur/" target="_blank" rel="noopener noreferrer"
               className="btn"
               style={{ textDecoration: "none", height: 36, padding: "0 14px" }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.38-1.85 3.61 0 4.28 2.38 4.28 5.47v6.27zM5.34 7.43a2.07 2.07 0 1 1 0-4.14 2.07 2.07 0 0 1 0 4.14zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.72v20.56C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.72V1.72C24 .77 23.2 0 22.22 0z"/>
              </svg>
              Connect on LinkedIn
              <Icon name="arrow" size={12} />
            </a>
          </footer>
        </div>
      </main>

      <TweaksPanel title="Tweaks">
        <TweakSection label="Theme" />
        <TweakColor
          label="Accent"
          value={t.accent}
          onChange={(v) => setTweak("accent", v)}
          options={Object.keys(ACCENTS)}
        />
        <TweakSection label="Layout" />
        <TweakRadio
          label="Density"
          value={t.density}
          onChange={(v) => setTweak("density", v)}
          options={[
            { value: "compact", label: "Tight" },
            { value: "cozy",    label: "Cozy" },
            { value: "comfy",   label: "Comfy" },
          ]}
        />
        <TweakSection label="View" />
        <TweakSelect
          label="Active view"
          value={t.view}
          onChange={(v) => setTweak("view", v)}
          options={navItems.map(n => ({ value: n.id, label: n.label }))}
        />
      </TweaksPanel>
    </div>
  );
};

ReactDOM.createRoot(document.getElementById("root")).render(
  <TipProvider><App /></TipProvider>
);
