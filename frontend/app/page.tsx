"use client";

import { useEffect, useRef, useState } from "react";

const BACKEND = "http://localhost:8000";

type PageEntry = { pageNum: number; imagePath: string; text: string };
type AudioState = "idle" | "loading" | "playing" | "paused";

/* ── icons ── */
function IconCamera() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
      <circle cx="12" cy="13" r="4"/>
    </svg>
  );
}
function IconPlay() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>;
}
function IconPause() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>;
}
function IconStop() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>;
}
function IconSpinner() {
  return (
    <svg className="animate-spin" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
    </svg>
  );
}
function IconFlip() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="15 18 21 12 15 6"/><line x1="21" y1="12" x2="9" y2="12"/>
      <polyline points="9 6 3 12 9 18"/>
    </svg>
  );
}
function IconChevron() {
  return <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9l6 6 6-6"/></svg>;
}

export default function Home() {
  const [cameras, setCameras] = useState<number[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<number>(0);
  const [showPreview, setShowPreview] = useState(true);

  const [pages, setPages] = useState<PageEntry[]>([]);
  const [currentPage, setCurrentPage] = useState<PageEntry | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);
  const [isFlipping, setIsFlipping] = useState(false);
  const [audioState, setAudioState] = useState<AudioState>("idle");
  const [error, setError] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const blobUrlRef = useRef<string | null>(null);

  /* fetch cameras on mount */
  useEffect(() => {
    fetch(`${BACKEND}/cameras`)
      .then((r) => r.json())
      .then((d) => {
        setCameras(d.cameras ?? []);
        setSelectedCamera(d.active ?? 0);
      })
      .catch(() => setCameras([0]));
  }, []);

  /* ── capture ── */
  async function capturePage() {
    setIsCapturing(true);
    setError(null);
    stopAudio();
    try {
      const res = await fetch(`/api/capture?camera=${selectedCamera}`, { method: "POST" });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      const entry: PageEntry = { pageNum: pages.length + 1, imagePath: data.imagePath, text: data.text };
      setPages((prev) => [...prev, entry]);
      setCurrentPage(entry);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Capture failed");
    } finally {
      setIsCapturing(false);
    }
  }

  /* ── flip ── */
  async function flipPage() {
    setIsFlipping(true);
    setError(null);
    try {
      const res = await fetch("/api/flip", { method: "POST" });
      if (!res.ok) throw new Error(await res.text());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Flip failed");
    } finally {
      setIsFlipping(false);
    }
  }

  /* ── audio ── */
  function stopAudio() {
    audioRef.current?.pause();
    if (audioRef.current) { audioRef.current.src = ""; audioRef.current = null; }
    if (blobUrlRef.current) { URL.revokeObjectURL(blobUrlRef.current); blobUrlRef.current = null; }
    setAudioState("idle");
  }

  async function playAudio(text: string) {
    stopAudio();
    setAudioState("loading");
    setError(null);
    try {
      const res = await fetch("/api/tts", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) });
      if (!res.ok) throw new Error(await res.text());
      const url = URL.createObjectURL(await res.blob());
      blobUrlRef.current = url;
      const audio = new Audio(url);
      audioRef.current = audio;
      audio.onended = stopAudio;
      audio.onerror = () => { setError("Playback error"); setAudioState("idle"); };
      await audio.play();
      setAudioState("playing");
    } catch (e) {
      setError(e instanceof Error ? e.message : "TTS failed");
      setAudioState("idle");
    }
  }

  function togglePause() {
    const a = audioRef.current;
    if (!a) return;
    if (audioState === "playing") { a.pause(); setAudioState("paused"); }
    else if (audioState === "paused") { a.play(); setAudioState("playing"); }
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-[#f7f3ee] text-[#1c1410]" style={{ fontFamily: "'Inter', system-ui, sans-serif" }}>

      {/* Header */}
      <header className="h-12 shrink-0 flex items-center justify-between px-5 bg-[#f0ebe3] border-b border-[#e0d5c8]">
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 rounded-md bg-[#c4622d] flex items-center justify-center text-white text-[11px] font-bold">F</div>
          <span className="text-[14px] font-semibold tracking-tight">Flipper</span>
        </div>
        <div className="flex items-center gap-3">
          {pages.length > 0 && <span className="text-xs text-[#9c8572]">{pages.length} {pages.length === 1 ? "page" : "pages"}</span>}
          {/* Camera selector */}
          <div className="relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-[#e0d5c8] text-[12px] text-[#5a4535] cursor-pointer select-none">
            <IconCamera />
            <select
              value={selectedCamera}
              onChange={(e) => setSelectedCamera(Number(e.target.value))}
              className="appearance-none bg-transparent pr-4 cursor-pointer outline-none text-[12px] text-[#5a4535]"
            >
              {cameras.map((c) => (
                <option key={c} value={c}>Camera {c}</option>
              ))}
            </select>
            <span className="pointer-events-none absolute right-2 text-[#9c8572]"><IconChevron /></span>
          </div>
          {/* Preview toggle */}
          <button
            onClick={() => setShowPreview((v) => !v)}
            className={`px-3 py-1.5 rounded-lg text-[12px] font-medium border transition-colors ${
              showPreview ? "bg-[#c4622d]/10 border-[#c4622d]/30 text-[#c4622d]" : "bg-white border-[#e0d5c8] text-[#9c8572] hover:text-[#5a4535]"
            }`}
          >
            {showPreview ? "Hide preview" : "Show preview"}
          </button>
        </div>
      </header>

      {/* Error */}
      {error && (
        <div className="shrink-0 flex items-center gap-2 px-5 py-2 bg-red-50 border-b border-red-200 text-red-600 text-xs">
          <span className="w-1.5 h-1.5 rounded-full bg-red-500 shrink-0" />
          {error}
          <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-600">✕</button>
        </div>
      )}

      <div className="flex flex-1 overflow-hidden">

        {/* Sidebar */}
        <aside className="w-40 shrink-0 border-r border-[#e0d5c8] bg-[#ede8e0] flex flex-col">
          <div className="px-4 pt-4 pb-2">
            <p className="text-[10px] font-bold uppercase tracking-widest text-[#b0997f]">Pages</p>
          </div>
          <div className="flex-1 overflow-y-auto">
            {pages.length === 0
              ? <p className="text-xs text-[#c4b09a] px-4 py-2 italic">None yet</p>
              : pages.map((p) => (
                <button key={p.pageNum} onClick={() => { stopAudio(); setCurrentPage(p); }}
                  className={`w-full text-left px-4 py-2.5 text-[13px] transition-colors border-b border-[#e0d5c8]/50 ${
                    currentPage?.pageNum === p.pageNum
                      ? "bg-[#c4622d]/10 text-[#c4622d] font-medium"
                      : "text-[#7a6555] hover:bg-[#e0d5c8]/60"
                  }`}>
                  <span className="text-[#c4b09a] text-[11px] mr-1 font-mono">{String(p.pageNum).padStart(2, "0")}</span>
                  Page {p.pageNum}
                </button>
              ))
            }
          </div>
        </aside>

        {/* Main */}
        <div className="flex-1 flex flex-col overflow-hidden">

          {/* Live camera preview */}
          {showPreview && (
            <div className="shrink-0 bg-[#111] flex flex-col items-center justify-center border-b border-[#e0d5c8] overflow-hidden relative" style={{ height: "50vh" }}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                key={selectedCamera}
                src={`${BACKEND}/stream?camera=${selectedCamera}`}
                alt="Live camera feed"
                className="h-full w-full object-contain"
              />
              <div className="absolute top-2 left-3 flex items-center gap-1.5 px-2 py-1 rounded bg-black/50 text-white text-[11px]">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                Live · Camera {selectedCamera}
              </div>
            </div>
          )}

          {/* Captured image (after capture) */}
          {!showPreview && currentPage?.imagePath && (
            <div className="shrink-0 h-48 bg-[#111] flex items-center justify-center border-b border-[#e0d5c8] overflow-hidden">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={`/api/image?path=${encodeURIComponent(currentPage.imagePath)}`}
                alt={`Page ${currentPage.pageNum}`}
                className="h-full w-full object-contain"
              />
            </div>
          )}

          {/* Text area */}
          <div className="flex-1 overflow-y-auto">
            {currentPage ? (
              <div className="max-w-2xl mx-auto px-8 py-7">
                {/* Audio bar */}
                <div className="flex items-center gap-3 mb-6 p-3 rounded-xl bg-white border border-[#e0d5c8] shadow-sm">
                  <div className="flex-1 min-w-0">
                    <p className="text-[11px] font-semibold uppercase tracking-widest text-[#b0997f]">Page {currentPage.pageNum}</p>
                    <p className="text-[12px] text-[#9c8572] mt-0.5">
                      {audioState === "loading" && "Generating…"}
                      {audioState === "playing" && "Playing…"}
                      {audioState === "paused" && "Paused"}
                      {audioState === "idle" && "Ready"}
                    </p>
                  </div>
                  <button
                    onClick={() => audioState === "idle" ? playAudio(currentPage.text) : togglePause()}
                    disabled={audioState === "loading"}
                    className="w-9 h-9 rounded-full flex items-center justify-center bg-[#c4622d] hover:bg-[#a84f24] text-white disabled:opacity-50 transition-colors shadow-sm"
                  >
                    {audioState === "loading" ? <IconSpinner /> : audioState === "playing" ? <IconPause /> : <IconPlay />}
                  </button>
                  {audioState !== "idle" && (
                    <button onClick={stopAudio} className="w-8 h-8 rounded-full flex items-center justify-center bg-[#e0d5c8] hover:bg-[#d0c5b6] text-[#7a6555] transition-colors">
                      <IconStop />
                    </button>
                  )}
                </div>
                <p className="text-[14.5px] leading-[1.9] text-[#3d2b1f] whitespace-pre-wrap" style={{ fontFamily: "'Georgia', serif" }}>
                  {currentPage.text}
                </p>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full gap-4 text-center px-6">
                <div className="w-14 h-14 rounded-2xl bg-white border border-[#e0d5c8] shadow-sm flex items-center justify-center text-2xl">📖</div>
                <div>
                  <p className="text-[14px] font-medium text-[#5a4535] mb-1">Ready to scan</p>
                  <p className="text-[12px] text-[#b0997f]">Position the book under the camera and press <span className="font-mono bg-white border border-[#e0d5c8] px-1.5 py-0.5 rounded text-[12px]">Capture</span></p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <footer className="shrink-0 h-14 border-t border-[#e0d5c8] bg-[#f0ebe3] flex items-center gap-2.5 px-5">
        <button
          onClick={capturePage}
          disabled={isCapturing || isFlipping}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-[13px] font-semibold bg-[#1c1410] hover:bg-[#2e1f14] text-white disabled:opacity-50 transition-colors shadow-sm"
        >
          {isCapturing ? <IconSpinner /> : <IconCamera />}
          {isCapturing ? "Capturing…" : "Capture page"}
        </button>

        <button
          onClick={flipPage}
          disabled={isFlipping || isCapturing}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-[13px] font-semibold bg-[#5a6e3a] hover:bg-[#4a5c2e] text-white disabled:opacity-50 transition-colors shadow-sm"
        >
          {isFlipping ? <IconSpinner /> : <IconFlip />}
          {isFlipping ? "Flipping…" : "Flip page"}
        </button>

        {currentPage && (
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => audioState === "idle" ? playAudio(currentPage.text) : togglePause()}
              disabled={audioState === "loading"}
              className="flex items-center gap-2 px-3.5 py-2 rounded-lg text-[13px] font-medium bg-[#c4622d] hover:bg-[#a84f24] text-white disabled:opacity-50 transition-colors shadow-sm"
            >
              {audioState === "loading" ? <IconSpinner /> : audioState === "playing" ? <IconPause /> : <IconPlay />}
              {audioState === "loading" ? "Loading…" : audioState === "playing" ? "Pause" : "Play"}
            </button>
            {audioState !== "idle" && (
              <button onClick={stopAudio} className="flex items-center gap-2 px-3.5 py-2 rounded-lg text-[13px] font-medium bg-[#e0d5c8] hover:bg-[#d0c5b6] text-[#5a4535] transition-colors">
                <IconStop /> Stop
              </button>
            )}
          </div>
        )}

        <div className="ml-auto">
          {isCapturing && <span className="text-xs text-[#9c8572] animate-pulse">Capturing & extracting…</span>}
          {isFlipping && <span className="text-xs text-[#9c8572] animate-pulse">Flipping & extracting…</span>}
        </div>
      </footer>
    </div>
  );
}
