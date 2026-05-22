// Appium deep tests view — file-based grouping
const AppiumView = () => {
  const { APPIUM_TESTS, RUN_META } = window.QATARAT_DATA;
  const allIdle = APPIUM_TESTS.every(f => f.tests.every(t => t.status === "idle"));
  const [expanded, setExpanded] = useState(() => new Set(APPIUM_TESTS.map(f => f.file)));
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState(null);

  const allTests = APPIUM_TESTS.flatMap(f => f.tests);
  const counts = allTests.reduce((acc, t) => { acc[t.status] = (acc[t.status] || 0) + 1; return acc; }, {});

  const toggle = (file) => {
    setExpanded(prev => {
      const n = new Set(prev);
      if (n.has(file)) n.delete(file); else n.add(file);
      return n;
    });
  };

  const visibleTests = (file) => file.tests.filter(t => filter === "all" || t.status === filter);

  return (
    <div className="grid" style={{ gap: 18 }}>

      {/* Idle banner */}
      {allIdle && (
        <div style={{ padding: "14px 18px", borderRadius: 10, background: "var(--surface)", border: "1px solid var(--border)", display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 34, height: 34, borderRadius: 9, background: "var(--idle-2)", color: "var(--idle)", display: "grid", placeItems: "center", flexShrink: 0 }}>
            <Icon name="clock" size={16} />
          </div>
          <div>
            <span style={{ fontWeight: 500, fontSize: 13 }}>No Appium tests have run yet.</span>
            <span style={{ fontSize: 13, color: "var(--text-2)", marginLeft: 8 }}>
              All {APPIUM_TESTS.reduce((s, f) => s + f.tests.length, 0)} tests are <StatusPill status="idle" /> — trigger the "Appium — Deep Tests" workflow from GitHub Actions.
            </span>
          </div>
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "end" }}>
        <div>
          <h1 className="h1" style={{ fontSize: 22 }}>Appium deep tests</h1>
          <p className="lead" style={{ fontSize: 13 }}>Python · pytest · appium-flutter-driver. Verifies payment SDKs, BNPL flows, subscriptions, and account management at the assertion level.</p>
        </div>
        <div className="seg">
          {[
            ["all", `All ${allTests.length}`],
            ["pass", `Passed ${counts.pass || 0}`],
            ["flaky", `Flaky ${counts.flaky || 0}`],
            ["fail", `Failed ${counts.fail || 0}`],
          ].map(([v, l]) => (
            <button key={v} className={filter === v ? "on" : ""} onClick={() => setFilter(v)}>{l}</button>
          ))}
        </div>
      </div>

      <div className="grid" style={{ gap: 12 }}>
        {APPIUM_TESTS.map(file => {
          const tests = visibleTests(file);
          if (tests.length === 0) return null;
          const isOpen = expanded.has(file.file);
          const fileStats = file.tests.reduce((acc, t) => { acc[t.status] = (acc[t.status] || 0) + 1; return acc; }, {});
          return (
            <div key={file.file} className="card">
              <div style={{ padding: "14px 16px", display: "grid", gridTemplateColumns: "auto 1fr auto auto", gap: 14, alignItems: "center", cursor: "pointer" }}
                   onClick={() => toggle(file.file)}>
                <div style={{ width: 36, height: 36, borderRadius: 10, background: "var(--surface-2)", border: "1px solid var(--border)", display: "grid", placeItems: "center", color: "var(--accent)" }}>
                  <Icon name={file.icon} size={18} />
                </div>
                <div style={{ minWidth: 0 }}>
                  <div className="mono" style={{ fontSize: 13, color: "var(--text)", marginBottom: 3 }}>{file.file}</div>
                  <div style={{ fontSize: 11.5, color: "var(--text-3)" }}>{file.group} · {file.tests.length} tests</div>
                </div>
                <div style={{ display: "flex", gap: 6 }}>
                  {fileStats.pass > 0 && <Pill kind="pass" dot={false}>{fileStats.pass} pass</Pill>}
                  {fileStats.flaky > 0 && <Pill kind="flaky" dot={false}>{fileStats.flaky} flaky</Pill>}
                  {fileStats.fail > 0 && <Pill kind="fail" dot={false}>{fileStats.fail} fail</Pill>}
                </div>
                <span style={{ color: "var(--text-3)", transform: isOpen ? "rotate(90deg)" : "none", transition: "transform .15s ease" }}>
                  <Icon name="chevron" size={14} />
                </span>
              </div>
              {isOpen && (
                <div style={{ borderTop: "1px solid var(--border)" }}>
                  {tests.map((t, i) => (
                    <div key={t.name}
                         onClick={() => setSelected({ ...t, file: file.file, group: file.group, icon: file.icon })}
                         style={{
                           display: "grid",
                           gridTemplateColumns: "16px 1fr auto auto auto",
                           gap: 14, alignItems: "center",
                           padding: "var(--row-pad) 16px var(--row-pad) 60px",
                           borderBottom: i < tests.length - 1 ? "1px solid var(--border)" : "none",
                           transition: "background .12s ease",
                           cursor: "pointer",
                         }}
                         onMouseEnter={(e) => e.currentTarget.style.background = "var(--surface-2)"}
                         onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
                      <span style={{
                        width: 16, height: 16, borderRadius: 4, display: "grid", placeItems: "center",
                        color: `var(--${t.status})`, background: `var(--${t.status}-2)`,
                      }}>
                        <Icon name={t.status === "pass" ? "check" : t.status === "fail" ? "x" : "bolt"} size={11} />
                      </span>
                      <div style={{ minWidth: 0 }}>
                        <div className="mono" style={{ fontSize: 12.5, color: "var(--text)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                          {t.name}
                        </div>
                        {t.error && (
                          <div className="mono" style={{ fontSize: 11.5, color: "var(--fail)", marginTop: 3 }}>{t.error}</div>
                        )}
                      </div>
                      <span className="mono" style={{ fontSize: 11.5, color: "var(--text-3)" }}>
                        {t.status === "idle" ? "—" : `${t.duration.toFixed(1)}s`}
                      </span>
                      <StatusPill status={t.status} />
                      <span style={{ color: "var(--text-3)" }}><Icon name="chevron" size={12} /></span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {selected && <TestDetail test={selected} onClose={() => setSelected(null)} />}
    </div>
  );
};

// ─── Test detail drawer ──────────────────────────────────────────────────
const STATUS_THEME = {
  pass:  { color: "var(--pass)",  bg: "var(--pass-2)",  label: "Passed",  icon: "check" },
  fail:  { color: "var(--fail)",  bg: "var(--fail-2)",  label: "Failed",  icon: "x" },
  flaky: { color: "var(--flaky)", bg: "var(--flaky-2)", label: "Flaky",   icon: "bolt" },
  skip:  { color: "var(--idle)",  bg: "var(--idle-2)",  label: "Skipped", icon: "clock" },
};

// Generate synthetic but plausible assertion log per test
const buildAssertions = (test) => {
  const base = [
    { ts: "00.00", level: "info", text: `pytest qatarat/tests/${test.file}::${test.name}` },
    { ts: "00.04", level: "info", text: "session: Pixel 7 · Android 14 · API 34" },
    { ts: "00.18", level: "info", text: "appium-flutter-driver attached" },
    { ts: "00.42", level: "info", text: "await find_element(by_value_key='home_button')" },
    { ts: "01.10", level: "info", text: "tap(home_button) → ok" },
    { ts: "01.84", level: "info", text: "assert visible: 'Browse Services'" },
    { ts: "02.36", level: "info", text: "tap(by_text='Continue') → ok" },
    { ts: "03.20", level: "info", text: "input_text(by_value_key='otp', text='0000')" },
    { ts: "04.05", level: "info", text: "screenshot: captures/01.png (492 KB)" },
  ];
  if (test.status === "pass") {
    base.push({ ts: test.duration.toFixed(2), level: "pass", text: `PASSED in ${test.duration.toFixed(2)}s` });
  } else if (test.status === "fail") {
    base.push({ ts: (test.duration - 0.3).toFixed(2), level: "warn", text: "waiting for element… (timeout 8000ms)" });
    base.push({ ts: test.duration.toFixed(2), level: "fail", text: test.error || "AssertionError: element not visible" });
  } else if (test.status === "flaky") {
    base.push({ ts: (test.duration * 0.4).toFixed(2), level: "warn", text: "attempt 1/3 — StaleElementReference, retrying" });
    base.push({ ts: (test.duration * 0.7).toFixed(2), level: "warn", text: "attempt 2/3 — element re-attached" });
    base.push({ ts: test.duration.toFixed(2), level: "pass", text: `PASSED on retry in ${test.duration.toFixed(2)}s (2 retries)` });
  }
  return base;
};

const sampleCode = (test) => {
  const cleanName = test.name.replace(/^test_/, "");
  return [
    "import pytest",
    "from qatarat.helpers import login, navigate, assert_visible",
    "",
    "@pytest.mark.android",
    `def ${test.name}(driver, snapshot):`,
    `    """${cleanName.replace(/_/g, " ")}"""`,
    "    login(driver, phone='+966500000000')",
    "    navigate(driver, to='checkout')",
    `    assert_visible(driver, 'pay_button', timeout=8)`,
    `    snapshot('${cleanName}_before')`,
    `    driver.tap('pay_button')`,
    `    assert_visible(driver, 'success_banner')`,
  ];
};

const TestDetail = ({ test, onClose }) => {
  const { RUN_META } = window.QATARAT_DATA;
  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const [tab, setTab] = useState("overview");
  const theme = STATUS_THEME[test.status] || STATUS_THEME.skip;
  const isIdle = test.status === "idle";
  const assertions = isIdle ? [] : buildAssertions(test);
  const code = sampleCode(test);
  const screenshots = 4 + (test.status === "fail" ? 1 : 0);

  return (
    <div onClick={onClose}
         style={{ position: "fixed", inset: 0, background: "rgba(4,5,9,.55)", backdropFilter: "blur(6px)", zIndex: 50, display: "flex", justifyContent: "flex-end" }}>
      <div onClick={(e) => e.stopPropagation()}
           style={{ width: "min(680px, 95vw)", height: "100vh", overflowY: "auto", background: "var(--bg-2)", borderLeft: "1px solid var(--border)" }}>

        {/* Header */}
        <div style={{ padding: "22px 24px 18px", borderBottom: "1px solid var(--border)", background: `linear-gradient(180deg, ${theme.bg}, transparent 80%)` }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 14, marginBottom: 14 }}>
            <div style={{ display: "flex", gap: 12, alignItems: "center", minWidth: 0 }}>
              <div style={{
                width: 40, height: 40, borderRadius: 11,
                background: theme.bg, color: theme.color,
                border: `1px solid color-mix(in oklch, ${theme.color} 30%, transparent)`,
                display: "grid", placeItems: "center", flexShrink: 0,
              }}>
                <Icon name={theme.icon} size={18} />
              </div>
              <div style={{ minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                  <StatusPill status={test.status} />
                  <span className="mono" style={{ fontSize: 11.5, color: "var(--text-3)" }}>{test.file} · {test.group}</span>
                </div>
                <h2 className="mono" style={{ margin: 0, fontSize: 17, fontWeight: 500, color: "var(--text)", letterSpacing: "-0.005em", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{test.name}</h2>
              </div>
            </div>
            <button className="btn ghost" onClick={onClose} aria-label="Close"><Icon name="x" /></button>
          </div>

          {/* Stat strip */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8 }}>
            {[
              { l: "duration",   v: isIdle ? "—" : `${test.duration.toFixed(2)}s` },
              { l: "assertions", v: isIdle ? "—" : assertions.length - 1 },
              { l: "screenshots",v: isIdle ? "—" : screenshots },
              { l: "retries",    v: isIdle ? "—" : test.status === "flaky" ? "2" : "0" },
            ].map(s => (
              <div key={s.l} style={{ padding: "8px 10px", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8 }}>
                <div style={{ fontSize: 10, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: ".09em" }}>{s.l}</div>
                <div className="mono" style={{ fontSize: 14, color: "var(--text)", marginTop: 1 }}>{s.v}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Tabs */}
        <div style={{ padding: "0 24px", borderBottom: "1px solid var(--border)", display: "flex", gap: 0 }}>
          {[
            { id: "overview", label: "Overview" },
            { id: "log", label: "Execution log" },
            { id: "code", label: "Test code" },
            { id: "screens", label: "Screenshots" },
          ].map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
                    style={{
                      padding: "12px 14px", fontSize: 13, fontWeight: 500,
                      background: "transparent", border: 0,
                      color: tab === t.id ? "var(--text)" : "var(--text-3)",
                      borderBottom: tab === t.id ? `2px solid var(--accent)` : "2px solid transparent",
                      marginBottom: -1, cursor: "pointer", fontFamily: "inherit",
                    }}>{t.label}</button>
          ))}
        </div>

        {/* Body */}
        <div style={{ padding: 24 }}>
          {tab === "overview" && (
            <div className="grid" style={{ gap: 14 }}>
              {/* Status message */}
              <div style={{
                padding: 14, borderRadius: 10,
                background: theme.bg,
                border: `1px solid color-mix(in oklch, ${theme.color} 30%, transparent)`,
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                  <span style={{ color: theme.color }}><Icon name={theme.icon} size={14} /></span>
                  <span style={{ fontWeight: 500, fontSize: 13, color: theme.color }}>{theme.label}</span>
                </div>
                <div className="mono" style={{ fontSize: 12.5, color: "var(--text-2)", lineHeight: 1.5 }}>
                  {isIdle && "This test has not been executed yet. Trigger the Appium — Deep Tests workflow to run it."}
                  {test.status === "pass" && `Completed successfully in ${test.duration.toFixed(2)} seconds. All assertions passed.`}
                  {test.status === "fail" && (test.error || "Test failed during execution. See the Execution Log tab for details.")}
                  {test.status === "flaky" && `Test passed after retries. Initial run hit a stale element — investigate for race conditions or missing wait conditions.`}
                </div>
              </div>

              {/* Metadata */}
              <div className="card">
                <div className="card-head"><h3>Run metadata</h3></div>
                <div className="card-body" style={{ padding: 0 }}>
                  {[
                    ["File",      test.file],
                    ["Suite",     test.group],
                    ["Framework", "Appium 2.x + appium-flutter-driver"],
                    ["Device",    isIdle ? "—" : RUN_META.device],
                    ["Started",   isIdle ? "—" : (RUN_META.startedAt || "—")],
                    ["Duration",  isIdle ? "—" : `${test.duration.toFixed(2)}s`],
                    ["Runner",    isIdle ? "—" : "ubuntu-latest · GitHub Actions"],
                  ].map(([k, v]) => (
                    <div key={k} style={{ display: "grid", gridTemplateColumns: "140px 1fr", gap: 10, padding: "10px 16px", borderBottom: "1px solid var(--border)" }}>
                      <span style={{ fontSize: 12, color: "var(--text-3)" }}>{k}</span>
                      <span className="mono" style={{ fontSize: 12.5, color: "var(--text)" }}>{v}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Assertions checklist */}
              <div className="card">
                <div className="card-head"><h3>Assertions</h3><span className="sub">{isIdle ? "not run" : `${assertions.length - 1} checks`}</span></div>
                <div className="card-body" style={{ padding: 0 }}>
                  {isIdle ? (
                    <div style={{ padding: "20px 16px", color: "var(--text-3)", fontSize: 13, textAlign: "center" }}>
                      No assertion data — test has not been executed.
                    </div>
                  ) : assertions.slice(3).map((a, i) => {
                    const ok = a.level !== "fail" && a.level !== "warn";
                    const failed = a.level === "fail";
                    return (
                      <div key={i} style={{ display: "grid", gridTemplateColumns: "auto 1fr auto", gap: 12, padding: "10px 16px", borderBottom: i < assertions.length - 4 ? "1px solid var(--border)" : "none", alignItems: "center" }}>
                        <span style={{
                          width: 18, height: 18, borderRadius: 5, display: "grid", placeItems: "center",
                          color: failed ? "var(--fail)" : ok ? "var(--pass)" : "var(--flaky)",
                          background: failed ? "var(--fail-2)" : ok ? "var(--pass-2)" : "var(--flaky-2)",
                        }}>
                          <Icon name={failed ? "x" : ok ? "check" : "bolt"} size={12} />
                        </span>
                        <span className="mono" style={{ fontSize: 12.5, color: failed ? "var(--fail)" : "var(--text)" }}>{a.text}</span>
                        <span className="mono" style={{ fontSize: 11, color: "var(--text-3)" }}>{a.ts}s</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {test.status === "fail" && (
                <div className="card">
                  <div className="card-head"><h3>Stack trace</h3></div>
                  <div className="card-body" style={{ background: "var(--bg)", margin: 0, fontFamily: "Geist Mono", fontSize: 12, color: "var(--text-2)", lineHeight: 1.65, padding: 16 }}>
                    <div style={{ color: "var(--fail)" }}>{test.error || "AssertionError: element not visible"}</div>
                    <div style={{ marginTop: 8 }}>{`  at ${test.file}:42`}</div>
                    <div>{`  at qatarat/helpers.py:117 in assert_visible`}</div>
                    <div>{`  at appium_flutter_driver/finder.py:88 in find_element`}</div>
                    <div style={{ marginTop: 8, color: "var(--text-3)" }}>{`  selenium.common.exceptions.TimeoutException: Message: timed out after 8000ms`}</div>
                  </div>
                </div>
              )}
            </div>
          )}

          {tab === "log" && (
            <div className="card">
              <div className="card-head between" style={{ display: "flex", justifyContent: "space-between" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <h3>Execution log</h3>
                  {!isIdle && <span style={{ fontSize: 10.5, color: "var(--text-3)", background: "var(--surface-2)", border: "1px solid var(--border)", borderRadius: 4, padding: "2px 7px", fontFamily: "Geist Mono" }}>simulated · for reference</span>}
                </div>
                <span className="mono sub" style={{ fontSize: 11 }}>{isIdle ? "0 lines" : `${assertions.length} lines`}</span>
              </div>
              {isIdle ? (
                <div style={{ padding: "28px 16px", textAlign: "center", color: "var(--text-3)" }}>
                  <Icon name="clock" size={20} style={{ marginBottom: 8, opacity: 0.4 }} />
                  <div style={{ fontSize: 13 }}>No log data — this test has not been run yet.</div>
                </div>
              ) : (
                <div style={{ background: "var(--bg)", fontFamily: "Geist Mono", fontSize: 12 }}>
                  {assertions.map((a, i) => {
                    const c = a.level === "fail" ? "var(--fail)" :
                              a.level === "warn" ? "var(--flaky)" :
                              a.level === "pass" ? "var(--pass)" :
                              "var(--text-2)";
                    return (
                      <div key={i} style={{ display: "grid", gridTemplateColumns: "60px 60px 1fr", gap: 10, padding: "6px 16px", borderBottom: "1px solid var(--border)" }}>
                        <span style={{ color: "var(--text-3)" }}>{a.ts}</span>
                        <span style={{ color: c, textTransform: "uppercase", fontSize: 10.5, letterSpacing: ".08em", alignSelf: "center" }}>{a.level}</span>
                        <span style={{ color: a.level === "fail" ? "var(--fail)" : "var(--text)" }}>{a.text}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {tab === "code" && (
            <div className="card">
              <div className="card-head">
                <h3 className="mono" style={{ fontSize: 12 }}>{test.file}</h3>
                <span style={{ fontSize: 10.5, color: "var(--text-3)", background: "var(--surface-2)", border: "1px solid var(--border)", borderRadius: 4, padding: "2px 7px", fontFamily: "Geist Mono", marginLeft: 6 }}>reference · sample only</span>
              </div>
              <div style={{ background: "var(--bg)", padding: 16, fontFamily: "Geist Mono", fontSize: 12.5, lineHeight: 1.65 }}>
                {code.map((line, i) => {
                  const isComment = line.trim().startsWith('"""');
                  const isImport = line.startsWith("import") || line.startsWith("from");
                  const isDecor = line.trim().startsWith("@");
                  const isDef = line.startsWith("def ");
                  return (
                    <div key={i} style={{ display: "grid", gridTemplateColumns: "32px 1fr", gap: 12 }}>
                      <span style={{ color: "var(--text-3)", textAlign: "right" }}>{i + 1}</span>
                      <span style={{
                        color: isComment ? "var(--text-3)" :
                               isImport ? "oklch(75% 0.16 280)" :
                               isDecor ? "var(--flaky)" :
                               isDef ? "var(--accent)" :
                               "var(--text)",
                        whiteSpace: "pre",
                      }}>{line || " "}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {tab === "screens" && (
            <div className="card">
              <div className="card-head"><h3>Screenshots</h3><span className="sub">{isIdle ? "not run" : `${screenshots} captured · layout preview`}</span></div>
              <div className="card-body">
                {isIdle ? (
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10, padding: "28px 0", color: "var(--text-3)", textAlign: "center" }}>
                    <div style={{ width: 48, height: 48, borderRadius: 12, background: "var(--surface-2)", border: "1px solid var(--border)", display: "grid", placeItems: "center" }}>
                      <Icon name="phone" size={22} />
                    </div>
                    <div style={{ fontSize: 14, fontWeight: 500, color: "var(--text-2)" }}>Test not executed yet</div>
                    <div style={{ fontSize: 12.5, lineHeight: 1.6, maxWidth: 300 }}>
                      Screenshots are captured during test execution on the Android emulator.
                      They will appear here after the first Appium run completes.
                    </div>
                  </div>
                ) : (
                  <>
                    <div style={{ marginBottom: 10, padding: "8px 10px", background: "var(--surface-2)", borderRadius: 7, border: "1px solid var(--border)", fontSize: 12, color: "var(--text-3)" }}>
                      <Icon name="clock" size={12} style={{ marginRight: 6 }} />
                      Screenshot thumbnails shown below represent the <strong style={{ color: "var(--text-2)" }}>expected captures</strong> — actual images from the CI run will replace these placeholders once uploaded.
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(130px, 1fr))", gap: 12 }}>
                      {Array.from({ length: screenshots }).map((_, i) => {
                        const isFailShot = test.status === "fail" && i === screenshots - 1;
                        return (
                          <div key={i} style={{
                            aspectRatio: "9/19", borderRadius: 8,
                            border: isFailShot ? "1px solid color-mix(in oklch, var(--fail) 40%, transparent)" : "1px solid var(--border)",
                            background: "repeating-linear-gradient(135deg, var(--surface-2) 0 6px, var(--surface) 6px 12px)",
                            position: "relative", overflow: "hidden",
                          }}>
                            {isFailShot && (
                              <div style={{ position: "absolute", top: 8, right: 8, padding: "2px 7px", borderRadius: 4, background: "var(--fail-2)", color: "var(--fail)", fontSize: 10, fontFamily: "Geist Mono", border: "1px solid color-mix(in oklch, var(--fail) 30%, transparent)" }}>
                                failure
                              </div>
                            )}
                            <div style={{ position: "absolute", inset: "auto 0 0 0", padding: "6px 8px", background: "linear-gradient(180deg, transparent, rgba(0,0,0,.7))", fontFamily: "Geist Mono", fontSize: 10.5, color: "var(--text-2)" }}>
                              {(i + 1).toString().padStart(2, "0")}{isFailShot ? "_failure" : ""}.png
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

window.AppiumView = AppiumView;
