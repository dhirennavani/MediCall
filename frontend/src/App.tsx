import React, { useState } from 'react';
import InsuranceUpload from './components/InsuranceUpload';
import ChatInterface from './components/ChatInterface';

function App() {
  const [insuranceFile, setInsuranceFile] = useState<File | null>(null);
  const [currentView, setCurrentView] = useState<'upload' | 'chat'>('upload');

  const handleUploadComplete = (file: File) => {
    setInsuranceFile(file);
    setTimeout(() => {
      setCurrentView('chat');
    }, 500);
  };

  const handleBackToUpload = () => {
    setCurrentView('upload');
    setInsuranceFile(null);
  };

  return (
    <div className="min-h-screen">
      {currentView === 'upload' ? (
        <InsuranceUpload onUploadComplete={handleUploadComplete} />
      ) : (
        insuranceFile && (
          <ChatInterface 
            insuranceFile={insuranceFile} 
            onBack={handleBackToUpload}
          />
        )
      )}
    </div>
  );
}

export default App;