import { useState, useEffect, useCallback } from "react";
import FileUpload from "./components/FileUpload";
import StatusBar from "./components/StatusBar";
import MeetingDoc from "./components/MeetingDoc";
import { uploadFile, getJobStatus } from "./api";

export default function App() {
  const [job, setJob] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleUpload = async (file) => {
    setUploading(true);
    setError(null);
    setJob(null);
    try {
      const { job_id } = await uploadFile(file);
      setJob({ job_id, status: "pending" });
    } catch (e) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  };

  const poll = useCallback(async () => {
    if (!job?.job_id) return;
    try {
      const data = await getJobStatus(job.job_id);
      setJob(data);
    } catch (e) {
      setError(e.message);
    }
  }, [job?.job_id]);

  useEffect(() => {
    if (!job || job.status === "done" || job.status === "failed") return;
    const interval = setInterval(poll, 3000);
    return () => clearInterval(interval);
  }, [job, poll]);

  return (
    <div style={styles.root}>
      <div style={styles.container}>
        <header style={styles.header}>
          <h1 style={styles.title}>🎙️ MeetBot</h1>
          <p style={styles.subtitle}>音声・動画ファイルから議事録を自動生成</p>
        </header>

        <FileUpload onUpload={handleUpload} disabled={uploading || (job && job.status !== "done" && job.status !== "failed")} />

        {error && (
          <div style={styles.error}>{error}</div>
        )}

        {job && (
          <StatusBar status={job.status} jobId={job.job_id} />
        )}

        {job?.status === "done" && (
          <MeetingDoc structure={job.structure} docUrl={job.doc_url} />
        )}
      </div>
    </div>
  );
}

const styles = {
  root: {
    minHeight: "100vh",
    background: "#f1f5f9",
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "center",
    padding: "40px 16px",
  },
  container: {
    width: "100%",
    maxWidth: "720px",
    display: "flex",
    flexDirection: "column",
    gap: "20px",
  },
  header: {
    textAlign: "center",
  },
  title: {
    margin: "0 0 8px",
    fontSize: "2rem",
    fontWeight: "800",
    color: "#1e293b",
  },
  subtitle: {
    margin: 0,
    color: "#64748b",
    fontSize: "1rem",
  },
  error: {
    background: "#fee2e2",
    color: "#dc2626",
    padding: "12px 16px",
    borderRadius: "8px",
    fontSize: "0.9rem",
  },
};
