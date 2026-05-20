import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../AuthContext';
import { apiFetch } from '../api';
import { 
  RefreshCw, 
  FileText, 
  FolderTree, 
  ChevronRight, 
  ChevronDown, 
  Clock, 
  CheckCircle2, 
  AlertCircle,
  Cpu,
  File,
  Save,
  Box
} from 'lucide-react';

const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

// ---- File Tree Node ---------------------------------------------------------

const TreeNode = ({ node, depth = 0, onFileSelect, selectedPath }) => {
  const [expanded, setExpanded] = useState(depth < 1);
  const isDir = node.type === 'directory';
  const isSelected = !isDir && node.path === selectedPath;

  return (
    <div>
      <button
        onClick={() => isDir ? setExpanded(!expanded) : onFileSelect(node.path)}
        className={`w-full flex items-center gap-2 px-3 py-1.5 text-left text-sm transition-all rounded-lg group
          ${isSelected 
            ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/20' 
            : 'text-white/60 hover:text-white hover:bg-white/5 border border-transparent'}`}
        style={{ paddingLeft: `${depth * 16 + 12}px` }}
      >
        {isDir ? (
          expanded ? <ChevronDown className="w-3.5 h-3.5 text-white/30 flex-shrink-0" /> : <ChevronRight className="w-3.5 h-3.5 text-white/30 flex-shrink-0" />
        ) : (
          <File className="w-3.5 h-3.5 text-white/20 flex-shrink-0" />
        )}
        <span className={`truncate ${isDir ? 'font-semibold text-white/80' : ''}`}>
          {node.name}
        </span>
        {!isDir && node.size !== undefined && (
          <span className="ml-auto text-[10px] text-white/20 font-mono">{node.size}b</span>
        )}
      </button>
      {isDir && expanded && node.children?.map((child, i) => (
        <TreeNode key={child.path || i} node={child} depth={depth + 1} onFileSelect={onFileSelect} selectedPath={selectedPath} />
      ))}
    </div>
  );
};

// ---- Main Component ---------------------------------------------------------

