import Link from "next/link";
import { Show, SignInButton } from "@clerk/nextjs";

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col items-center bg-background selection:bg-brand/30 selection:text-white">
      
      {/* NAVBAR */}
      <nav className="w-full max-w-6xl flex justify-between items-center py-8 px-6 md:px-12">
        <div className="text-2xl font-bold tracking-tighter text-white">
          Niche<span className="text-brand">Hunter</span> AI
        </div>
        <div className="flex items-center gap-4">
          <Show when="signed-out">
            <SignInButton mode="modal" forceRedirectUrl="/dashboard">
              <button className="text-sm font-medium text-gray-400 hover:text-white transition-colors cursor-pointer">
                Sign In
              </button>
            </SignInButton>
            <SignInButton mode="modal" forceRedirectUrl="/dashboard">
              <button className="bg-brand/10 text-brand border border-brand/30 hover:bg-brand hover:text-black transition-all px-5 py-2 rounded-lg text-sm font-medium cursor-pointer shadow-[0_0_15px_rgba(0,255,65,0.15)]">
                Get Started for Free
              </button>
            </SignInButton>
          </Show>
          <Show when="signed-in">
            <Link href="/dashboard" className="bg-brand text-black hover:bg-brand/80 transition-all px-5 py-2 rounded-lg text-sm font-bold cursor-pointer">
              Go to Dashboard
            </Link>
          </Show>
        </div>
      </nav>

      {/* HERO SECTION */}
      <section className="w-full max-w-6xl flex flex-col items-center text-center px-6 mt-20 md:mt-32 mb-32 relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-brand/5 rounded-full blur-[120px] pointer-events-none"></div>
        
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-panel border border-border-subtle text-xs font-mono text-gray-400 mb-8">
          <span className="w-2 h-2 rounded-full bg-brand animate-pulse"></span>
          AI Engine v1.0 Active
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold tracking-tighter text-white mb-6 leading-tight max-w-4xl relative z-10">
          Discover hidden <br className="hidden md:block"/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand to-emerald-600">Startups on the internet</span>
        </h1>
        
        <p className="text-lg md:text-xl text-gray-400 max-w-2xl mb-12 leading-relaxed">
          Navigate business opportunities no one else sees. Our AI scans thousands of real complaints on Reddit and delivers validated SaaS ideas before you write a single line of code.
        </p>

        <Show when="signed-out">
          <SignInButton mode="modal" forceRedirectUrl="/dashboard">
            <button className="group relative bg-brand text-black font-bold text-lg px-8 py-4 rounded-xl transition-all hover:scale-105 cursor-pointer flex items-center gap-3">
              Infiltrate a Niche
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="group-hover:translate-x-1 transition-transform"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
            </button>
          </SignInButton>
        </Show>
        <Show when="signed-in">
          <Link href="/dashboard" className="group relative bg-brand text-black font-bold text-lg px-8 py-4 rounded-xl transition-all hover:scale-105 cursor-pointer flex items-center gap-3">
            Access Terminal
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="group-hover:translate-x-1 transition-transform"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
          </Link>
        </Show>
      </section>

      {/* PAIN POINTS SECTION */}
      <section className="w-full max-w-6xl px-6 py-24 border-t border-border-subtle relative">
        <h2 className="text-3xl font-bold text-center text-white mb-16">Stop guessing what to build</h2>
        
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              title: "Hours wasted searching",
              desc: "Reading thousands of Reddit threads to find a real problem takes days. Our AI does it in seconds.",
              icon: "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            },
            {
              title: "Building without demand",
              desc: "90% of startups die because they solve problems that do not exist. We start from real pain.",
              icon: "M13 10V3L4 14h7v7l9-11h-7z"
            },
            {
              title: "Lack of clarity",
              desc: "Finding a complaint is easy, converting it into a profitable business model (SaaS) is hard. We give you the plan.",
              icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            }
          ].map((item, i) => (
            <div key={i} className="bg-panel border border-border-subtle p-8 rounded-2xl hover:border-brand/30 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-brand/10 flex items-center justify-center text-brand mb-6">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d={item.icon}></path></svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">{item.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS SECTION */}
      <section className="w-full max-w-6xl px-6 py-24 border-t border-border-subtle">
        <h2 className="text-3xl font-bold text-center text-white mb-16">How does the engine work?</h2>
        
        <div className="flex flex-col space-y-12 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-border-subtle before:to-transparent">
          {[
            {
              step: "01",
              title: "Define the Objective",
              desc: "You enter a specific niche or audience. (Ex: Freelance video editors)."
            },
            {
              step: "02",
              title: "Deep Extraction",
              desc: "Our spiders navigate specific subreddits looking for toxic posts, complaints, and repetitive frustrations."
            },
            {
              step: "03",
              title: "Vector Clustering",
              desc: "We use OpenAI Embeddings and HDBSCAN to group similar complaints and discover hidden patterns."
            },
            {
              step: "04",
              title: "Business Opportunity",
              desc: "Azure GPT-4o analyzes the mathematical groups and returns a startup pitch with a monetization model and solution."
            }
          ].map((item, i) => (
            <div key={i} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
              <div className="flex items-center justify-center w-10 h-10 rounded-full border border-brand bg-black text-brand font-bold text-sm shadow-[0_0_10px_rgba(0,255,65,0.2)] shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                {item.step}
              </div>
              <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-6 rounded-2xl bg-panel border border-border-subtle group-hover:border-brand/20 transition-colors">
                <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                <p className="text-sm text-gray-400">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* FOOTER */}
      <footer className="w-full py-8 text-center border-t border-border-subtle mt-auto">
        <p className="text-gray-600 text-sm font-mono">
          © {new Date().getFullYear()} NicheHunter AI. All rights reserved.
        </p>
      </footer>
    </div>
  );
}
