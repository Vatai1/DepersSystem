import { useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, Image, Table, X } from "lucide-react";
import "./FileDropzone.css";

interface Props {
  onFile: (file: File) => void;
}

const ICONS: Record<string, typeof FileText> = {
  "text/": FileText,
  "application/pdf": FileText,
  "application/vnd.openxmlformats-officedocument": FileText,
  "image/": Image,
  "text/csv": Table,
  "application/vnd.ms-excel": Table,
};

function getFileIcon(file: File) {
  for (const [mime, Icon] of Object.entries(ICONS)) {
    if (file.type.startsWith(mime) || file.type === mime) return Icon;
  }
  return FileText;
}

export default function FileDropzone({ onFile }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const Icon = file ? getFileIcon(file) : Upload;

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (accepted) => {
      if (accepted[0]) {
        setFile(accepted[0]);
        onFile(accepted[0]);
      }
    },
    multiple: false,
    maxSize: 100 * 1024 * 1024,
  });

  return (
    <div
      {...getRootProps()}
      className={`file-dropzone ${isDragActive ? "drag-active" : ""} ${file ? "has-file" : ""}`}
    >
      <input {...getInputProps()} />
      {file ? (
        <div className="file-preview">
          <Icon size={32} className="file-icon" />
          <div className="file-info">
            <span className="file-name">{file.name}</span>
            <span className="file-size">
              {(file.size / 1024).toFixed(1)} KB
            </span>
          </div>
          <button
            className="file-remove"
            onClick={(e) => {
              e.stopPropagation();
              setFile(null);
            }}
          >
            <X size={16} />
          </button>
        </div>
      ) : (
        <div className="file-prompt">
          <Upload size={32} className="file-icon" />
          <p>
            {isDragActive
              ? "Отпустите файл..."
              : "Перетащите файл или нажмите для выбора"}
          </p>
          <span className="file-hint">
            TXT, PDF, DOCX, CSV, XLSX, PNG, JPG — до 100 MB
          </span>
        </div>
      )}
    </div>
  );
}
