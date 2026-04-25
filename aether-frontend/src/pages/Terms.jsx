import React from 'react';
import { FileText, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Terms() {
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
                        <FileText className="w-3 h-3" /> Legal Document
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight mb-4">
                        Terms of Service
                    </h1>
                    <p className="text-lg text-white/50 font-medium">Last Updated: February 1, 2026</p>
                </div>

                {/* Content */}
                <div className="prose prose-neutral prose-lg max-w-none text-white/50 space-y-8 leading-loose">
                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">1. Introduction</h2>
                        <p>Welcome to Aether Lab ("the Company", "we", "us", "our"). These terms define the conditions for using the Aether platform, including the website, API services, and related tools. Using the system constitutes full agreement to these terms.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">2. Nature of Service and Disclaimer</h2>
                        <p>Aether provides a platform for indexing and analyzing AI tools based on independent laboratory tests. However:</p>
                        <ul className="list-disc pl-6 space-y-2 marker:text-white/30">
                            <li>Information is provided "as-is" without warranty of absolute accuracy, given the dynamic nature of AI tools.</li>
                            <li>Aether bears no responsibility for any damage, direct or indirect, caused by reliance on laboratory data.</li>
                            <li>The responsibility for reviewing use terms and licenses of any AI tool presented on the platform lies solely with the user.</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">3. Data and Objectivity</h2>
                        <p>We guarantee that the Trust Score index and Intent Resolution engine results are not subject to financial manipulation by commercial companies (Pay-to-Play). In cases of sponsored content, it will be explicitly and prominently marked as "Promoted".</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">4. API Usage</h2>
                        <p>Users with access to the Vault API are required to maintain the confidentiality of access keys. Aether reserves the right to suspend or block API access in cases of unusual load or abuse that does not meet the SLA terms.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">5. Changes to Terms</h2>
                        <p>The company may update these terms from time to time without prior notice. Continued use of the service after the update is published constitutes agreement to the new terms. Material updates will be sent to registered users via email.</p>
                    </section>
                </div>

            </main>
        </div>
    );
}
