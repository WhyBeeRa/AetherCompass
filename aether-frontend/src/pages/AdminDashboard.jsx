import React, { useState, useEffect, useRef } from 'react';
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
import ErrorBoundary from '../components/ErrorBoundary';

const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

const SystemPulse = () => {
  const { currentUser } = useAuth();
  const [heartbeat, setHeartbeat] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeLog, setActiveLog] = useState('tasks');
  const [isPulsing, setIsPulsing] = useState(false);
  const [connectionActive, setConnectionActive] = useState(true);
  const [telemetry, setTelemetry] = useState({
    ram_usage: 'N/A',
    db_status: 'N/A',
    embedder: 'N/A'
  });
  const terminalRef = useRef(null);
  const wsRef = useRef(null);

  const fetchTelemetry = async () => {
    try {
      const res = await apiFetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        setTelemetry(data);
      }
    } catch (err) {
      console.error("Telemetry error:", err);
    }
  };

  const fetchLogs = async () => {
    try {
      const token = isLocal ? "dev-admin-token" : await currentUser.getIdToken();
      const resLogs = await apiFetch(`/admin/logs?log_type=${activeLog}&lines=50`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (resLogs.ok) {
        const dataLogs = await resLogs.json();
        setLogs(dataLogs.lines || []);
      }
    } catch (err) {
      console.error("Log fetch error:", err);
    }
  };

  const fetchDiagnostics = async () => {
    try {
      const token = isLocal ? "dev-admin-token" : await currentUser.getIdToken();
      
      // Heartbeat Only
      const resHb = await apiFetch('/admin/heartbeat', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (resHb.ok) {
        const dataHb = await resHb.json();
        setHeartbeat(dataHb);
        setIsPulsing(true);
        setTimeout(() => setIsPulsing(false), 600);
        setConnectionActive(true);
      } else {
        setConnectionActive(false);
      }
    } catch (err) {
      console.error("Diagnostic error:", err);
      setConnectionActive(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDiagnostics();
    fetchTelemetry();
    fetchLogs();
    
    // Initialize WebSocket for Live Logs
    const wsProtocol = API_BASE.startsWith('https') ? 'wss:' : 'ws:';
    const wsHost = API_BASE.replace(/^https?:\/\//, '');
    const wsUrl = `${wsProtocol}//${wsHost}/ws/logs`;
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
        setConnectionActive(true);
        console.log("WebSocket connected to:", wsUrl);
    };

    ws.onmessage = (event) => {
        const message = event.data;
        setLogs(prev => {
            const updated = [...prev, message];
            return updated.slice(-200); // Keep last 200 lines
        });
    };

    ws.onclose = () => {
        setConnectionActive(false);
        console.log("WebSocket disconnected");
    };

    ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        setConnectionActive(false);
    };

    const diagInterval = setInterval(fetchDiagnostics, 3000);
    const telInterval = setInterval(fetchTelemetry, 10000);

    return () => {
      clearInterval(diagInterval);
      clearInterval(telInterval);
      if (wsRef.current) wsRef.current.close();
    };
  }, [activeLog]);

  // Auto-scroll terminal
  useEffect(() => {
    if (terminalRef.current) {
        terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

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
            <div className="flex justify-between items-center text-sm">
                <span className="text-white/40">Status</span>
                <span className="flex items-center gap-2 text-emerald-400 font-bold">
                    <div className={`w-2 h-2 rounded-full bg-emerald-500 transition-all duration-300 ${isPulsing ? 'scale-150 shadow-[0_0_10px_#10b981]' : 'scale-100 shadow-none'}`} />
                    ONLINE
                </span>
            </div>
            <div className="flex justify-between items-center text-sm">
                <span className="text-white/40">Embedder (ONNX)</span>
                <span className={`font-bold ${telemetry.embedder === 'Online' ? 'text-cyan-400' : 'text-rose-400'}`}>
                    {telemetry.embedder}
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
                <span className="text-white/80 font-mono">{telemetry.ram_usage}</span>
            </div>

            <button 
                onClick={async () => {
                    try {
                    const token = isLocal ? "dev-admin-token" : await currentUser.getIdToken();
                    const res = await apiFetch('/admin/live-metrics/trigger', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                        if (res.ok) alert("Live Pulse Refresh Triggered");
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
            <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                <div className="text-[10px] text-white/30 uppercase tracking-widest mb-1">System Load (RAM)</div>
                <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                    <motion.div 
                        initial={{ width: 0 }} 
                        animate={{ width: telemetry.ram_usage !== 'N/A' ? telemetry.ram_usage : '0%' }} 
                        className="h-full bg-indigo-500" 
                    />
                </div>
            </div>
             <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                <div className="text-[10px] text-white/30 uppercase tracking-widest mb-1">Worker Latency</div>
                <div className="text-xl font-mono font-bold text-white">0.42s <span className="text-xs text-white/20">avg</span></div>
            </div>
             <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                <div className="text-[10px] text-white/30 uppercase tracking-widest mb-1">Open Threads</div>
                <div className="text-xl font-mono font-bold text-white">12 <span className="text-xs text-emerald-500">stable</span></div>
            </div>
             <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                <div className="text-[10px] text-white/30 uppercase tracking-widest mb-1">Last Error</div>
                <div className="text-[10px] font-mono text-rose-400/80 truncate">Gemini 503: High Demand (resolved)</div>
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
  }, [currentUser, isAdmin, navigate, isLocal]);

  if (!isLocal && (!currentUser || !isAdmin)) return null;

  const currentPath = location.pathname;

  const menuItems = [
    { id: 'pulse', label: 'System Pulse', icon: Activity, path: '/admin' },
    { id: 'review', label: 'Review Queue', icon: Layers, path: '/admin/requests' },
    { id: 'manual', label: 'Manual Entry', icon: PlusSquare, path: '/admin/vault' },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, path: '/admin/analytics' },
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
                        <Route path="/requests" element={<ReviewQueue />} />
                        <Route path="/analytics" element={<AdminAnalytics />} />
                        <Route path="/vault" element={<AdminVault />} />
                    </Routes>
                </AnimatePresence>
            </ErrorBoundary>
        </div>
      </main>
    </div>
  );
}
