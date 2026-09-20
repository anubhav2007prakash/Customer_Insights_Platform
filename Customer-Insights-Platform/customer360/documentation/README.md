# Customer 360 Engine

The Customer 360 Engine provides a modular foundation for unified customer profiles, identity resolution, lifecycle tracking, scoring, and timeline generation.

## Architecture
- Profiles: create and update a shared customer record.
- Identity: resolve duplicate identities with configurable confidence signals.
- Timeline: store activity events in chronological order.
- Lifecycle: track stages such as lead, active customer, or churned customer.
- Scoring: calculate reusable customer scores from profile completeness and engagement signals.

## Extension Guide
New capabilities can be added by introducing additional services under the domain folders and wiring them through the repository layer.
