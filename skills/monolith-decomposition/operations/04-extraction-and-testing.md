# Operation 04 - Extraction and Testing

Execute one approved migration slice at a time.

1. Create or complete the service specification using `templates/service-spec.md`.
2. Create the test plan using `templates/test-plan.md`.
3. Add characterization tests around the monolith behavior.
4. Write failing domain and contract tests for the approved target behavior.
5. Generate the smallest service implementation in the user-approved language and
   repository conventions.
6. Run unit, contract, integration, regression, migration, and rollback tests
   applicable to the slice.
7. Compare observable outcomes and record evidence.
8. Stop when behavior diverges or a new business gap appears; ask before continuing.

Do not silently redesign behavior during extraction.
