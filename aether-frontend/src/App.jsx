import { Suspense, lazy, useState, useEffect } from "react";
import { Routes, Route, Link, Navigate, useLocation } from "react-router-dom";
import { AlertCircle, Server, Shield, ShieldCheck, Settings as SettingsIcon, LogOut, User, BarChart3, PlusSquare, Scale, Zap, Activity, GitBranch, Coins, X, Menu } from "lucide-react";
import SparklesBackground from "./components/SparklesBackground";
import { useAuth } from "./AuthContext";
import Lenis from 'lenis';
import 'lenis/dist/lenis.css';
import { useTranslation } from 'react-i18next';

// Lazy load all pages for Code Splitting
const Home = lazy(() => import("./pages/Home"));
const ToolDetails = lazy(() => import("./pages/ToolDetails"));
const NotFound = lazy(() => import("./pages/NotFound"));
const NoInsights = lazy(() => import("./pages/NoInsights"));
const Activation = lazy(() => import("./pages/Activation"));
const MyStack = lazy(() => import("./pages/MyStack"));
const Settings = lazy(() => import("./pages/Settings"));
const Support = lazy(() => import("./pages/Support"));
const UseCases = lazy(() => import("./pages/UseCases"));
const Discover = lazy(() => import("./pages/Discover"));
const Blog = lazy(() => import("./pages/Blog"));
const ApiDocs = lazy(() => import("./pages/ApiDocs"));
const Contact = lazy(() => import("./pages/Contact"));
const Terms = lazy(() => import("./pages/Terms"));
const Privacy = lazy(() => import("./pages/Privacy"));
const Vault = lazy(() => import("./pages/Vault"));
const BlogPost = lazy(() => import("./pages/BlogPost"));
const AdminDashboard = lazy(() => import("./pages/AdminDashboard"));
const AetherInsiders = lazy(() => import("./pages/AetherInsiders"));

const Compare = lazy(() => import("./pages/Compare"));
const VendorInsights = lazy(() => import("./pages/VendorInsights"));

