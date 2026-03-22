import { useState } from 'react'
import { UploadCloud, Search, Bot, Code } from 'lucide-react'

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
  const [uploading, setUploading] = useState(false)
  const [query, setQuery] = useState('')
  const [searching, setSearching] = useState(false)
  
  const [response, setResponse] = useState<SearchResponse | null>(null)

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    const formData = new FormData()
    formData.append("file", file)
    try {
      const res = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData
      })
      const data = await res.json()
      alert(`Upload complete! Found ${data.python_files_discovered} python files and embedded ${data.total_chunks} chunks.`)
    } catch (e) {
      alert("Error uploading file.")
    } finally {
      setUploading(false)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return;
    
    setSearching(true);
    setResponse(null);
    try {
      const res = await fetch("http://localhost:8000/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ query })
      })
      const data = await res.json()
      setResponse(data)
    } catch (e) {
      alert("Error searching.")
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center p-8 max-w-4xl mx-auto space-y-8">
      <header className="w-full space-y-2 text-center mt-12 mb-8">
        <h1 className="text-5xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
          Semantic RAG Engine
        </h1>
        <p className="text-gray-400 text-lg font-medium">Ask questions about your codebase, answered by AI</p>
      </header>

      {/* Upload Section */}
      <div className="w-full bg-gray-800/80 p-8 rounded-3xl border border-gray-700/50 shadow-2xl backdrop-blur-sm transition-all">
        <h2 className="text-2xl font-semibold mb-6 flex items-center gap-3 text-white"><UploadCloud className="text-blue-400"/> Index Repository</h2>
        <div className="flex gap-4 items-center">
          <input 
            type="file" 
            accept=".zip,.tar,.tar.gz" 
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-base text-gray-300 file:mr-4 file:py-3 file:px-6 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 transition-colors bg-gray-900/50 rounded-full border border-gray-700/50"
          />
          <button 
            onClick={handleUpload}
            disabled={!file || uploading}
            className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-full font-bold transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/20"
          >
            {uploading ? "Indexing..." : "Upload"}
          </button>
        </div>
      </div>

      {/* Search Section */}
      <div className="w-full flex-1 flex flex-col items-center w-full">
        <form onSubmit={handleSearch} className="w-full relative shadow-2xl group">
          <input 
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything about the codebase... (e.g. 'How is authentication handled?')"
            className="w-full bg-gray-800/90 border border-gray-700 text-white rounded-full py-5 pl-8 pr-16 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/50 transition-all font-medium text-lg placeholder-gray-500"
          />
          <button 
            type="submit"
            disabled={searching || !query}
            className="absolute right-3 top-3 bottom-3 bg-blue-600 hover:bg-blue-500 p-4 rounded-full transition-colors disabled:opacity-50 text-white shadow-md shadow-blue-500/30"
          >
            <Search size={22} />
          </button>
        </form>

        {searching && (
          <div className="mt-12 text-blue-400 animate-pulse flex items-center gap-3 font-semibold text-lg bg-blue-500/10 px-6 py-3 rounded-full border border-blue-500/20">
            <Bot size={24} className="animate-bounce" /> Agent is synthesizing a response...
          </div>
        )}

        {response && (
          <div className="w-full mt-10 flex flex-col gap-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="bg-gray-800/90 p-8 rounded-3xl border border-gray-700 flex gap-6 shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
              <div className="mt-1"><Bot className="text-blue-400 p-2 bg-blue-500/10 rounded-xl" size={48}/></div>
              <div className="text-gray-100 leading-relaxed whitespace-pre-wrap text-lg font-medium">{response.agent_message}</div>
            </div>

            <div className="space-y-4">
              <h3 className="text-xl font-bold text-gray-200 flex items-center gap-3 pl-2">
                <Code size={24} className="text-gray-400" /> Retrieved Context
              </h3>
              {response.references.map((ref, i) => (
                <details key={i} className="group bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden [&_summary::-webkit-details-marker]:hidden shadow-lg transition-all hover:border-gray-700">
                  <summary className="flex items-center justify-between p-5 cursor-pointer bg-gray-800/30 hover:bg-gray-800/80 transition-colors select-none">
                    <div className="flex items-center gap-4">
                      <span className="font-mono text-base text-blue-400 font-semibold">{ref.file_path}</span>
                      <span className="text-xs text-gray-500 bg-gray-950 px-3 py-1 rounded-full border border-gray-800">Lines {ref.start_line}-{ref.end_line}</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className={`px-4 py-1.5 text-xs font-bold rounded-full border ${ref.relevance_score > 80 ? 'bg-green-900/30 text-green-400 border-green-700/50' : 'bg-blue-900/30 text-blue-400 border-blue-700/50'}`}>
                        Relevance: {ref.relevance_score}%
                      </span>
                      <div className="w-6 h-6 rounded-full bg-gray-700 flex items-center justify-center group-open:rotate-180 transition-transform">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="text-gray-300"><polyline points="6 9 12 15 18 9"></polyline></svg>
                      </div>
                    </div>
                  </summary>
                  <div className="p-6 bg-[#0d1117] border-t border-gray-800 overflow-x-auto">
                    <pre className="text-sm text-gray-300 font-mono leading-relaxed">
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
  )
}
