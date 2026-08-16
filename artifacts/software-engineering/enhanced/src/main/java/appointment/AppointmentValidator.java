package appointment;

import java.time.Clock;
import java.util.Date;
import java.util.Objects;

/** Centralizes all Appointment business rules for consistent validation. */
public final class AppointmentValidator {
    public static final int MAX_ID_LENGTH = 10;
    public static final int MAX_DESCRIPTION_LENGTH = 50;

    private final Clock clock;

    public AppointmentValidator(Clock clock) {
        this.clock = Objects.requireNonNull(clock, "clock");
    }

    public String normalizeId(String id) {
        if (id == null || id.trim().isEmpty() || id.trim().length() > MAX_ID_LENGTH) {
            throw new AppointmentValidationException("Appointment ID must contain 1 to 10 characters.");
        }
        return id.trim();
    }

    public String normalizeDescription(String description) {
        if (description == null || description.trim().isEmpty()
                || description.trim().length() > MAX_DESCRIPTION_LENGTH) {
            throw new AppointmentValidationException("Description must contain 1 to 50 characters.");
        }
        return description.trim();
    }

    public Date validateDate(Date date) {
        if (date == null) {
            throw new AppointmentValidationException("Appointment date is required.");
        }
        Date copy = new Date(date.getTime());
        if (copy.toInstant().isBefore(clock.instant())) {
            throw new AppointmentValidationException("Appointment date cannot be in the past.");
        }
        return copy;
    }
}
