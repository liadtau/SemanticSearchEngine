import { useState, useCallback } from 'react'
import { UploadCloud, Search, Bot, Code, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import axios from 'axios'

interface Reference {
  code_snippet: string;
  relevance_score: number;
  file_path: string;
  start_line: number;
  end_line: number;
  type: string;
}

interface SearchResponse {
  agent_message: string;
  references: Reference[];
}

export default function App() {
  const [file, setFile] = useState<File | null>(null)
  const [uploadState, setUploadState] = useState<'idle' | 'uploading' | 'processing' | 'success' | 'error'>('idle')
  const [uploadMessage, setUploadMessage] = useState('')
  const [dragActive, setDragActive] = useState(false)
  
  const [query, setQuery] = useState('')
  const [searching, setSearching] = useState(false)
  const [response, setResponse] = useState<SearchResponse | null>(null)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const f = e.dataTransfer.files[0]
      if (f.name.endsWith('.zip') || f.name.endsWith('.tar.gz') || f.name.endsWith('.tar')) {
        setFile(f)
      } else {
        setUploadState('error')
        setUploadMessage('Invalid file type. Please upload .zip or .tar.gz')
      }
    }
  }, [])

  const handleUpload = async () => {
    if (!file) return;
    setUploadState('uploading')
    setUploadMessage('Uploading archive...')
    
    const formData = new FormData()
    formData.append("file", file)
    
    try {
      // Since the backend processes immediately in the background, we update message
      setUploadState('processing')
      setUploadMessage('Extracting, Chunking & Embedding...')
      
      const res = await axios.post("http://localhost:8000/api/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      })
      
      const data = res.data
      setUploadState('success')
      setUploadMessage(`Success! Indexed ${data.python_files_discovered} files and ${data.total_chunks} chunks.`)
    } catch (e: any) {
      setUploadState('error')
      setUploadMessage(e?.response?.data?.detail || "Error uploading and processing file.")
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return;
    
    setSearching(true);
    setResponse(null);
    try {
      const res = await axios.post("http://localhost:8000/api/search", { query })
      setResponse(res.data)
    } catch (e: any) {
      alert("Error searching the codebase: " + (e.message || 'unknown error'))
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0A0D14] text-white flex font-sans">
      {/* Sidebar - Ingestion Layout */}
      <aside className="w-80 border-r border-gray-800/50 bg-[#0F131D] p-6 flex flex-col justify-start">
        <header className="mb-10">
          <h1 className="text-xl font-bold flex items-center gap-3 w-full text-blue-400 tracking-tight">
            <UploadCloud size={24} /> Repository Indexer
          </h1>
          <p className="text-xs text-gray-500 mt-2">Upload your Python application compressed archive to semantic vector mapping.</p>
        </header>
        
        <div 
          className={`w-full border-2 border-dashed rounded-3xl p-8 flex flex-col items-center justify-center text-center transition-all duration-200 shadow-inner ${dragActive ? 'border-blue-400 bg-blue-500/10 scale-105' : 'border-gray-700/50 hover:border-gray-600 bg-gray-900/50'} ${uploadState === 'processing' || uploadState === 'uploading' ? 'opacity-50 pointer-events-none' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <UploadCloud className={`${dragActive ? 'text-blue-400' : 'text-gray-500'} mb-4 transition-colors`} size={36} />
          <p className="text-sm text-gray-200 font-semibold mb-1">Drag codebase here</p>
          <p className="text-xs text-gray-500 mb-6 font-medium">.zip, .tar, .tar.gz</p>
          <input 
            type="file" 
            id="file-upload"
            className="hidden"
            accept=".zip,.tar,.tar.gz"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <label htmlFor="file-upload" className="bg-[#1C2333] hover:bg-[#252D40] text-sm px-5 py-2.5 rounded-full cursor-pointer transition-all border border-gray-700/50 font-medium text-gray-300 shadow-sm">
            Browse Files
          </label>
        </div>

        {file && (
          <div className="w-full mt-6 p-4 bg-[#141A26] border border-gray-700/50 rounded-2xl flex justify-between items-center group shadow-md">
            <div className="flex flex-col overflow-hidden w-full">
              <span className="truncate text-sm font-semibold text-gray-200">{file.name}</span>
              <span className="text-xs text-gray-500 mt-0.5">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
            </div>
            <button 
              onClick={() => { setFile(null); setUploadState('idle'); setUploadMessage(''); }}
              className="text-gray-600 hover:text-red-400 p-1 bg-gray-900/50 rounded-full transition-colors opacity-0 group-hover:opacity-100"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            </button>
          </div>
        )}

        <button 
          onClick={handleUpload}
          disabled={!file || uploadState === 'uploading' || uploadState === 'processing'}
          className="w-full mt-8 bg-blue-600 hover:bg-blue-500 text-white px-4 py-3.5 rounded-2xl font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_15px_rgba(37,99,235,0.2)] active:scale-[0.98]"
        >
          {uploadState === 'idle' || uploadState === 'success' || uploadState === 'error' ? "Start Indexing" : "Processing..."}
        </button>

        {/* Status Indicators / Toast Notifications Space */}
        {uploadState !== 'idle' && (
          <div className="w-full mt-6">
            <div className={`p-4 rounded-2xl text-sm flex items-start gap-3 border shadow-sm ${
              uploadState === 'error' ? 'bg-red-950/40 border-red-900/50 text-red-400' :
              uploadState === 'success' ? 'bg-green-950/40 border-green-900/50 text-green-400' :
              'bg-blue-950/40 border-blue-900/50 text-blue-400'
            }`}>
              {uploadState === 'error' && <AlertCircle size={18} className="shrink-0 mt-0.5 opacity-80" />}
              {uploadState === 'success' && <CheckCircle size={18} className="shrink-0 mt-0.5 opacity-80" />}
              {(uploadState === 'uploading' || uploadState === 'processing') && <Loader2 size={18} className="shrink-0 mt-0.5 animate-spin opacity-80" />}
              <span className="leading-snug font-medium pt-0.5">{uploadMessage}</span>
            </div>
          </div>
        )}
      </aside>

      {/* Main Chat Panel */}
      <main className="flex-1 flex flex-col h-screen relative bg-gradient-to-br from-[#0A0D14] to-[#0d121c]">
        
        {/* Chat Log History Area */}
        <div className="flex-1 overflow-y-auto p-10 flex flex-col gap-8 scroll-smooth">
          {!response && !searching && (
            <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-6 select-none max-w-md mx-auto text-center">
              <div className="bg-gray-900/50 p-6 rounded-3xl border border-gray-800/50 shadow-2xl">
                <Bot size={56} className="text-gray-600 mb-6 mx-auto" />
                <h3 className="text-xl font-bold text-gray-300 mb-2">Codebase AI RAG Explorer</h3>
                <p className="text-sm font-medium leading-relaxed">I have a local language model and a semantic vector database. Upload an archive on the left, then ask me anything about your logic.</p>
              </div>
            </div>
          )}

          {searching && (
             <div className="w-full max-w-3xl mx-auto flex gap-4 animate-in fade-in duration-300">
                <div className="shrink-0"><Bot className="text-blue-500 bg-blue-500/10 p-2.5 rounded-xl border border-blue-500/20 shadow-sm" size={44}/></div>
                <div className="text-blue-400 animate-pulse flex items-center font-semibold text-lg">
                  Agents synthesizing semantic vectors...
                </div>
            </div>
          )}

          {response && (
            <div className="flex flex-col gap-6 w-full max-w-3xl mx-auto animate-in fade-in slide-in-from-bottom-2 duration-500">
              {/* Query Bubble */}
              <div className="self-end bg-[#2563eb] text-white px-5 py-3.5 rounded-3xl rounded-tr-sm max-w-[85%] shadow-md">
                <p className="text-[15px] font-medium leading-snug">{query}</p>
              </div>

              {/* Agent LLM Reply Bubble */}
              <div className="self-start w-full">
                <div className="flex gap-4">
                  <div className="mt-1 shrink-0"><Bot className="text-gray-300 bg-gray-800 p-2.5 rounded-xl border border-gray-700 shadow-sm" size={44}/></div>
                  <div className="text-gray-200 leading-relaxed whitespace-pre-wrap text-[15px] font-medium pt-2">
                    {response.agent_message}
                  </div>
                </div>

                {/* Vector References */}
                {response.references.length > 0 && (
                  <div className="mt-8 ml-[60px] space-y-3">
                    <h3 className="text-[11px] font-bold text-gray-500 flex items-center gap-1.5 uppercase tracking-wider mb-4">
                      <Code size={14} /> Retrieved Context
                    </h3>
                    <div className="grid grid-cols-1 gap-2.5">
                      {response.references.map((ref, i) => (
                        <details key={i} className="group bg-[#111621] border border-gray-800 hover:border-gray-700/70 rounded-2xl overflow-hidden [&_summary::-webkit-details-marker]:hidden transition-all shadow-sm">
                          <summary className="flex items-center justify-between p-3.5 px-4 cursor-pointer select-none">
                            <div className="flex items-center gap-3 overflow-hidden pr-4">
                              <span className="font-mono text-[13px] text-blue-400 font-semibold truncate hover:text-blue-300" title={ref.file_path}>{ref.file_path}</span>
                              <span className="text-[10px] text-gray-500 font-mono bg-gray-900/80 px-2 py-0.5 rounded-md border border-gray-800 shrink-0">L{ref.start_line}-{ref.end_line}</span>
                            </div>
                            <div className="flex items-center gap-3 shrink-0">
                              <span className={`px-2.5 py-1 text-[10px] font-bold rounded-full border ${ref.relevance_score > 80 ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-blue-500/10 text-blue-400 border-blue-500/20'}`}>
                                Match: {ref.relevance_score}%
                              </span>
                              <div className="w-5 h-5 rounded-full bg-gray-800 flex items-center justify-center group-open:rotate-180 transition-transform">
                                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400"><polyline points="6 9 12 15 18 9"></polyline></svg>
                              </div>
                            </div>
                          </summary>
                          <div className="p-4 bg-[#0A0D14] border-t border-gray-800 overflow-x-auto shadow-inner">
                            <pre className="text-[12px] text-emerald-400/90 font-mono leading-relaxed">
                              <code>{ref.code_snippet}</code>
                            </pre>
                          </div>
                        </details>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Bottom Input Area */}
        <div className="p-6 pb-8 bg-gradient-to-t from-[#0A0D14] via-[#0A0D14] to-transparent shrink-0">
          <form onSubmit={handleSearch} className="max-w-3xl mx-auto relative group">
            <input 
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Message your RAG Semantic Agent..."
              className="w-full bg-[#181F2E] border border-gray-700 flex text-white rounded-[24px] py-4.5 pl-6 pr-16 focus:outline-none focus:border-blue-500 focus:bg-[#1E273A] transition-all shadow-xl font-medium text-[15px] placeholder-gray-500"
              style={{ minHeight: '60px' }}
            />
            <button 
              type="submit"
              disabled={searching || !query.trim()}
              className="absolute right-2 top-2 bottom-2 bg-white text-black hover:bg-gray-200 aspect-square rounded-full transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-md flex items-center justify-center active:scale-95"
            >
              <Search size={18} strokeWidth={2.5} />
            </button>
          </form>
          <div className="text-center mt-3">
             <span className="text-[11px] font-medium text-gray-500 tracking-wide">AI-generated answers are synthezised locally and do not leave your machine.</span>
          </div>
        </div>
      </main>
    </div>
  )
}
