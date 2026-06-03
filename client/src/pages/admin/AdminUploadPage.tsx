import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CloudUpload, FileText, X, CheckCircle } from 'lucide-react';
import api from '../../lib/api';

export default function AdminUploadPage() {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const MIN_FILES = 1;

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
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/webp'];
      const ALLOWED_EXTS = /\.(pdf|jpg|jpeg|png|webp)$/i;
      const newFiles = Array.from(e.dataTransfer.files).filter(
        file => ALLOWED_TYPES.includes(file.type) || ALLOWED_EXTS.test(file.name)
      );

      if (newFiles.length !== e.dataTransfer.files.length) {
        setError("Some files were skipped. Only PDF and image files (JPG, PNG, WEBP) are allowed.");
      } else {
        setError(null);
      }

      setSelectedFiles(prev => [...prev, ...newFiles]);
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/webp'];
      const ALLOWED_EXTS = /\.(pdf|jpg|jpeg|png|webp)$/i;
      const newFiles = Array.from(e.target.files).filter(
        file => ALLOWED_TYPES.includes(file.type) || ALLOWED_EXTS.test(file.name)
      );
      setSelectedFiles(prev => [...prev, ...newFiles]);
    }
  };

  const removeFile = (indexToRemove: number) => {
    setSelectedFiles(prev => prev.filter((_, idx) => idx !== indexToRemove));
  };

  const handleStartUpload = async () => {
    if (selectedFiles.length < MIN_FILES) return;
    
    setIsUploading(true);
    setError(null);
    setSuccess(false);
    setUploadProgress(0);
    
    let uploadedCount = 0;
    
    try {
      // Upload each file to the backend
      // Using Promise.all with a concurrency limit or just sequentially for now
      for (const file of selectedFiles) {
        const formData = new FormData();
        formData.append("file", file);
        
        await api.post('/resumes/upload', formData, {
          headers: { 'Content-Type': undefined }, // Let axios auto-set multipart/form-data with correct boundary
        });
        
        uploadedCount++;
        setUploadProgress(Math.round((uploadedCount / selectedFiles.length) * 100));
      }
      
      setSuccess(true);
      setSelectedFiles([]);
    } catch (err: any) {
      console.error("Bulk upload failed", err);
      setError(err.response?.data?.detail || "An error occurred during upload. Some files may not have been processed.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="h-full overflow-y-auto bg-cream p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-display font-bold text-text-primary mb-2">Bulk Resume Upload</h1>
          <p className="text-text-secondary text-sm font-medium">
            Upload candidate resumes (PDF or images). They will be processed through the VLM extraction pipeline automatically.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-danger-soft border border-danger text-danger rounded-xl text-sm font-medium">
            {error}
          </div>
        )}
        
        {success && (
          <div className="mb-6 p-4 bg-success/20 border border-success text-success rounded-xl text-sm font-bold flex items-center gap-2">
            <CheckCircle size={18} />
            Successfully uploaded all resumes to the intelligence pipeline!
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
            multiple
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={isUploading}
          />
          
          <div className="flex flex-col items-center pointer-events-none">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-colors duration-300 ${
              dragActive ? 'bg-accent text-white shadow-lg shadow-accent/20' : 'bg-accent-soft text-accent'
            }`}>
              <CloudUpload size={30} strokeWidth={2.5} />
            </div>
            <h3 className="text-xl font-bold text-text-primary mb-2">
              {dragActive ? 'Drop them here!' : 'Drag & drop PDFs or Images'}
            </h3>
            <p className="text-text-secondary text-sm font-medium">or click to browse — PDF, JPG, PNG, WEBP supported</p>
          </div>
        </div>

        <AnimatePresence>
          {selectedFiles.length > 0 && !isUploading && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8"
            >
              <div className="flex justify-between items-end mb-4">
                <h3 className="font-bold text-text-primary">
                  Selected Files ({selectedFiles.length})
                </h3>
                <span className={`text-xs font-bold px-3 py-1 rounded-full border ${selectedFiles.length >= MIN_FILES ? 'bg-success/20 text-success border-success' : 'bg-warning/20 text-warning border-warning'}`}>
                  {selectedFiles.length >= MIN_FILES ? 'Ready to upload' : `Need ${MIN_FILES - selectedFiles.length} more`}
                </span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-64 overflow-y-auto p-2 -mx-2">
                {selectedFiles.map((file, idx) => (
                  <div key={idx} className="bg-surface border border-border p-3 rounded-xl flex items-center justify-between shadow-sm">
                    <div className="flex items-center gap-3 overflow-hidden">
                      <div className="w-8 h-8 flex-none bg-accent-soft rounded-lg flex items-center justify-center text-accent">
                        <FileText size={16} />
                      </div>
                      <div className="truncate">
                        <p className="font-bold text-text-primary text-xs truncate">{file.name}</p>
                        <p className="text-[10px] text-text-secondary font-medium">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                      </div>
                    </div>
                    <button 
                      onClick={() => removeFile(idx)}
                      className="p-1.5 flex-none text-text-muted hover:text-danger hover:bg-danger-soft rounded-md transition-colors"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ))}
              </div>
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
              <h4 className="font-bold text-text-primary mb-4 flex justify-between">
                <span>Uploading Resumes...</span>
                <span className="text-accent">{uploadProgress}%</span>
              </h4>
              <div className="w-full bg-cream h-4 rounded-full overflow-hidden shadow-inner">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: `${uploadProgress}%` }}
                  className="h-full bg-accent"
                />
              </div>
              <p className="text-center text-xs text-text-secondary mt-3 font-medium">
                Please do not close this window. The backend will extract and analyze them in the background.
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {selectedFiles.length > 0 && !isUploading && (
          <motion.button
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            onClick={handleStartUpload}
            disabled={selectedFiles.length < MIN_FILES}
            className={`w-full mt-8 py-4 rounded-xl font-bold text-lg transition-all shadow-md flex justify-center items-center ${
              selectedFiles.length >= MIN_FILES 
                ? 'bg-accent hover:bg-accent/90 text-white hover:shadow-lg' 
                : 'bg-surface border-2 border-border text-text-muted cursor-not-allowed'
            }`}
          >
            Start Bulk Pipeline
          </motion.button>
        )}
      </div>
    </div>
  );
}
