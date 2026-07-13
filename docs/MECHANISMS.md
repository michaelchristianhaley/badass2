# Mechanisms

Each mechanism states what it is, why it exists, when it applies, who owns it, how it is checked, how it fails, and how it recovers.

## Authority

Prevents The Assistant from silently expanding its role. The User grants authority; The Assistant tracks its limits. Failure requires stop, disclosure, and restoration where possible.

## Grounding

Requires contact with relevant current information before action. `control/inspection.json` maps operation classes to required sources. Missing or falsely claimed inspection is a failure.

## Evidence and Claims

`control/evidence.json` defines evidence strengths and permitted claim labels. Stronger claims require stronger evidence.

## Verification

Checks outcomes against the original objective and acceptance conditions. Command completion alone is insufficient.

## Drift and Thrash

Drift loses the objective. Thrash changes direction without enough new evidence. Recovery returns to the last verified objective and path.

## Generated Views

`MAP.md` is the human repository view. `LANDING_PAD.md` is the complete assistant-readable view. Both are regenerated and byte-compared.

## External Continuity

`control/support.json` detects continuity systems, including owlbox-compatible files, and requires The Assistant to inspect them. BADASS does not own those systems.

## Wins

Wins preserve evidence-backed success without turning it automatically into authority.

## Recovery

Recovery returns failed or uncertain work to verified state and reruns affected gates.
