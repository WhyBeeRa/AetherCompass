import { Suspense, lazy, useState } from "react";
import { Routes, Route, Link } from "react-router-dom";
import { AlertCircle, Server, Shield, Settings as SettingsIcon, LogOut, User, BarChart3, PlusSquare, Scale, Zap, Activity, GitBranch, Coins } from "lucide-react";
import SpaceBackground from "./components/SpaceBackground";
import { useAuth } from "./AuthContext";

// Lazy load all pages for Code Splitting
const Home = lazy(() => import("./pages/Home"));
const Pricing = lazy(() => import("./pages/Pricing"));
const ToolDetails = lazy(() => import("./pages/ToolDetails"));
const NotFound = lazy(() => import("./pages/NotFound"));
const NoInsights = lazy(() => import("./pages/NoInsights"));
const Activation = lazy(() => import("./pages/Activation"));
const MyStack = lazy(() => import("./pages/MyStack"));
const Settings = lazy(() => import("./pages/Settings"));
const Upgrade = lazy(() => import("./pages/Upgrade"));
const UseCases = lazy(() => import("./pages/UseCases"));
const About = lazy(() => import("./pages/About"));
const Blog = lazy(() => import("./pages/Blog"));
const ApiDocs = lazy(() => import("./pages/ApiDocs"));
const Contact = lazy(() => import("./pages/Contact"));
const Terms = lazy(() => import("./pages/Terms"));
const Privacy = lazy(() => import("./pages/Privacy"));
const Vault = lazy(() => import("./pages/Vault"));
const BlogPost = lazy(() => import("./pages/BlogPost"));
const AdminAnalytics = lazy(() => import("./pages/AdminAnalytics"));
const AdminVault = lazy(() => import("./pages/AdminVault"));
const AetherInsiders = lazy(() => import("./pages/AetherInsiders"));
const EloBattle = lazy(() => import("./pages/EloBattle"));
const Compare = lazy(() => import("./pages/Compare"));
const VendorInsights = lazy(() => import("./pages/VendorInsights"));

