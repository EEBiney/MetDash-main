import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { base44 } from '@/api/base44Client';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Grid3X3, BarChart3, Circle, Plus, Database, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { createPageUrl } from '@/utils';

import FileUploader from '@/components/analysis/FileUploader';
import MetaboliteCleanup from '@/components/analysis/MetaboliteCleanup';
import DatasetSelector from '@/components/analysis/DatasetSelector';
import DataSummary from '@/components/analysis/DataSummary';
import HeatmapChart from '@/components/analysis/HeatmapChart';
import BoxplotChart from '@/components/analysis/BoxplotChart';
import ScatterPlotChart from '@/components/analysis/ScatterPlotChart';

export default function Dashboard() {
  const [selectedDatasetId, setSelectedDatasetId] = useState(null);
  const [uploadSheetOpen, setUploadSheetOpen] = useState(false);
  const [cleanupSheetOpen, setCleanupSheetOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data: datasets, isLoading } = useQuery({
    queryKey: ['datasets'],
    queryFn: () => base44.entities.AnalysisData.list('-created_date', 50),
  });

  const selectedDataset = datasets?.find(d => d.id === selectedDatasetId);

  const handleUploadSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['datasets'] });
    setUploadSheetOpen(false);
  };

  const handleCleanupComplete = async (cleanupResult) => {
    // Save cleaned data to database
    await base44.entities.AnalysisData.create({
      name: `Cleaned Metabolite Data - ${new Date().toLocaleDateString()}`,
      description: cleanupResult.message,
      file_url: cleanupResult.cleaned_data_url,
      data_type: 'metabolite',
      row_count: cleanupResult.row_count,
      column_count: cleanupResult.column_count,
      columns: cleanupResult.columns,
      parsed_data: cleanupResult.cleaned_data
    });
    
    queryClient.invalidateQueries({ queryKey: ['datasets'] });
    setCleanupSheetOpen(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-white/70 border-b border-slate-200/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800">MetaboViz</h1>
                <p className="text-xs text-slate-500 -mt-0.5">Metabolite Analysis Dashboard</p>
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button 
                asChild
                className="bg-purple-600 hover:bg-purple-700 shadow-lg shadow-purple-500/25"
              >
                <a href={createPageUrl('CleanupComparison')}>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Cleanup Data
                </a>
              </Button>

              <Sheet open={uploadSheetOpen} onOpenChange={setUploadSheetOpen}>
                <SheetTrigger asChild>
                  <Button className="bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-500/25">
                    <Plus className="w-4 h-4 mr-2" />
                    Upload Data
                  </Button>
                </SheetTrigger>
                <SheetContent className="w-full sm:max-w-lg">
                  <SheetHeader>
                    <SheetTitle className="text-xl">Upload Dataset</SheetTitle>
                  </SheetHeader>
                  <div className="mt-6">
                    <FileUploader onUploadSuccess={handleUploadSuccess} />
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Dataset Selector */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-slate-400" />
              <span className="text-sm font-medium text-slate-600">Active Dataset</span>
            </div>
            <DatasetSelector
              datasets={datasets}
              selectedId={selectedDatasetId}
              onSelect={setSelectedDatasetId}
              isLoading={isLoading}
            />
          </div>
          
          <DataSummary dataset={selectedDataset} />
        </motion.div>

        {/* Visualizations */}
        {selectedDataset && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Tabs defaultValue="heatmap" className="space-y-6">
              <TabsList className="bg-white/80 backdrop-blur border border-slate-200 p-1 rounded-xl shadow-sm">
                <TabsTrigger 
                  value="heatmap"
                  className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white rounded-lg px-4 py-2 transition-all"
                >
                  <Grid3X3 className="w-4 h-4 mr-2" />
                  Heatmap
                </TabsTrigger>
                <TabsTrigger 
                  value="boxplot"
                  className="data-[state=active]:bg-teal-500 data-[state=active]:text-white rounded-lg px-4 py-2 transition-all"
                >
                  <BarChart3 className="w-4 h-4 mr-2" />
                  Boxplot
                </TabsTrigger>
                <TabsTrigger 
                  value="scatter"
                  className="data-[state=active]:bg-orange-500 data-[state=active]:text-white rounded-lg px-4 py-2 transition-all"
                >
                  <Circle className="w-4 h-4 mr-2" />
                  Scatter
                </TabsTrigger>
              </TabsList>

              <TabsContent value="heatmap" className="mt-6">
                <HeatmapChart 
                  data={selectedDataset.parsed_data} 
                  columns={selectedDataset.columns} 
                />
              </TabsContent>

              <TabsContent value="boxplot" className="mt-6">
                <BoxplotChart 
                  data={selectedDataset.parsed_data} 
                  columns={selectedDataset.columns} 
                />
              </TabsContent>

              <TabsContent value="scatter" className="mt-6">
                <ScatterPlotChart 
                  data={selectedDataset.parsed_data} 
                  columns={selectedDataset.columns} 
                />
              </TabsContent>
            </Tabs>
          </motion.div>
        )}

        {/* Empty State */}
        {!selectedDataset && !isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20"
          >
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center mx-auto mb-6">
              <Database className="w-12 h-12 text-indigo-400" />
            </div>
            <h2 className="text-2xl font-semibold text-slate-700 mb-2">Get Started</h2>
            <p className="text-slate-500 mb-6 max-w-md mx-auto">
              Upload a CSV file with your metabolite data to explore interactive visualizations
            </p>
            <Button 
              onClick={() => setUploadSheetOpen(true)}
              className="bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-500/25"
            >
              <Plus className="w-4 h-4 mr-2" />
              Upload Your First Dataset
            </Button>
          </motion.div>
        )}
      </main>
    </div>
  );
}