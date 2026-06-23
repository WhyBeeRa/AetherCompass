import React, { useState, useEffect, useRef, Suspense } from 'react';
import { Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Shield, 
  Activity, 
  Layers, 
  BarChart3, 
  Box, 
  LogOut, 
  ChevronRight, 
  AlertCircle, 
  Database, 
  Cpu, 
  Terminal,
  RefreshCw,
  Search,
  CheckCircle2,
  XCircle,
  Clock,
  ExternalLink,
  PlusSquare,
  Zap
} from 'lucide-react';
import { useAuth } from '../AuthContext';
import { apiFetch, API_BASE } from '../api';
import { motion, AnimatePresence } from 'framer-motion';

// --- Sub-Components (Sections) ---
import ReviewQueue from './ReviewQueue';
import AdminAnalytics from './AdminAnalytics';
import AdminVault from './AdminVault';
import AdminAgentConsole from './AdminAgentConsole';
import AdminSentinel from './AdminSentinel';
import ErrorBoundary from '../components/ErrorBoundary';

// Lazy load the AI Factory Panel (local-only)
const AIFactoryPanel = React.lazy(() => import('./AIFactoryPanel'));

const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

const SystemPulse = () => {
  const { currentUser } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeLog, setActiveLog] = useState('tasks');
  const [isPulsing, setIsPulsing] = useState(false);
  const [connectionActive, setConnectionActive] = useState(false);
  const [telemetry, setTelemetry] = useState({
    ram_usage: 'N/A',
    db_status: 'N/A',
    embedder: 'N/A',
    memory_usage_mb: 'N/A',
    embedder_status: 'N/A',
    timestamp: null
  });
  const terminalRef = useRef(null);
  const wsRef = useRef(null);
  const heartbeatInterval = useRef(null);
  const reconnectTimeout = useRef(null);

  // BUG-6 fix: Consolidated into single health fetch using /admin/heartbeat for richer data
  const fetchHealthData = async () => {
    try {
      const token = isLocal ? "dev-admin-token" : await currentUser.getIdToken();
      const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };

      // Fetch detailed heartbeat (admin endpoint with memory, embedder status, db)
      const resHb = await apiFetch('/admin/heartbeat', { headers });
      if (resHb.ok) {
        const data = await resHb.json();
        setTelemetry(prev => ({
          ...prev,
          memory_usage_mb: data.memory_usage_mb,
          embedder_status: data.embedder_status,
          db_status: data.database_status === 'CONNECTED' ? 'Connected' : data.database_status,
          embedder: data.embedder_status === 'ACTIVE' ? 'Online' : data.embedder_status,
          timestamp: data.timestamp
        }));
        setConnectionActive(true);
        setIsPulsing(true);
        setTimeout(() => setIsPulsing(false), 600);
      } else {
        // Fallback to public health endpoint if admin heartbeat fails
        const resPub = await apiFetch('/api/health', { headers });
        if (resPub.ok) {
          const pubData = await resPub.json();
          setTelemetry(prev => ({ ...prev, ...pubData }));
          setConnectionActive(true);
          setIsPulsing(true);
          setTimeout(() => setIsPulsing(false), 600);
        } else {
          setConnectionActive(false);
        }
      }
    } catch (err) {
      console.error("Health data error:", err);
      setConnectionActive(false);
    } finally {
      setLoading(false);
    }
  };

  // REST-based log fetch (for tab switching)
  const fetchLogs = async () => {
    try {
      const token = isLocal ? "dev-admin-token" : await currentUser.getIdToken();
      const resLogs = await apiFetch(`/admin/logs?log_type=${activeLog}&lines=50`, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      if (resLogs.ok) {
        const dataLogs = await resLogs.json();
        setLogs(dataLogs.lines || []);
      }
    } catch (err) {
      console.error("Log fetch error:", err);
    }
  };

  // BUG-13 fix: Strip trailing slashes from API_BASE to prevent double-slash in WS URL
  const connectWS = async () => {
    if (wsRef.current) wsRef.current.close();
    if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
    if (heartbeatInterval.current) clearInterval(heartbeatInterval.current);

    try {
        const token = isLocal ? "dev-admin-token" : (currentUser ? await currentUser.getIdToken() : "");
        const wsProtocol = API_BASE.startsWith('https') ? 'wss:' : 'ws:';
        const wsHost = API_BASE.replace(/^https?:\/\//, '').replace(/\/+$/, '');
        const wsUrl = `${wsProtocol}//${wsHost}/ws/logs?token=${encodeURIComponent(token)}`;
        
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
            setConnectionActive(true);
            console.log("WebSocket connected to:", wsUrl);
            
            heartbeatInterval.current = setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: 'ping' }));
                }
            }, 30000);
        };

        ws.onmessage = (event) => {
            const message = event.data;
            try {
                const data = JSON.parse(message);
                if (data.type === 'pong') return;
            } catch (e) {
                // Not JSON, treat as raw log line
            }
            
            setLogs(prev => {
                const updated = [...prev, message];
                return updated.slice(-200); 
            });
        };

        ws.onclose = (event) => {
            setConnectionActive(false);
            if (event.code === 1008) {
                console.error("WebSocket connection rejected: unauthorized access.");
                return;
            }
            console.log("WebSocket disconnected. Retrying in 5s...");
            if (heartbeatInterval.current) clearInterval(heartbeatInterval.current);
            reconnectTimeout.current = setTimeout(connectWS, 5000);
        };

        ws.onerror = (err) => {
            console.error("WebSocket error:", err);
            ws.close();
        };
    } catch (e) {
        console.error("Failed to connect to logs WebSocket:", e);
        reconnectTimeout.current = setTimeout(connectWS, 5000);
    }
  };

  // BUG-7 fix: WebSocket connection — independent of activeLog tab
  useEffect(() => {
    fetchHealthData();
    connectWS();

    // BUG-8 fix: Reduced from 3s to 15s
    const healthInterval = setInterval(fetchHealthData, 15000);

    return () => {
      clearInterval(healthInterval);
      if (wsRef.current) wsRef.current.close();
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      if (heartbeatInterval.current) clearInterval(heartbeatInterval.current);
    };
  }, []);

  // BUG-7 fix: REST logs — re-fetch only on tab change
  useEffect(() => {
    fetchLogs();
  }, [activeLog]);

  // Auto-scroll terminal
  useEffect(() => {
    if (terminalRef.current) {
        terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  // BUG-5 fix: Parse RAM percentage as number for progress bar
  const ramPercent = telemetry.ram_usage && telemetry.ram_usage !== 'N/A' 
    ? parseFloat(telemetry.ram_usage) 
    : 0;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Heartbeat Card */}
        <div className="bg-white/[0.02] border border-white/10 rounded-3xl p-6 backdrop-blur-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-cyan-500/10 rounded-xl">
              <Activity className="w-5 h-5 text-cyan-400" />
            </div>
            <h3 className="font-bold text-white text-sm uppercase tracking-widest">Backend Heartbeat</h3>
          </div>
          
          <div className="space-y-4">
            {/* BUG-3 fix: Dynamic status based on connectionActive state */}
            <div className="flex justify-between items-center text-sm">
                <span className="text-white/40">Status</span>
                <span className={`flex items-center gap-2 font-bold ${connectionActive ? 'text-emerald-400' : 'text-rose-400'}`}>
                    <div className={`w-2 h-2 rounded-full ${connectionActive ? 'bg-emerald-500' : 'bg-rose-500'} transition-all duration-300 ${isPulsing ? 'scale-150 shadow-[0_0_10px_#10b981]' : 'scale-100 shadow-none'}`} />
                    {connectionActive ? 'ONLINE' : 'OFFLINE'}
                </span>
            </div>
            {/* BUG-6 fix: Updated label from ONNX to Gemini */}
            <div className="flex justify-between items-center text-sm">
                <span className="text-white/40">Embedder (Gemini)</span>
                <span className={`font-bold ${telemetry.embedder === 'Online' || telemetry.embedder_status === 'ACTIVE' ? 'text-cyan-400' : 'text-rose-400'}`}>
                    {telemetry.embedder_status !== 'N/A' ? telemetry.embedder_status : telemetry.embedder}
                </span>
            </div>
            <div className="flex justify-between items-center text-sm">
                <span className="text-white/40">Database</span>
                <span className={`font-bold ${telemetry.db_status === 'Connected' ? 'text-white/80' : 'text-rose-400'}`}>
                    {telemetry.db_status}
                </span>
            </div>
             <div className="flex justify-between items-center text-sm mb-4">
                <span className="text-white/40">RAM Usage</span>
                <span className="text-white/80 font-mono">{telemetry.ram_usage !== 'N/A' ? telemetry.ram_usage : (telemetry.memory_usage_mb !== 'N/A' ? `${telemetry.memory_usage_mb} MB` : 'N/A')}</span>
            </div>

            <button 
                onClick={async () => {
                    try {
                    const token = isLocal ? "dev-admin-token" : await currentUser.getIdToken();
                    const res = await apiFetch('/api/agents/metrics/run', {
                        method: 'POST',
                        headers: { 
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        }
                    });
                        if (res.ok) alert("Live Pulse Refresh Triggered (Metrics Agent)");
                        else alert("Manual Refresh Failed");
                    } catch (err) {
                        alert("Network error during pulse refresh");
                    }
                }}
                className="w-full mt-4 py-2 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-2"
            >
                <RefreshCw className="w-3 h-3" />
                Refresh Live Pulse
            </button>
          </div>
        </div>

        {/* Resources Card */}
        <div className="bg-white/[0.02] border border-white/10 rounded-3xl p-6 backdrop-blur-xl md:col-span-2">
           <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-indigo-500/10 rounded-xl">
              <Cpu className="w-5 h-5 text-indigo-400" />
            </div>
            <h3 className="font-bold text-white text-sm uppercase tracking-widest">Resource Monitor</h3>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* BUG-5 fix: Parse RAM percentage as number for reliable animation */}
            <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                <div className="text-[10px] text-white/30 uppercase tracking-widest mb-1">System Load (RAM)</div>
                <div className="flex items-center gap-3">
                  <div className="h-2 flex-1 bg-white/5 rounded-full overflow-hidden">
                    <motion.div 
                        initial={{ width: 0 }} 
                        animate={{ width: `${ramPercent}%` }} 
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                        className={`h-full rounded-full ${ramPercent > 80 ? 'bg-rose-500' : ramPercent > 60 ? 'bg-amber-500' : 'bg-indigo-500'}`} 
                    />
                  </div>
                  <span className="text-xs font-mono text-white/60 min-w-[40px] text-right">{ramPercent > 0 ? `${ramPercent}%` : 'N/A'}</span>
                </div>
            </div>
             {/* BUG-4 fix: Wired to real data instead of hardcoded values */}
             <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                <div className="text-[10px] text-white/30 uppercase tracking-widest mb-1">Process Memory</div>
                <div className="text-xl font-mono font-bold text-white">{telemetry.memory_usage_mb !== 'N/A' ? `${telemetry.memory_usage_mb}` : '—'} <span className="text-xs text-white/20">MB</span></div>
            </div>
             <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                <div className="text-[10px] text-white/30 uppercase tracking-widest mb-1">Embedder Status</div>
                <div className={`text-sm font-mono font-bold ${telemetry.embedder_status === 'ACTIVE' ? 'text-emerald-400' : telemetry.embedder_status === 'LOADING' ? 'text-amber-400' : 'text-rose-400'}`}>
                  {telemetry.embedder_status !== 'N/A' ? telemetry.embedder_status : '—'} <span className="text-xs text-white/20">{telemetry.embedder_status === 'ACTIVE' ? 'Gemini API' : ''}</span>
                </div>
            </div>
             <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                <div className="text-[10px] text-white/30 uppercase tracking-widest mb-1">Last Heartbeat</div>
                <div className="text-[10px] font-mono text-white/60 truncate">{telemetry.timestamp ? new Date(telemetry.timestamp).toLocaleTimeString() : '—'}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Log Console */}
      <div className="bg-[#040914] border border-white/10 rounded-3xl overflow-hidden shadow-2xl">
        <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-3">
                <Terminal className="w-5 h-5 text-cyan-400" />
                <h3 className="font-bold text-white text-sm uppercase tracking-widest font-mono">Kernel Log Terminal</h3>
                <div className={`ml-4 px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-widest flex items-center gap-1.5 transition-all ${connectionActive ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20 animate-pulse'}`}>
                    <div className={`w-1 h-1 rounded-full ${connectionActive ? 'bg-emerald-500' : 'bg-rose-500'}`} />
                    {connectionActive ? 'Link Active' : 'Link Lost'}
                </div>
            </div>
            <div className="flex gap-2">
                <button 
                  onClick={() => setActiveLog('tasks')}
                  className={`px-3 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider transition-all ${activeLog === 'tasks' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'text-white/30 hover:text-white'}`}
                >
                  Tasks
                </button>
                 <button 
                  onClick={() => setActiveLog('error')}
                  className={`px-3 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider transition-all ${activeLog === 'error' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 'text-white/30 hover:text-white'}`}
                >
                  Errors
                </button>
            </div>
        </div>
        <div 
            ref={terminalRef}
            className="p-6 bg-black min-h-[400px] max-h-[600px] overflow-y-auto font-mono text-[11px] leading-relaxed scrollbar-hide"
        >
            {loading ? (
                <div className="flex items-center justify-center h-full text-white/20 animate-pulse">Initializing direct neural link...</div>
            ) : logs.length === 0 ? (
                <div className="text-white/20">No new logs in buffer.</div>
            ) : (
                logs.map((line, i) => (
                    <div key={i} className="py-0.5">
                        <span className="text-white/20 mr-4">[{i+1}]</span>
                        <span className={line.includes('FAIL') || line.includes('ERROR') ? 'text-rose-400' : line.includes('SUCCESS') ? 'text-emerald-400' : 'text-white/60'}>
                            {line}
                        </span>
                    </div>
                ))
            )}
        </div>
      </div>
    </div>
  );
};