function App() {
  const [appError, setAppError] = useState(null);
  const { currentUser, isAdmin, logout } = useAuth();
  const { t, i18n } = useTranslation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const location = useLocation();

  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 2,
      infinite: false,
    });

    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }

    requestAnimationFrame(raf);

    return () => {
      lenis.destroy();
    };
  }, []);
  useEffect(() => {
    // Ko-fi Widget Integration
    const script = document.createElement('script');
    script.src = 'https://storage.ko-fi.com/cdn/scripts/overlay-widget.js';
    script.async = true;
    script.onload = () => {
      if (window.kofiWidgetOverlay) {
        window.kofiWidgetOverlay.draw('aethercompass', {
          'type': 'floating-chat',
          'floating-chat.donateButton.text': 'Support us',
          'floating-chat.donateButton.background-color': '#1a1a1a',
          'floating-chat.donateButton.text-color': '#fff'
        });
      }
    };
    document.body.appendChild(script);
  }, []);

  const isDiscoverPage = location.pathname === '/discover';

  // Auto-dismiss error after 6 seconds
  useEffect(() => {
    if (appError) {
      const timer = setTimeout(() => {
        setAppError(null);
      }, 6000);
      return () => clearTimeout(timer);
    }
  }, [appError]);

  const [prevPath, setPrevPath] = useState(location.pathname);
  if (location.pathname !== prevPath) {
    setPrevPath(location.pathname);
    if (appError) {
      setAppError(null);
    }
  }

  const dir = i18n.dir();

  return (
    <div className="min-h-screen font-sans antialiased flex flex-col w-full relative text-slate-200" dir={dir}>
      <SparklesBackground />

      {/* 1. Enterprise Header - PERSISTENT OUTSIDE ROUTES */}
      <header className="sticky top-0 z-50 w-full bg-[#02050a]/70 backdrop-blur-xl border-b border-white/5 px-4 md:px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Link to="/" className="flex items-center gap-3 hover:opacity-90 transition-all group" dir="ltr">
            <div className="relative">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-indigo-600 flex items-center justify-center text-white font-black text-xl shadow-[0_0_20px_rgba(6,182,212,0.3)] group-hover:scale-110 transition-transform duration-500">
                A
              </div>
              <div className="absolute -inset-1 bg-cyan-400/20 blur-xl rounded-full -z-10 group-hover:bg-cyan-400/40 transition-all duration-500"></div>
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold tracking-[-0.03em] text-white">{t('branding.title')}</span>
              <span className="text-[0.6rem] font-bold text-white/30 tracking-[0.3em] uppercase leading-none mt-0.5">{t('branding.subtitle')}</span>
            </div>
          </Link>
        </div>

        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-white/50">
          <Link to="/discover#how-it-works" className="hover:text-cyan-300 transition-colors">{t('footer.about') || 'About Us'}</Link>
          <Link to="/use-cases" className="hover:text-cyan-300 transition-colors">{t('nav.use_cases')}</Link>
          <Link to="/vault" className="flex items-center gap-1.5 hover:text-cyan-300 transition-colors">
            <Server className="w-3.5 h-3.5" />
            {t('nav.vault')}
          </Link>
          <Link to="/insiders" className="flex items-center gap-1.5 hover:text-cyan-300 transition-colors">
            <User className="w-3.5 h-3.5" />
            {t('nav.community')}
          </Link>
          <Link to="/compare" className="flex items-center gap-1.5 hover:text-indigo-400 transition-colors text-indigo-300/80">
            <Scale className="w-3.5 h-3.5" />
            {t('nav.compare')}
          </Link>

          {isAdmin && (
            <Link to="/admin" className="flex items-center gap-1.5 text-cyan-400 hover:text-cyan-300 drop-shadow-[0_0_8px_rgba(6,182,212,0.3)] transition-all font-bold group">
              <Shield className="w-3.5 h-3.5 group-hover:rotate-12 transition-transform" />
              {t('nav.admin')}
            </Link>
          )}
        </nav>
        <div className="flex items-center gap-4">
          {currentUser ? (
            <div className="flex items-center gap-4" dir="ltr">
              <div className="flex flex-col items-start leading-tight hidden sm:flex">
                <span className="text-[10px] text-white/40 uppercase tracking-widest font-bold">{t('nav.hello')}</span>
                <span className="text-sm font-bold text-white tracking-tight">
                  {currentUser.displayName || currentUser.email.split('@')[0]}
                </span>
              </div>
              
              <div className="flex items-center gap-1.5 p-1 bg-white/5 backdrop-blur-md border border-white/10 rounded-xl">
                <Link 
                  to="/settings" 
                  className="p-2 hover:bg-white/10 rounded-lg transition-all text-white/60 hover:text-cyan-400 group"
                  title={t('nav.settings_title')}
                >
                  <SettingsIcon className="w-5 h-5 group-hover:rotate-45 transition-transform duration-300" />
                </Link>
                <button 
                  onClick={logout}
                  className="p-2 hover:bg-rose-500/10 rounded-lg transition-all text-white/60 hover:text-rose-400"
                  title={t('nav.logout')}
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            </div>
          ) : (
            <>
              <Link to="/activation" className="text-sm font-medium text-white/50 hover:text-slate-200 transition-colors hidden sm:block">
                {t('nav.login')}
              </Link>
              <Link to="/activation" className="px-4 py-2 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-sm font-medium rounded-lg hover:bg-cyan-500/20 hover:shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all">
                {t('nav.get_started')}
              </Link>
            </>
          )}

          {/* Mobile Menu Toggle Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2.5 rounded-xl bg-white/5 border border-white/10 text-white/70 hover:text-white hover:bg-white/10 transition-all active:scale-95 shrink-0"
            aria-label="Toggle navigation menu"
          >
            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </header>

      {/* Mobile Navigation Menu */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-[#02050a]/95 backdrop-blur-2xl md:hidden flex flex-col pt-24 px-6 animate-in fade-in duration-300">
          <nav className="flex flex-col gap-6 text-xl font-semibold text-white/80">
            <Link to="/discover#how-it-works" onClick={() => setIsMobileMenuOpen(false)} className="hover:text-cyan-300 transition-colors py-2 border-b border-white/5">{t('footer.about') || 'About Us'}</Link>
            <Link to="/use-cases" onClick={() => setIsMobileMenuOpen(false)} className="hover:text-cyan-300 transition-colors py-2 border-b border-white/5">{t('nav.use_cases')}</Link>
            <Link to="/vault" className="flex items-center gap-3 hover:text-cyan-300 transition-colors py-2 border-b border-white/5">
              <Server className="w-5 h-5" />
              {t('nav.vault')}
            </Link>
            <Link to="/insiders" className="flex items-center gap-3 hover:text-cyan-300 transition-colors py-2 border-b border-white/5">
              <User className="w-5 h-5" />
              {t('nav.community')}
            </Link>
            <Link to="/compare" className="flex items-center gap-3 hover:text-indigo-400 transition-colors text-indigo-300/80 py-2 border-b border-white/5">
              <Scale className="w-5 h-5" />
              {t('nav.compare')}
            </Link>

            {isAdmin && (
              <Link to="/admin" className="flex items-center gap-3 text-cyan-400 hover:text-cyan-300 transition-all font-bold py-2 border-b border-white/5">
                <Shield className="w-5 h-5" />
                {t('nav.admin')}
              </Link>
            )}

            {!currentUser && (
              <Link to="/activation" className="text-center mt-4 px-6 py-4 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 rounded-xl hover:bg-cyan-500/20 transition-all">
                {t('nav.login')} / {t('nav.get_started')}
              </Link>
            )}
          </nav>
        </div>
      )}

      {/* Main Container - The dynamic part */}
      <main className={`w-full flex flex-col items-center flex-1 ${isDiscoverPage ? '' : 'max-w-4xl mx-auto px-4 pt-8 pb-24'}`}>
        <Suspense fallback={<div className="min-h-[50vh] w-full bg-[#040914]" />}>
          <Routes>
            <Route path="/" element={<Home setAppError={setAppError} />} />
            <Route path="/tool/:id" element={<ToolDetails setAppError={setAppError} />} />
            <Route path="/vault" element={<Vault setAppError={setAppError} />} />
            <Route path="/no-insights" element={<NoInsights setAppError={setAppError} />} />
            <Route path="/activation" element={<Activation setAppError={setAppError} />} />
            <Route path="/my-stack" element={<MyStack setAppError={setAppError} />} />
            <Route path="/settings" element={<Settings setAppError={setAppError} />} />
            <Route path="/support" element={<Support setAppError={setAppError} />} />
            <Route path="/use-cases" element={<UseCases setAppError={setAppError} />} />
            <Route path="/discover" element={<Discover setAppError={setAppError} />} />
            <Route path="/blog" element={<Blog setAppError={setAppError} />} />
            <Route path="/blog/:slug" element={<BlogPost setAppError={setAppError} />} />
            <Route path="/api-docs" element={<ApiDocs setAppError={setAppError} />} />
            <Route path="/contact" element={<Contact setAppError={setAppError} />} />
            <Route path="/terms" element={<Terms setAppError={setAppError} />} />
            <Route path="/privacy" element={<Privacy setAppError={setAppError} />} />
            {isAdmin && <Route path="/admin/*" element={<AdminDashboard />} />}
            <Route path="/insiders" element={<AetherInsiders setAppError={setAppError} />} />

            <Route path="/compare" element={<Compare setAppError={setAppError} />} />
            <Route path="/vendor/insights" element={<VendorInsights />} />

            {/* Catch All 404 Redirect to Home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </main>

      {/* 7. Minimalist Footer - PERSISTENT OUTSIDE ROUTES */}
      <footer className="w-full border-t border-white/5 bg-[#02050a]/90 backdrop-blur-md pt-16 pb-8 px-6 md:px-12 mt-auto" dir="ltr">

        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
          <div>
            <h4 className="font-semibold text-white mb-4 text-sm">{t('footer.product')}</h4>
            <ul className="space-y-2 text-sm text-white/60">
              <li><Link to="/use-cases" className="hover:text-cyan-400 transition-colors">{t('footer.tool_index')}</Link></li>
              <li><Link to="/vault" className="hover:text-cyan-400 transition-colors">{t('footer.vault_live')}</Link></li>
              <li><Link to="/insiders" className="hover:text-cyan-400 transition-colors font-bold text-cyan-400/80">{t('footer.insiders')}</Link></li>
              <li><Link to="/support" className="hover:text-cyan-400 transition-colors">{t('footer.support')}</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-white mb-4 text-sm">{t('footer.company')}</h4>
            <ul className="space-y-2 text-sm text-white/60">
              <li><Link to="/discover" className="hover:text-cyan-400 transition-colors">{t('footer.about')}</Link></li>
              <li><Link to="/blog" className="hover:text-cyan-400 transition-colors">{t('footer.blog')}</Link></li>
              <li><Link to="/contact" className="hover:text-cyan-400 transition-colors">{t('footer.contact')}</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-white mb-4 text-sm">{t('footer.legal')}</h4>
            <ul className="space-y-2 text-sm text-white/60">
              <li><Link to="/terms" className="hover:text-cyan-400 transition-colors">{t('footer.terms')}</Link></li>
              <li><Link to="/privacy" className="hover:text-cyan-400 transition-colors">{t('footer.privacy')}</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-white mb-4 text-sm">{t('footer.social')}</h4>
            <ul className="space-y-2 text-sm text-white/60">
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Twitter (X)</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">LinkedIn</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">GitHub</a></li>
            </ul>
          </div>
        </div>
        <div className="max-w-4xl mx-auto flex flex-col md:flex-row items-center justify-between pt-8 border-t border-white/5 text-xs text-white/70">
          <span>{t('footer.rights')}</span>
          <div className="flex items-center gap-3 mt-4 md:mt-0 opacity-80 hover:opacity-100 transition-all duration-300" dir="ltr">
            <div className="flex flex-col items-center justify-center gap-2">
              <span className="text-lg font-bold tracking-tight text-white/80">{t('branding.title')} <span className="text-cyan-500">{t('branding.subtitle')}</span></span>
              <span className="text-[0.55rem] tracking-widest text-white/30 uppercase leading-none">{t('branding.tagline')}</span>
            </div>
          </div>
        </div>
      </footer>

      {/* Subtle Error Toast Fixed at corner (Clinical Light Mode Fallback) */}
      {appError && (
        <div className="fixed top-4 right-4 z-[9999] max-w-sm px-4 py-3 rounded-xl bg-red-500/90 backdrop-blur-md border border-red-500/50 text-white text-sm flex items-center justify-between gap-4 font-medium shadow-2xl transition-all animate-in slide-in-from-top-5">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-white shrink-0" />
            <span>{appError}</span>
          </div>
          <button 
            onClick={() => setAppError(null)} 
            className="p-1 hover:bg-white/10 rounded-lg transition-colors cursor-pointer text-white/80 hover:text-white shrink-0"
            aria-label="Dismiss notification"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
