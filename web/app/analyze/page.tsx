"use client"

import { useState, useRef, useCallback } from "react"
import Link from "next/link"

function compressImage(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      const MAX = 1600
      let w = img.width
      let h = img.height
      if (w > MAX || h > MAX) {
        if (w > h) { h = Math.round((h * MAX) / w); w = MAX }
        else { w = Math.round((w * MAX) / h); h = MAX }
      }
      const canvas = document.createElement("canvas")
      canvas.width = w
      canvas.height = h
      const ctx = canvas.getContext("2d")!
      ctx.drawImage(img, 0, 0, w, h)
      resolve(canvas.toDataURL("image/jpeg", 0.82))
    }
    img.onerror = reject
    img.src = URL.createObjectURL(file)
  })
}

export default function AnalyzePage() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = useCallback((f: File) => {
    if (!f.type.startsWith("image/")) { setError("Please upload an image file."); return }
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setError(null)
  }, [])

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }, [handleFile])

  const onInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) handleFile(f)
  }, [handleFile])

  const handleSubmit = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const compressed = await compressImage(file)

      // Store image so results page can retrieve it
      localStorage.setItem("fs_image", compressed)

      // Create Stripe checkout session
      const res = await fetch("/api/checkout", { method: "POST" })
      const data = await res.json()
      if (data.error) throw new Error(data.error)
      window.location.href = data.url
    } catch (err: any) {
      setError(err.message || "Something went wrong. Please try again.")
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-[#080808] text-white flex flex-col">
      <nav className="max-w-5xl mx-auto px-6 py-5 w-full flex items-center justify-between">
        <Link href="/" className="font-bold text-lg tracking-tight">FinalOffer</Link>
        <span className="text-gray-500 text-sm">Step 1 of 2: Upload your menu</span>
      </nav>

      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-xl">
          <h1 className="text-3xl font-bold mb-2 text-center">Upload your finance menu</h1>
          <p className="text-gray-400 text-center mb-8">
            In the dealership, photograph the add-on sheet or price menu they show you. Any angle works.
          </p>

          {!preview ? (
            <div
              onClick={() => inputRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              className={`border-2 border-dashed rounded-2xl p-16 text-center cursor-pointer transition-colors ${
                dragging
                  ? "border-amber-400 bg-amber-400/5"
                  : "border-[#2a2a2a] hover:border-[#3a3a3a] bg-[#0f0f0f]"
              }`}
            >
              <div className="text-5xl mb-4">📄</div>
              <p className="font-semibold text-lg mb-2">Drop your photo here</p>
              <p className="text-gray-500 text-sm mb-4">or click to browse</p>
              <p className="text-gray-600 text-xs">JPG, PNG, HEIC · up to 20MB</p>
            </div>
          ) : (
            <div className="relative rounded-2xl overflow-hidden border border-[#1e1e1e] bg-[#0f0f0f]">
              <img src={preview} alt="Finance menu" className="w-full max-h-80 object-contain" />
              <button
                onClick={() => { setFile(null); setPreview(null) }}
                className="absolute top-3 right-3 bg-black/70 hover:bg-black text-white rounded-full w-8 h-8 flex items-center justify-center text-sm transition"
              >
                ✕
              </button>
            </div>
          )}

          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={onInputChange}
            className="hidden"
          />

          {error && (
            <p className="mt-4 text-red-400 text-sm text-center bg-red-400/10 rounded-lg p-3">{error}</p>
          )}

          <button
            onClick={handleSubmit}
            disabled={!file || loading}
            className="mt-6 w-full bg-amber-400 hover:bg-amber-300 disabled:opacity-40 disabled:cursor-not-allowed text-black font-bold py-4 rounded-xl text-lg transition"
          >
            {loading ? "Preparing your checkout…" : "Get My Report — $19"}
          </button>

          <p className="text-center text-gray-600 text-xs mt-4">
            Secure payment via Stripe · Your report appears immediately after payment
          </p>

          <div className="mt-8 bg-[#0f0f0f] border border-[#1a1a1a] rounded-xl p-4">
            <p className="text-xs text-gray-500 mb-2 font-semibold uppercase tracking-widest">Pro tip</p>
            <p className="text-sm text-gray-400">
              Ask the F&I manager to "give you a minute to review the figures." They legally must.
              Use that time to snap this photo and run it through FinalOffer.
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
