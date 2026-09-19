# EasyLLM • Figma Design System & UI Specification

Welcome to the **EasyLLM** Figma design package. This folder contains the complete UI artboards, vector frames, design tokens, and components for the EasyLLM Autonomous AI Model Architect web application.

---

## 📦 Design Assets Included

| File | Type | Description |
| :--- | :--- | :--- |
| [`EasyLLM-UI-Figma-Board.svg`](./EasyLLM-UI-Figma-Board.svg) | **Vector Artboard** | High-fidelity 1920x2680 vector canvas with full dark-mode layouts, glassmorphism cards, badges, and real-time inference views. |
| [`figma-tokens.json`](./figma-tokens.json) | **Design Tokens (JSON)** | Standard W3C/Figma Token Studio schema containing color palettes, typography scales, radii, shadows, and component variables. |
| [`FIGMA_DESIGN_SYSTEM.md`](./FIGMA_DESIGN_SYSTEM.md) | **Spec & Guide** | Detailed walkthrough on importing, editing, and using the design files in Figma. |

---

## 🚀 How to Import into Figma

### Method 1: Direct Vector Artboard Import (Recommended)
1. Open [Figma](https://www.figma.com) in your browser or desktop app.
2. Create a new file or open your project canvas.
3. Drag and drop [`EasyLLM-UI-Figma-Board.svg`](./EasyLLM-UI-Figma-Board.svg) directly onto your canvas (or click **Figma Menu -> File -> Place Image/SVG** and select `EasyLLM-UI-Figma-Board.svg`).
4. Figma will automatically convert all groups, text elements, SVG gradients, and vector shapes into editable **Figma Frames & Layers**.

### Method 2: Import Design Tokens with Tokens Studio
1. Install the **Tokens Studio for Figma** (formerly Figma Tokens) plugin in Figma.
2. Open the plugin on your canvas.
3. Click **Settings -> Load from JSON** and upload [`figma-tokens.json`](./figma-tokens.json).
4. Click **Apply to Canvas** to bind all Figma variables and color styles.

---

## 🎨 Design System Anatomy

### 1. Color Palette (Dark Void Glassmorphism)
- **Canvas Base**: `#030712` (Tailwind `gray-950`)
- **Card Surface**: `#0b1120` (Glass opacity: 90% with 1px border `#1e293b`)
- **Primary Brand Gradient**: `linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #06b6d4 100%)`
- **RAG Sky Cyan**: `#0284c7` (Border `#38bdf8`)
- **Success Emerald**: `#10b981` (Glow `#34d399`)
- **Fine-Tune Purple**: `#a855f7`

### 2. Typography Scale
- **Display Headings**: `38px` (Font Weight: 800 ExtraBold, Letter Spacing: -0.03em)
- **Card Titles**: `22px` (Font Weight: 700 Bold)
- **Body Regular**: `14px` (Font Weight: 400 Regular / Line Height: 1.6)
- **Code / Monospace**: `12px` (`SF Mono` / `JetBrains Mono` / `Fira Code`)

### 3. Screen Structure & Frames
1. **Header & Hardware Telemetry**: Live VRAM indicator, Gemini LLM badge, pipeline status.
2. **Step 1: Input & Ingestion**: Multimodal dropzone supporting `.docx`, `.pdf`, `.jsonl`, `.csv`, `.txt` with real-time extraction stats.
3. **Step 2: Autonomous Decision Engine**: 3-card layout (RAG, QLoRA, Hybrid) with confidence score rings and auto-reconciliation notes.
4. **Step 3: Fast-Track 20s Pipeline Monitor**: Horizontal step progress (Parsing &rarr; Embedding &rarr; Indexing &rarr; Quantization &rarr; Deployment) with live terminal logs.
5. **Step 4: Interactive Playground**: Dual-pane testing interface with direct document citations, faithfulness metrics, and latency monitor (<300ms).
