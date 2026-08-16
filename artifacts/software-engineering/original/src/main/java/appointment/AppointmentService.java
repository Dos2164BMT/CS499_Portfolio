/*************************
 * Name: 	Bruno Manuel
 * Course: 	CS-320 
 * Date: 	04/08/2026
 * Description: This is the AppointmentService class. It maintains appointments and has capabilities
 * for adding and deleting appointments.
 *************************/

package Appointment;

import java.util.ArrayList;

public class AppointmentService {
	private final ArrayList<Appointment> appointmentList = new ArrayList<>();

	// Add a new appointment if the ID is unique
	public void addAppointment(Appointment appointment) {
		if (appointment == null) {
			throw new IllegalArgumentException("Appointment cannot be null.");
		}

		for (Appointment existingAppointment : appointmentList) {
			if (existingAppointment.getAppointmentID().equals(appointment.getAppointmentID())) {
				throw new IllegalArgumentException("Appointment ID must be unique.");
			}
		}

		appointmentList.add(appointment);
	}

	// Return an appointment by ID, or null if not found
	public Appointment getAppointment(String appointmentID) {
		for (Appointment appointment : appointmentList) {
			if (appointment.getAppointmentID().equals(appointmentID)) {
				return appointment;
			}
		}
		return null;
	}

	// Delete appointment by ID
	public void deleteAppointment(String appointmentID) {
		for (int i = 0; i < appointmentList.size(); i++) {
			if (appointmentList.get(i).getAppointmentID().equals(appointmentID)) {
				appointmentList.remove(i);
				return;
			}
		}

		throw new IllegalArgumentException("Appointment ID not found.");
	}
}