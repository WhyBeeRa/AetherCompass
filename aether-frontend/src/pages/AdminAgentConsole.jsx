import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { apiFetch, API_BASE } from '../api';
import { Terminal, Shield, Play, Loader2, CheckCircle2, AlertTriangle, Info, PlusSquare } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function AdminAgentConsole() {
  const { currentUser } = useAuth();
  const [url, setUrl] = useState('');
  const [isAuditing, setIsAuditing] = useState(false);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const logsEndRef = useRef(null);

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs, result]);

  const startAudit = async (e) => {
    e.preventDefault();
    if (!url) return;

    setLogs([]);
    setResult(null);
    setError(null);
    setIsAuditing(true);

    try {
      const token = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') 
          ? "dev-admin-token" 
          : await currentUser.getIdToken();
          
      const response = await apiFetch('/admin/agent/investigate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url })
      });

      if (!response.ok) {
        let errStr = `status: ${response.status}`;
        try {
          const errObj = await response.json();
          errStr += ` - ${errObj.detail || JSON.stringify(errObj)}`;
        } catch (e) {
          try {
             const errText = await response.text();
             errStr += ` - ${errText}`;
          } catch(e2) {}
        }
        throw new Error(`HTTP error! ${errStr}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n').filter(line => line.trim() !== '');
        
        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            if (data.type === 'log') {
              setLogs(prev => [...prev, data.message]);
            } else if (data.type === 'result') {
              setResult(data.data);
            } else if (data.type === 'error') {
              setError(data.message);
              setLogs(prev => [...prev, `ERROR: ${data.message}`]);
            }
          } catch (e) {
            console.error("Error parsing JSON chunk:", e, line);
          }
        }
      }
    } catch (err) {
      console.error(err);
      setError(err.message);
      setLogs(prev => [...prev, `CRITICAL FAILURE: ${err.message}`]);
    } finally {
      setIsAuditing(false);
    }
  };

  const saveToVault = async () => {
    if (!result) return;
    try {
      const token = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') 
          ? "dev-admin-token" 
          : await currentUser.getIdToken();

      const payload = {
        name: result.name,
        description: result.web_consensus || result.audit_notes,
        website_url: url,
        intent_category: result.category,
        use_cases: result.use_cases || [],
        pros: result.pros || [],
        cons: result.cons || [],
        accuracy: 5,
        speed: 5,
        value: 5,
        ease_of_use: 5,
        pricing: result.pricing_model || "Unknown",
        learning_curve: "Medium",
        latency_label: "Unknown",
        cost_label: result.pricing_details || "Unknown",
        privacy_grade: "Unknown",
        integration: "Web",
        visual_quality: "Mid",
        trust_score: result.trust_score || 50
      };

      const response = await apiFetch('/admin/vault/tool', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        alert("Tool successfully added to Vault!");
      } else {
        const err = await response.json();
        alert("Failed to save: " + (err.detail || "Unknown error"));
      }
    } catch (error) {
      alert("Error: " + error.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-8">
        <div className="p-3 bg-indigo-500/10 rounded-2xl border border-indigo-500/20">
          <Terminal className="w-6 h-6 text-indigo-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Agent Console</h2>
          <p className="text-sm text-white/40 font-mono tracking-wider uppercase mt-1">Deep Auditor Protocol</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Control Panel */}
        <div className="bg-white/[0.02] border border-white/10 rounded-3xl p-6 backdrop-blur-xl h-fit">
          <form onSubmit={startAudit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-white/50 uppercase tracking-widest mb-2">Target URL</label>
              <input
                type="url"
                required
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-indigo-500/50 transition-colors"
                disabled={isAuditing}
              />
            </div>
            <button
              type="submit"
              disabled={isAuditing || !url}
              className="w-full flex items-center justify-center gap-2 bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-400 border border-indigo-500/50 rounded-xl py-3 font-black uppercase tracking-widest transition-all disabled:opacity-50"
            >
              {isAuditing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Auditing...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 fill-current" />
                  Initiate Deep Audit
                </>
              )}
            </button>
          </form>

          {/* Terminal Output */}
          <div className="mt-8 bg-black border border-white/10 rounded-2xl overflow-hidden shadow-inner h-[400px] flex flex-col">
            <div className="px-4 py-2 bg-white/5 border-b border-white/10 flex items-center justify-between">
              <span className="text-[10px] font-mono text-white/50 uppercase tracking-widest">Execution Log</span>
              <span className="flex items-center gap-2 text-[10px] text-white/30">
                <div className={`w-2 h-2 rounded-full ${isAuditing ? 'bg-amber-500 animate-pulse' : 'bg-white/20'}`} />
                {isAuditing ? 'Active' : 'Standby'}
              </span>
            </div>
            <div className="p-4 overflow-y-auto flex-1 font-mono text-xs leading-relaxed space-y-2 scrollbar-hide">
              {logs.length === 0 && !isAuditing && (
                <div className="text-white/20 text-center mt-10">Awaiting target parameters...</div>
              )}
              {logs.map((log, idx) => (
                <motion.div 
                  initial={{ opacity: 0, x: -10 }} 
                  animate={{ opacity: 1, x: 0 }} 
                  key={idx} 
                  className={log.includes('ERROR') || log.includes('FAILED') ? 'text-rose-400' : 'text-indigo-200'}
                >
                  <span className="text-white/30 mr-3">[{new Date().toLocaleTimeString()}]</span>
                  {log}
                </motion.div>
              ))}
              <div ref={logsEndRef} />
            </div>
          </div>
        </div>

        {/* Results Panel */}
        <div className="bg-white/[0.02] border border-white/10 rounded-3xl p-6 backdrop-blur-xl flex flex-col">
          <h3 className="text-sm font-bold text-white uppercase tracking-widest mb-6 flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-400" /> Intelligence Report
          </h3>

          {!result && !isAuditing && !error && (
            <div className="flex-1 flex items-center justify-center text-white/20 text-sm font-mono border border-dashed border-white/10 rounded-2xl">
              No report generated yet.
            </div>
          )}

          {isAuditing && !result && (
            <div className="flex-1 flex flex-col items-center justify-center text-indigo-400 gap-4">
              <Loader2 className="w-10 h-10 animate-spin opacity-50" />
              <div className="text-sm font-mono tracking-widest uppercase animate-pulse">Compiling Intel...</div>
            </div>
          )}

          <AnimatePresence>
            {result && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }} 
                animate={{ opacity: 1, y: 0 }} 
                className="flex-1 overflow-y-auto space-y-6 scrollbar-hide"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="text-2xl font-bold text-white">{result.name}</h4>
                    <span className="text-xs text-white/50 bg-white/5 px-2 py-1 rounded-md font-mono mt-2 inline-block">{result.category}</span>
                  </div>
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center text-2xl font-black ${result.trust_score >= 80 ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : result.trust_score >= 50 ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'}`}>
                    {Math.round(result.trust_score)}
                  </div>
                </div>

                <div className="bg-black/30 p-4 rounded-xl border border-white/5">
                  <p className="text-sm text-white/80 leading-relaxed"><span className="text-indigo-400 font-bold mr-2">Consensus:</span> {result.web_consensus}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/5 p-3 rounded-xl">
                    <div className="text-[10px] text-white/40 uppercase tracking-widest mb-1">Pricing Model</div>
                    <div className="text-sm text-white font-bold">{result.pricing_model}</div>
                  </div>
                  <div className="bg-white/5 p-3 rounded-xl">
                    <div className="text-[10px] text-white/40 uppercase tracking-widest mb-1">Pricing Details</div>
                    <div className="text-sm text-white/80 truncate">{result.pricing_details || "N/A"}</div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 uppercase tracking-widest mb-3">
                      <CheckCircle2 className="w-4 h-4" /> Pros
                    </div>
                    <ul className="space-y-2">
                      {result.pros.map((pro, i) => (
                        <li key={i} className="text-xs text-white/70 bg-emerald-500/5 border border-emerald-500/10 px-3 py-2 rounded-lg">{pro}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <div className="flex items-center gap-2 text-xs font-bold text-rose-400 uppercase tracking-widest mb-3">
                      <AlertTriangle className="w-4 h-4" /> Cons
                    </div>
                    <ul className="space-y-2">
                      {result.cons.map((con, i) => (
                        <li key={i} className="text-xs text-white/70 bg-rose-500/5 border border-rose-500/10 px-3 py-2 rounded-lg">{con}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="bg-amber-500/5 border border-amber-500/20 p-4 rounded-xl">
                  <div className="flex items-center gap-2 text-xs font-bold text-amber-400 uppercase tracking-widest mb-2">
                    <Info className="w-4 h-4" /> Audit Notes
                  </div>
                  <p className="text-xs text-amber-100/70">{result.audit_notes}</p>
                </div>

                <button 
                  onClick={saveToVault}
                  className="w-full py-4 mt-6 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 hover:from-emerald-500/30 hover:to-cyan-500/30 border border-emerald-500/50 text-emerald-400 font-black uppercase tracking-widest rounded-xl transition-all flex items-center justify-center gap-2"
                >
                  <PlusSquare className="w-5 h-5" /> Commit to Vault
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
