"use client";

import { useState, useCallback } from "react";
import { useDropzone, FileRejection } from "react-dropzone";
import {
  FolderUp,
  FileText,
  CheckCircle2,
  X,
  FileCheck,
  Database,
  Loader2,
  Image as ImageIcon,
  Mic,
  FileCode,
  AlertTriangle,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import { useAppStore } from "@/lib/store";
import { getProvider } from "@/lib/providers";
import { formatBytes } from "@/lib/utils";
import { toast } from "sonner";

export function FileDropzone() {
  const {
    datasetFile,
    datasetMetadata,
    setDatasetFile,
    setDatasetMetadata,
    useLocalProvider,
  } = useAppStore();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [showErrorDetails, setShowErrorDetails] = useState(false);

  const processFile = useCallback(
    async (file: File) => {
      setDatasetFile(file);
      setUploadError(null);
      setIsUploading(true);

      try {
        const provider = getProvider(useLocalProvider);
        const meta = await provider.uploadDataset(file);
        setDatasetMetadata(meta);

        if (meta.validation_errors && meta.validation_errors.length > 0) {
          setUploadError(meta.validation_errors.join(" | "));
          toast.warning(`Uploaded ${file.name} with processing notices`);
        } else {
          toast.success(`Processed ${file.name} (${formatBytes(meta.file_size_bytes)})`);
        }
      } catch (err: any) {
        const msg = err.message || "Failed to inspect file";
        setUploadError(msg);
        toast.error(msg);
      } finally {
        setIsUploading(false);
      }
    },
    [setDatasetFile, setDatasetMetadata, useLocalProvider]
  );

  const onDrop = useCallback(
    (acceptedFiles: File[], fileRejections: FileRejection[]) => {
      const file = acceptedFiles[0] || (fileRejections[0] && fileRejections[0].file);
      if (file) {
        processFile(file);
      }
    },
    [processFile]
  );

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    maxFiles: 1,
    noClick: false,
    noKeyboard: false,
  });

  const removeFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setDatasetFile(null);
    setDatasetMetadata(null);
    setUploadError(null);
  };

  const currentFile = datasetFile;
  const modality = datasetMetadata?.modality || "text";

  const getModalityIcon = (mod: string) => {
    switch (mod) {
      case "image":
        return <ImageIcon className="h-4 w-4 text-purple-600" />;
      case "audio":
        return <Mic className="h-4 w-4 text-amber-600" />;
      case "document":
        return <FileText className="h-4 w-4 text-blue-600" />;
      default:
        return <FileCode className="h-4 w-4 text-emerald-600" />;
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
        <label className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
          <Database className="h-3.5 w-3.5 text-blue-600" />
          Knowledge Documents & Data (Optional)
        </label>
        <span className="text-[11px] font-medium text-slate-400">
          Optional · Build from prompt alone or upload docs
        </span>
      </div>

      {!currentFile ? (
        /* Sleek Modern Multimodal Dropzone Card */
        <div
          {...getRootProps()}
          className={`relative flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-xl border p-4 sm:p-5 transition cursor-pointer ${
            isDragActive
              ? "border-blue-500 bg-blue-50/60 ring-2 ring-blue-500/20"
              : "border-slate-200/90 bg-slate-50/50 hover:border-slate-300 hover:bg-slate-50"
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex items-center gap-3.5">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white border border-slate-200/80 text-blue-600 shadow-2xs">
              <FolderUp className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-800">
                {isDragActive ? "Drop media or document to inspect" : "Add domain reference documents (Optional)"}
              </p>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Upload files to give your AI specific reference material, or leave empty to build from prompt instructions alone.
              </p>
              <div className="flex flex-wrap items-center gap-1.5 mt-2">
                <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-200/60 shadow-2xs">
                  <FileText className="h-2.5 w-2.5" />
                  PDF / DOCX
                </span>
                <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-purple-700 bg-purple-50 px-1.5 py-0.5 rounded border border-purple-200/60 shadow-2xs">
                  <ImageIcon className="h-2.5 w-2.5" />
                  PNG / JPG / WEBP
                </span>
                <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200/60 shadow-2xs">
                  <Mic className="h-2.5 w-2.5" />
                  MP3 / WAV / M4A
                </span>
                <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200/60 shadow-2xs">
                  <FileCode className="h-2.5 w-2.5" />
                  TXT / JSONL / CSV
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                open();
              }}
              className="rounded-lg border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-semibold text-slate-700 shadow-2xs hover:bg-slate-50 transition shrink-0"
            >
              Browse files
            </button>
          </div>
        </div>
      ) : (
        /* Verified Multimodal File Card */
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-xs space-y-3">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 overflow-hidden">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-50 border border-slate-200/80">
                {isUploading ? (
                  <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                ) : (
                  getModalityIcon(modality)
                )}
              </div>
              <div className="truncate">
                <div className="flex items-center gap-2">
                  <h4 className="text-xs font-bold text-slate-900 truncate">
                    {currentFile.name}
                  </h4>
                  <span className="rounded bg-slate-100 px-1.5 py-0.2 text-[10px] font-mono font-bold text-slate-700 uppercase shrink-0">
                    {datasetMetadata?.modality ? datasetMetadata.modality.toUpperCase() : currentFile.name.split(".").pop()?.toUpperCase()}
                  </span>
                  {!isUploading && !uploadError && (
                    <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-600">
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      Processed
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-slate-500 font-medium">
                  {formatBytes(currentFile.size)} ·{" "}
                  {datasetMetadata?.format ? datasetMetadata.format.replace("_", " ") : "Inspecting stream..."}
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={removeFile}
              className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition"
              title="Remove file"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Processing Error / Notification Banner */}
          {uploadError && (
            <div className="rounded-lg bg-amber-50/80 border border-amber-200 p-3 text-xs text-amber-900 space-y-1.5">
              <div className="flex items-start gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
                <div className="flex-1">
                  <span className="font-bold">Multimodal Processing Notice</span>
                  <p className="text-[11px] text-amber-800 leading-relaxed">{uploadError}</p>
                </div>
              </div>
            </div>
          )}

          {/* Normalized Content Preview Snippet */}
          {datasetMetadata?.normalized_content && (
            <div className="rounded-lg bg-slate-50 p-2.5 border border-slate-200/60 text-xs">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                Extracted Normalized Content Preview:
              </span>
              <p className="text-[11px] font-mono text-slate-700 line-clamp-2">
                {datasetMetadata.normalized_content}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
