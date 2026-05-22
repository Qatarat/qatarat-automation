// CI/CD pipeline view — workflows + visualized pipeline
const PipelineView = () => {
  const { CI_WORKFLOWS, RUN_META } = window.QATARAT_DATA;
  const neverRan = RUN_META.neverRan || CI_WORKFLOWS.every(w => w.status === "idle");
  const idleCount = CI_WORKFLOWS.filter(w => w.status === "idle").length;

  return (
    <div className="grid" style={{ gap: 18 }}>
      <div>
        <h1 className="h1" style={{ fontSize: 22 }}>CI / CD pipeline</h1>
        <p className="lead" style={{ fontSize: 13 }}>
          GitHub Actions on Ubuntu runners with Android emulator (API 33).
          {neverRan
            ? " No workflows have been triggered yet — see below to get started."
            : ` ${CI_WORKFLOWS.length - idleCount} of ${CI_WORKFLOWS.length} workflows have run.`}
        </p>
      </div>

      {/* Getting started when nothing ran */}
      {neverRan && (
        <div style={{ padding: "18px 20px", borderRadius: 12, background: "var(--surface)", border: "1px solid var(--border)" }}>
          <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 12, display: "flex", alignItems: "center", gap: 8 }}>
            <Icon name="bolt" size={15} style={{ color: "var(--accent)" }} />
            Getting started — how to run your first workflow
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 10 }}>
            {[
              { n: "1", title: "Smoke (fast)", desc: "5 core flows · ~10 min. Best for a quick sanity check after each push.", wf: "Maestro — Smoke (Android)" },
              { n: "2", title: "Full Regression", desc: "All 16 flows · ~30 min. Runs nightly via cron.", wf: "Maestro — Full Regression (Android)" },
              { n: "3", title: "Appium Deep Tests", desc: "22 Python/pytest tests · ~60 min. Verifies payment SDKs in depth.", wf: "Appium — Deep Tests (Android)" },
            ].map(s => (
              <div key={s.n} style={{ padding: "12px 14px", background: "var(--surface-2)", borderRadius: 9, border: "1px solid var(--border)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                  <span style={{ width: 22, height: 22, borderRadius: 50, background: "var(--accent-2)", color: "var(--accent)", fontFamily: "Geist Mono", fontSize: 11, fontWeight: 600, display: "grid", placeItems: "center", flexShrink: 0 }}>{s.n}</span>
                  <span style={{ fontWeight: 500, fontSize: 13 }}>{s.title}</span>
                </div>
                <p style={{ margin: "0 0 8px", fontSize: 12.5, color: "var(--text-2)", lineHeight: 1.5 }}>{s.desc}</p>
                <span className="mono" style={{ fontSize: 11, color: "var(--text-3)", background: "var(--surface)", border: "1px solid var(--border)", padding: "2px 8px", borderRadius: 4, display: "inline-block" }}>{s.wf}</span>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 12, fontSize: 12.5, color: "var(--text-3)" }}>
            Go to <strong style={{ color: "var(--text-2)" }}>GitHub → Actions tab</strong> → select a workflow → click <strong style={{ color: "var(--text-2)" }}>Run workflow</strong>. After it completes, "Publish Test Report" fires automatically and updates this page.
          </div>
        </div>
      )}

      {/* Pipeline diagram */}
      <div className="card">
        <div className="card-head"><h3>Pipeline</h3><span className="sub">push → install → test → publish</span></div>
        <div className="card-body">
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 0, alignItems: "stretch", position: "relative" }}>
            {[
              { label: "Source",  icon: "branch",   note: "Push to main or PR",         color: "oklch(70% 0.04 260)" },
              { label: "Install", icon: "bolt",     note: "APK install on emulator",    color: "oklch(74% 0.16 195)" },
              { label: "Maestro", icon: "flows",    note: "16 flows · ~30 min",         color: "oklch(74% 0.18 155)" },
              { label: "Appium",  icon: "appium",   note: "22 deep tests · ~60 min",    color: "oklch(80% 0.16 75)" },
              { label: "Publish", icon: "download", note: "GitHub Pages report",         color: "oklch(75% 0.16 280)" },
            ].map((s, i, arr) => (
              <div key={s.label} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10, position: "relative" }}>
                {i < arr.length - 1 && (
                  <div style={{
                    position: "absolute", top: 28, left: "60%", right: "-40%", height: 2,
                    background: `linear-gradient(90deg, ${s.color} 0%, ${arr[i+1].color} 100%)`,
                    opacity: 0.4,
                  }} />
                )}
                <div style={{
                  width: 56, height: 56, borderRadius: 14,
                  background: `linear-gradient(180deg, color-mix(in oklch, ${s.color} 16%, var(--surface)), var(--surface))`,
                  border: `1px solid color-mix(in oklch, ${s.color} 32%, var(--border))`,
                  display: "grid", placeItems: "center", color: s.color,
                  boxShadow: `0 12px 24px -16px color-mix(in oklch, ${s.color} 50%, transparent)`,
                  position: "relative", zIndex: 1,
                }}>
                  <Icon name={s.icon} size={22} />
                </div>
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 13, fontWeight: 500 }}>{s.label}</div>
                  <div className="mono" style={{ fontSize: 11, color: "var(--text-3)", marginTop: 2 }}>{s.note}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Workflows table */}
      <div className="card">
        <div className="card-head">
          <h3>Workflows</h3>
          <span className="sub">{CI_WORKFLOWS.length} configured · {CI_WORKFLOWS.length - idleCount} run</span>
        </div>
        <div className="card-body" style={{ padding: 0 }}>
          <table className="t">
            <thead>
              <tr>
                <th>Workflow</th>
                <th>Trigger</th>
                <th>Duration</th>
                <th>Last run</th>
                <th>Pass rate</th>
                <th style={{ textAlign: "right" }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {CI_WORKFLOWS.map(w => (
                <tr key={w.name}>
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                      <div style={{
                        width: 30, height: 30, borderRadius: 8,
                        background: w.status === "pass" ? "var(--pass-2)" : w.status === "fail" ? "var(--fail-2)" : "var(--idle-2)",
                        color: w.status === "pass" ? "var(--pass)" : w.status === "fail" ? "var(--fail)" : "var(--idle)",
                        display: "grid", placeItems: "center",
                      }}>
                        <Icon name={w.status === "pass" ? "check" : w.status === "fail" ? "x" : "clock"} size={14} />
                      </div>
                      <div>
                        <div className="name">{w.name}</div>
                        <div className="meta">{w.coverage}</div>
                      </div>
                    </div>
                  </td>
                  <td className="mono" style={{ fontSize: 12, color: "var(--text-2)" }}>{w.trigger}</td>
                  <td className="mono" style={{ fontSize: 12, color: "var(--text-2)" }}>{w.duration}</td>
                  <td className="mono" style={{ fontSize: 12, color: "var(--text-3)" }}>{w.lastRun}</td>
                  <td style={{ minWidth: 160 }}>
                    {w.status === "idle" ? (
                      <span style={{ fontSize: 12, color: "var(--text-3)" }}>awaiting first run</span>
                    ) : (
                      <>
                        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                          <div style={{ flex: 1, height: 5, background: "var(--surface-3)", borderRadius: 999, overflow: "hidden" }}>
                            <div style={{
                              width: `${w.passRate}%`, height: "100%",
                              background: w.passRate >= 95 ? "var(--pass)" : w.passRate >= 80 ? "var(--flaky)" : "var(--fail)",
                              transition: "width .6s ease",
                            }} />
                          </div>
                          <span className="mono" style={{ fontSize: 11.5, color: "var(--text-2)", minWidth: 40, textAlign: "right" }}>{w.passRate.toFixed(1)}%</span>
                        </div>
                        <div className="mono" style={{ fontSize: 10.5, color: "var(--text-3)", marginTop: 3 }}>{w.runs} run{w.runs !== 1 ? "s" : ""}</div>
                      </>
                    )}
                  </td>
                  <td style={{ textAlign: "right" }}><StatusPill status={w.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Tech stack */}
      <div className="card">
        <div className="card-head"><h3>Tech stack</h3><span className="sub">end-to-end</span></div>
        <div className="card-body">
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12 }}>
            {[
              { layer: "App under test",  tech: "Flutter / Dart",              icon: "phone",    c: "oklch(74% 0.16 195)", desc: "Qatarat — Arabic Islamic app for Android & iOS" },
              { layer: "UI automation",   tech: "Maestro 2.x",                 icon: "flows",    c: "oklch(74% 0.18 155)", desc: "YAML flows that simulate real user taps" },
              { layer: "Deep tests",      tech: "Appium 2.x + flutter-driver", icon: "appium",   c: "oklch(80% 0.16 75)",  desc: "Python/pytest for payment SDKs and data checks" },
              { layer: "Test language",   tech: "Python 3 + pytest",           icon: "bolt",     c: "oklch(75% 0.14 230)", desc: "Assertions, fixtures, parametrize decorators" },
              { layer: "Report",          tech: "Allure + GitHub Pages",       icon: "overview", c: "oklch(75% 0.16 280)", desc: "Auto-published HTML report after every run" },
              { layer: "CI / CD",         tech: "GitHub Actions",              icon: "pipeline", c: "oklch(70% 0.18 25)",  desc: "Free Ubuntu runners with KVM-accelerated emulator" },
            ].map(s => (
              <div key={s.layer} style={{ display: "flex", gap: 12, alignItems: "flex-start", padding: 12, background: "var(--surface-2)", borderRadius: 10, border: "1px solid var(--border)" }}>
                <div style={{
                  width: 36, height: 36, borderRadius: 9, flexShrink: 0, marginTop: 1,
                  background: `color-mix(in oklch, ${s.c} 14%, transparent)`,
                  border: `1px solid color-mix(in oklch, ${s.c} 30%, transparent)`,
                  color: s.c, display: "grid", placeItems: "center",
                }}>
                  <Icon name={s.icon} size={16} />
                </div>
                <div>
                  <div style={{ fontSize: 10.5, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: ".08em", marginBottom: 2 }}>{s.layer}</div>
                  <div style={{ fontSize: 13, color: "var(--text)", fontWeight: 500 }}>{s.tech}</div>
                  <div style={{ fontSize: 12, color: "var(--text-3)", marginTop: 3, lineHeight: 1.4 }}>{s.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

window.PipelineView = PipelineView;
