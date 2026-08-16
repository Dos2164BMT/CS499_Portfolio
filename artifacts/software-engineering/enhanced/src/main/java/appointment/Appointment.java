package appointment;

import java.util.Date;
import java.util.Objects;

/** Immutable appointment value object with defensive Date copies. */
public final class Appointment {
    private final String appointmentId;
    private final Date appointmentDate;
    private final String description;

    public Appointment(String appointmentId, Date appointmentDate, String description,
                       AppointmentValidator validator) {
        Objects.requireNonNull(validator, "validator");
        this.appointmentId = validator.normalizeId(appointmentId);
        this.appointmentDate = validator.validateDate(appointmentDate);
        this.description = validator.normalizeDescription(description);
    }

    public String getAppointmentId() {
        return appointmentId;
    }

    public Date getAppointmentDate() {
        return new Date(appointmentDate.getTime());
    }

    public String getDescription() {
        return description;
    }
}
