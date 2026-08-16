# Appointment Service: Software Design and Engineering

This artifact compares the original CS 320 Appointment Service with a reconstructed
enhancement based on the completed CS 499 Milestone Two narrative.

The enhanced project centralizes validation, introduces custom exceptions, injects a
`Clock` for deterministic date testing, makes defensive `Date` copies, adds update and
required-lookup operations, and exposes an immutable collection snapshot.

Run the enhanced tests with Java 17 and Maven:

```bash
cd enhanced
mvn test
```
