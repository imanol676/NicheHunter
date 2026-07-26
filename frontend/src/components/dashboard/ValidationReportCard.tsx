import { Trash2 } from "lucide-react";

export default function ValidationReportCard({ report, onClick, onDelete, isDeleting }: any) {
  // Parse verdict
  const shortVerdict = report.validation_verdict ? report.validation_verdict.split(".")[0] : "";

  return (
    <div 
      className="flex flex-col bg-panel border border-border-subtle rounded-2xl p-6 relative cursor-pointer hover:border-brand/50 transition-colors group"
      onClick={onClick}
    >
      <button 
        onClick={(e) => {
          e.stopPropagation();
          onDelete(report.id);
        }}
        disabled={isDeleting}
        className="absolute top-4 right-4 p-2 text-gray-500 hover:text-red-500 bg-[#111] hover:bg-red-500/10 rounded-lg transition-colors opacity-0 group-hover:opacity-100 disabled:opacity-50"
      >
        <Trash2 size={16} />
      </button>

      <div className="flex justify-between items-start mb-4 pr-8">
        <div>
          <h3 className="text-xl font-bold text-white mb-1 leading-tight">{report.report_title}</h3>
          <span className="text-xs text-brand font-mono border border-brand/30 bg-brand/10 px-2 py-0.5 rounded-full inline-block">
            {shortVerdict}
          </span>
        </div>
      </div>
      
      <p className="text-gray-300 text-sm leading-relaxed mb-6 line-clamp-3">
        {report.friction_summary}
      </p>

      <div className="mt-auto flex items-center justify-between border-t border-white/5 pt-4">
        <div className="flex gap-4 text-xs font-bold text-gray-500">
          <span title="Willingness to Pay">WTP: <span className="text-white">{report.willingness_to_pay}</span></span>
          {report.market_size_tam && report.market_size_tam !== "Unknown" && (
            <span title="Total Addressable Market">TAM: <span className="text-brand">{report.market_size_tam}</span></span>
          )}
        </div>
        
        <div className="text-xs font-mono text-gray-500">
          {report.post_count} posts analyzed
        </div>
      </div>
    </div>
  );
}
