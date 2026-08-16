package appointment;

import static org.junit.jupiter.api.Assertions.*;

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Date;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class AppointmentServiceTest {
    private static final Instant NOW = Instant.parse("2026-07-01T12:00:00Z");
    private AppointmentService service;

    @BeforeEach
    void setUp() {
        service = new AppointmentService(Clock.fixed(NOW, ZoneOffset.UTC));
    }

    @Test void createsSequentialAppointments() {
        assertEquals("1", service.createAppointment(future(), "Review").getAppointmentId());
        assertEquals("2", service.createAppointment(future(), "Deploy").getAppointmentId());
    }

    @Test void normalizesInput() {
        Appointment item = service.addAppointment(" ABC ", future(), " Review ");
        assertEquals("ABC", item.getAppointmentId());
        assertEquals("Review", item.getDescription());
    }

    @Test void rejectsBlankAndOversizedValues() {
        assertThrows(AppointmentValidationException.class,
                () -> service.addAppointment(" ", future(), "Review"));
        assertThrows(AppointmentValidationException.class,
                () -> service.addAppointment("12345678901", future(), "Review"));
        assertThrows(AppointmentValidationException.class,
                () -> service.addAppointment("A", future(), " "));
    }

    @Test void acceptsCurrentInstantAndRejectsPast() {
        assertDoesNotThrow(() -> service.addAppointment("A", Date.from(NOW), "Review"));
        assertThrows(AppointmentValidationException.class,
                () -> service.addAppointment("B", Date.from(NOW.minusSeconds(1)), "Review"));
    }

    @Test void protectsStoredDate() {
        Date supplied = future();
        Appointment item = service.addAppointment("A", supplied, "Review");
        supplied.setTime(0);
        Date returned = item.getAppointmentDate();
        returned.setTime(0);
        assertEquals(Date.from(NOW.plusSeconds(3600)), item.getAppointmentDate());
    }

    @Test void updatesWhilePreservingId() {
        service.addAppointment("A", future(), "Review");
        Appointment updated = service.updateAppointment("A", later(), "Deploy");
        assertEquals("A", updated.getAppointmentId());
        assertEquals("Deploy", updated.getDescription());
    }

    @Test void deleteAndRequireReportMissingRecords() {
        assertThrows(AppointmentNotFoundException.class, () -> service.deleteAppointment("missing"));
        service.addAppointment("A", future(), "Review");
        service.deleteAppointment("A");
        assertEquals(0, service.size());
    }

    @Test void nullableLookupRemainsCompatible() {
        assertNull(service.getAppointment("missing"));
    }

    @Test void duplicateIdsAreRejected() {
        service.addAppointment("A", future(), "Review");
        assertThrows(AppointmentValidationException.class,
                () -> service.addAppointment("A", later(), "Deploy"));
    }

    @Test void snapshotCannotBeModified() {
        service.addAppointment("A", future(), "Review");
        assertThrows(UnsupportedOperationException.class, () -> service.snapshot().clear());
        assertEquals(1, service.size());
    }

    @Test void exactDocumentedLimitsAreAccepted() {
        assertDoesNotThrow(() -> service.addAppointment(
                "1234567890", future(), "x".repeat(50)));
    }

    private Date future() { return Date.from(NOW.plusSeconds(3600)); }
    private Date later() { return Date.from(NOW.plusSeconds(7200)); }
}
