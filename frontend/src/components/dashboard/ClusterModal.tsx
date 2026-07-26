"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/apiClient";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { X, Activity, TrendingUp, Users } from "lucide-react";

export default function ClusterModal({ cluster, onClose, onGenerate, isGenerating }: any) {
  // Fetch pain points for this cluster to build charts
  const { data: painPoints, isLoading } = useQuery({
    queryKey: ["clusterPainPoints", cluster.id],
    queryFn: async () => {
      const response = await apiClient.get(`/clusters/${cluster.id}/pain_points`);
      return response.data;
    },
  });

  // Prepare chart data
  const severityData = [
    { name: "1-4 (Baja)", value: 0 },
    { name: "5-7 (Media)", value: 0 },
    { name: "8-10 (Alta)", value: 0 },
  ];

  const sourceData: Record<string, number> = {};

  if (painPoints) {
    painPoints.forEach((pp: any) => {
      // Severity
      const sev = parseFloat(pp.severity);
      if (!isNaN(sev)) {
        if (sev <= 4) severityData[0].value += 1;
        else if (sev <= 7) severityData[1].value += 1;
        else severityData[2].value += 1;
      }
    });
  }
  
  const avgConfidence = painPoints && painPoints.length > 0 
    ? (painPoints.reduce((acc: number, pp: any) => acc + (pp.confidence_score || 0), 0) / painPoints.length) * 100
    : 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose}></div>
      <div className="relative bg-[#111] border border-border-subtle rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl">
        
        <div className="sticky top-0 bg-[#111]/90 backdrop-blur-md border-b border-border-subtle p-6 flex justify-between items-start z-10">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="bg-brand/10 text-brand px-3 py-1 rounded-full text-xs font-mono font-bold">
                {cluster.niche}
              </span>
              <span className="bg-red-500/10 text-red-500 px-3 py-1 rounded-full text-xs font-mono font-bold">
                Avg Severity: {cluster.avg_severity_score?.toFixed(1)}
              </span>
            </div>
            <h2 className="text-3xl font-bold text-white capitalize">{cluster.label}</h2>
          </div>
          <button onClick={onClose} className="p-2 text-gray-400 hover:text-white transition-colors">
            <X size={24} />
          </button>
        </div>

        <div className="p-6 space-y-8">
          <section className="bg-panel p-6 rounded-xl border border-white/5">
             <h3 className="text-sm font-mono text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-2">
              <Activity size={16} />
              Resumen Analítico
            </h3>
            <p className="text-gray-200 text-lg leading-relaxed italic">"{cluster.summary}"</p>
          </section>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-panel p-6 rounded-xl border border-white/5 flex flex-col items-center justify-center">
              <h3 className="text-sm font-mono text-gray-400 uppercase tracking-widest mb-6 w-full flex items-center gap-2">
                <Users size={16} />
                Volumen
              </h3>
              <div className="text-5xl font-bold text-white mb-2">{cluster.size}</div>
              <div className="text-[10px] text-gray-500 uppercase tracking-wider text-center">Quejas Detectadas</div>
            </div>
            
            <div className="bg-panel p-6 rounded-xl border border-white/5 flex flex-col items-center justify-center">
              <h3 className="text-sm font-mono text-gray-400 uppercase tracking-widest mb-6 w-full flex items-center gap-2">
                <Activity size={16} />
                Fiabilidad AI
              </h3>
              <div className="text-5xl font-bold text-brand mb-2">{avgConfidence.toFixed(0)}%</div>
              <div className="text-[10px] text-gray-500 uppercase tracking-wider text-center">Nivel de Confianza</div>
            </div>

            <div className="bg-panel p-6 rounded-xl border border-white/5 h-48 col-span-1 md:col-span-1">
              <h3 className="text-sm font-mono text-gray-400 uppercase tracking-widest mb-2 flex items-center gap-2">
                <TrendingUp size={16} />
                Severidad
              </h3>
              {isLoading ? (
                <div className="w-full h-full flex items-center justify-center text-brand animate-pulse">Loading data...</div>
              ) : (
                <ResponsiveContainer width="100%" height="80%">
                  <BarChart data={severityData}>
                    <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} contentStyle={{ backgroundColor: '#111', borderColor: '#333' }} />
                    <XAxis dataKey="name" stroke="#666" fontSize={10} tickLine={false} axisLine={false} />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                      {severityData.map((entry, index) => (
                         <Cell key={`cell-${index}`} fill={index === 2 ? '#ef4444' : index === 1 ? '#eab308' : '#22c55e'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
          
          <div className="flex flex-col items-center pt-4">
              {cluster.has_opportunity ? (
                <div className="w-full text-center py-4 text-brand font-bold border border-brand/30 bg-brand/10 rounded-xl">
                  El Reporte de Validación de este mercado ya fue emitido y está en tu panel.
                </div>
              ) : (
                <button 
                  onClick={() => onGenerate(cluster.id)}
                  disabled={isGenerating}
                  className="px-6 py-2 bg-brand text-black hover:bg-brand/80 rounded-lg transition-colors font-medium flex-1 disabled:opacity-50"
                >
                  {isGenerating ? "Processing Market Analysis..." : "Generate Validation Report"}
                </button>
              )}
              <p className="text-xs text-gray-500 mt-4 text-center max-w-md">
                Al generar el reporte, nuestro Analista B2B estructurará el perfil del mercado, evaluando fricciones, alternativas y disposición de pago.
              </p>
          </div>
          
          {/* Individual Pain Points List */}
          <div className="pt-8 border-t border-white/5">
            <h3 className="text-lg font-bold text-white mb-4">Evidencia Bruta ({painPoints?.length || 0})</h3>
            <div className="space-y-3">
              {isLoading ? (
                <p className="text-gray-500">Cargando quejas...</p>
              ) : (
                painPoints?.map((pp: any) => (
                  <div key={pp.id} className="bg-[#1a1a1c] p-4 rounded-xl border border-white/5 flex flex-col gap-2">
                    <p className="text-sm text-gray-300">"{pp.description}"</p>
                    <div className="flex items-center gap-3 text-xs">
                      <span className={`font-mono font-bold ${parseFloat(pp.severity) >= 8 ? 'text-red-500' : parseFloat(pp.severity) >= 5 ? 'text-yellow-500' : 'text-green-500'}`}>
                        Sev: {pp.severity}
                      </span>
                      {pp.url && (
                        <a href={pp.url} target="_blank" rel="noopener noreferrer" className="text-brand hover:underline">
                          Ver Fuente Original
                        </a>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
