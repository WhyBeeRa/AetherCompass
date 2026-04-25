import React from 'react';
import { ShieldCheck, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Privacy() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen w-full flex flex-col items-center bg-[#0a0a0c] pt-24 pb-24 ltr animate-in fade-in duration-700" dir="ltr">
            <main className="w-full max-w-3xl px-6">

                {/* Header */}
                <div className="mb-16">
                    <button onClick={() => navigate(-1)} className="text-white/50 hover:text-white mb-8 transition-colors flex items-center gap-2 text-sm font-bold bg-white/5 backdrop-blur-md px-3 py-1.5 rounded-md border border-white/10 aspect-fit inline-flex w-auto">
                        <ArrowLeft className="w-4 h-4" /> Back
                    </button>
                    <div className="inline-flex items-center gap-2 px-3 py-1 mb-6 rounded-md bg-white/5 backdrop-blur-md border border-white/10 text-white/50 text-xs font-bold tracking-widest uppercase">
                        <ShieldCheck className="w-3 h-3" /> Privacy Policy
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight mb-4">
                        Data Retention Policy
                    </h1>
                    <p className="text-lg text-white/50 font-medium">Last Updated: February 1, 2026</p>
                </div>

                {/* Content */}
                <div className="prose prose-neutral prose-lg max-w-none text-white/70 space-y-8 leading-loose">
                    <div className="p-6 bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl mb-8">
                        <p className="text-sm text-white/70 font-bold m-0 leading-relaxed">
                            Executive Summary: We built Aether around truth, and that includes your privacy. We do not sell our database to third parties. Information is stored securely and encrypted on our servers and is used solely to improve our search engine and manage your personal tool stacks.
                        </p>
                    </div>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">1. Information We Collect</h2>
                        <p className="text-white/50">When you use the service, we collect the following types of information:</p>
                        <ul className="list-disc pl-6 space-y-2 text-white/50 marker:text-white/30">
                            <li><strong className="text-white/80">Information Provided by You:</strong> Email address, user profile (if you joined Aether Patronage or created a My Stack).</li>
                            <li><strong className="text-white/80">Search Information:</strong> Intents entered in the search box. This data is stored anonymously (without linking to user identity) to understand market gaps and direct our agents for investigation.</li>
                            <li><strong className="text-white/80">Automated Technical Data:</strong> IP address, browser type, and standard analytical usage data (e.g., for DDoS prevention).</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">2. How We Use Information</h2>
                        <p className="text-white/50">Our sole goal is to improve Aether's truth-finding service. We do not engage in retargeting or advertising. Primary uses include:</p>
                        <ul className="list-disc pl-6 space-y-2 text-white/50 marker:text-white/30">
                            <li>Storing and synchronizing your My Stack lists.</li>
                            <li>Securing the system and preventing API abuse.</li>
                            <li>Creating aggregate and anonymous statistics.</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">3. Third Parties We Share Information With</h2>
                        <p className="text-white/50">Aether does not sell personal information. We share information minimally only with infrastructure providers necessary for website activity (such as cloud providers and database servers), subject to all strict data security requirements.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">4. Your Rights</h2>
                        <p className="text-white/50">Your digital space belongs to you. You may at any time request the deletion or export of your personal data by visiting the "Contact Us" page. Due to system architecture, we perform a hard delete from the database within 48 hours of receiving the request.</p>
                    </section>
                </div>

            </main>
        </div>
    );
}