export default function AdminDashboard() {
  const { currentUser, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Guard Clause
  useEffect(() => {
    if (isLocal) return; // Skip redirects on local development
    
    if (!currentUser) {
      navigate('/activation');
    } else if (currentUser && !isAdmin) {
      navigate('/');
    }
  }, [currentUser, isAdmin, navigate]);

  if (!isLocal && (!currentUser || !isAdmin)) return null;

  const currentPath = location.pathname;

  const menuItems = [
    { id: 'pulse', label: 'System Pulse', icon: Activity, path: '/admin' },
    { id: 'sentinel', label: 'Sentinel', icon: Shield, path: '/admin/sentinel' },
    { id: 'review', label: 'Review Queue', icon: Layers, path: '/admin/requests' },
    { id: 'agent', label: 'Agent Console', icon: Terminal, path: '/admin/agent' },
    { id: 'manual', label: 'Manual Entry', icon: PlusSquare, path: '/admin/vault' },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, path: '/admin/analytics' },
    ...(isLocal ? [{ id: 'factory', label: 'AI Factory', icon: Cpu, path: '/admin/factory' }] : []),
  ];

  return (
    <div className="fixed inset-0 bg-[#040914] z-[60] flex overflow-hidden">
      {/* --- Sidebar --- */}
      <aside className="w-72 bg-black border-r border-white/5 flex flex-col items-center py-10 px-6">
        {/* Brand */}
        <Link to="/" className="flex flex-col items-center gap-2 mb-16 hover:opacity-80 transition-all group">
            <div className="relative">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-cyan-400 to-indigo-600 flex items-center justify-center text-white font-black text-2xl shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
                A
              </div>
              <div className="absolute -inset-2 bg-cyan-400/20 blur-xl rounded-full -z-10 group-hover:bg-cyan-400/30 transition-colors"></div>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-xl font-bold tracking-tight text-white uppercase italic">Protocol <span className="text-cyan-400">Admin</span></span>
              <span className="text-[0.6rem] font-medium text-white/30 tracking-[0.4em] uppercase leading-none">Command Center</span>
            </div>
        </Link>

        {/* Navigation */}
        <nav className="flex-1 w-full space-y-2">
            {menuItems.map((item) => {
                const isActive = (item.id === 'pulse' && currentPath === '/admin') || (item.id !== 'pulse' && currentPath.includes(item.path));
                return (
                    <Link 
                        key={item.id} 
                        to={item.path}
                        className={`w-full flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-300 group ${isActive ? 'bg-white/10 text-white' : 'text-white/40 hover:text-white hover:bg-white/5'}`}
                    >
                        <item.icon className={`w-5 h-5 ${isActive ? 'text-cyan-400' : 'group-hover:text-cyan-300'} transition-colors`} />
                        <span className="text-sm font-bold tracking-wide">{item.label}</span>
                        {isActive && <ChevronRight className="w-4 h-4 ml-auto text-white/20" />}
                    </Link>
                );
            })}
        </nav>

        {/* Footer info/Logout */}
        <div className="w-full pt-10 mt-auto border-t border-white/5 space-y-6">
            <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/10 border border-white/10 flex items-center justify-center overflow-hidden">
                    {currentUser?.photoURL ? (
                        <img src={currentUser.photoURL} alt={currentUser.email} className="w-full h-full object-cover" />
                    ) : (
                        <span className="text-xs font-bold text-white/40 uppercase">{currentUser?.email ? currentUser.email[0] : 'L'}</span>
                    )}
                </div>
                <div className="flex-1 truncate">
                    <div className="text-xs font-bold text-white truncate">{currentUser?.displayName || currentUser?.email?.split('@')[0] || 'Local Admin'}</div>
                    <div className="text-[10px] text-white/20 uppercase tracking-widest font-black">Authorized Level 5</div>
                </div>
            </div>
            
            <button 
                onClick={logout}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-black uppercase tracking-[0.2em] transition-all border border-rose-500/20"
            >
                <LogOut className="w-4 h-4" />
                Terminate Session
            </button>
        </div>
      </aside>

      {/* --- Main Content Area --- */}
      <main className="flex-1 h-screen overflow-y-auto bg-[#040914] relative scrollbar-hide">
        {/* Grain Overlay */}
        <div className="absolute inset-0 pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] mix-blend-overlay"></div>
        
        <header className="sticky top-0 z-40 w-full h-24 flex items-center justify-between px-12 border-b border-white/5 backdrop-blur-md bg-[#040914]/80">
            <div>
                <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
                    {menuItems.find(i => (i.id === 'pulse' && currentPath === '/admin') || (i.id !== 'pulse' && currentPath.includes(i.path)))?.label || 'Admin'}
                    <span className="text-[10px] text-white/20 font-mono tracking-[0.3em] uppercase">• Real-time Link Active</span>
                </h2>
            </div>
            
            <div className="flex items-center gap-6">
                 <div className="flex items-center gap-2 px-4 py-2 bg-indigo-500/10 border border-indigo-500/20 rounded-full">
                    <Zap className="w-3.5 h-3.5 text-indigo-400" />
                    <span className="text-[10px] font-bold text-indigo-300 uppercase tracking-widest">Enterprise Protocol</span>
                </div>
                <div className="w-px h-8 bg-white/5"></div>
                <Link to="/" className="text-sm font-bold text-white/40 hover:text-white flex items-center gap-2 transition-all">
                    Exit Control Room <XCircle className="w-4 h-4" />
                </Link>
            </div>
        </header>

        <div className="p-12 max-w-7xl mx-auto min-h-[calc(100vh-6rem)]">
            <ErrorBoundary>
                <AnimatePresence mode="wait">
                    <Routes>
                        <Route path="/" element={<SystemPulse />} />
                        <Route path="/sentinel" element={<AdminSentinel />} />
                        <Route path="/requests" element={<ReviewQueue />} />
                        <Route path="/agent" element={<AdminAgentConsole />} />
                        <Route path="/analytics" element={<AdminAnalytics />} />
                        <Route path="/vault" element={<AdminVault />} />
                        {isLocal && <Route path="/factory" element={
                          <Suspense fallback={<div className="text-white/20 animate-pulse p-8">Loading AI Factory...</div>}>
                            <AIFactoryPanel />
                          </Suspense>
                        } />}
                    </Routes>
                </AnimatePresence>
            </ErrorBoundary>
        </div>
      </main>
    </div>
  );
}
