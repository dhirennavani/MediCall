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
    available_doctors?: Array<{
        title: string;
        phone: string;
        address: string;
        website: string;
    }>;
}

interface InsuranceDetailsData {
    member_id: string;
    group_number?: string;
    insured_name: string;
    dependent_name?: string;
    insurance_company: string;
    plan_type?: string;
    customer_service_number?: string;
    rx_bin?: string;
    rx_pcn?: string;
}

interface CallResultData {
    status: string;
    message: string;
    appointment_date?: string;
    confirmation_number?: string;
    call_time: string;
    phone_number: string;
    follow_up_needed?: boolean;
    retry_scheduled?: boolean;
    waiting_list_position?: number;
}

function App() {
  const [appointmentDetails, setAppointmentDetails] = useState<AppointmentDetailsData | null>(null);
  const [insuranceDetails, setInsuranceDetails] = useState<InsuranceDetailsData | null>(null);
  const [callResult, setCallResult] = useState<CallResultData | null>(null);
  const [currentView, setCurrentView] = useState<'upload' | 'results'>('upload');

  const handleBookingComplete = (details: AppointmentDetailsData, insurance?: InsuranceDetailsData, call?: CallResultData) => {
    setAppointmentDetails(details);
    setInsuranceDetails(insurance || null);
    setCallResult(call || null);
    setCurrentView('results');
  };

  const handleBackToUpload = () => {
    setCurrentView('upload');
    setAppointmentDetails(null);
    setInsuranceDetails(null);
    setCallResult(null);
  };

  return (
    <div className="min-h-screen">
      {currentView === 'upload' ? (
        <InsuranceUpload onBookingComplete={handleBookingComplete} />
      ) : (
        appointmentDetails && (
          <AppointmentDetails 
            details={appointmentDetails}
            insuranceDetails={insuranceDetails}
            callResult={callResult}
            onBack={handleBackToUpload}
          />
        )
      )}
    </div>
  );
}

export default App;
