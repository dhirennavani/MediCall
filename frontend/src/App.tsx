import React, { useState } from 'react';
import InsuranceUpload from './components/InsuranceUpload';
import AppointmentDetails from './components/AppointmentDetails';

interface AppointmentDetailsData {
    doctor_name: string;
    specialty: string;
    location: string;
    address: string;
    appointment_time: string;
    notes: string;
}

function App() {
  const [appointmentDetails, setAppointmentDetails] = useState<AppointmentDetailsData | null>(null);
  const [currentView, setCurrentView] = useState<'upload' | 'results'>('upload');

  const handleBookingComplete = (details: AppointmentDetailsData) => {
    setAppointmentDetails(details);
    setCurrentView('results');
  };

  const handleBackToUpload = () => {
    setCurrentView('upload');
    setAppointmentDetails(null);
  };

  return (
    <div className="min-h-screen">
      {currentView === 'upload' ? (
        <InsuranceUpload onBookingComplete={handleBookingComplete} />
      ) : (
        appointmentDetails && (
          <AppointmentDetails 
            details={appointmentDetails} 
            onBack={handleBackToUpload}
          />
        )
      )}
    </div>
  );
}

export default App;