/*************************
 * Name: 	Bruno Manuel
 * Course: 	CS 320 
 * Date: 	04/08/2026
 * Description: This is the test class for TaskService.
 *************************/

package Test;

import static org.junit.jupiter.api.Assertions.*;

import java.util.Calendar;
import java.util.Date;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import Appointment.Appointment;
import Appointment.AppointmentService;

public class AppointmentServiceTest {

    private Date futureDate() {
        Calendar cal = Calendar.getInstance();
        cal.add(Calendar.DAY_OF_MONTH, 1);
        return cal.getTime();
    }

    private Date anotherFutureDate() {
        Calendar cal = Calendar.getInstance();
        cal.add(Calendar.DAY_OF_MONTH, 2);
        return cal.getTime();
    }

    @Test
    @DisplayName("Test adding an appointment")
    public void testAddAppointment() {
        AppointmentService service = new AppointmentService();
        Appointment appointment = new Appointment("1", futureDate(), "Doctor visit");

        service.addAppointment(appointment);

        assertEquals("1", service.getAppointment("1").getAppointmentID());
    }

    @Test
    @DisplayName("Test deleting an appointment")
    public void testDeleteAppointment() {
        AppointmentService service = new AppointmentService();
        Appointment appointment = new Appointment("1", futureDate(), "Doctor visit");

        service.addAppointment(appointment);
        service.deleteAppointment("1");

        assertNull(service.getAppointment("1"));
    }

    @Test
    @DisplayName("Test duplicate appointment IDs are rejected")
    public void testDuplicateAppointmentID() {
        AppointmentService service = new AppointmentService();
        Appointment appointment1 = new Appointment("1", futureDate(), "Doctor visit");
        Appointment appointment2 = new Appointment("1", anotherFutureDate(), "Dentist visit");

        service.addAppointment(appointment1);

        assertThrows(IllegalArgumentException.class, () -> {
            service.addAppointment(appointment2);
        });
    }

    @Test
    @DisplayName("Test deleting missing appointment throws exception")
    public void testDeleteMissingAppointment() {
        AppointmentService service = new AppointmentService();

        assertThrows(IllegalArgumentException.class, () -> {
            service.deleteAppointment("99");
        });
    }
}