function App() {
  const [appError, setAppError] = useState(null);
  const { currentUser, isAdmin, logout } = useAuth();
  
  console.log("Debug Auth:", { 
      email: currentUser?.email, 
      envEmails: import.meta.env.VITE_ADMIN_EMAILS, 
      isAdmin 
  });

  return (
    <div className="min-h-screen font-sans antialiased flex flex-col w-full relative text-slate-200" dir="rtl">
      <SpaceBackground />

      {/* 1. Enterprise Header - PERSISTENT OUTSIDE ROUTES */}
      <header className="sticky top-0 z-50 w-full bg-[#040914]/80 backdrop-blur-md border-b border-white/5 px-4 md:px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Link to="/" className="flex flex-col items-center gap-1.5 hover:opacity-80 transition-opacity" dir="ltr">
            <img src="/logo.png.png" alt="Aether Logo" className="h-20 w-auto object-contain drop-shadow-md" />
            <span className="text-[0.65rem] font-medium text-white/50 tracking-widest uppercase leading-none mt-1">The Ultimate AI Compass</span>
          </Link>
        </div>
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-white/50">
          <Link to="/#how-it-works" className="hover:text-cyan-300 transition-colors">איך זה עובד</Link>
          <Link to="/use-cases" className="hover:text-cyan-300 transition-colors">תרחישים</Link>
          <Link to="/vault" className="flex items-center gap-1.5 hover:text-cyan-300 transition-colors">
            <Server className="w-3.5 h-3.5" />
            הכספת
          </Link>
          <Link to="/insiders" className="flex items-center gap-1.5 hover:text-cyan-300 transition-colors">
            <User className="w-3.5 h-3.5" />
            הקהילה
          </Link>
          <Link to="/compare" className="flex items-center gap-1.5 hover:text-indigo-400 transition-colors text-indigo-300/80">
            <Scale className="w-3.5 h-3.5" />
            השוואה
          </Link>

          {isAdmin && (
            <>
              <Link to="/admin/vault" className="flex items-center gap-1.5 text-cyan-400 hover:text-cyan-300 drop-shadow-[0_0_8px_rgba(6,182,212,0.3)] transition-all font-bold">
                <Shield className="w-3.5 h-3.5" />
                Vault
              </Link>
              <Link to="/admin/analytics" className="flex items-center gap-1.5 text-indigo-400 hover:text-indigo-300 drop-shadow-[0_0_8px_rgba(129,140,248,0.3)] transition-all font-bold">
                <BarChart3 className="w-3.5 h-3.5" />
                Analytics
              </Link>
            </>
          )}
        </nav>
        <div className="flex items-center gap-4">
          {currentUser ? (
            <div className="flex items-center gap-4" dir="rtl">
              <div className="flex flex-col items-start leading-tight">
                <span className="text-[10px] text-white/40 uppercase tracking-widest font-bold">שלום,</span>
                <span className="text-sm font-bold text-white tracking-tight">
                  {currentUser.displayName || currentUser.email.split('@')[0]}
                </span>
              </div>
              
              <div className="flex items-center gap-1.5 p-1 bg-white/5 backdrop-blur-md border border-white/10 rounded-xl">
                <Link 
                  to="/settings" 
                  className="p-2 hover:bg-white/10 rounded-lg transition-all text-white/60 hover:text-cyan-400 group"
                  title="הגדרות חשבון"
                >
                  <SettingsIcon className="w-5 h-5 group-hover:rotate-45 transition-transform duration-300" />
                </Link>
                <button 
                  onClick={logout}
                  className="p-2 hover:bg-rose-500/10 rounded-lg transition-all text-white/60 hover:text-rose-400"
                  title="התנתק"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            </div>
          ) : (
            <>
              <Link to="/activation" className="text-sm font-medium text-white/50 hover:text-slate-200 transition-colors hidden sm:block">
                התחבר
              </Link>
              <Link to="/activation" className="px-4 py-2 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-sm font-medium rounded-lg hover:bg-cyan-500/20 hover:shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all">
                התחל בחינם
              </Link>
            </>
          )}
        </div>
      </header>

      {/* Main Container - The dynamic part */}
      <main className="max-w-4xl mx-auto w-full px-4 flex flex-col items-center pt-8 pb-24 flex-1">
        <Suspense fallback={<div className="min-h-[50vh] w-full bg-[#040914]" />}>
          <Routes>
            <Route path="/" element={<Home setAppError={setAppError} />} />
            <Route path="/pricing" element={<Pricing setAppError={setAppError} />} />
            <Route path="/tool/:id" element={<ToolDetails setAppError={setAppError} />} />
            <Route path="/vault" element={<Vault setAppError={setAppError} />} />
            <Route path="/no-insights" element={<NoInsights setAppError={setAppError} />} />
            <Route path="/activation" element={<Activation setAppError={setAppError} />} />
            <Route path="/my-stack" element={<MyStack setAppError={setAppError} />} />
            <Route path="/settings" element={<Settings setAppError={setAppError} />} />
            <Route path="/upgrade" element={<Upgrade setAppError={setAppError} />} />
            <Route path="/use-cases" element={<UseCases setAppError={setAppError} />} />
            <Route path="/about" element={<About setAppError={setAppError} />} />
            <Route path="/blog" element={<Blog setAppError={setAppError} />} />
            <Route path="/blog/:slug" element={<BlogPost setAppError={setAppError} />} />
            <Route path="/api-docs" element={<ApiDocs setAppError={setAppError} />} />
            <Route path="/contact" element={<Contact setAppError={setAppError} />} />
            <Route path="/terms" element={<Terms setAppError={setAppError} />} />
            <Route path="/privacy" element={<Privacy setAppError={setAppError} />} />
            <Route path="/admin/vault" element={<AdminVault />} />
            <Route path="/admin/analytics" element={<AdminAnalytics setAppError={setAppError} />} />
            <Route path="/insiders" element={<AetherInsiders setAppError={setAppError} />} />
            <Route path="/insiders/battle" element={<EloBattle setAppError={setAppError} />} />
            <Route path="/compare" element={<Compare setAppError={setAppError} />} />
            <Route path="/vendor/insights" element={<VendorInsights />} />

            {/* Catch All 404 */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </main>

      {/* 7. Minimalist Footer - PERSISTENT OUTSIDE ROUTES */}
      <footer className="w-full border-t border-white/5 bg-[#040914] pt-16 pb-8 px-6 md:px-12 mt-auto" dir="rtl">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
          <div>
            <h4 className="font-semibold text-white mb-4 text-sm">מוצר</h4>
            <ul className="space-y-2 text-sm text-white/60">
              <li><Link to="/use-cases" className="hover:text-cyan-400 transition-colors">אינדקס כלים</Link></li>
              <li><Link to="/vault" className="hover:text-cyan-400 transition-colors">הכספת (Live Data)</Link></li>
              <li><Link to="/insiders" className="hover:text-cyan-400 transition-colors font-bold text-cyan-400/80">Aether Insiders</Link></li>
              <li><Link to="/upgrade" className="hover:text-cyan-400 transition-colors">Aether Pro</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-white mb-4 text-sm">חברה</h4>
            <ul className="space-y-2 text-sm text-white/60">
              <li><Link to="/about" className="hover:text-cyan-400 transition-colors">אודות</Link></li>
              <li><Link to="/blog" className="hover:text-cyan-400 transition-colors">בלוג</Link></li>
              <li><Link to="/contact" className="hover:text-cyan-400 transition-colors">צור קשר</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-white mb-4 text-sm">חוקי</h4>
            <ul className="space-y-2 text-sm text-white/60">
              <li><Link to="/terms" className="hover:text-cyan-400 transition-colors">תנאי שימוש</Link></li>
              <li><Link to="/privacy" className="hover:text-cyan-400 transition-colors">פרטיות</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-white mb-4 text-sm">רשתות</h4>
            <ul className="space-y-2 text-sm text-white/60">
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Twitter (X)</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">LinkedIn</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">GitHub</a></li>
            </ul>
          </div>
        </div>
        <div className="max-w-4xl mx-auto flex flex-col md:flex-row items-center justify-between pt-8 border-t border-white/5 text-xs text-white/70">
          <span>© 2026 Aether AI. כל הזכויות שמורות.</span>
          <div className="flex items-center gap-3 mt-4 md:mt-0 opacity-60 hover:opacity-100 transition-all duration-300" dir="ltr">
            <div className="flex flex-col items-center justify-center gap-2">
              <img src="/logo.png.png" alt="Aether Logo" className="h-12 w-auto object-contain grayscale hover:grayscale-0 transition-all duration-300" />
              <span className="text-[0.55rem] tracking-wider text-white/60 uppercase leading-none">The Ultimate AI Compass</span>
            </div>
          </div>
        </div>
      </footer>

      {/* Subtle Error Toast Fixed at bottom (Clinical Light Mode Fallback) */}
      {appError && (
        <div className="fixed top-4 right-4 z-[9999] px-4 py-3 rounded-xl bg-red-500/90 backdrop-blur-md border border-red-500/50 text-white text-sm flex items-center justify-center gap-2 font-medium shadow-2xl transition-all animate-in slide-in-from-top-5">
          <AlertCircle className="w-5 h-5 text-white" />
          {appError}
        </div>
      )}
    </div>
  );
}

export default App;
