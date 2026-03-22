const STEPS = [
  { key: "pending", label: "待機中" },
  { key: "transcribing", label: "文字起こし中" },
  { key: "structuring", label: "構造化中" },
  { key: "writing", label: "Docs書き込み中" },
  { key: "done", label: "完了" },
];

const STATUS_ORDER = STEPS.map((s) => s.key);

export default function StatusBar({ status, jobId }) {
  const currentIndex = STATUS_ORDER.indexOf(status);
  const isFailed = status === "failed";

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <span style={styles.label}>処理状況</span>
        <span style={styles.jobId}>Job: {jobId?.slice(0, 8)}...</span>
      </div>
      {isFailed ? (
        <div style={styles.failed}>処理に失敗しました</div>
      ) : (
        <div style={styles.steps}>
          {STEPS.map((step, i) => {
            const isCompleted = i < currentIndex;
            const isCurrent = i === currentIndex;
            return (
              <div key={step.key} style={styles.stepItem}>
                <div style={{ ...styles.dot, ...(isCompleted ? styles.dotCompleted : {}), ...(isCurrent ? styles.dotCurrent : {}) }}>
                  {isCompleted ? "✓" : i + 1}
                </div>
                <span style={{ ...styles.stepLabel, ...(isCurrent ? styles.stepLabelCurrent : {}), ...(isCompleted ? styles.stepLabelCompleted : {}) }}>
                  {step.label}
                </span>
                {i < STEPS.length - 1 && <div style={{ ...styles.line, ...(isCompleted ? styles.lineCompleted : {}) }} />}
              </div>
            );
          })}
        </div>
      )}
      {!isFailed && status !== "done" && (
        <div style={styles.spinner}><div style={styles.spinnerDot} />処理中...</div>
      )}
    </div>
  );
}

const styles = {
  card: { background: "#fff", borderRadius: "12px", padding: "24px", boxShadow: "0 2px 8px rgba(0,0,0,0.08)" },
  header: { display: "flex", justifyContent: "space-between", marginBottom: "20px" },
  label: { fontWeight: "700", color: "#1e293b" },
  jobId: { fontSize: "0.75rem", color: "#94a3b8", fontFamily: "monospace" },
  steps: { display: "flex", alignItems: "center", gap: 0 },
  stepItem: { display: "flex", alignItems: "center", flex: 1 },
  dot: { width: "28px", height: "28px", borderRadius: "50%", background: "#e2e8f0", color: "#94a3b8", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.75rem", fontWeight: "700", flexShrink: 0, zIndex: 1 },
  dotCompleted: { background: "#10b981", color: "#fff" },
  dotCurrent: { background: "#6366f1", color: "#fff", boxShadow: "0 0 0 4px rgba(99,102,241,0.2)" },
  stepLabel: { fontSize: "0.7rem", color: "#94a3b8", marginLeft: "4px", whiteSpace: "nowrap" },
  stepLabelCurrent: { color: "#6366f1", fontWeight: "600" },
  stepLabelCompleted: { color: "#10b981" },
  line: { flex: 1, height: "2px", background: "#e2e8f0", margin: "0 4px" },
  lineCompleted: { background: "#10b981" },
  failed: { color: "#dc2626", fontWeight: "600", padding: "8px 0" },
  spinner: { marginTop: "16px", display: "flex", alignItems: "center", gap: "8px", color: "#6366f1", fontSize: "0.85rem" },
  spinnerDot: { width: "8px", height: "8px", borderRadius: "50%", background: "#6366f1", animation: "pulse 1s infinite" },
};
