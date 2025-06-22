import React from 'react';
import { ArrowLeft, Calendar, Clock, MapPin, User, Info } from 'lucide-react';

interface AppointmentDetailsData {
    doctor_name: string;
    specialty: string;
    location: string;
    address: string;
    appointment_time: string;
    notes: string;
}

interface AppointmentDetailsProps {
  details: AppointmentDetailsData;
  onBack: () => void;
}

export default function AppointmentDetails({ details, onBack }: AppointmentDetailsProps) {
  const appointmentDate = new Date(details.appointment_time);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-6">
      <div className="max-w-2xl w-full bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
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
        
        <div className="space-y-6 text-white">
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

      </div>
    </div>
  );
}