export default function MeetingDoc({ structure, docUrl }) {
  if (!structure) return null;

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <h2 style={styles.title}>議事録</h2>
        {docUrl && <a href={docUrl} target="_blank" rel="noreferrer" style={styles.docsLink}>Google Docsで開く</a>}
      </div>
      <Section title="要約"><ul style={styles.list}>{structure.summary.map((l, i) => <li key={i} style={styles.listItem}>{l}</li>)}</ul></Section>
      <Section title="議論ポイント"><ul style={styles.list}>{structure.discussion_points.map((p, i) => <li key={i} style={styles.listItem}>{p}</li>)}</ul></Section>
      <Section title="アクションアイテム">
        {structure.action_items.length === 0 ? <p style={styles.empty}>なし</p> : (
          <div style={styles.actionTable}>
            {structure.action_items.map((item, i) => (
              <div key={i} style={styles.actionRow}>
                <span style={styles.owner}>{item.owner}</span>
                <span style={styles.action}>{item.action}</span>
                <span style={styles.deadline}>{item.deadline}</span>
              </div>
            ))}
          </div>
        )}
      </Section>
      <Section title="決定事項">
        {structure.decisions.length === 0 ? <p style={styles.empty}>なし</p> : <ul style={styles.list}>{structure.decisions.map((d, i) => <li key={i} style={styles.listItem}>{d}</li>)}</ul>}
      </Section>
    </div>
  );
}

function Section({ title, children }) {
  return <div style={sec.container}><h3 style={sec.title}>{title}</h3>{children}</div>;
}

const styles = {
  card: { background: "#fff", borderRadius: "12px", padding: "24px", boxShadow: "0 2px 8px rgba(0,0,0,0.08)", display: "flex", flexDirection: "column", gap: "20px" },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center" },
  title: { margin: 0, fontSize: "1.3rem", color: "#1e293b" },
  docsLink: { background: "#4285f4", color: "#fff", textDecoration: "none", padding: "8px 16px", borderRadius: "6px", fontSize: "0.875rem", fontWeight: "600" },
  list: { margin: 0, paddingLeft: "20px" },
  listItem: { marginBottom: "6px", color: "#334155", lineHeight: 1.6 },
  empty: { margin: 0, color: "#94a3b8", fontStyle: "italic" },
  actionTable: { display: "flex", flexDirection: "column", gap: "8px" },
  actionRow: { display: "grid", gridTemplateColumns: "120px 1fr 100px", gap: "8px", background: "#f8fafc", borderRadius: "6px", padding: "10px 12px", alignItems: "center" },
  owner: { fontWeight: "700", color: "#6366f1", fontSize: "0.85rem" },
  action: { color: "#334155", fontSize: "0.9rem" },
  deadline: { color: "#64748b", fontSize: "0.8rem", textAlign: "right" },
};

const sec = {
  container: { borderTop: "1px solid #f1f5f9", paddingTop: "16px" },
  title: { margin: "0 0 12px", fontSize: "0.95rem", fontWeight: "700", color: "#475569", textTransform: "uppercase", letterSpacing: "0.05em" },
};
