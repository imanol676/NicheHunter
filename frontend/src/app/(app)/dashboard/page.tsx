"use client";

import { useState, useEffect } from "react";
import { Show, SignInButton, UserButton } from "@clerk/nextjs";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/apiClient";
import ClusterCard from "@/components/dashboard/ClusterCard";
import ValidationReportCard from "@/components/dashboard/ValidationReportCard";
import ClusterModal from "@/components/dashboard/ClusterModal";
import ValidationReportModal from "@/components/dashboard/ValidationReportModal";
import { Trash2 } from "lucide-react";

export default function DashboardPage() {
  const [targetIndustry, setTargetIndustry] = useState("");
  const [businessProcess, setBusinessProcess] = useState("");
  const [competitors, setCompetitors] = useState("");
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  
  // Modals state
  const [selectedReport, setSelectedReport] = useState<any | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<any | null>(null);
  
  const [selectedNiche, setSelectedNiche] = useState<string>("All");
  const [activeScanJobId, setActiveScanJobId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"clusters" | "reports">("clusters");
  const queryClient = useQueryClient();

  const createScan = useMutation({
    mutationFn: async (data: { target_industry: string, business_process: string, competitors?: string }) => {
      const response = await apiClient.post("/scans/", data);
      return response.data;
    },
    onSuccess: (data) => {
      setActiveTaskId(data.task_id);
      setActiveScanJobId(data.scan_job_id);
    },
  });

  const analyzeScan = useMutation({
    mutationFn: async () => {
      if (!activeScanJobId) return;
      const response = await apiClient.post(`/scans/${activeScanJobId}/analyze`);
      return response.data;
    },
    onSuccess: (data) => {
      setActiveTaskId(data.task_id);
    },
  });

  const generateReport = useMutation({
    mutationFn: async (clusterId: string) => {
      const response = await apiClient.post(`/clusters/${clusterId}/generate-report`);
      return response.data;
    },
    onSuccess: (data) => {
      setSelectedCluster(null); // Close modal when starting generation
      setActiveTaskId(data.task_id);
    },
  });

  // Polling scan task status
  const scanStatus = useQuery({
    queryKey: ["scanStatus", activeTaskId],
    queryFn: async () => {
      if (!activeTaskId) return null;
      const response = await apiClient.get(`/scans/${activeTaskId}/status`);
      return response.data;
    },
    enabled: !!activeTaskId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "SUCCESS" || status === "FAILURE") {
        return false;
      }
      return 2000;
    },
  });

  const isPhase1Finished = scanStatus.data?.status === "SUCCESS" && (scanStatus.data?.phase === "pending_payment" || scanStatus.data?.phase === "failed_no_data");
  const scanPreview = useQuery({
    queryKey: ["scanPreview", activeScanJobId],
    queryFn: async () => {
      if (!activeScanJobId) return null;
      const response = await apiClient.get(`/scans/${activeScanJobId}/preview`);
      return response.data;
    },
    enabled: isPhase1Finished && !!activeScanJobId,
  });

  const isFinished = scanStatus.data?.status === "SUCCESS" && scanStatus.data?.phase === "completed";
  
  // Invalidate cache when a task finishes successfully (e.g. generating a report)
  useEffect(() => {
    if (scanStatus.data?.status === "SUCCESS") {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      queryClient.invalidateQueries({ queryKey: ["clusters"] });
      
      // Auto-switch to reports tab if a report was just generated
      if (scanStatus.data?.phase === "completed" && activeTab === "clusters" && selectedCluster === null) {
         // Wait, it might be better to just clear the task ID if it was a report generation
         // so it resets the state cleanly, but let's just invalidate for now.
         setActiveTab("reports");
         setTimeout(() => setActiveTaskId(null), 2000);
      }
    }
  }, [scanStatus.data?.status, queryClient, scanStatus.data?.phase]);
  
  const clustersQuery = useQuery({
    queryKey: ["clusters"],
    queryFn: async () => {
      const response = await apiClient.get("/clusters/");
      return response.data as any[];
    },
    enabled: isFinished || activeTaskId === null,
  });

  const reportsQuery = useQuery({
    queryKey: ["reports"],
    queryFn: async () => {
      const response = await apiClient.get("/reports/");
      return response.data as any[];
    },
    enabled: isFinished || activeTaskId === null,
  });

  // Mutations for deletions
  const deleteReport = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/reports/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      queryClient.invalidateQueries({ queryKey: ["clusters"] });
      setSelectedReport(null);
    },
  });

  const deleteAllreports = useMutation({
    mutationFn: async () => {
      await apiClient.delete("/reports/all");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      queryClient.invalidateQueries({ queryKey: ["clusters"] });
    },
  });

  const deleteAllPainPoints = useMutation({
    mutationFn: async () => {
      await apiClient.delete("/pain-points/all");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clusters"] });
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      setActiveScanJobId(null);
      setTargetIndustry("");
      setBusinessProcess("");
      setCompetitors("");
    },
  });

  const deleteCurrentScan = useMutation({
    mutationFn: async () => {
      if (!activeScanJobId) return;
      await apiClient.delete(`/scans/${activeScanJobId}`);
    },
    onSuccess: () => {
      setActiveScanJobId(null);
      setActiveTaskId(null);
      setTargetIndustry("");
      setBusinessProcess("");
      setCompetitors("");
      queryClient.invalidateQueries({ queryKey: ["clusters"] });
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
  });

  if (scanStatus.data?.status === "SUCCESS" && scanStatus.data?.phase === "completed_no_reports") {
    queryClient.invalidateQueries({ queryKey: ["userCoins"] });
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetIndustry || !businessProcess) return;
    createScan.mutate({ target_industry: targetIndustry, business_process: businessProcess, competitors: competitors });
  };

  const hasSearched = !!activeTaskId;
  const hasFailed = scanStatus.data?.status === "FAILURE" || scanStatus.isError;
  const isRunning = (scanStatus.isLoading || scanStatus.data?.status === "PROGRESS" || scanStatus.data?.status === "PENDING" || createScan.isPending || analyzeScan.isPending || generateReport.isPending) && !isPhase1Finished && !hasFailed && scanStatus.data?.status !== "SUCCESS";

  const clustersData = clustersQuery.data || [];
  const reportsData = reportsQuery.data || [];
  
  const uniqueNiches = ["All", ...Array.from(new Set(clustersData.map((c: any) => c.niche).filter(Boolean)))];
  const selectedClusters = selectedNiche === "All" ? clustersData : clustersData.filter((c: any) => c.niche === selectedNiche);
  const selectedReports = selectedNiche === "All" ? reportsData : reportsData.filter((o: any) => o.niche === selectedNiche);

  // Global KPIs
  const totalPainPoints = clustersData.reduce((acc: number, c: any) => acc + (c.size || 0), 0);
  const totalSeveritySum = clustersData.reduce((acc: number, c: any) => acc + ((c.avg_severity_score || 0) * (c.size || 0)), 0);
  const globalSeverity = totalPainPoints > 0 ? (totalSeveritySum / totalPainPoints).toFixed(1) : "0.0";
  const uniqueMarketsCount = uniqueNiches.length > 1 ? uniqueNiches.length - 1 : 0;
  const reportsCount = reportsData.length;

  return (
    <main className="flex min-h-screen flex-col items-center p-8 md:p-24 bg-background relative">
      {/* Header */}
      <div className="w-full max-w-6xl flex justify-between items-center mb-16 relative z-10">
        <div className="text-xl font-bold tracking-tighter text-white flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-brand"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
          Market<span className="text-brand">Hunter</span>
        </div>
        <div className="flex items-center gap-4 text-sm font-mono text-gray-500">
          <Show when="signed-out">
            <SignInButton mode="modal">
              <button className="bg-brand/10 text-brand border border-brand/30 hover:bg-brand hover:text-black transition-all px-4 py-1.5 rounded-lg font-medium cursor-pointer">
                Login
              </button>
            </SignInButton>
          </Show>
          <Show when="signed-in">
            <div className="flex items-center gap-3">
              <UserButton appearance={{ elements: { avatarBox: "w-8 h-8 rounded-lg border border-brand/30" } }} />
            </div>
          </Show>
        </div>
      </div>

      {/* Search Engine */}
      <div className={`w-full max-w-3xl transition-all duration-700 ease-in-out relative z-10 ${hasSearched ? "mt-0 mb-12" : "mt-32"}`}>
        {!hasSearched && (
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-semibold tracking-tight mb-4 text-white">
              Market Intelligence Engine
            </h1>
            <p className="text-gray-400 text-lg">Study your environment and launch your venture intelligently.</p>
          </div>
        )}

        <form onSubmit={handleSearch} className="relative group">
          <div className="absolute -inset-0.5 bg-brand rounded-xl blur opacity-10 group-hover:opacity-20 transition duration-500"></div>
          <div className="relative flex flex-col bg-[#111] border border-border-subtle rounded-xl p-4 backdrop-blur-md gap-4">
            
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <label className="text-xs font-bold text-gray-400 mb-1 block">Target Industry <span className="font-normal text-gray-500">(Who are they?)</span></label>
                <input
                  type="text"
                  value={targetIndustry}
                  onChange={(e) => setTargetIndustry(e.target.value)}
                  placeholder="e.g. Dentistry, Real Estate"
                  className="w-full bg-[#1a1a1c] border border-white/10 rounded-lg outline-none text-sm py-3 px-4 text-white placeholder-gray-600 focus:border-brand/50 transition-colors"
                  disabled={isRunning}
                  required
                />
              </div>
              
              <div className="flex-1">
                <label className="text-xs font-bold text-gray-400 mb-1 block">Business Process <span className="font-normal text-gray-500">(What are they doing?)</span></label>
                <input
                  type="text"
                  value={businessProcess}
                  onChange={(e) => setBusinessProcess(e.target.value)}
                  placeholder="e.g. Payroll, Client Onboarding"
                  className="w-full bg-[#1a1a1c] border border-white/10 rounded-lg outline-none text-sm py-3 px-4 text-white placeholder-gray-600 focus:border-brand/50 transition-colors"
                  disabled={isRunning}
                  required
                />
              </div>
            </div>

            <div className="flex flex-col md:flex-row gap-4 items-end">
              <div className="flex-1 w-full">
                <label className="text-xs font-bold text-gray-400 mb-1 block">Competitors <span className="font-normal text-gray-500">(Scrapes G2/Capterra for weaknesses - Optional)</span></label>
                <input
                  type="text"
                  value={competitors}
                  onChange={(e) => setCompetitors(e.target.value)}
                  placeholder="e.g. Salesforce, Hubspot (comma separated)"
                  className="w-full bg-[#1a1a1c] border border-white/10 rounded-lg outline-none text-sm py-3 px-4 text-white placeholder-gray-600 focus:border-brand/50 transition-colors"
                  disabled={isRunning}
                />
              </div>

              <button
                type="submit"
                disabled={isRunning || !targetIndustry || !businessProcess}
                className="w-full md:w-[30%] bg-white text-black hover:bg-gray-200 transition-colors px-6 py-3 rounded-lg font-bold disabled:opacity-50 cursor-pointer text-sm h-[46px] flex items-center justify-center"
              >
                {isRunning ? "Processing..." : "Run Analysis"}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Loading Terminal */}
      {isRunning && (
        <div className="w-full max-w-3xl p-6 rounded-xl bg-panel border border-border-subtle font-mono text-sm shadow-[0_0_30px_rgba(0,255,65,0.05)] relative z-10">
          <div className="flex items-center gap-2 mb-4 border-b border-border-subtle pb-4">
            <span className="text-brand animate-pulse">Running AI Pipeline...</span>
          </div>
          <div className="flex items-center gap-3 text-gray-400">
            <span className="text-brand">➜</span>
            <span>{scanStatus.data?.info || "Connecting..."}</span>
          </div>
        </div>
      )}

      {/* Error Terminal */}
      {hasFailed && (
        <div className="w-full max-w-3xl p-6 rounded-xl bg-panel border border-red-500/50 text-center">
          <h2 className="text-2xl font-bold text-red-500 mb-2">Error</h2>
          <p className="text-gray-300 font-mono text-sm">{scanStatus.data?.info}</p>
          <button onClick={() => setActiveTaskId(null)} className="mt-4 bg-red-500/10 text-red-500 px-4 py-2 rounded-lg">Close</button>
        </div>
      )}

      {/* Phase 1 Validation Preview */}
      {scanPreview.data && isPhase1Finished && (
        <div className="w-full max-w-3xl p-8 rounded-xl bg-[#111] border border-border-subtle shadow-xl relative z-10 text-center">
          {scanPreview.data.phase === "failed_no_data" ? (
            <div>
              <h2 className="text-2xl font-bold text-red-500 mb-2">Dry Ground</h2>
              <p className="text-gray-400 mb-6">Not enough valid complaints found.</p>
              <button onClick={() => { setActiveTaskId(null); setActiveScanJobId(null); setTargetIndustry(""); setBusinessProcess(""); }} className="bg-white text-black px-6 py-2 rounded-lg font-bold">New Search</button>
            </div>
          ) : (
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Extraction Complete</h2>
              <p className="text-gray-400 mb-8">Found <span className="text-brand font-bold">{scanPreview.data.pain_points_extracted}</span> valid complaints in <span className="text-white">{scanPreview.data.posts_found}</span> posts.</p>
              
                <div className="flex gap-4 mt-4">
                  <button onClick={() => { setActiveTaskId(null); setActiveScanJobId(null); }} className="px-4 py-2 text-gray-400 hover:text-white">Cancel</button>
                  <button 
                    onClick={() => analyzeScan.mutate()}
                    disabled={analyzeScan.isPending}
                    className="bg-brand text-black px-6 py-2 rounded-lg font-bold hover:bg-brand/90 disabled:opacity-50"
                  >
                    {analyzeScan.isPending ? "Running..." : "Run Analytics"}
                  </button>
                </div>
              </div>
          )}
        </div>
      )}

      {/* Main Results / History View */}
      {!isRunning && !isPhase1Finished && clustersQuery.data && (
        <div className="w-full max-w-6xl animate-in fade-in relative z-10 mt-8">
          
          {/* KPI Dashboard */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-panel border border-border-subtle p-5 rounded-xl">
              <div className="text-gray-500 text-xs font-mono uppercase tracking-wider mb-2">Markets Analyzed</div>
              <div className="text-3xl font-bold text-white">{uniqueMarketsCount}</div>
            </div>
            <div className="bg-panel border border-border-subtle p-5 rounded-xl">
              <div className="text-gray-500 text-xs font-mono uppercase tracking-wider mb-2">Frictions Extracted</div>
              <div className="text-3xl font-bold text-white">{totalPainPoints}</div>
            </div>
            <div className="bg-panel border border-border-subtle p-5 rounded-xl">
              <div className="text-gray-500 text-xs font-mono uppercase tracking-wider mb-2">Global Heat (Severity)</div>
              <div className="text-3xl font-bold text-brand">{globalSeverity} <span className="text-lg text-gray-600">/ 10</span></div>
            </div>
            <div className="bg-panel border border-border-subtle p-5 rounded-xl">
              <div className="text-gray-500 text-xs font-mono uppercase tracking-wider mb-2">Validation Reports</div>
              <div className="text-3xl font-bold text-white">{reportsCount}</div>
            </div>
          </div>

          <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 border-b border-border-subtle pb-4">
            {/* Tabs */}
            <div className="flex gap-2 p-1 bg-[#111] border border-border-subtle rounded-lg">
              <button onClick={() => setActiveTab("clusters")} className={`px-4 py-2 rounded-md font-bold text-sm ${activeTab === "clusters" ? "bg-white text-black" : "text-gray-400 hover:text-white"}`}>📊 Market Analytics</button>
              <button onClick={() => setActiveTab("reports")} className={`px-4 py-2 rounded-md font-bold text-sm ${activeTab === "reports" ? "bg-brand text-black" : "text-gray-400 hover:text-white"}`}>📑 Validation Reports</button>
            </div>
            
            <div className="flex items-center gap-4 mt-4 md:mt-0">
              {/* Niche Filter */}
              <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide border-r border-border-subtle pr-4">
                {uniqueNiches.map(niche => (
                  <button
                    key={niche as string}
                    onClick={() => setSelectedNiche(niche as string)}
                    className={`px-3 py-1.5 rounded-md font-medium text-xs whitespace-nowrap border ${
                      selectedNiche === niche ? "bg-white/10 text-white border-white/20" : "bg-transparent text-gray-500 border-transparent hover:text-gray-300"
                    }`}
                  >
                    {niche as string}
                  </button>
                ))}
              </div>
              
              {/* Bulk Actions Menu (Danger Zone) */}
              <div className="flex items-center gap-2">
                 <button 
                  onClick={() => {
                    if(confirm("Are you sure you want to clear ALL generated startups? This action cannot be undone.")) {
                      deleteAllreports.mutate();
                    }
                  }}
                  className="p-2 text-gray-500 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-colors flex items-center gap-2"
                  title="Clear all generated startups"
                >
                  <Trash2 size={16} /> <span className="text-xs font-bold hidden lg:block">Clear Reports</span>
                </button>
                
                <button 
                  onClick={() => {
                    if(confirm("Are you sure you want to delete ALL pain points, clusters and historical data? Your account will be reset.")) {
                      deleteAllPainPoints.mutate();
                    }
                  }}
                  className="p-2 text-gray-500 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-colors flex items-center gap-2"
                  title="Clear all pain points (Reset data)"
                >
                  <Trash2 size={16} /> <span className="text-xs font-bold hidden lg:block">Clear Data</span>
                </button>
              </div>
            </div>
          </div>

          {activeTab === "clusters" && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {selectedClusters.length === 0 ? (
                <p className="col-span-full text-center text-gray-500 py-12">No data found.</p>
              ) : (
                selectedClusters.map((cluster) => (
                  <div key={cluster.id} onClick={() => setSelectedCluster(cluster)} className="cursor-pointer">
                    <ClusterCard 
                      cluster={cluster} 
                      onGenerate={(id: string) => {
                        generateReport.mutate(id);
                      }}
                      isGenerating={generateReport.isPending}
                    />
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === "reports" && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {selectedReports.length === 0 ? (
                <p className="col-span-full text-center text-gray-500 py-12">No reports generated yet.</p>
              ) : (
                selectedReports.map((report) => (
                  <ValidationReportCard 
                    key={report.id} 
                    report={report} 
                    onClick={() => setSelectedReport(report)}
                    onDelete={(id: string) => deleteReport.mutate(id)}
                    isDeleting={deleteReport.isPending}
                  />
                ))
              )}
            </div>
          )}
        </div>
      )}

      {/* Modals */}
      {selectedCluster && (
        <ClusterModal 
          cluster={selectedCluster} 
          onClose={() => setSelectedCluster(null)}
          onGenerate={(id: string) => {
            generateReport.mutate(id);
          }}
          isGenerating={generateReport.isPending}
        />
      )}

      {selectedReport && (
        <ValidationReportModal 
          report={selectedReport} 
          onClose={() => setSelectedReport(null)}
          onDelete={(id: string) => deleteReport.mutate(id)}
        />
      )}
    </main>
  );
}

