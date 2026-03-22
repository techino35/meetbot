import { useRef, useState } from "react";

const ACCEPTED = ".mp3,.wav,.m4a,.ogg,.flac,.aac,.mp4,.mov,.mkv,.avi,.webm";

export default function FileUpload({ onUpload, disabled }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFile = (file) => {
    if (!file) return;
    setSelectedFile(file);
  };

  const handleSubmit = () => {
    if (selectedFile) onUpload(selectedFile);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div style={styles.card}>
      <div
        style={{
          ...styles.dropzone,
          ...(dragging ? styles.dropzoneDragging : {}),
          ...(disabled ? styles.dropzoneDisabled : {}),
        }}
        onClick={() => !disabled && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <div style={styles.icon}>🎙️</div>
        {selectedFile ? (
          <p style={styles.filename}>{selectedFile.name}</p>
        ) : (
          <>
            <p style={styles.hint}>クリックまたはドラッグ&amp;ドロップでファイルを選択</p>
            <p style={styles.formats}>対応: mp3, wav, m4a, mp4, mov, mkv など</p>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          style={{ display: "none" }}
          onChange={(e) => handleFile(e.target.files[0])}
        />
      </div>

      <button
        style={{
          ...styles.button,
          ...(disabled || !selectedFile ? styles.buttonDisabled : {}),
        }}
        onClick={handleSubmit}
        disabled={disabled || !selectedFile}
      >
        {disabled ? "アップロード中..." : "議事録を生成する"}
      </button>
    </div>
  );
}

const styles = {
  card: { background: "#fff", borderRadius: "12px", padding: "24px", boxShadow: "0 2px 8px rgba(0,0,0,0.08)", display: "flex", flexDirection: "column", gap: "16px" },
  dropzone: { border: "2px dashed #cbd5e1", borderRadius: "8px", padding: "40px 24px", textAlign: "center", cursor: "pointer", transition: "all 0.2s", background: "#f8fafc" },
  dropzoneDragging: { border: "2px dashed #6366f1", background: "#eef2ff" },
  dropzoneDisabled: { opacity: 0.5, cursor: "not-allowed" },
  icon: { fontSize: "2.5rem", marginBottom: "12px" },
  hint: { margin: "0 0 4px", color: "#475569", fontSize: "0.95rem" },
  formats: { margin: 0, color: "#94a3b8", fontSize: "0.8rem" },
  filename: { margin: 0, color: "#1e40af", fontWeight: "600" },
  button: { background: "#6366f1", color: "#fff", border: "none", borderRadius: "8px", padding: "14px", fontSize: "1rem", fontWeight: "600", cursor: "pointer", transition: "background 0.2s" },
  buttonDisabled: { background: "#cbd5e1", cursor: "not-allowed" },
};
