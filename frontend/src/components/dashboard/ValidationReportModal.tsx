import { Download, Trash2, X } from "lucide-react";

export default function ValidationReportModal({ report, onClose, onDelete }: any) {
  const exportToMarkdown = () => {
    const mdContent = `
# Market Intelligence Report: ${report.report_title}

## Executive Verdict
**Verdict:** ${report.validation_verdict}
**Overall Opportunity Score:** ${report.opportunity_score}/10
**Demand:** ${report.demand_score}/10 | **Pain Severity:** ${report.pain_severity_score}/10 | **Competition:** ${report.competition_score}/10

## Market Metrics
**Total Addressable Market (TAM):** ${report.market_size_tam || "N/A"}
**Compound Annual Growth Rate (CAGR):** ${report.market_growth_cagr || "N/A"}
**Willingness to Pay:** ${report.willingness_to_pay}
**Trend Velocity:** ${report.trend_velocity}
${report.tam_cagr_sources?.length ? `\n**Financial Sources:**\n${report.tam_cagr_sources.map((url: string) => `- ${url}`).join('\n')}` : ""}

## Evidence Dashboard
* **Sources Analyzed:** ${report.post_count} discussions
* **Community Engagement:** ${report.total_upvotes} upvotes, ${report.total_comments} comments

### Representative Quotes
${report.representative_quotes?.map((q: string) => `> "${q}"`).join('\n\n') || "> No quotes available."}

### Top Pain Points
| Issue | Mentions | Severity (0-10) |
|-------|----------|-----------------|
${report.top_pain_points?.map((p: any) => `| ${p.issue} | ${p.mentions} | ${p.severity} |`).join('\n') || "| N/A | N/A | N/A |"}

## Executive Summary
${report.friction_summary}

## Cost of Inaction
${report.cost_of_inaction}

## Target Audience
${report.audience_profile}

## Market Landscape
**Existing Alternatives:**
${report.existing_alternatives}

**Competitor Gaps:**
${report.competitor_gaps}

## Risk Profile
${report.risk_profile}

## Opportunity Assessment
**Why this score (${report.opportunity_score}/10)?**
${report.opportunity_why?.map((w: string) => `- ${w}`).join('\n')}

**Strategic Recommendations:**
${report.strategic_recommendations?.map((r: string) => `- ${r}`).join('\n')}

**Recommended Positioning:**
> ${report.recommended_positioning}

**MVP Features:**
${report.mvp_features?.map((f: string) => `- ${f}`).join('\n')}
`;
    
    const blob = new Blob([mdContent.trim()], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Report-${report.report_title.replace(/\s+/g, '-').toLowerCase()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Parse verdict if it contains a long rationale
  const verdictParts = report.validation_verdict.split(".");
  const shortVerdict = verdictParts[0];
  const rationale = verdictParts.slice(1).join(".").trim();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose}></div>
      <div className="relative w-full max-w-4xl bg-[#111] border border-border-subtle rounded-2xl shadow-2xl max-h-[90vh] overflow-y-auto flex flex-col">
        
        <div className="sticky top-0 flex items-start justify-between p-6 border-b border-white/5 bg-[#111]/95 backdrop-blur-md rounded-t-2xl z-10 gap-4 shrink-0">
          <div className="flex flex-col gap-2">
            <h2 className="text-2xl font-bold text-white">{report.report_title}</h2>
            <div className="px-3 py-1 bg-brand/10 border border-brand/30 text-brand rounded-full text-sm font-bold w-fit">
              {shortVerdict}
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button 
              onClick={exportToMarkdown}
              className="p-2 text-gray-400 hover:text-white bg-white/5 hover:bg-white/10 rounded-lg transition-colors flex items-center gap-2 text-sm font-medium"
            >
              <Download size={16} /> <span className="hidden sm:inline">Export</span>
            </button>
            <button onClick={onClose} className="p-2 text-gray-400 hover:text-white bg-white/5 hover:bg-white/10 rounded-lg transition-colors">
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="p-8 space-y-8">
          
          {/* Executive Scores Breakdown */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-[#1a1a1c] p-4 rounded-xl text-center border border-white/5">
              <div className="text-gray-500 text-[10px] font-mono uppercase tracking-wider mb-2">Demand</div>
              <div className="text-xl font-bold text-white">{report.demand_score}<span className="text-gray-600 text-sm">/10</span></div>
            </div>
            <div className="bg-[#1a1a1c] p-4 rounded-xl text-center border border-white/5">
              <div className="text-gray-500 text-[10px] font-mono uppercase tracking-wider mb-2">Pain Severity</div>
              <div className="text-xl font-bold text-white">{report.pain_severity_score}<span className="text-gray-600 text-sm">/10</span></div>
            </div>
            <div className="bg-[#1a1a1c] p-4 rounded-xl text-center border border-white/5">
              <div className="text-gray-500 text-[10px] font-mono uppercase tracking-wider mb-2">Competition</div>
              <div className="text-xl font-bold text-white">{report.competition_score}<span className="text-gray-600 text-sm">/10</span></div>
            </div>
            <div className="bg-[#1a1a1c] p-4 rounded-xl text-center border border-white/5">
              <div className="text-gray-500 text-[10px] font-mono uppercase tracking-wider mb-2">Confidence</div>
              <div className="text-xl font-bold text-white">{report.overall_confidence_score}<span className="text-gray-600 text-sm">/10</span></div>
            </div>
            <div className="bg-brand/10 p-4 rounded-xl text-center border border-brand/30 col-span-2 md:col-span-1 shadow-[0_0_15px_rgba(255,255,255,0.05)]">
              <div className="text-brand/80 text-[10px] font-mono uppercase tracking-wider mb-2">Opportunity</div>
              <div className="text-2xl font-bold text-brand">{report.opportunity_score}<span className="text-brand/50 text-sm">/10</span></div>
            </div>
          </div>

          {rationale && (
            <section className="bg-brand/5 border border-brand/20 p-5 rounded-xl">
              <p className="text-brand/90 leading-relaxed font-medium">"{rationale}"</p>
            </section>
          )}

          {/* Evidence Dashboard */}
          <section>
            <h3 className="text-xl font-bold text-white mb-4 border-b border-white/5 pb-2">Evidence Dashboard</h3>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* Voice of the Customer */}
              <div className="lg:col-span-2 space-y-4">
                <h4 className="text-sm font-bold text-gray-400 mb-2">Representative Quotes</h4>
                <div className="space-y-3">
                  {report.representative_quotes?.map((quote: string, idx: number) => (
                    <blockquote key={idx} className="bg-[#1a1a1c] p-4 rounded-lg border-l-2 border-brand text-gray-300 italic text-sm">
                      "{quote}"
                    </blockquote>
                  ))}
                  {(!report.representative_quotes || report.representative_quotes.length === 0) && (
                    <p className="text-gray-500 text-sm">No quotes available.</p>
                  )}
                </div>
              </div>

              {/* Data Sources Stats */}
              <div className="bg-[#1a1a1c] p-5 rounded-xl border border-white/5 flex flex-col gap-4">
                <h4 className="text-sm font-bold text-gray-400">Sources Analyzed</h4>
                <div className="flex justify-between items-center border-b border-white/5 pb-2">
                  <span className="text-gray-400 text-sm">Discussions</span>
                  <span className="text-white font-bold">{report.post_count}</span>
                </div>
                <div className="flex justify-between items-center border-b border-white/5 pb-2">
                  <span className="text-gray-400 text-sm">Total Upvotes</span>
                  <span className="text-white font-bold">{report.total_upvotes}</span>
                </div>
                <div className="flex justify-between items-center border-b border-white/5 pb-2">
                  <span className="text-gray-400 text-sm">Total Comments</span>
                  <span className="text-white font-bold">{report.total_comments}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">Pain Points</span>
                  <span className="text-brand font-bold">{report.top_pain_points?.length || 0}</span>
                </div>
              </div>
            </div>
          </section>

          {/* Top Pain Points Table */}
          {report.top_pain_points && report.top_pain_points.length > 0 && (
            <section className="bg-panel border border-border-subtle p-6 rounded-xl">
              <h3 className="text-lg font-bold text-white mb-4">Top Pain Points</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-[#1a1a1c] text-gray-400 font-mono text-[10px] uppercase">
                    <tr>
                      <th className="px-4 py-3 rounded-tl-lg">Issue</th>
                      <th className="px-4 py-3 text-right">Mentions</th>
                      <th className="px-4 py-3 text-right rounded-tr-lg">Severity</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {report.top_pain_points.map((pt: any, idx: number) => (
                      <tr key={idx} className="hover:bg-white/5 transition-colors">
                        <td className="px-4 py-3 text-white font-medium">{pt.issue}</td>
                        <td className="px-4 py-3 text-gray-400 text-right">{pt.mentions}</td>
                        <td className="px-4 py-3 text-brand text-right font-bold">{pt.severity}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          <section className="bg-panel border border-border-subtle p-6 rounded-xl">
            <h3 className="text-lg font-bold text-white mb-3">Executive Summary (Friction)</h3>
            <p className="text-gray-300 leading-relaxed">{report.friction_summary}</p>
          </section>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <section className="bg-panel border border-border-subtle p-6 rounded-xl">
              <h3 className="text-sm font-mono text-gray-500 uppercase mb-2 tracking-wider">Target Audience</h3>
              <p className="text-white font-medium">{report.audience_profile}</p>
            </section>
            
            <section className="bg-panel border border-border-subtle p-6 rounded-xl">
              <h3 className="text-sm font-mono text-gray-500 uppercase mb-2 tracking-wider">Cost of Inaction</h3>
              <p className="text-red-400 font-medium">{report.cost_of_inaction}</p>
            </section>
          </div>

          <section>
            <h3 className="text-xl font-bold text-white mb-4 border-b border-white/5 pb-2">Market Landscape</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-panel p-5 rounded-xl border border-border-subtle">
                <h4 className="font-bold text-gray-400 mb-2 text-sm">Existing Alternatives</h4>
                <p className="text-gray-300 text-sm leading-relaxed">{report.existing_alternatives}</p>
              </div>
              <div className="bg-panel p-5 rounded-xl border border-brand/30">
                <h4 className="font-bold text-brand mb-2 text-sm">Competitor Gaps</h4>
                <p className="text-gray-300 text-sm leading-relaxed">{report.competitor_gaps}</p>
              </div>
            </div>
          </section>

          <section className="bg-panel border border-border-subtle p-6 rounded-xl">
            <h3 className="text-lg font-bold text-white mb-3">Risk Profile</h3>
            <p className="text-gray-300 leading-relaxed">{report.risk_profile}</p>
          </section>

          <section className="bg-brand/5 border border-brand/20 p-6 rounded-xl">
            <h3 className="text-xl font-bold text-white mb-6 border-b border-brand/20 pb-2 flex items-center justify-between">
              Opportunity Assessment
              <span className="text-brand text-2xl">{report.opportunity_score}/10</span>
            </h3>
            
            <div className="space-y-6">
              <div>
                <h4 className="text-sm font-bold text-brand mb-2">Why?</h4>
                <ul className="list-disc pl-5 space-y-1">
                  {report.opportunity_why?.map((reason: string, idx: number) => (
                    <li key={idx} className="text-gray-300 text-sm">{reason}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="text-sm font-bold text-brand mb-2">Strategic Recommendations</h4>
                <ul className="list-disc pl-5 space-y-1">
                  {report.strategic_recommendations?.map((rec: string, idx: number) => (
                    <li key={idx} className="text-gray-300 text-sm">{rec}</li>
                  ))}
                </ul>
              </div>

              <div className="bg-[#111] p-4 rounded-lg border border-brand/10">
                <h4 className="text-sm font-bold text-gray-400 mb-2">Recommended Positioning</h4>
                <p className="text-white italic">"{report.recommended_positioning}"</p>
              </div>

              <div>
                <h4 className="text-sm font-bold text-brand mb-2">MVP Features</h4>
                <ul className="flex flex-wrap gap-2">
                  {report.mvp_features?.map((feature: string, idx: number) => (
                    <li key={idx} className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs text-gray-300">
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </section>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 border-t border-white/5 pt-8">
            <div className="p-4 bg-[#1a1a1c] rounded-xl text-center">
              <div className="text-gray-500 text-[10px] font-mono uppercase mb-1">Total Market (TAM)</div>
              <div className="text-brand font-bold text-sm">{report.market_size_tam || "N/A"}</div>
            </div>
            <div className="p-4 bg-[#1a1a1c] rounded-xl text-center">
              <div className="text-gray-500 text-[10px] font-mono uppercase mb-1">Market Growth</div>
              <div className="text-brand font-bold text-sm">{report.market_growth_cagr || "N/A"}</div>
            </div>
            <div className="p-4 bg-[#1a1a1c] rounded-xl text-center">
              <div className="text-gray-500 text-[10px] font-mono uppercase mb-1">Willingness to Pay</div>
              <div className="text-white font-bold text-sm">{report.willingness_to_pay}</div>
            </div>
            <div className="p-4 bg-[#1a1a1c] rounded-xl text-center">
              <div className="text-gray-500 text-[10px] font-mono uppercase mb-1">Trend Velocity</div>
              <div className="text-white font-bold text-sm">{report.trend_velocity}</div>
            </div>
          </div>
          
          {/* Fuentes Financieras */}
          <div className="mt-4 pt-4 border-t border-white/5">
            <h3 className="text-xs font-mono text-gray-500 uppercase mb-2 tracking-wider">Financial Data Sources</h3>
            {report.tam_cagr_sources && report.tam_cagr_sources.length > 0 ? (
              <ul className="flex flex-col gap-1">
                {report.tam_cagr_sources.map((url: string, idx: number) => (
                  <li key={idx}>
                    <a href={url} target="_blank" rel="noopener noreferrer" className="text-brand/80 hover:text-brand text-xs flex items-center gap-1 hover:underline truncate max-w-full">
                      ↳ {url}
                    </a>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500 text-xs italic">
                * AI Estimated Data. No direct web sources available at the time of generation.
              </p>
            )}
          </div>
        </div>
        
        <div className="p-6 border-t border-white/5 bg-[#111] rounded-b-2xl flex justify-between items-center">
            <button 
                onClick={() => {
                  onDelete(report.id);
                  onClose();
                }}
                className="flex items-center gap-2 text-red-500 hover:text-white hover:bg-red-500 px-4 py-2 rounded-lg transition-colors font-bold text-sm"
              >
                <Trash2 size={16} /> Delete Report
            </button>
            <button onClick={onClose} className="bg-white text-black px-6 py-2 rounded-lg font-bold hover:bg-gray-200 transition-colors">
              Close
            </button>
        </div>
      </div>
    </div>
  );
}