export default function AIFactoryPanel() {
  const { currentUser } = useAuth();

  const [tree, setTree] = useState([]);
  const [selectedPath, setSelectedPath] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [fileName, setFileName] = useState('');
  const [fileLastModified, setFileLastModified] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState('');

  const [systemLog, setSystemLog] = useState('');
  const [engineStatus, setEngineStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const getToken = useCallback(async () => {
    return isLocal ? "dev-admin-token" : await currentUser?.getIdToken();
  }, [currentUser]);

  const headers = useCallback(async () => {
    const token = await getToken();
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }, [getToken]);

  // Fetch tree + status + system log on mount
  useEffect(() => {
    const init = async () => {
      setLoading(true);
      try {
        const h = await headers();

        const [treeRes, statusRes, logRes] = await Promise.all([
          apiFetch('/admin/factory/tree', { headers: h }),
          apiFetch('/admin/factory/status', { headers: h }),
          apiFetch('/admin/factory/memory/system-log', { headers: h }),
        ]);

        if (treeRes.ok) {
          const data = await treeRes.json();
          setTree(data.tree || []);
        }

        if (statusRes.ok) {
          setEngineStatus(await statusRes.json());
        }

        if (logRes.ok) {
          const logData = await logRes.json();
          setSystemLog(logData.content || '');
        }
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    init();
  }, [headers]);

  // Load a file when selected
  const handleFileSelect = async (path) => {
    setSelectedPath(path);
    setIsEditing(false);
    try {
      const h = await headers();
      const res = await apiFetch(`/admin/factory/file?path=${encodeURIComponent(path)}`, { headers: h });
      if (res.ok) {
        const data = await res.json();
        setFileContent(data.content);
        setFileName(data.name);
        setFileLastModified(data.last_modified);
        setEditContent(data.content);
      }
    } catch (e) {
      setError(e.message);
    }
  };

  // Save file
  const handleSave = async () => {
    if (!selectedPath) return;
    setSaving(true);
    try {
      const h = await headers();
      const res = await apiFetch(`/admin/factory/file?path=${encodeURIComponent(selectedPath)}`, {
        method: 'PUT',
        headers: h,
        body: JSON.stringify({ content: editContent }),
      });
      if (res.ok) {
        setFileContent(editContent);
        setIsEditing(false);
        const result = await res.json();
        setFileLastModified(result.last_modified);
      } else {
        const err = await res.json();
        setError(err.detail || 'Save failed');
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  // Refresh system log
  const refreshLog = async () => {
    try {
      const h = await headers();
      const [logRes, statusRes] = await Promise.all([
        apiFetch('/admin/factory/memory/system-log', { headers: h }),
        apiFetch('/admin/factory/status', { headers: h }),
      ]);
      if (logRes.ok) {
        const data = await logRes.json();
        setSystemLog(data.content || '');
      }
      if (statusRes.ok) {
        setEngineStatus(await statusRes.json());
      }
    } catch (e) {
      setError(e.message);
    }
  };

  const statusColor = engineStatus?.engine_status === 'RUNNING' 
    ? 'text-emerald-400' 
    : engineStatus?.engine_status === 'STOPPED' 
      ? 'text-amber-400' 
      : 'text-white/40';

  const statusBg = engineStatus?.engine_status === 'RUNNING'
    ? 'bg-emerald-500/10 border-emerald-500/20'
    : engineStatus?.engine_status === 'STOPPED'
      ? 'bg-amber-500/10 border-amber-500/20'
      : 'bg-white/5 border-white/10';

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* Error Banner */}
      {error && (
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
          <button onClick={() => setError(null)} className="ml-auto text-rose-300 hover:text-white text-xs">Dismiss</button>
        </div>
      )}

      {/* Engine Status Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className={`rounded-2xl p-5 border backdrop-blur-sm ${statusBg}`}>
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-white/5 rounded-xl">
              <Cpu className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h3 className="text-xs font-black uppercase tracking-widest text-white/50">Factory Engine</h3>
              <span className={`text-sm font-bold ${statusColor}`}>
                {engineStatus?.engine_status || 'Loading...'}
              </span>
            </div>
          </div>
          <div className="text-[10px] text-white/30 font-mono">
            {engineStatus?.directory_count || 0} directories active
          </div>
        </div>

        <div className="rounded-2xl p-5 border border-white/10 bg-white/[0.02] backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-white/5 rounded-xl">
              <Clock className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-xs font-black uppercase tracking-widest text-white/50">Last Cycle</h3>
              <span className="text-sm font-bold text-white/80 truncate block max-w-[200px]">
                {engineStatus?.last_cycle || 'No cycles yet'}
              </span>
            </div>
          </div>
        </div>

        <div className="rounded-2xl p-5 border border-white/10 bg-white/[0.02] backdrop-blur-sm flex items-center justify-center">
          <button
            onClick={refreshLog}
            className="flex items-center gap-2 px-5 py-2.5 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-cyan-500/20 transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh Status
          </button>
        </div>
      </div>

      {/* Split Pane: File Tree + Editor */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[500px]">
        
        {/* Left: File Tree */}
        <div className="lg:col-span-4 bg-[#040914] border border-white/10 rounded-2xl overflow-hidden">
          <div className="px-5 py-4 border-b border-white/5 flex items-center gap-3">
            <FolderTree className="w-4 h-4 text-cyan-400" />
            <h3 className="text-xs font-black uppercase tracking-widest text-white/60">Factory Files</h3>
          </div>
          <div className="p-3 max-h-[500px] overflow-y-auto scrollbar-hide">
            {loading ? (
              <div className="text-white/20 text-sm animate-pulse p-4">Loading tree...</div>
            ) : tree.length === 0 ? (
              <div className="text-white/20 text-sm p-4">No files found</div>
            ) : (
              tree.map((node, i) => (
                <TreeNode key={node.path || i} node={node} onFileSelect={handleFileSelect} selectedPath={selectedPath} />
              ))
            )}
          </div>
        </div>

        {/* Right: File Viewer / Editor */}
        <div className="lg:col-span-8 bg-[#040914] border border-white/10 rounded-2xl overflow-hidden flex flex-col">
          <div className="px-5 py-4 border-b border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="w-4 h-4 text-indigo-400" />
              <h3 className="text-xs font-black uppercase tracking-widest text-white/60">
                {fileName || 'Select a file'}
              </h3>
              {fileLastModified && (
                <span className="text-[10px] text-white/20 font-mono ml-2">
                  Modified: {new Date(fileLastModified).toLocaleString()}
                </span>
              )}
            </div>
            {selectedPath && fileName.endsWith('.md') && (
              <div className="flex items-center gap-2">
                {isEditing ? (
                  <>
                    <button
                      onClick={() => { setIsEditing(false); setEditContent(fileContent); }}
                      className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-white/40 hover:text-white border border-white/10 rounded-lg transition-all"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSave}
                      disabled={saving}
                      className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 rounded-lg hover:bg-cyan-500/20 transition-all flex items-center gap-1.5"
                    >
                      <Save className="w-3 h-3" />
                      {saving ? 'Saving...' : 'Save'}
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-white/40 hover:text-cyan-400 border border-white/10 hover:border-cyan-500/20 rounded-lg transition-all"
                  >
                    Edit
                  </button>
                )}
              </div>
            )}
          </div>

          <div className="flex-1 p-6 overflow-y-auto scrollbar-hide">
            {!selectedPath ? (
              <div className="flex flex-col items-center justify-center h-full text-white/20 gap-3">
                <FolderTree className="w-10 h-10 opacity-30" />
                <span className="text-sm">Select a file from the tree to view or edit</span>
              </div>
            ) : isEditing ? (
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                className="w-full h-full min-h-[400px] bg-black/40 border border-white/10 rounded-xl p-4 text-white/80 font-mono text-sm leading-relaxed focus:outline-none focus:border-cyan-500/30 resize-none scrollbar-hide"
                spellCheck={false}
              />
            ) : (
              <pre className="text-white/70 font-mono text-sm leading-relaxed whitespace-pre-wrap break-words">
                {fileContent}
              </pre>
            )}
          </div>
        </div>
      </div>

      {/* System Log Section */}
      <div className="bg-[#040914] border border-white/10 rounded-2xl overflow-hidden">
        <div className="px-5 py-4 border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Box className="w-4 h-4 text-emerald-400" />
            <h3 className="text-xs font-black uppercase tracking-widest text-white/60">Factory System Log</h3>
            <div className={`px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-widest border ${statusBg} ${statusColor}`}>
              {engineStatus?.engine_status || '...'}
            </div>
          </div>
          <button
            onClick={refreshLog}
            className="text-white/30 hover:text-cyan-400 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
        <div className="p-6 bg-black min-h-[200px] max-h-[400px] overflow-y-auto font-mono text-[11px] leading-relaxed scrollbar-hide">
          {systemLog ? (
            systemLog.split('\n').filter(l => l.trim()).map((line, i) => (
              <div key={i} className="py-0.5">
                <span className="text-white/15 mr-3">[{i + 1}]</span>
                <span className={
                  line.includes('FAILED') || line.includes('ERROR')
                    ? 'text-rose-400'
                    : line.includes('started') || line.includes('Started')
                      ? 'text-emerald-400'
                      : line.includes('Scanning')
                        ? 'text-cyan-300'
                        : 'text-white/50'
                }>
                  {line}
                </span>
              </div>
            ))
          ) : (
            <div className="text-white/20">No system log entries yet. Engine will write here on each cycle.</div>
          )}
        </div>
      </div>
    </div>
  );
}
