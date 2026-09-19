"use client";

import { useState, useCallback } from "react";
import { useDropzone, FileRejection } from "react-dropzone";
import { FolderUp, FileText, CheckCircle2, X, FileCheck, Database, Loader2, RefreshCw } from "lucide-react";
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

  const processFile = useCallback(
    async (file: File) => {
      setDatasetFile(file);
      setUploadError(null);
      setIsUploading(true);

      try {
        const provider = getProvider(useLocalProvider);
        const meta = await provider.uploadDataset(file);
        setDatasetMetadata(meta);
        toast.success(`Loaded ${file.name} (${formatBytes(meta.file_size_bytes)})`);
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

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
          <Database className="h-3.5 w-3.5 text-blue-600" />
          Step 2 · Upload Reference Data
        </label>
        <span className="text-[11px] font-medium text-slate-400">DOCX, PDF, JSONL, CSV, TXT</span>
      </div>

      {!currentFile ? (
        /* Sleek Modern Dropzone Card */
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
                {isDragActive ? "Drop document to inspect" : "Select or drop dataset or document"}
              </p>
              <div className="flex flex-wrap items-center gap-1.5 mt-1">
                <span className="text-[10px] font-semibold text-slate-600 bg-white px-1.5 py-0.5 rounded border border-slate-200 shadow-2xs">
                  .DOCX
                </span>
                <span className="text-[10px] font-semibold text-slate-600 bg-white px-1.5 py-0.5 rounded border border-slate-200 shadow-2xs">
                  .PDF
                </span>
                <span className="text-[10px] font-semibold text-slate-600 bg-white px-1.5 py-0.5 rounded border border-slate-200 shadow-2xs">
                  .JSONL
                </span>
                <span className="text-[10px] font-semibold text-slate-600 bg-white px-1.5 py-0.5 rounded border border-slate-200 shadow-2xs">
                  .CSV
                </span>
                <span className="text-[10px] text-slate-400 ml-1">Word, PDFs, datasets or manuals</span>
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
              className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-2xs hover:bg-slate-50 transition shrink-0"
            >
              Browse file
            </button>
          </div>
        </div>
      ) : (
        /* Elevated Verified File Card */
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-xs space-y-3">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 overflow-hidden">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600 border border-blue-100">
                {isUploading ? (
                  <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                ) : (
                  <FileCheck className="h-4 w-4" />
                )}
              </div>
              <div className="truncate">
                <div className="flex items-center gap-2">
                  <h4 className="text-xs font-bold text-slate-900 truncate">
                    {currentFile.name}
                  </h4>
                  <span className="rounded bg-slate-100 px-1.5 py-0.2 text-[10px] font-mono font-bold text-slate-600 uppercase shrink-0">
                    {currentFile.name.split(".").pop() || "FILE"}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  {formatBytes(currentFile.size)}
                  {datasetMetadata && ` · ${datasetMetadata.num_records} records`}
                  {isUploading && " · Scanning document..."}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1.5 shrink-0">
              {uploadError && (
                <button
                  onClick={() => processFile(currentFile)}
                  title="Retry inspection"
                  className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition"
                >
                  <RefreshCw className="h-3.5 w-3.5" />
                </button>
              )}
              <button
                onClick={removeFile}
                title="Remove file"
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Detailed analysis summary badge strip */}
          {datasetMetadata && (
            <div className="flex flex-wrap items-center gap-2 border-t border-slate-100 pt-3 text-[11px]">
              <span className="rounded-md bg-slate-50 px-2.5 py-1 text-slate-700 border border-slate-200/60 font-medium">
                Valid Samples: <strong className="text-emerald-700 font-bold">{datasetMetadata.num_valid_examples}</strong>
              </span>
              <span className="rounded-md bg-slate-50 px-2.5 py-1 text-slate-700 border border-slate-200/60 font-medium">
                Invalid: <strong className="text-slate-900">{datasetMetadata.num_invalid_examples}</strong>
              </span>
              <span className="rounded-md bg-blue-50 px-2.5 py-1 text-blue-800 border border-blue-200/60 font-medium flex items-center gap-1">
                {datasetMetadata.training_compatible ? (
                  <>
                    <CheckCircle2 className="h-3 w-3 text-blue-600" /> SFT Training Ready
                  </>
                ) : (
                  <>
                    <FileText className="h-3 w-3 text-blue-600" /> RAG Knowledge Ready
                  </>
                )}
              </span>
            </div>
          )}

          {uploadError && (
            <div className="rounded-lg bg-rose-50 p-2.5 text-[11px] text-rose-700 border border-rose-200 flex items-center justify-between">
              <span>{uploadError}</span>
              <span className="font-semibold text-rose-800 underline cursor-pointer" onClick={() => processFile(currentFile)}>
                Retry
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
