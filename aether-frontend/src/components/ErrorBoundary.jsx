import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 rounded-3xl bg-rose-500/5 border border-rose-500/20 backdrop-blur-xl flex flex-col items-center justify-center text-center min-h-[300px]">
          <div className="p-4 bg-rose-500/10 rounded-full mb-6">
            <AlertCircle className="w-12 h-12 text-rose-400" />
          </div>
          <h2 className="text-2xl font-black text-rose-400 mb-2 uppercase tracking-tight">Component Decoupled</h2>
          <p className="text-white/50 text-sm max-w-md mb-8 leading-relaxed">
            The sub-module encountered a critical failure. The system has isolated the error to prevent mission-wide instability.
          </p>
          <button 
            onClick={() => window.location.reload()}
            className="flex items-center gap-2 px-6 py-3 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-2xl text-xs font-black uppercase tracking-[0.2em] transition-all"
          >
            <RefreshCw className="w-4 h-4" />
            Re-init Protocol
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
