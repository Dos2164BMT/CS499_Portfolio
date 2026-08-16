package Test;

import static org.junit.jupiter.api.Assertions.*;

import java.util.Calendar;
import java.util.Date;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import Appointment.Appointment;

public class AppointmentTest {

    private Date futureDate() {
        Calendar cal = Calendar.getInstance();
        cal.add(Calendar.DAY_OF_MONTH, 1);
        return cal.getTime();
    }

    private Date pastDate() {
        Calendar cal = Calendar.getInstance();
        cal.add(Calendar.DAY_OF_MONTH, -1);
        return cal.getTime();
    }

    @Test
    @DisplayName("Valid appointment should be created")
    public void testValidAppointment() {
        Appointment appointment = new Appointment("1", futureDate(), "Doctor visit");

        assertEquals("1", appointment.getAppointmentID());
        assertEquals("Doctor visit", appointment.getAppointmentDesc());
        assertNotNull(appointment.getAppointmentDate());
    }

    @Test
    @DisplayName("Appointment ID cannot be null")
    public void testNullAppointmentID() {
        assertThrows(IllegalArgumentException.class, () -> {
            new Appointment(null, futureDate(), "Doctor visit");
        });
    }

    @Test
    @DisplayName("Appointment date cannot be null")
    public void testNullAppointmentDate() {
        assertThrows(IllegalArgumentException.class, () -> {
            new Appointment("1", null, "Doctor visit");
        });
    }

    @Test
    @DisplayName("Appointment description cannot be null")
    public void testNullAppointmentDescription() {
        assertThrows(IllegalArgumentException.class, () -> {
            new Appointment("1", futureDate(), null);
        });
    }

    @Test
    @DisplayName("Appointment date cannot be in the past")
    public void testPastAppointmentDate() {
        assertThrows(IllegalArgumentException.class, () -> {
            new Appointment("1", pastDate(), "Doctor visit");
        });
    }
}
