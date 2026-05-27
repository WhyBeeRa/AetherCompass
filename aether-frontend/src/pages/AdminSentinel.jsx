import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  ShieldAlert,
  Activity, 
  Mail, 
  Clock, 
  RefreshCw, 
  CheckCircle2, 
  XCircle,
  Database,
  Cpu,
  AlertTriangle,
  Save,
  Play
} from 'lucide-react';
import { useAuth } from '../AuthContext';
import { apiFetch } from '../api';
import { motion } from 'framer-motion';

const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

export default function AdminSentinel() {
  const { currentUser } = useAuth();
  
  // Settings state
  const [settings, setSettings] = useState({
    enabled: false,
    alert_email: '',
    frequency_minutes: 30,
    failure_threshold: 3
  });
  
  // Real-time status / stats
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [saveStatus, setSaveStatus] = useState(null); // 'success', 'error', or null

  const fetchSentinelData = async () => {
    try {
      const token = isLocal ? "dev-admin-token" : await currentUser.getIdToken();
      const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
      
      // Fetch settings
      const settingsRes = await apiFetch('/admin/sentinel/settings', { headers });
      if (settingsRes.ok) {
        const settingsData = await settingsRes.json();
        setSettings({
          enabled: settingsData.enabled,
          alert_email: settingsData.alert_email || '',
          frequency_minutes: settingsData.frequency_minutes || 30,
          failure_threshold: settingsData.failure_threshold || 3
        });
      }
      
      // Fetch logs
      const logsRes = await apiFetch('/admin/sentinel/logs?limit=30', { headers });
      if (logsRes.ok) {
        const logsData = await logsRes.json();
        setLogs(logsData || []);
      }
    } catch (err) {
      console.error("Failed to load Sentinel telemetry:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSentinelData();
  }, []);

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaveStatus(null);
    
    try {
      const token = isLocal ? "dev-admin-token" : await currentUser.getIdToken();
      const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
      
      const res = await apiFetch('/admin/sentinel/settings', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          enabled: settings.enabled,
          alert_email: settings.alert_email,
          frequency_minutes: Number(settings.frequency_minutes),
          failure_threshold: Number(settings.failure_threshold)
        })
      });
      
      if (res.ok) {
        setSaveStatus('success');
        setTimeout(() => setSaveStatus(null), 3000);
        fetchSentinelData();
      } else {
        setSaveStatus('error');
      }
    } catch (err) {
      console.error("Save error:", err);
      setSaveStatus('error');
    } finally {
      setSaving(false);
    }
  };

  const handleTriggerTestAudit = async () => {
    setTesting(true);
    setTestResult(null);
    
    try {
      const token = isLocal ? "dev-admin-token" : await currentUser.getIdToken();
      const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
      
      const res = await apiFetch('/admin/sentinel/test-audit', {
        method: 'POST',
        headers
      });
      
      if (res.ok) {
        const data = await res.json();
        setTestResult(data);
        fetchSentinelData();
      } else {
        setTestResult({
          status: 'RED',
          message: 'Real-time heartbeat call returned critical communication failure.'
        });
      }
    } catch (err) {
      console.error("Test execution failed:", err);
      setTestResult({
        status: 'RED',
        message: `Network transaction failed: ${err.message}`
      });
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px] text-white/20 animate-pulse font-mono uppercase tracking-widest text-xs">
        Synchronizing Sentinel Core Telemetry...
      </div>
    );
  }

  // Derive status details
  const lastLog = logs[0];
  const lastStatus = lastLog ? lastLog.status : 'STANDBY';
  const isHealthy = lastStatus === 'GREEN' || lastStatus === 'STANDBY' || !settings.enabled;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Overview Dashboard Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Core Sentinel status display */}
        <div className="bg-white/[0.02] border border-white/10 rounded-3xl p-6 backdrop-blur-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-3xl -z-10 group-hover:bg-cyan-500/15 transition-all"></div>
          
          <div className="flex items-center gap-3 mb-6">
            <div className={`p-2 rounded-xl ${settings.enabled ? 'bg-cyan-500/10' : 'bg-white/5'}`}>
              <Shield className={`w-5 h-5 ${settings.enabled ? 'text-cyan-400' : 'text-white/30'}`} />
            </div>
            <h3 className="font-bold text-white text-sm uppercase tracking-widest">Sentinel Core</h3>
          </div>
          
          <div className="flex flex-col items-center justify-center py-6">
            <div className="relative">
              {/* Pulsing visual core */}
              <div className={`w-20 h-20 rounded-full flex items-center justify-center border ${
                !settings.enabled 
                  ? 'border-white/5 bg-white/[0.02]' 
                  : isHealthy 
                    ? 'border-emerald-500/30 bg-emerald-500/5' 
                    : 'border-rose-500/30 bg-rose-500/5 animate-pulse'
              }`}>
                <Activity className={`w-10 h-10 ${
                  !settings.enabled 
                    ? 'text-white/20' 
                    : isHealthy 
                      ? 'text-emerald-400' 
                      : 'text-rose-400'
                }`} />
              </div>
              {settings.enabled && (
                <div className={`absolute inset-0 rounded-full -z-10 animate-ping opacity-20 ${
                  isHealthy ? 'bg-emerald-500' : 'bg-rose-500'
                }`} />
              )}
            </div>
            
            <div className="text-center mt-6">
              <div className="text-xl font-bold tracking-tight text-white uppercase italic">
                {settings.enabled ? (isHealthy ? 'Active Monitor' : 'SYSTEM CRITICAL') : 'MUTED STANDBY'}
              </div>
              <div className="text-[10px] font-medium text-white/30 tracking-[0.2em] uppercase mt-1">
                {settings.enabled ? 'Sentinel autonomous worker active' : 'Automated checks suspended'}
              </div>
            </div>
          </div>
          
          {/* Diagnostic Stats summary */}
          <div className="border-t border-white/5 pt-4 mt-4 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-white/40">Last State Verified</span>
              <span className={`font-mono font-bold ${
                lastStatus === 'GREEN' ? 'text-emerald-400' : lastStatus === 'RED' ? 'text-rose-400' : 'text-white/40'
              }`}>
                {lastStatus}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/40">Email Alerts Route</span>
              <span className="font-mono font-bold text-white/70 truncate max-w-[160px]" title={settings.alert_email}>
                {settings.alert_email || 'UNCONFIGURED'}
              </span>
            </div>
          </div>
        </div>

        {/* Configuration settings form */}
        <div className="bg-white/[0.02] border border-white/10 rounded-3xl p-6 backdrop-blur-xl lg:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-500/10 rounded-xl">
                <Clock className="w-5 h-5 text-indigo-400" />
              </div>
              <h3 className="font-bold text-white text-sm uppercase tracking-widest">Sentinel Settings</h3>
            </div>
            
            {/* Quick Actions */}
            <button
              onClick={handleTriggerTestAudit}
              disabled={testing}
              className="py-1.5 px-3 bg-white/5 hover:bg-white/10 text-white border border-white/10 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-2 disabled:opacity-50"
            >
              {testing ? <RefreshCw className="w-3 h-3 animate-spin text-cyan-400" /> : <Play className="w-3 h-3 text-cyan-400" />}
              {testing ? 'Testing...' : 'Test Audit'}
            </button>
          </div>

          <form onSubmit={handleSaveSettings} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Automated Audit Toggle */}
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5">
                <div>
                  <label className="text-xs font-bold text-white uppercase tracking-wider block">Automated Auditing</label>
                  <span className="text-[10px] text-white/30 block mt-0.5">Toggle live system checks</span>
                </div>
                <button
                  type="button"
                  onClick={() => setSettings(prev => ({ ...prev, enabled: !prev.enabled }))}
                  className={`w-12 h-6 rounded-full p-1 transition-all duration-300 ${
                    settings.enabled ? 'bg-cyan-500' : 'bg-white/10'
                  }`}
                >
                  <div className={`w-4 h-4 rounded-full bg-white transition-all duration-300 transform ${
                    settings.enabled ? 'translate-x-6' : 'translate-x-0'
                  }`} />
                </button>
              </div>

              {/* Alert Destination Email */}
              <div className="p-4 bg-white/5 rounded-2xl border border-white/5 flex flex-col justify-center">
                <label className="text-xs font-bold text-white uppercase tracking-wider mb-2 block">Alert Email Destination</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-2.5 w-4 h-4 text-white/20" />
                  <input
                    type="email"
                    required
                    value={settings.alert_email}
                    onChange={(e) => setSettings(prev => ({ ...prev, alert_email: e.target.value }))}
                    placeholder="admin@aethercompass.com"
                    className="w-full bg-black/40 border border-white/10 rounded-xl py-2 pl-10 pr-4 text-xs text-white placeholder-white/20 focus:outline-none focus:border-cyan-500 transition-colors"
                  />
                </div>
              </div>

              {/* Health Check Frequency */}
              <div className="p-4 bg-white/5 rounded-2xl border border-white/5 flex flex-col justify-center">
                <div className="flex justify-between mb-2">
                  <label className="text-xs font-bold text-white uppercase tracking-wider">Health-Check Frequency</label>
                  <span className="text-xs font-mono font-bold text-cyan-400">{settings.frequency_minutes}m</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="120"
                  step="5"
                  value={settings.frequency_minutes}
                  onChange={(e) => setSettings(prev => ({ ...prev, frequency_minutes: Number(e.target.value) }))}
                  className="w-full accent-cyan-400 bg-white/10 rounded-lg appearance-none cursor-pointer h-1.5"
                />
                <div className="flex justify-between text-[8px] text-white/20 uppercase tracking-widest mt-2">
                  <span>5 Minutes</span>
                  <span>2 Hours</span>
                </div>
              </div>

              {/* Failures Threshold */}
              <div className="p-4 bg-white/5 rounded-2xl border border-white/5 flex flex-col justify-center">
                <div className="flex justify-between mb-2">
                  <label className="text-xs font-bold text-white uppercase tracking-wider">Failure Threshold</label>
                  <span className="text-xs font-mono font-bold text-indigo-400">{settings.failure_threshold} cycles</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="1"
                  value={settings.failure_threshold}
                  onChange={(e) => setSettings(prev => ({ ...prev, failure_threshold: Number(e.target.value) }))}
                  className="w-full accent-indigo-400 bg-white/10 rounded-lg appearance-none cursor-pointer h-1.5"
                />
                <div className="flex justify-between text-[8px] text-white/20 uppercase tracking-widest mt-2">
                  <span>1 Cycle</span>
                  <span>10 Cycles</span>
                </div>
              </div>
            </div>

            {/* Form Actions */}
            <div className="flex items-center justify-between border-t border-white/5 pt-4 mt-4">
              <div>
                {saveStatus === 'success' && (
                  <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Core configuration saved
                  </span>
                )}
                {saveStatus === 'error' && (
                  <span className="text-[10px] font-bold text-rose-400 uppercase tracking-widest flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5" /> Failed to save settings
                  </span>
                )}
              </div>

              <button
                type="submit"
                disabled={saving}
                className="py-2.5 px-6 bg-cyan-500 hover:bg-cyan-600 text-black rounded-xl text-xs font-black uppercase tracking-widest transition-all flex items-center gap-2 disabled:opacity-50"
              >
                <Save className="w-4 h-4" />
                {saving ? 'Saving...' : 'Commit Configuration'}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Manual Audit test output response display */}
      {testResult && (
        <div className={`p-6 rounded-3xl border animate-in slide-in-from-top-4 duration-300 ${
          testResult.status === 'GREEN' 
            ? 'bg-emerald-950/10 border-emerald-500/20 text-emerald-400' 
            : 'bg-rose-950/10 border-rose-500/20 text-rose-400'
        }`}>
          <div className="flex items-center gap-3 mb-3">
            {testResult.status === 'GREEN' ? <CheckCircle2 className="w-5 h-5" /> : <ShieldAlert className="w-5 h-5" />}
            <h4 className="font-bold uppercase tracking-widest text-xs">Real-Time Health Status: {testResult.status}</h4>
          </div>
          <p className="text-xs text-white/70 mb-4">{testResult.message}</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono border-t border-white/5 pt-4 mt-2">
            <div>
              <span className="block text-white/30 text-[9px] uppercase tracking-wider mb-1">Database Layer</span>
              <span className={`font-bold ${testResult.database_status === 'CONNECTED' ? 'text-white' : 'text-rose-400'}`}>{testResult.database_status}</span>
            </div>
            <div>
              <span className="block text-white/30 text-[9px] uppercase tracking-wider mb-1">Process memory</span>
              <span className="font-bold text-white">{testResult.memory_usage_mb} MB</span>
            </div>
            <div>
              <span className="block text-white/30 text-[9px] uppercase tracking-wider mb-1">Alert Dispatched</span>
              <span className="font-bold text-white">{testResult.email_sent ? 'SMTP Dispatched' : 'None Required'}</span>
            </div>
            <div>
              <span className="block text-white/30 text-[9px] uppercase tracking-wider mb-1">Failure Counter</span>
              <span className="font-bold text-white">{testResult.current_failures} cycles</span>
            </div>
          </div>
        </div>
      )}

      {/* Audit Log Console */}
      <div className="bg-[#040914] border border-white/10 rounded-3xl overflow-hidden shadow-2xl">
        <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Database className="w-5 h-5 text-cyan-400" />
            <h3 className="font-bold text-white text-sm uppercase tracking-widest font-mono">Sentinel Audit Logs</h3>
          </div>
          <button 
            onClick={fetchSentinelData}
            className="p-1 text-white/40 hover:text-white transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-white/5 text-white/30 uppercase font-black text-[9px] tracking-widest bg-black/20">
                <th className="py-4 px-6">Timestamp</th>
                <th className="py-4 px-6">Audit Status</th>
                <th className="py-4 px-6">Diagnostic Messages</th>
                <th className="py-4 px-6">Database Connectivity</th>
                <th className="py-4 px-6">System RAM</th>
                <th className="py-4 px-6">Email State</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 font-mono">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan="6" className="py-8 px-6 text-center text-white/20">No historical health checks mapped in SQLite memory yet.</td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-white/[0.01] transition-colors">
                    <td className="py-4 px-6 text-white/60">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="py-4 px-6">
                      <span className={`px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-widest ${
                        log.status === 'GREEN' 
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                          : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      }`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-white/40 max-w-xs truncate" title={log.message}>
                      {log.message}
                    </td>
                    <td className="py-4 px-6">
                      <span className={`font-bold ${log.database_status === 'CONNECTED' ? 'text-white/70' : 'text-rose-400'}`}>
                        {log.database_status}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-white/60">
                      {log.memory_usage_mb > 0 ? `${log.memory_usage_mb} MB` : 'N/A'}
                    </td>
                    <td className="py-4 px-6">
                      <span className={`text-[10px] font-bold ${log.email_sent ? 'text-cyan-400' : 'text-white/20'}`}>
                        {log.email_sent ? 'Dispatched' : 'Muted'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
