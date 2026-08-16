package appointment;

/** Signals that a requested appointment does not exist. */
public final class AppointmentNotFoundException extends RuntimeException {
    public AppointmentNotFoundException(String appointmentId) {
        super("Appointment not found: " + appointmentId);
    }
}
