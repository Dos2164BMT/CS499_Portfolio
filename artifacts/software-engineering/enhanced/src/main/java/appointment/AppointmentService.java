package appointment;

import java.time.Clock;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Objects;

/** Coordinates appointment creation, retrieval, update, and deletion. */
public final class AppointmentService {
    private final List<Appointment> appointments = new ArrayList<>();
    private final AppointmentValidator validator;
    private long nextId = 1;

    public AppointmentService() {
        this(Clock.systemUTC());
    }

    public AppointmentService(Clock clock) {
        validator = new AppointmentValidator(clock);
    }

    public Appointment createAppointment(Date date, String description) {
        String id = Long.toString(nextId++);
        Appointment appointment = new Appointment(id, date, description, validator);
        appointments.add(appointment);
        return appointment;
    }

    public Appointment addAppointment(String id, Date date, String description) {
        String normalizedId = validator.normalizeId(id);
        if (getAppointment(normalizedId) != null) {
            throw new AppointmentValidationException("Appointment ID must be unique.");
        }
        Appointment appointment = new Appointment(normalizedId, date, description, validator);
        appointments.add(appointment);
        return appointment;
    }

    /** Backward-compatible nullable lookup. */
    public Appointment getAppointment(String id) {
        if (id == null) {
            return null;
        }
        String normalizedId = id.trim();
        return appointments.stream()
                .filter(item -> item.getAppointmentId().equals(normalizedId))
                .findFirst()
                .orElse(null);
    }

    public Appointment requireAppointment(String id) {
        Appointment appointment = getAppointment(id);
        if (appointment == null) {
            throw new AppointmentNotFoundException(String.valueOf(id));
        }
        return appointment;
    }

    public Appointment updateAppointment(String id, Date date, String description) {
        Appointment current = requireAppointment(id);
        Appointment replacement = new Appointment(
                current.getAppointmentId(), date, description, validator);
        appointments.set(appointments.indexOf(current), replacement);
        return replacement;
    }

    public void deleteAppointment(String id) {
        Appointment appointment = requireAppointment(id);
        appointments.remove(appointment);
    }

    public List<Appointment> snapshot() {
        return Collections.unmodifiableList(new ArrayList<>(appointments));
    }

    public int size() {
        return appointments.size();
    }
}
