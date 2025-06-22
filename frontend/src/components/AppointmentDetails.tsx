import React from 'react';
import { ArrowLeft, Calendar, Clock, MapPin, User, Info, CreditCard, Phone } from 'lucide-react';

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

interface AppointmentDetailsProps {
  details: AppointmentDetailsData;
  insuranceDetails?: InsuranceDetailsData | null;
  callResult?: CallResultData | null;
  onBack: () => void;
}

export default function AppointmentDetails({ details, insuranceDetails, callResult, onBack }: AppointmentDetailsProps) {
  const appointmentDate = new Date(details.appointment_time);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-6">
      <div className="max-w-4xl w-full bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
        <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-white">
                Appointment Details
            </h1>
            <button
                onClick={onBack}
                className="inline-flex items-center text-slate-300 hover:text-white transition-colors"
            >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Book Another
            </button>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Appointment Information */}
          <div className="space-y-6 text-white">
            <h2 className="text-xl font-semibold text-blue-400 mb-4">Appointment Information</h2>
            
            <div className="flex items-start space-x-4">
                <User className="w-6 h-6 text-blue-400 mt-1" />
                <div>
                    <p className="text-slate-400">Doctor</p>
                    <p className="text-lg font-semibold">{details.doctor_name} ({details.specialty})</p>
                </div>
            </div>
            
            <div className="flex items-start space-x-4">
                <MapPin className="w-6 h-6 text-blue-400 mt-1" />
                <div>
                    <p className="text-slate-400">Location</p>
                    <p className="text-lg font-semibold">{details.address}, {details.location}</p>
                </div>
            </div>
            
            <div className="flex items-start space-x-4">
                <Calendar className="w-6 h-6 text-blue-400 mt-1" />
                <div>
                    <p className="text-slate-400">Date</p>
                    <p className="text-lg font-semibold">{appointmentDate.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                </div>
            </div>
            
            <div className="flex items-start space-x-4">
                <Clock className="w-6 h-6 text-blue-400 mt-1" />
                <div>
                    <p className="text-slate-400">Time</p>
                    <p className="text-lg font-semibold">{appointmentDate.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}</p>
                </div>
            </div>
            
            <div className="flex items-start space-x-4">
                <Info className="w-6 h-6 text-blue-400 mt-1" />
                <div>
                    <p className="text-slate-400">Notes</p>
                    <p className="text-lg font-semibold">{details.notes}</p>
                </div>
            </div>
          </div>

          {/* Insurance Information */}
          {insuranceDetails && (
            <div className="space-y-6 text-white">
              <h2 className="text-xl font-semibold text-green-400 mb-4">Insurance Information</h2>
              
              <div className="flex items-start space-x-4">
                  <CreditCard className="w-6 h-6 text-green-400 mt-1" />
                  <div>
                      <p className="text-slate-400">Insurance Company</p>
                      <p className="text-lg font-semibold">{insuranceDetails.insurance_company}</p>
                  </div>
              </div>
              
              <div className="flex items-start space-x-4">
                  <User className="w-6 h-6 text-green-400 mt-1" />
                  <div>
                      <p className="text-slate-400">Insured Name</p>
                      <p className="text-lg font-semibold">{insuranceDetails.insured_name}</p>
                  </div>
              </div>
              
              {insuranceDetails.dependent_name && (
                <div className="flex items-start space-x-4">
                    <User className="w-6 h-6 text-green-400 mt-1" />
                    <div>
                        <p className="text-slate-400">Patient Name</p>
                        <p className="text-lg font-semibold">{insuranceDetails.dependent_name}</p>
                    </div>
                </div>
              )}
              
              <div className="flex items-start space-x-4">
                  <CreditCard className="w-6 h-6 text-green-400 mt-1" />
                  <div>
                      <p className="text-slate-400">Member ID</p>
                      <p className="text-lg font-semibold">{insuranceDetails.member_id}</p>
                  </div>
              </div>
              
              {insuranceDetails.group_number && (
                <div className="flex items-start space-x-4">
                    <CreditCard className="w-6 h-6 text-green-400 mt-1" />
                    <div>
                        <p className="text-slate-400">Group Number</p>
                        <p className="text-lg font-semibold">{insuranceDetails.group_number}</p>
                    </div>
                </div>
              )}
              
              {insuranceDetails.plan_type && (
                <div className="flex items-start space-x-4">
                    <CreditCard className="w-6 h-6 text-green-400 mt-1" />
                    <div>
                        <p className="text-slate-400">Plan Type</p>
                        <p className="text-lg font-semibold">{insuranceDetails.plan_type}</p>
                    </div>
                </div>
              )}
              
              {insuranceDetails.customer_service_number && (
                <div className="flex items-start space-x-4">
                    <Phone className="w-6 h-6 text-green-400 mt-1" />
                    <div>
                        <p className="text-slate-400">Customer Service</p>
                        <p className="text-lg font-semibold">{insuranceDetails.customer_service_number}</p>
                    </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Available Doctors Section */}
        {details.available_doctors && details.available_doctors.length > 0 && (
          <div className="mt-8 text-white">
            <h2 className="text-xl font-semibold text-purple-400 mb-4">Other Available Doctors</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {details.available_doctors.slice(1, 4).map((doctor, index) => (
                <div key={index} className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
                  <h3 className="font-semibold text-blue-300">{doctor.title}</h3>
                  <p className="text-sm text-slate-400 mt-1">{doctor.address}</p>
                  {doctor.phone !== 'N/A' && (
                    <p className="text-sm text-slate-400 mt-1">📞 {doctor.phone}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Call Result Section */}
        {callResult && (
          <div className="mt-8 text-white">
            <h2 className="text-xl font-semibold text-orange-400 mb-4">Call Result</h2>
            <div className="bg-slate-700/50 rounded-lg p-6 border border-slate-600">
              <div className="flex items-center space-x-3 mb-4">
                <div className={`w-3 h-3 rounded-full ${
                  callResult.status === 'success' ? 'bg-green-500' :
                  callResult.status === 'voicemail' ? 'bg-yellow-500' :
                  callResult.status === 'busy' ? 'bg-red-500' :
                  'bg-gray-500'
                }`}></div>
                <span className="font-semibold capitalize">{callResult.status}</span>
              </div>
              
              <p className="text-lg mb-4">{callResult.message}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-slate-400">Call Time</p>
                  <p className="font-semibold">{callResult.call_time}</p>
                </div>
                <div>
                  <p className="text-slate-400">Phone Number</p>
                  <p className="font-semibold">{callResult.phone_number}</p>
                </div>
                {callResult.appointment_date && (
                  <div>
                    <p className="text-slate-400">Scheduled Date</p>
                    <p className="font-semibold">{callResult.appointment_date}</p>
                  </div>
                )}
                {callResult.confirmation_number && (
                  <div>
                    <p className="text-slate-400">Confirmation #</p>
                    <p className="font-semibold">{callResult.confirmation_number}</p>
                  </div>
                )}
                {callResult.waiting_list_position && (
                  <div>
                    <p className="text-slate-400">Waiting List Position</p>
                    <p className="font-semibold">#{callResult.waiting_list_position}</p>
                  </div>
                )}
              </div>
              
              {(callResult.follow_up_needed || callResult.retry_scheduled) && (
                <div className="mt-4 p-3 bg-yellow-500/20 border border-yellow-500/30 rounded-lg">
                  <p className="text-yellow-300 text-sm">
                    {callResult.follow_up_needed && "Follow-up call needed"}
                    {callResult.follow_up_needed && callResult.retry_scheduled && " • "}
                    {callResult.retry_scheduled && "Retry scheduled"}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}