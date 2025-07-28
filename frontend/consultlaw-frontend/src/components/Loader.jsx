const [selectedLawyer, setSelectedLawyer] = useState(null);
const [bookingDate, setBookingDate] = useState('');
const [bookingTime, setBookingTime] = useState('');
const [notes, setNotes] = useState('');


export default function Loader() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-indigo-600 border-opacity-50"></div>
    </div>
  );
}
