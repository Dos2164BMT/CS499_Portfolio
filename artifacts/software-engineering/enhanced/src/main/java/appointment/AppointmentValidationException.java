package appointment;

/** Signals that appointment input violates a documented business rule. */
public final class AppointmentValidationException extends IllegalArgumentException {
    public AppointmentValidationException(String message) {
        super(message);
    }
}
