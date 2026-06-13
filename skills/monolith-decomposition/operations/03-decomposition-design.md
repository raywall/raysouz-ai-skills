# Operation 03 - Decomposition Design

1. Confirm the user's decomposition axis and constraints again.
2. Use `templates/decomposition-plan.md` and `references/ddd-decomposition.md`.
3. Compare boundary alternatives against registered evidence.
4. Define the context map, ownership, contracts, data authority, consistency needs,
   migration dependencies, and risks.
5. Define the database split strategy when data is affected.
6. Define a reversible transition architecture that preserves approved existing
   routes and contracts during migration.
7. Generate the Mermaid diagrams required by `templates/decomposition-plan.md`.
8. Separate current facts from proposed target decisions.
9. Ask the user to resolve every blocking proposal or gap.
10. In `propose` mode, produce the completed plan and stop before code changes.
11. In `operate` mode, obtain explicit approval for boundaries and extraction order.

Do not generate microservice code before this approval.
