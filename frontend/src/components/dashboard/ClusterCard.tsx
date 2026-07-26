export default function ClusterCard({ cluster, onGenerate, isGenerating, onViewRaw }: any) {
  return (
    <div className="flex flex-col bg-panel border border-border-subtle rounded-2xl p-6 relative hover:border-brand/50 transition-colors">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-bold text-white mb-1 capitalize">{cluster.label}</h3>
          <span className="text-xs text-gray-500 font-mono">{cluster.niche}</span>
        </div>
        <div className="flex flex-col items-end">
          <div className="text-2xl font-bold text-brand">{cluster.size}</div>
          <div className="text-[10px] text-gray-500 uppercase tracking-wider">Quejas</div>
        </div>
      </div>
      
      <div className="mb-4">
        <span className="bg-red-500/10 text-red-400 border border-red-500/30 px-3 py-1 rounded-full text-xs font-mono font-bold">
          Severidad Avg: {cluster.avg_severity_score?.toFixed(1) || "N/A"}/10
        </span>
      </div>

      <p className="text-gray-300 text-sm leading-relaxed mb-6 italic line-clamp-3">
        "{cluster.summary}"
      </p>

      <div className="mt-auto flex flex-col gap-2 border-t border-white/5 pt-4">
        {cluster.has_opportunity ? (
          <div className="text-center py-2 text-sm text-brand font-bold border border-brand/30 bg-brand/10 rounded-lg">
            ✓ Report Generated
          </div>
        ) : (
          <button 
            onClick={(e) => {
              e.stopPropagation();
              onGenerate(cluster.id);
            }}
            disabled={isGenerating}
            className="w-full bg-brand text-white hover:bg-brand/80 disabled:opacity-50 transition-colors py-2 rounded-lg font-bold text-sm flex items-center justify-center gap-2"
          >
            {isGenerating ? "Generating..." : "Generate Report"}
          </button>
        )}
      </div>
    </div>
  );
}
