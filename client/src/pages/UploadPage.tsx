import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { CloudUpload, FileText, X } from 'lucide-react';
import { useResume } from '../hooks/useResume';

export default function UploadPage() {
  const navigate = useNavigate();
  const { uploadResume, isUploading, uploadProgress, error } = useResume();
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (['application/pdf', 'image/jpeg', 'image/png', 'image/webp'].includes(file.type) || 
          /\.(pdf|jpg|jpeg|png|webp)$/i.test(file.name)) {
        setSelectedFile(file);
      } else {
        alert("Please upload a PDF or Image (JPG/PNG) file.");
      }
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleStartAnalysis = async () => {
    if (!selectedFile) return;
    try {
      const resume = await uploadResume(selectedFile);
      navigate(`/workspace/analysis/overview?id=${resume.id}`);
    } catch (err) {
      console.error("Upload failed", err);
    }
  };

  return (
    <div className="min-h-screen bg-cream p-8 flex flex-col items-center justify-center">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-display font-bold text-text-primary mb-3">Upload Resume</h1>
          <p className="text-text-secondary text-lg">Let's analyze your profile and build your intelligence report.</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-danger-soft border border-danger text-danger rounded-xl text-sm font-medium">
            {error}
          </div>
        )}

        <div 
          className={`relative bg-surface rounded-3xl border-2 border-dashed p-12 text-center transition-all duration-300 ${
            dragActive ? 'border-accent bg-accent-soft/50' : 'border-border hover:border-accent/50 hover:bg-subtle'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png,.webp"
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={isUploading}
          />
          
          <div className="flex flex-col items-center pointer-events-none">
            <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-6 transition-colors duration-300 ${
              dragActive ? 'bg-accent text-white shadow-lg shadow-accent/20' : 'bg-accent-soft text-accent'
            }`}>
              <CloudUpload size={36} strokeWidth={2.5} />
            </div>
            <h3 className="text-xl font-bold text-text-primary mb-2">
              {dragActive ? 'Drop it here!' : 'Drag & drop your file'}
            </h3>
            <p className="text-text-secondary font-medium">or click to browse from your computer (PDF, JPG, PNG)</p>
          </div>
        </div>

        <AnimatePresence>
          {selectedFile && !isUploading && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-6 bg-surface border border-border p-4 rounded-2xl flex items-center justify-between shadow-sm"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-accent-soft rounded-xl flex items-center justify-center text-accent">
                  <FileText size={20} />
                </div>
                <div>
                  <p className="font-bold text-text-primary text-sm">{selectedFile.name}</p>
                  <p className="text-xs text-text-secondary font-medium">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
              <button 
                onClick={() => setSelectedFile(null)}
                className="p-2 text-text-muted hover:text-danger transition-colors"
              >
                <X size={20} />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {isUploading && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-8 bg-surface border border-border p-6 rounded-2xl shadow-sm"
            >
              <h4 className="font-bold text-text-primary mb-4">Pipeline Status</h4>
              <div className="space-y-4">
                <div className="w-full bg-cream h-3 rounded-full overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${uploadProgress}%` }}
                    className="h-full bg-accent"
                  />
                </div>
                <div className="flex justify-between text-xs font-bold text-text-secondary uppercase tracking-wider">
                  <span className={uploadProgress > 0 ? 'text-accent' : ''}>Extracting</span>
                  <span className={uploadProgress > 30 ? 'text-accent' : ''}>Analyzing</span>
                  <span className={uploadProgress > 60 ? 'text-accent' : ''}>Scoring</span>
                  <span className={uploadProgress > 90 ? 'text-accent' : ''}>Complete</span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {selectedFile && !isUploading && (
          <motion.button
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            onClick={handleStartAnalysis}
            className="w-full mt-6 bg-accent hover:bg-accent/90 text-white py-4 rounded-xl font-bold text-lg transition-colors shadow-md hover:shadow-lg"
          >
            Start Intelligence Pipeline
          </motion.button>
        )}
      </div>
    </div>
  );
}
