import React, { useCallback, useState } from 'react';
import { Upload, FileText, CheckCircle, Camera, ArrowRight } from 'lucide-react';

interface InsuranceUploadProps {
  onUploadComplete: (file: File) => void;
}

export default function InsuranceUpload({ onUploadComplete }: InsuranceUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, []);

  const handleFileUpload = async (file: File) => {
    setUploadedFile(file);
    setIsProcessing(true);
    
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setIsProcessing(false);
    onUploadComplete(file);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-6">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-teal-500 rounded-full mb-6">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">
            Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-teal-400">MediCall AI</span>
          </h1>
          <p className="text-slate-300 text-lg leading-relaxed">
            Your personal healthcare appointment assistant. Upload your insurance card to get started.
          </p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
          {!uploadedFile ? (
            <>
              <div
                className={`relative border-2 border-dashed rounded-xl p-12 transition-all duration-300 ${
                  isDragOver
                    ? 'border-blue-400 bg-blue-500/10'
                    : 'border-slate-600 bg-slate-800/30 hover:border-slate-500 hover:bg-slate-800/50'
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <div className="text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-slate-700 rounded-full mb-6">
                    <Upload className="w-8 h-8 text-slate-300" />
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">
                    Upload Your Insurance Card
                  </h3>
                  <p className="text-slate-400 mb-6">
                    Drag and drop your insurance card image, or click to browse
                  </p>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileInput}
                    className="hidden"
                    id="file-input"
                  />
                  <label
                    htmlFor="file-input"
                    className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-500 to-teal-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-teal-600 transition-all duration-300 cursor-pointer"
                  >
                    <Camera className="w-5 h-5 mr-2" />
                    Choose File
                  </label>
                </div>
              </div>
              
              <div className="mt-6 text-center">
                <p className="text-sm text-slate-400">
                  Supported formats: JPG, PNG, WEBP • Max size: 10MB
                </p>
              </div>
            </>
          ) : (
            <div className="text-center">
              {isProcessing ? (
                <div className="space-y-6">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-500 rounded-full">
                    <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">
                      Processing Your Insurance Card
                    </h3>
                    <p className="text-slate-400">
                      Our AI is extracting your insurance information...
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-green-500 rounded-full">
                    <CheckCircle className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">
                      Insurance Card Processed Successfully!
                    </h3>
                    <p className="text-slate-400 mb-6">
                      We've extracted your insurance details. Ready to book your appointment?
                    </p>
                    <div className="bg-slate-700/50 rounded-lg p-4 mb-6">
                      <p className="text-sm text-slate-300">
                        <span className="font-medium">File:</span> {uploadedFile.name}
                      </p>
                    </div>
                    <button
                      onClick={() => onUploadComplete(uploadedFile)}
                      className="inline-flex items-center px-8 py-3 bg-gradient-to-r from-blue-500 to-teal-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-teal-600 transition-all duration-300"
                    >
                      Start Booking
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        
        <div className="mt-8 text-center">
          <p className="text-slate-500 text-sm">
            Your insurance information is processed securely and never stored permanently
          </p>
        </div>
      </div>
    </div>
  );
}