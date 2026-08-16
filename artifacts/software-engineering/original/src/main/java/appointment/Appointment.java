/*************************
 * Name:    Bruno Manuel
 * Course:  CS-320
 * Date:    04/08/2026
 * Description: This is the Appointment class. It creates and stores appointment information.
 *************************/

package Appointment;

import java.util.Date;

public class Appointment {
    private final String appointmentID;
    private final Date appointmentDate;
    private final String appointmentDesc;

    public Appointment(String appointmentID, Date appointmentDate, String appointmentDesc) {
        if (appointmentID == null || appointmentID.length() > 10) {
            throw new IllegalArgumentException("Appointment ID is invalid.");
        }

        if (appointmentDate == null) {
            throw new IllegalArgumentException("Appointment date cannot be null.");
        }

        if (appointmentDate.before(new Date())) {
            throw new IllegalArgumentException("Appointment date cannot be in the past.");
        }

        if (appointmentDesc == null || appointmentDesc.length() > 50) {
            throw new IllegalArgumentException("Appointment description is invalid.");
        }

        this.appointmentID = appointmentID;
        this.appointmentDate = appointmentDate;
        this.appointmentDesc = appointmentDesc;
    }

    public String getAppointmentID() {
        return appointmentID;
    }

    public Date getAppointmentDate() {
        return appointmentDate;
    }

    public String getAppointmentDesc() {
        return appointmentDesc;
    }
}